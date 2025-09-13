from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal
from .models import Market, Share, Order, OrderBook
from .serializers import (
    MarketSerializer, ShareSerializer, OrderSerializer, CreateOrderSerializer,
    OrderBookSerializer, OrderBookDepthSerializer
)
from accounts.models import Account, Transaction


class MarketListView(generics.ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer


class MarketDetailView(generics.RetrieveAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer


class ShareListView(generics.ListAPIView):
    serializer_class = ShareSerializer
    
    def get_queryset(self):
        return Share.objects.filter(user=self.request.user)


class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer


@api_view(['GET'])
def order_book(request, market_id, outcome):
    """Get order book depth for a market outcome"""
    try:
        market = Market.objects.get(id=market_id)
    except Market.DoesNotExist:
        return Response({'error': 'Market not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create order book
    orderbook, created = OrderBook.objects.get_or_create(
        market=market,
        outcome=outcome
    )
    orderbook.update_book()
    
    # Get bid/ask depth
    bids = get_order_depth(market, outcome, 'BUY')
    asks = get_order_depth(market, outcome, 'SELL')
    
    data = {
        'outcome': outcome,
        'bids': bids,
        'asks': asks,
        'spread': orderbook.spread,
        'mid_price': orderbook.mid_price
    }
    
    serializer = OrderBookDepthSerializer(data)
    return Response(serializer.data)


def get_order_depth(market, outcome, order_type, levels=10):
    """Get order book depth for bids or asks"""
    orders = Order.objects.filter(
        market=market,
        outcome=outcome,
        order_type=order_type,
        status__in=['PENDING', 'PARTIAL'],
        price__isnull=False
    ).order_by('-price' if order_type == 'BUY' else 'price')
    
    depth = {}
    for order in orders:
        price = float(order.price)
        if price in depth:
            depth[price] += order.remaining_quantity
        else:
            depth[price] = order.remaining_quantity
    
    # Convert to list and limit levels
    result = []
    sorted_prices = sorted(depth.keys(), reverse=(order_type == 'BUY'))
    
    for price in sorted_prices[:levels]:
        result.append({
            'price': price,
            'quantity': depth[price]
        })
    
    return result


@csrf_exempt
@api_view(['POST'])
def place_order(request):
    """Place a buy or sell order with proper order matching"""
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    market = data['market']
    order_type = data['order_type']
    order_class = data['order_class']
    outcome = data['outcome']
    quantity = data['quantity']
    price = data.get('price')
    
    # Get user account
    account, created = Account.objects.get_or_create(user=request.user)
    
    try:
        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                user=request.user,
                market=market,
                order_type=order_type,
                order_class=order_class,
                outcome=outcome,
                quantity=quantity,
                price=price
            )
            
            # Process the order
            if order_class == 'MARKET':
                result = process_market_order(order, account)
            else:  # LIMIT order
                result = process_limit_order(order, account)
            
            if result['success']:
                # Update order book
                update_order_book(market, outcome)
                
                return Response({
                    'message': result['message'],
                    'order': OrderSerializer(order).data,
                    'fills': result.get('fills', [])
                }, status=status.HTTP_201_CREATED)
            else:
                order.delete()  # Remove failed order
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
    except Exception as e:
        return Response(
            {'error': f'Order processing failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def process_market_order(order, account):
    """Process a market order - fills immediately at best available price"""
    opposite_type = 'SELL' if order.order_type == 'BUY' else 'BUY'
    
    # Validate SELL orders - user must own the shares they're trying to sell
    if order.order_type == 'SELL':
        share, created = Share.objects.get_or_create(
            user=order.user,
            market=order.market,
            outcome=order.outcome,
            defaults={'quantity': 0, 'average_price': Decimal('0.00')}
        )
        if share.quantity < order.quantity:
            return {
                'success': False,
                'error': f'Insufficient shares. You own {share.quantity} shares but trying to sell {order.quantity}'
            }
    
    # Find matching orders
    matching_orders = Order.objects.filter(
        market=order.market,
        outcome=order.outcome,
        order_type=opposite_type,
        status__in=['PENDING', 'PARTIAL'],
        price__isnull=False
    ).exclude(user=order.user).order_by(
        'price' if order.order_type == 'BUY' else '-price'
    )
    
    if not matching_orders.exists():
        return {
            'success': False,
            'error': 'No matching orders available for market order'
        }
    
    remaining_quantity = order.quantity
    total_cost = Decimal('0')
    fills = []
    
    for matching_order in matching_orders:
        if remaining_quantity <= 0:
            break
            
        # Calculate fill quantity
        fill_quantity = min(remaining_quantity, matching_order.remaining_quantity)
        fill_price = matching_order.price
        
        # Check if user can afford the fill
        if order.order_type == 'BUY':
            fill_cost = fill_quantity * fill_price
            if not account.can_afford(total_cost + fill_cost):
                # Partial fill with remaining funds
                max_affordable = int((account.balance - total_cost) / fill_price)
                if max_affordable <= 0:
                    break
                fill_quantity = max_affordable
                fill_cost = fill_quantity * fill_price
            
            total_cost += fill_cost
        
        # Execute the fill
        execute_fill(order, matching_order, fill_quantity, fill_price)
        
        fills.append({
            'price': float(fill_price),
            'quantity': fill_quantity,
            'counterparty': matching_order.user.username
        })
        
        remaining_quantity -= fill_quantity
    
    # Update account balance
    if order.order_type == 'BUY':
        account.deduct_funds(total_cost)
        Transaction.objects.create(
            account=account,
            transaction_type='BUY',
            amount=total_cost,
            description=f'Market buy {order.quantity} {order.outcome} shares in {order.market.title}'
        )
    
    if remaining_quantity > 0:
        order.status = 'PARTIAL'
        order.save()
        return {
            'success': True,
            'message': f'Order partially filled. {order.quantity - remaining_quantity} shares filled.',
            'fills': fills
        }
    else:
        order.status = 'FILLED'
        order.filled_at = timezone.now()
        order.save()
        return {
            'success': True,
            'message': 'Order filled completely.',
            'fills': fills
        }


def process_limit_order(order, account):
    """Process a limit order - adds to order book or fills if price matches"""
    opposite_type = 'SELL' if order.order_type == 'BUY' else 'BUY'
    
    # Check if order can be filled immediately
    matching_orders = Order.objects.filter(
        market=order.market,
        outcome=order.outcome,
        order_type=opposite_type,
        status__in=['PENDING', 'PARTIAL'],
        price__isnull=False
    ).exclude(user=order.user).order_by(
        'price' if order.order_type == 'BUY' else '-price'
    )
    
    # For buy orders, check if our limit price >= ask price
    # For sell orders, check if our limit price <= bid price
    can_fill = False
    if order.order_type == 'BUY':
        best_ask = matching_orders.first()
        can_fill = best_ask and order.price >= best_ask.price
    else:
        best_bid = matching_orders.first()
        can_fill = best_bid and order.price <= best_bid.price
    
    if can_fill:
        # Try to fill the order
        return process_market_order(order, account)
    else:
        # Add to order book (check funds/shares first)
        if order.order_type == 'BUY':
            total_cost = order.quantity * order.price
            if not account.can_afford(total_cost):
                return {
                    'success': False,
                    'error': 'Insufficient funds for limit order'
                }
            # Reserve funds
            account.deduct_funds(total_cost)
            Transaction.objects.create(
                account=account,
                transaction_type='BUY_LIMIT',
                amount=total_cost,
                description=f'Limit buy order: {order.quantity} {order.outcome} @ {order.price} in {order.market.title}'
            )
        else:
            # Check if user has enough shares to sell
            share, created = Share.objects.get_or_create(
                user=order.user,
                market=order.market,
                outcome=order.outcome
            )
            if share.quantity < order.quantity:
                return {
                    'success': False,
                    'error': 'Insufficient shares for limit sell order'
                }
            # Reserve shares
            share.remove_shares(order.quantity)
        
        order.status = 'PENDING'
        order.save()
        
        return {
            'success': True,
            'message': 'Limit order placed in order book.'
        }


def execute_fill(buy_order, sell_order, quantity, price):
    """Execute a trade between two orders"""
    # Update order quantities
    buy_order.fill_order(quantity)
    sell_order.fill_order(quantity)
    
    # Update shares
    if buy_order.order_type == 'BUY':
        # Buyer gets shares
        buy_share, created = Share.objects.get_or_create(
            user=buy_order.user,
            market=buy_order.market,
            outcome=buy_order.outcome
        )
        buy_share.add_shares(quantity, price)
        
        # Seller's account gets funds
        sell_account, created = Account.objects.get_or_create(user=sell_order.user)
        sell_account.add_funds(quantity * price)
        
        Transaction.objects.create(
            account=sell_account,
            transaction_type='SELL',
            amount=quantity * price,
            description=f'Sell {quantity} {sell_order.outcome} shares in {sell_order.market.title}'
        )
    else:
        # Seller gets shares
        sell_share, created = Share.objects.get_or_create(
            user=sell_order.user,
            market=sell_order.market,
            outcome=sell_order.outcome
        )
        sell_share.add_shares(quantity, price)
        
        # Buyer's account gets funds
        buy_account, created = Account.objects.get_or_create(user=buy_order.user)
        buy_account.add_funds(quantity * price)


def update_order_book(market, outcome):
    """Update the order book for a market outcome"""
    orderbook, created = OrderBook.objects.get_or_create(
        market=market,
        outcome=outcome
    )
    orderbook.update_book()


@csrf_exempt
@api_view(['POST'])
def cancel_order(request, order_id):
    """Cancel a pending order"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if order.status not in ['PENDING', 'PARTIAL']:
        return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Refund reserved funds/shares
    account, created = Account.objects.get_or_create(user=request.user)
    
    if order.order_type == 'BUY':
        # Refund reserved funds
        refund_amount = order.remaining_quantity * order.price
        account.add_funds(refund_amount)
        Transaction.objects.create(
            account=account,
            transaction_type='CANCEL_BUY',
            amount=refund_amount,
            description=f'Cancelled buy order: {order.remaining_quantity} {order.outcome} @ {order.price}'
        )
    else:
        # Return reserved shares
        share, created = Share.objects.get_or_create(
            user=order.user,
            market=order.market,
            outcome=order.outcome
        )
        share.add_shares(order.remaining_quantity, order.price)
    
    # Cancel the order
    order.cancel_order()
    
    # Update order book
    update_order_book(order.market, order.outcome)
    
    return Response({'message': 'Order cancelled successfully'})