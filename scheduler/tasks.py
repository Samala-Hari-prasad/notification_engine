import logging
from django.utils import timezone
from .models import DeferredNotification
from engine.services import decide_notification

logger = logging.getLogger(__name__)

def process_due_deferred():
    now = timezone.now()
    due = DeferredNotification.objects.filter(status='PENDING', scheduled_for__lte=now)
    for defer in due:
        try:
            classification, explanation = decide_notification(defer.event)
            if classification == 'NOW':
                defer.status = 'DELIVERED'
                logger.info(f'Delivered deferred event {defer.event.id}')
            elif classification == 'NEVER':
                defer.status = 'DROPPED'
                logger.info(f'Dropped deferred event {defer.event.id}')
            else:
                defer.scheduled_for = now + timezone.timedelta(minutes=5)
                defer.retry_count += 1
                logger.info(f'Rescheduled deferred event {defer.event.id}')
            defer.save()
        except Exception as exc:
            logger.exception(f'Error processing deferred {defer.id}: {exc}')
            if defer.retry_count >= 3:
                defer.status = 'EXPIRED'
                defer.save()
