from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIF_INFO = 'info'
    NOTIF_SUCCESS = 'success'
    NOTIF_WARNING = 'warning'
    NOTIF_ERROR = 'error'

    NOTIF_TYPES = [
        (NOTIF_INFO, 'Info'),
        (NOTIF_SUCCESS, 'Success'),
        (NOTIF_WARNING, 'Warning'),
        (NOTIF_ERROR, 'Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES, default=NOTIF_INFO)
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username}: {self.title}'
