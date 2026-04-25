from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_type', 'amount', 'fee', 'status', 'created_at')
    list_filter = ('payment_type', 'status', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
