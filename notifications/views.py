from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import Notification


@login_required
def notification_list_view(request):
    """List all notifications grouped by recency; mark all unread as read on open."""
    from django.utils.timezone import now, timedelta
    notifs = request.user.notifications.all()

    # Mark unread as read
    notifs.filter(is_read=False).update(is_read=True)

    today_start     = now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    today_notifs     = notifs.filter(created_at__gte=today_start)
    yesterday_notifs = notifs.filter(created_at__gte=yesterday_start, created_at__lt=today_start)
    older_notifs     = notifs.filter(created_at__lt=yesterday_start)

    return render(request, 'notifications/notification_list.html', {
        'today_notifs':     today_notifs,
        'yesterday_notifs': yesterday_notifs,
        'older_notifs':     older_notifs,
        'total_count':      notifs.count(),
    })


@login_required
def notification_mark_read_view(request, pk):
    """Mark a specific notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
def mark_all_read_view(request):
    """Phase 8: Mark all notifications as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


@login_required
def unread_notif_count_api(request):
    """Phase 8: JSON API — returns unread notification count."""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread': count})

