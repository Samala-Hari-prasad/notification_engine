import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_engine.settings')
django.setup()

from api.models import NotificationEvent
from rules.models import RuleConfig
from audit.models import DecisionRecord
from scheduler.models import DeferredNotification

def clear_existing_data():
    DecisionRecord.objects.all().delete()
    DeferredNotification.objects.all().delete()
    NotificationEvent.objects.all().delete()
    print('🧹 Cleared existing notifications and audits')

def create_dataset_marketing(base_date):
    """Creates a dataset for marketing notifications, typically lower priority."""
    print("📈 Generating Marketing Dataset...")
    for i in range(20):
        ts = base_date - timedelta(days=random.randint(0, 5), hours=random.randint(10, 18))
        NotificationEvent.objects.create(
            user_id=f'user{random.randint(1, 10)}',
            event_type='promotional',
            title=f'Spring Sale Offer {i}',
            source='marketing_platform',
            priority_hint='low',
            timestamp=ts,
            channel='email',
            metadata={'campaign': 'spring_2026', 'discount': '20%'},
        )

def create_dataset_system_alerts(base_date):
    """Creates a dataset for system alerts, typically higher priority and near real-time."""
    print("⚙️ Generating System Alerts Dataset...")
    for i in range(15):
        ts = base_date - timedelta(hours=random.randint(0, 48), minutes=random.randint(0, 59))
        NotificationEvent.objects.create(
            user_id=f'admin{random.randint(1, 3)}',
            event_type='system_alert',
            title=f'High CPU Usage on Node {i}',
            source='monitoring_system',
            priority_hint='high',
            timestamp=ts,
            channel='sms',
            metadata={'node': f'app-node-{i}', 'cpu_percent': random.randint(85, 99)},
        )

def create_dataset_user_activity(base_date):
    """Creates a dataset of user activity notifications (e.g., likes, comments)."""
    print("👤 Generating User Activity Dataset...")
    for i in range(25):
        ts = base_date - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
        NotificationEvent.objects.create(
            user_id=f'user{random.randint(1, 15)}',
            event_type='social_interaction',
            title=f'Someone liked your post {i}',
            source='app_frontend',
            priority_hint='medium',
            timestamp=ts,
            channel='push',
            metadata={'post_id': i, 'interaction_type': 'like'},
        )

def create_rules():
    """Create example RuleConfig entries with distinct requirements."""
    RuleConfig.objects.update_or_create(
        key='max_daily_marketing',
        defaults={
            'value': {'limit': 2},
            'description': 'Max 2 marketing emails per user per day',
        },
    )
    RuleConfig.objects.update_or_create(
        key='quiet_hours',
        defaults={
            'value': {'start': '22:00', 'end': '08:00'},
            'description': 'Do not deliver non-high-priority notifications during night hours',
        },
    )
    RuleConfig.objects.update_or_create(
        key='system_alert_routing',
        defaults={
            'value': {'always_now': True, 'escalate_if_unseen': True},
            'description': 'System alerts bypass quiet hours and daily limits',
        },
    )
    print('✅ Created RuleConfig requirements')

if __name__ == '__main__':
    clear_existing_data()
    # Use timezone-aware datetime
    now = timezone.now()
    create_dataset_marketing(now)
    create_dataset_system_alerts(now)
    create_dataset_user_activity(now)
    create_rules()
    
    total = NotificationEvent.objects.count()
    print(f'✅ Successfully generated a total of {total} categorized notifications.')
