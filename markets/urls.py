from django.urls import path
from . import views

urlpatterns = [
    path('markets/', views.MarketListView.as_view(), name='market-list'),
    path('markets/<int:pk>/', views.MarketDetailView.as_view(), name='market-detail'),
    path('shares/', views.ShareListView.as_view(), name='share-list'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel-order'),
    path('place-order/', views.place_order, name='place-order'),
    path('markets/<int:market_id>/orderbook/<str:outcome>/', views.order_book, name='order-book'),
]
