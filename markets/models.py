from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account


class Market(models.Model):
    """Prediction market"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('RESOLVED', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    outcome_yes = models.CharField(max_length=100, default="Yes")
    outcome_no = models.CharField(max_length=100, default="No")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    resolution_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_markets')
    
    # Market resolution
    resolved_outcome = models.CharField(max_length=100, blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def current_yes_price(self):
        """Calculate current YES price based on outstanding shares"""
        yes_shares = Share.objects.filter(market=self, outcome='YES').aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        no_shares = Share.objects.filter(market=self, outcome='NO').aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        
        total_shares = yes_shares + no_shares
        if total_shares == 0:
            return 0.50  # Default 50/50 if no trades
        
        return round(yes_shares / total_shares, 4)

    @property
    def current_no_price(self):
        """Calculate current NO price based on outstanding shares"""
        return round(1 - self.current_yes_price, 4)


class Share(models.Model):
    """User's shares in a market"""
    OUTCOME_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='shares')
    outcome = models.CharField(max_length=3, choices=OUTCOME_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    average_price = models.DecimalField(max_digits=6, decimal_places=4, default=0.0000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'market', 'outcome']

    def __str__(self):
        return f"{self.user.username} - {self.market.title} - {self.outcome}: {self.quantity}"

    def add_shares(self, quantity, price):
        """Add shares at a specific price"""
        if self.quantity == 0:
            self.average_price = price
        else:
            # Calculate weighted average
            total_cost = (self.quantity * self.average_price) + (quantity * price)
            self.average_price = total_cost / (self.quantity + quantity)
        
        self.quantity += quantity
        self.save()

    def remove_shares(self, quantity):
        """Remove shares (for selling)"""
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.save()
            return True
        return False


class Order(models.Model):
    """Buy/Sell orders with proper order book functionality"""
    ORDER_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    ORDER_CLASSES = [
        ('MARKET', 'Market Order'),
        ('LIMIT', 'Limit Order'),
    ]

    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('FILLED', 'Filled'),
        ('CANCELLED', 'Cancelled'),
        ('PARTIAL', 'Partially Filled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    order_class = models.CharField(max_length=6, choices=ORDER_CLASSES, default='LIMIT')
    outcome = models.CharField(max_length=3, choices=Share.OUTCOME_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)  # None for market orders
    filled_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    filled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        price_str = f"@ {self.price}" if self.price else "Market"
        return f"{self.user.username} - {self.order_type} {self.quantity} {self.outcome} {price_str}"

    @property
    def remaining_quantity(self):
        return self.quantity - self.filled_quantity

    @property
    def is_market_order(self):
        return self.order_class == 'MARKET'

    @property
    def is_limit_order(self):
        return self.order_class == 'LIMIT'

    def fill_order(self, quantity, fill_price=None):
        """Fill part or all of the order"""
        from django.utils import timezone
        
        if quantity <= self.remaining_quantity:
            self.filled_quantity += quantity
            if self.filled_quantity >= self.quantity:
                self.status = 'FILLED'
                self.filled_at = timezone.now()
            else:
                self.status = 'PARTIAL'
            self.save()
            return True
        return False

    def cancel_order(self):
        """Cancel the order"""
        if self.status in ['PENDING', 'PARTIAL']:
            self.status = 'CANCELLED'
            self.save()
            return True
        return False


class OrderBook(models.Model):
    """Represents the order book for a market outcome"""
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='orderbooks')
    outcome = models.CharField(max_length=3, choices=Share.OUTCOME_CHOICES)
    
    # Best bid/ask prices
    best_bid = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    best_ask = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Volume at best prices
    bid_volume = models.PositiveIntegerField(default=0)
    ask_volume = models.PositiveIntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['market', 'outcome']

    def __str__(self):
        return f"{self.market.title} - {self.outcome}: {self.best_bid}/{self.best_ask}"

    def update_book(self):
        """Update the order book with current best bid/ask"""
        # Get best bid (highest buy price)
        best_bid_order = Order.objects.filter(
            market=self.market,
            outcome=self.outcome,
            order_type='BUY',
            status__in=['PENDING', 'PARTIAL'],
            price__isnull=False
        ).order_by('-price').first()
        
        if best_bid_order:
            self.best_bid = best_bid_order.price
            self.bid_volume = best_bid_order.remaining_quantity
        else:
            self.best_bid = None
            self.bid_volume = 0

        # Get best ask (lowest sell price)
        best_ask_order = Order.objects.filter(
            market=self.market,
            outcome=self.outcome,
            order_type='SELL',
            status__in=['PENDING', 'PARTIAL'],
            price__isnull=False
        ).order_by('price').first()
        
        if best_ask_order:
            self.best_ask = best_ask_order.price
            self.ask_volume = best_ask_order.remaining_quantity
        else:
            self.best_ask = None
            self.ask_volume = 0

        self.save()

    @property
    def spread(self):
        """Calculate the bid-ask spread"""
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None

    @property
    def mid_price(self):
        """Calculate the mid-price"""
        if self.best_bid and self.best_ask:
            return (self.best_bid + self.best_ask) / 2
        elif self.best_bid:
            return self.best_bid
        elif self.best_ask:
            return self.best_ask
        return 0.50  # Default if no orders