from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
from markets.models import Market, Order, Share, OrderBook
from accounts.models import Account


class Command(BaseCommand):
    help = 'Seed markets with initial liquidity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--market-id',
            type=int,
            help='Seed specific market by ID',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=10.0,
            help='Amount in dollars to seed each side (default: 10.0)',
        )

    def handle(self, *args, **options):
        market_id = options.get('market_id')
        seed_amount = Decimal(str(options['amount']))
        
        # Create or get the liquidity provider user
        liquidity_user, created = User.objects.get_or_create(
            username='liquidity_provider',
            defaults={
                'email': 'liquidity@predictionmarket.com',
                'first_name': 'Liquidity',
                'last_name': 'Provider',
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f'Created liquidity provider user: {liquidity_user.username}')
        
        # Create account for liquidity provider
        liquidity_account, created = Account.objects.get_or_create(
            user=liquidity_user,
            defaults={'balance': Decimal('10000.00')}  # Give them plenty of funds
        )
        
        if created:
            self.stdout.write(f'Created liquidity account with balance: ${liquidity_account.balance}')
        
        # Get markets to seed
        if market_id:
            markets = Market.objects.filter(id=market_id)
        else:
            markets = Market.objects.all()
        
        if not markets.exists():
            self.stdout.write(self.style.WARNING('No markets found to seed'))
            return
        
        seeded_count = 0
        
        for market in markets:
            self.stdout.write(f'Seeding market: {market.title}')
            
            try:
                with transaction.atomic():
                    # Seed YES outcome
                    self.seed_outcome_liquidity(
                        market, 'YES', liquidity_user, liquidity_account, seed_amount
                    )
                    
                    # Seed NO outcome  
                    self.seed_outcome_liquidity(
                        market, 'NO', liquidity_user, liquidity_account, seed_amount
                    )
                    
                    # Update order books
                    for outcome in ['YES', 'NO']:
                        orderbook, created = OrderBook.objects.get_or_create(
                            market=market,
                            outcome=outcome
                        )
                        orderbook.update_book()
                    
                    seeded_count += 1
                    self.stdout.write(f'  ✓ Seeded {market.title}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed to seed {market.title}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {seeded_count} markets')
        )

    def seed_outcome_liquidity(self, market, outcome, user, account, seed_amount):
        """Seed liquidity for a specific market outcome"""
        # Calculate number of shares (assuming $0.50 per share)
        shares_per_side = int(seed_amount / Decimal('0.50'))
        
        # Create bid orders (buy orders) - slightly below 50¢
        bid_price = Decimal('0.49')
        buy_order = Order.objects.create(
            user=user,
            market=market,
            order_type='BUY',
            order_class='LIMIT',
            outcome=outcome,
            quantity=shares_per_side,
            price=bid_price,
            status='PENDING'
        )
        
        # Create ask orders (sell orders) - slightly above 50¢
        ask_price = Decimal('0.51')
        sell_order = Order.objects.create(
            user=user,
            market=market,
            order_type='SELL',
            order_class='LIMIT',
            outcome=outcome,
            quantity=shares_per_side,
            price=ask_price,
            status='PENDING'
        )
        
        # Reserve funds for the buy order
        total_cost = shares_per_side * bid_price
        account.deduct_funds(total_cost)
        
        # Create initial shares for the sell order (the liquidity provider needs to own shares to sell them)
        share, created = Share.objects.get_or_create(
            user=user,
            market=market,
            outcome=outcome,
            defaults={'quantity': 0, 'average_price': Decimal('0.50')}
        )
        share.add_shares(shares_per_side, Decimal('0.50'))
        
        self.stdout.write(f'    Created {shares_per_side} share bid @ {bid_price}¢ and ask @ {ask_price}¢ for {outcome}')
