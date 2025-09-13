from rest_framework import serializers
from .models import Market, Share, Order, OrderBook


class MarketSerializer(serializers.ModelSerializer):
    current_yes_price = serializers.ReadOnlyField()
    current_no_price = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Market
        fields = [
            'id', 'title', 'description', 'outcome_yes', 'outcome_no',
            'status', 'resolution_date', 'current_yes_price', 'current_no_price',
            'created_by_username', 'created_at', 'resolved_outcome', 'resolved_at'
        ]


class ShareSerializer(serializers.ModelSerializer):
    market_title = serializers.CharField(source='market.title', read_only=True)
    
    class Meta:
        model = Share
        fields = [
            'id', 'market', 'market_title', 'outcome', 'quantity',
            'average_price', 'created_at', 'updated_at'
        ]


class OrderBookSerializer(serializers.ModelSerializer):
    spread = serializers.ReadOnlyField()
    mid_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderBook
        fields = [
            'id', 'market', 'outcome', 'best_bid', 'best_ask',
            'bid_volume', 'ask_volume', 'spread', 'mid_price', 'updated_at'
        ]


class OrderSerializer(serializers.ModelSerializer):
    market_title = serializers.CharField(source='market.title', read_only=True)
    remaining_quantity = serializers.ReadOnlyField()
    is_market_order = serializers.ReadOnlyField()
    is_limit_order = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'market', 'market_title', 'order_type', 'order_class',
            'outcome', 'quantity', 'price', 'filled_quantity', 'remaining_quantity',
            'status', 'is_market_order', 'is_limit_order', 'created_at', 'updated_at', 'filled_at'
        ]


class CreateOrderSerializer(serializers.ModelSerializer):
    order_class = serializers.ChoiceField(choices=Order.ORDER_CLASSES, default='LIMIT')
    
    class Meta:
        model = Order
        fields = ['market', 'order_type', 'order_class', 'outcome', 'quantity', 'price']
    
    def validate(self, data):
        """Validate order data"""
        order_class = data.get('order_class')
        price = data.get('price')
        
        # Market orders don't need a price
        if order_class == 'MARKET':
            data['price'] = None
        elif order_class == 'LIMIT' and price is None:
            raise serializers.ValidationError("Limit orders require a price")
        
        return data


class OrderBookDepthSerializer(serializers.Serializer):
    """Serializer for order book depth data"""
    outcome = serializers.CharField()
    bids = serializers.ListField(child=serializers.DictField())
    asks = serializers.ListField(child=serializers.DictField())
    spread = serializers.DecimalField(max_digits=6, decimal_places=4, allow_null=True)
    mid_price = serializers.DecimalField(max_digits=6, decimal_places=4)
