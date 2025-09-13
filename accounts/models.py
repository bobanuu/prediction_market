from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    """User account with virtual currency balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ${self.balance}"

    def can_afford(self, amount):
        """Check if account has enough balance for a transaction"""
        return self.balance >= amount

    def add_funds(self, amount):
        """Add funds to account"""
        self.balance += amount
        self.save()

    def deduct_funds(self, amount):
        """Deduct funds from account"""
        if self.can_afford(amount):
            self.balance -= amount
            self.save()
            return True
        return False


class Transaction(models.Model):
    """Transaction history for account"""
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('BUY', 'Buy Shares'),
        ('SELL', 'Sell Shares'),
        ('REFUND', 'Refund'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.user.username} - {self.transaction_type} - ${self.amount}"