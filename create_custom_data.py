import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_engine.settings')
django.setup()

from api.models import NotificationEvent
from rules.models import RuleConfig

def create_notifications():
    """Create a set of sample NotificationEvent records spread across dates.
    Generates 30 events with timestamps ranging from today back up to 10 days.
    """
    base = datetime.now()
    sources = ['system', 'user', 'external']
    channels = ['email', 'push', 'sms']
    for i in range(30):
        ts = base - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))
        NotificationEvent.objects.create(
            user_id=f'user{i % 5}',
            event_type=random.choice(['email', 'sms', 'push']),
            title=f'Event {i}',
            source=random.choice(sources),
            priority_hint=random.choice(['high', 'medium', 'low']),
            timestamp=ts,
            channel=random.choice(channels),
            metadata={},
        )
    print('✅ Created 30 NotificationEvent records')

def create_rules():
    """Create a few example RuleConfig entries.
    These illustrate how rules can be stored and later evaluated.
    """
    RuleConfig.objects.get_or_create(
        key='max_daily',
        defaults={
            'value': {'limit': 5},
            'description': 'Maximum notifications per user per day',
        },
    )
    RuleConfig.objects.get_or_create(
        key='quiet_hours',
        defaults={
            'value': {'start': '22:00', 'end': '07:00'},
            'description': 'Do not deliver notifications during night hours',
        },
    )
    print('✅ Created example RuleConfig entries')

if __name__ == '__main__':
    create_notifications()
    create_rules()
