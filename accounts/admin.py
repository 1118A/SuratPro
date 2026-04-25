from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html, mark_safe
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = [
        'avatar_thumb', 'username', 'full_name', 'email',
        'role_badge', 'verified_badge', 'is_active', 'created_at',
    ]
    list_display_links = ['username', 'full_name']
    list_filter   = ['role', 'is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering      = ['-date_joined']
    list_per_page = 25
    date_hierarchy = 'date_joined'
    save_on_top   = True

    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'avatar'),
        }),
        ('Role & Profile', {
            'fields': ('role', 'bio', 'phone', 'location', 'website', 'is_verified'),
        }),
        ('Payments & Registration', {
            'fields': ('has_paid_registration', 'wallet_balance', 'first_project_completed'),
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        ('Account Setup', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    # ---- Custom display methods ----

    @admin.display(description='')
    def avatar_thumb(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="34" height="34" '
                'style="border-radius:50%;object-fit:cover;border:2px solid #e2e8f0;" />',
                obj.avatar.url,
            )
        # Build initials safely
        initials = ((obj.first_name[:1] if obj.first_name else '')
                    + (obj.last_name[:1] if obj.last_name else '')).upper()
        if not initials:
            initials = obj.username[:2].upper()
        return format_html(
            '<div style="width:34px;height:34px;border-radius:50%;'
            'background:linear-gradient(135deg,#2563eb,#7c3aed);'
            'display:flex;align-items:center;justify-content:center;'
            'color:#fff;font-size:12px;font-weight:700;">{}</div>',
            initials,
        )

    @admin.display(description='Name', ordering='first_name')
    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else '—'

    @admin.display(description='Role')
    def role_badge(self, obj):
        colors = {
            'freelancer': ('#dbeafe', '#1d4ed8'),
            'client':     ('#ede9fe', '#6d28d9'),
        }
        bg, fg = colors.get(obj.role, ('#f1f5f9', '#475569'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:20px;font-size:11px;font-weight:700;">{}</span>',
            bg, fg, obj.get_role_display(),
        )

    @admin.display(description='Verified', boolean=True)
    def verified_badge(self, obj):
        return obj.is_verified
