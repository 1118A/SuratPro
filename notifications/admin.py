from django.contrib import admin
from django.utils.html import format_html
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'title', 'type_badge', 'read_badge', 'created_at']
    list_filter   = ['notif_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    ordering      = ['-created_at']
    list_per_page = 30
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    actions       = ['mark_as_read', 'mark_as_unread']

    fieldsets = (
        ('Recipient', {'fields': ('user',)}),
        ('Content',   {'fields': ('title', 'message', 'notif_type', 'link')}),
        ('Status',    {'fields': ('is_read', 'created_at')}),
    )

    @admin.display(description='Type')
    def type_badge(self, obj):
        palette = {
            'info':    ('#dbeafe', '#1d4ed8', 'Info'),
            'success': ('#d1fae5', '#065f46', 'Success'),
            'warning': ('#fef3c7', '#92400e', 'Warning'),
            'error':   ('#fee2e2', '#991b1b', 'Error'),
        }
        bg, fg, label = palette.get(obj.notif_type, ('#f1f5f9', '#475569', obj.notif_type))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description='Read', boolean=True)
    def read_badge(self, obj):
        return obj.is_read

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} notification(s) marked as read.')

    @admin.action(description='Mark selected notifications as unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} notification(s) marked as unread.')
