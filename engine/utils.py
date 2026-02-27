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
def evaluate_rules(event):
    """Placeholder for rule engine.
    Returns a tuple (action, description) where action is one of
    'NOW', 'LATER', 'NEVER' or None if no rule matches.
    """
    return None, None
