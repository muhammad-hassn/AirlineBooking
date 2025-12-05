from django.contrib import admin
from .models import UserContact, PaymentAttempt, UserProfile

@admin.register(UserContact)
class UserContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'country', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('country', 'created_at')

@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'route', 'timestamp')
    list_filter = ('status', 'timestamp', 'currency')
    search_fields = ('user__name', 'user__email', 'route')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'postal_code', 'phone')
    search_fields = ('user__username', 'user__email', 'country')
