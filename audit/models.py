from django.db import models
from django.utils import timezone
from api.models import NotificationEvent

class DecisionRecord(models.Model):
    CLASSIFICATION_CHOICES = [
        ('NOW', 'Now'),
        ('LATER', 'Later'),
        ('NEVER', 'Never'),
    ]

    event = models.ForeignKey(NotificationEvent, on_delete=models.CASCADE, related_name='decisions')
    classification = models.CharField(max_length=6, choices=CLASSIFICATION_CHOICES)
    explanation = models.TextField()
    duplicate_result = models.CharField(max_length=10, null=True, blank=True)
    rules_triggered = models.JSONField(default=dict, blank=True)
    fatigue_snapshot = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.event.id} → {self.classification} @ {self.timestamp}"
