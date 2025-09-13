from django.contrib import admin
from .models import Market, Share, Order


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'resolution_date', 'created_by', 'created_at']
    list_filter = ['status', 'created_at', 'resolution_date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'current_yes_price', 'current_no_price']
    fieldsets = (
        ('Market Information', {
            'fields': ('title', 'description', 'outcome_yes', 'outcome_no')
        }),
        ('Status', {
            'fields': ('status', 'resolution_date', 'resolved_outcome', 'resolved_at')
        }),
        ('Pricing', {
            'fields': ('current_yes_price', 'current_no_price'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['user', 'market', 'outcome', 'quantity', 'average_price', 'updated_at']
    list_filter = ['outcome', 'market', 'created_at']
    search_fields = ['user__username', 'market__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'market', 'order_type', 'outcome', 'quantity', 'price', 'status', 'created_at']
    list_filter = ['order_type', 'outcome', 'status', 'created_at']
    search_fields = ['user__username', 'market__title']
    readonly_fields = ['created_at', 'updated_at', 'filled_quantity', 'remaining_quantity']