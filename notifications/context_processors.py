def notification_count(request):
    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            count = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            count = 0
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}
