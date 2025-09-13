from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.AccountDetailView.as_view(), name='account-detail'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('add-funds/', views.add_funds, name='add-funds'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
