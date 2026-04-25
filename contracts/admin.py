from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'client', 'freelancer', 'status', 'agreed_amount', 'deadline')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'client__username', 'freelancer__username')
