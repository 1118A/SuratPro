from django.contrib import admin
from django.utils.html import format_html
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = ['title', 'client', 'status_badge', 'budget_display', 'proposal_count', 'views_count', 'created_at']
    list_filter   = ['status', 'budget_type', 'experience_level', 'created_at']
    search_fields = ['title', 'description', 'client__username']
    ordering      = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    filter_horizontal = ['skills_required']
    readonly_fields   = ['views_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Job Info',    {'fields': ('client', 'title', 'description', 'skills_required')}),
        ('Budget',      {'fields': ('budget_type', 'budget_min', 'budget_max', 'deadline', 'experience_level')}),
        ('Status',      {'fields': ('status',)}),
        ('Metadata',    {'classes': ('collapse',), 'fields': ('views_count', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'open':        ('#d1fae5', '#065f46', 'Open'),
            'in_progress': ('#dbeafe', '#1d4ed8', 'In Progress'),
            'closed':      ('#f1f5f9', '#64748b', 'Closed'),
        }
        bg, fg, label = colors.get(obj.status, ('#f1f5f9', '#64748b', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description='Budget')
    def budget_display(self, obj):
        return obj.budget_display

    @admin.display(description='Proposals')
    def proposal_count(self, obj):
        return obj.proposal_count
