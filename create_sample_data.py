#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prediction_marketplace.settings')
django.setup()

from django.contrib.auth.models import User
from markets.models import Market
from accounts.models import Account
from django.db import transaction
from decimal import Decimal

def create_sample_data():
    # Create sample users if they don't exist
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Create regular user
    user, created = User.objects.get_or_create(
        username='trader1',
        defaults={
            'email': 'trader1@example.com'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    
    # Create accounts for users
    Account.objects.get_or_create(user=admin_user, defaults={'balance': 10000.00})
    Account.objects.get_or_create(user=user, defaults={'balance': 1000.00})
    
    # Create sample markets
    markets_data = [
        {
            'title': 'Will Bitcoin reach $100,000 by end of 2024?',
            'description': 'This market will resolve to YES if Bitcoin reaches $100,000 or higher by December 31, 2024.',
            'outcome_yes': 'Yes - Bitcoin reaches $100,000+',
            'outcome_no': 'No - Bitcoin stays below $100,000',
            'resolution_date': datetime.now() + timedelta(days=30)
        },
        {
            'title': 'Will it rain in New York tomorrow?',
            'description': 'This market will resolve to YES if there is measurable precipitation in New York City on the day after market creation.',
            'outcome_yes': 'Yes - It will rain',
            'outcome_no': 'No - It will not rain',
            'resolution_date': datetime.now() + timedelta(days=1)
        },
        {
            'title': 'Will the S&P 500 close above 5000 by year end?',
            'description': 'This market will resolve to YES if the S&P 500 index closes at or above 5000 on December 31, 2024.',
            'outcome_yes': 'Yes - S&P 500 >= 5000',
            'outcome_no': 'No - S&P 500 < 5000',
            'resolution_date': datetime.now() + timedelta(days=60)
        }
    ]
    
    for market_data in markets_data:
        market, created = Market.objects.get_or_create(
            title=market_data['title'],
            defaults={
                'description': market_data['description'],
                'outcome_yes': market_data['outcome_yes'],
                'outcome_no': market_data['outcome_no'],
                'resolution_date': market_data['resolution_date'],
                'created_by': admin_user
            }
        )
        if created:
            print(f"Created market: {market.title}")
            # Seed the new market with liquidity
            seed_market_liquidity(market, admin_user)
    
    print("Sample data created successfully!")
    print(f"Admin user: admin / admin123")
    print(f"Regular user: trader1 / password123")

def seed_market_liquidity(market, user):
    """Seed a market with initial liquidity"""
    try:
        # Get or create liquidity provider account
        liquidity_account, created = Account.objects.get_or_create(
            user=user,
            defaults={'balance': Decimal('10000.00')}
        )
        
        # Seed each outcome with $10 worth of liquidity
        seed_amount = Decimal('10.00')
        shares_per_side = int(seed_amount / Decimal('0.50'))
        
        for outcome in ['YES', 'NO']:
            # Create bid order (buy) at 49¢
            from markets.models import Order, Share
            Order.objects.create(
                user=user,
                market=market,
                order_type='BUY',
                order_class='LIMIT',
                outcome=outcome,
                quantity=shares_per_side,
                price=Decimal('0.49'),
                status='PENDING'
            )
            
            # Create ask order (sell) at 51¢
            Order.objects.create(
                user=user,
                market=market,
                order_type='SELL',
                order_class='LIMIT',
                outcome=outcome,
                quantity=shares_per_side,
                price=Decimal('0.51'),
                status='PENDING'
            )
            
            # Create shares for the sell orders
            share, created = Share.objects.get_or_create(
                user=user,
                market=market,
                outcome=outcome,
                defaults={'quantity': 0, 'average_price': Decimal('0.50')}
            )
            share.add_shares(shares_per_side, Decimal('0.50'))
            
            # Reserve funds for buy orders
            liquidity_account.deduct_funds(shares_per_side * Decimal('0.49'))
        
        print(f"  Seeded {market.title} with initial liquidity")
        
    except Exception as e:
        print(f"  Failed to seed {market.title}: {str(e)}")

if __name__ == '__main__':
    create_sample_data()
