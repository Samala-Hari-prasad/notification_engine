from django.db import models
from django.utils import timezone
from api.models import NotificationEvent

class DeferredNotification(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('EXPIRED', 'Expired'),
        ('DELIVERED', 'Delivered'),
        ('DROPPED', 'Dropped'),
    ]

    event = models.ForeignKey(NotificationEvent, on_delete=models.CASCADE, related_name='deferred')
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    retry_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Deferred {self.event.id} - {self.scheduled_for} [{self.status}]'
