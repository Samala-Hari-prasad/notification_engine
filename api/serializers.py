from rest_framework import serializers
from .models import NotificationEvent

class NotificationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEvent
        fields = ['id', 'user_id', 'event_type', 'title', 'source', 'priority_hint',
                  'timestamp', 'channel', 'metadata', 'dedupe_key', 'expires_at']
