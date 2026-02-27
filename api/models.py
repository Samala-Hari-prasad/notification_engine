from django.db import models
from django.db.models import JSONField

class NotificationEvent(models.Model):
    user_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255, blank=True, null=True)
    priority_hint = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField()
    channel = models.CharField(max_length=20)
    metadata = JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user_id} - {self.event_type} - {self.title}"
