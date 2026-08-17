from django.contrib import admin
from .models import Transaction, UserProfile


class TransactionInline(admin.TabularInline):
  model = Transaction
  extra = 50  # This creates 50 blank rows for you to fill in at once


class UserProfileAdmin(admin.ModelAdmin):
  inlines = [TransactionInline]


admin.site.register(UserProfile, UserProfileAdmin)