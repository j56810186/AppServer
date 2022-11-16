from django.contrib import admin
from market.models import Wallet

# Register your models here.
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    search_fields = ['name', 'user']
    list_filter = ['name', 'balance']
    list_display = ['name', 'balance', 'user']