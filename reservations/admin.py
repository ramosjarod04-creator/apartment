from django.contrib import admin
from .models import Apartment, Reservation, Tenant, Notification, Conversation, Message

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'name', 'apartment_type', 'floor', 'status', 'price_per_month']
    list_filter = ['status', 'apartment_type', 'floor']
    search_fields = ['unit_number', 'name', 'description']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'apartment', 'check_in', 'status', 'created_at']  # REMOVED: 'check_out', 'months'
    list_filter = ['status', 'check_in', 'created_at']  # REMOVED: 'check_out'
    search_fields = ['user__username', 'apartment__unit_number']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'id_number', 'created_at']
    search_fields = ['user__username', 'phone', 'id_number']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'created_at', 'updated_at']
    search_fields = ['subject']
    filter_horizontal = ['participants']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'content']