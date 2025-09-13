from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer


class AccountDetailView(generics.RetrieveAPIView):
    serializer_class = AccountSerializer
    
    def get_object(self):
        account, created = Account.objects.get_or_create(user=self.request.user)
        return account


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        account, created = Account.objects.get_or_create(user=self.request.user)
        return account.transactions.all().order_by('-created_at')


@api_view(['POST'])
def add_funds(request):
    """Add virtual funds to user account"""
    amount = request.data.get('amount', 0)
    
    if amount <= 0:
        return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    
    account, created = Account.objects.get_or_create(user=request.user)
    account.add_funds(amount)
    
    # Create transaction record
    Transaction.objects.create(
        account=account,
        transaction_type='DEPOSIT',
        amount=amount,
        description=f'Admin added ${amount}'
    )
    
    return Response({'message': f'Added ${amount} to account', 'new_balance': account.balance})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        account, created = Account.objects.get_or_create(user=user)
        return Response({'message': 'Login successful'})
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    """Logout endpoint"""
    logout(request)
    return Response({'message': 'Logout successful'})


@csrf_exempt
@api_view(['POST'])
def register_view(request):
    """Register endpoint"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not all([username, email, password]):
        return Response({'error': 'Username, email, and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    account, created = Account.objects.get_or_create(user=user)
    
    return Response({'message': 'Registration successful'})