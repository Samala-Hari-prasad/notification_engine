import hashlib
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings

# -------------------------------------------------------------------
# Fingerprint generation (deterministic SHA‑256)
# -------------------------------------------------------------------
def fingerprint_event(event):
    """Create a deterministic fingerprint for a NotificationEvent.
    Uses dedupe_key if present, otherwise hashes a JSON representation of
    the most important fields.
    """
    if event.dedupe_key:
        return event.dedupe_key
    payload = {
        "user_id": event.user_id,
        "event_type": event.event_type,
        "title": event.title,
        "source": event.source,
        "metadata": event.metadata,
    }
    json_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

# -------------------------------------------------------------------
# Exact duplicate detection
# -------------------------------------------------------------------
def is_exact_duplicate(fingerprint, window_seconds=600):
    """Return True if the fingerprint exists in cache within the window."""
    key = f"dup:{fingerprint}"
    if cache.get(key):
        return True
    # Not seen – store it for future checks
    cache.set(key, 1, timeout=window_seconds)
    return False

# -------------------------------------------------------------------
# Near‑duplicate detection (Bypassed for simple caching backends)
# -------------------------------------------------------------------
def is_near_duplicate(event, similarity_threshold=0.85, recent_seconds=300):
    """Near-duplicate detection logic built for Redis has been turned off
    temporarily to support SQLite and LocMem cache environments.
    """
    return False

# -------------------------------------------------------------------
# Rate‑limit / fatigue counters
# -------------------------------------------------------------------
def exceeds_rate_limits(user_id, event, max_per_10min=3, daily_cap=30):
    """Check if the user has exceeded notification caps using simple cache framework.
    """
    key_10min = f"rate10:{user_id}"
    
    try:
        count_10 = cache.incr(key_10min)
    except ValueError:
        # Cache incr throws ValueError if key doesn't exist in LocMemCache
        cache.set(key_10min, 1, timeout=600)
        count_10 = 1

    if count_10 > max_per_10min:
        return True

    today = datetime.utcnow().strftime('%Y-%m-%d')
    key_daily = f"rate_day:{user_id}:{today}"
    
    try:
        count_day = cache.incr(key_daily)
    except ValueError:
        cache.set(key_daily, 1, timeout=86400)
        count_day = 1

    if count_day > daily_cap:
        return True
        
    return False

# -------------------------------------------------------------------
# Dynamic rule evaluation stub (reads RuleConfig model)
# -------------------------------------------------------------------
from rules.models import RuleConfig
import datetime as dt

def evaluate_rules(event):
    """Placeholder for rule engine.
    Returns a tuple (action, description) where action is one of
    'NOW', 'LATER', 'NEVER' or None if no rule matches.
    """
    now = datetime.utcnow()
    action, description = None, None

    # 1️⃣ Rule: System Alerts Bypass
    if event.event_type == 'system_alert' and event.priority_hint == 'high':
        # Check if the routing rule exists and allows bypass
        rule_qs = RuleConfig.objects.filter(key='system_alert_routing').first()
        if rule_qs and rule_qs.value.get('always_now'):
            return "NOW", "Critical system alert forced immediate delivery (Rule Bypass)"

    # 2️⃣ Rule: Quiet Hours (e.g., Suppress promotions during night)
    rule_qh = RuleConfig.objects.filter(key='quiet_hours').first()
    if rule_qh:
        start_str = rule_qh.value.get('start', '22:00')
        end_str = rule_qh.value.get('end', '08:00')
        start_time = dt.datetime.strptime(start_str, '%H:%M').time()
        end_time = dt.datetime.strptime(end_str, '%H:%M').time()
        
        current_time = now.time()
        in_quiet_time = False
        
        if start_time <= end_time:
            in_quiet_time = start_time <= current_time <= end_time
        else:
            in_quiet_time = current_time >= start_time or current_time <= end_time
            
        if in_quiet_time and event.priority_hint != 'high':
            # Send to deferred queue instead of NEVER
            return "LATER", f"Currently in quiet hours ({start_str} - {end_str}). Scheduled for Later."

    # 3️⃣ Rule: Daily Cap specifically for Marketing
    if event.event_type == 'promotional':
        rule_mx = RuleConfig.objects.filter(key='max_daily_marketing').first()
        if rule_mx:
            limit = rule_mx.value.get('limit', 2)
            today = now.strftime('%Y-%m-%d')
            marketing_key = f"market_cap:{event.user_id}:{today}"
            
            try:
                count = cache.incr(marketing_key)
            except ValueError:
                cache.set(marketing_key, 1, timeout=86400)
                count = 1
                
            if count > limit:
                return "NEVER", f"Max daily marketing limit of {limit} reached."

    return None, None
