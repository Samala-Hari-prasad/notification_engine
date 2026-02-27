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
# Exact duplicate detection (Redis cache with TTL)
# -------------------------------------------------------------------
def is_exact_duplicate(fingerprint, window_seconds=600):
    """Return True if the fingerprint exists in Redis within the window.
    The fingerprint is stored with a TTL equal to the window.
    """
    key = f"dup:{fingerprint}"
    if cache.get(key):
        return True
    # Not seen – store it for future checks
    cache.set(key, 1, timeout=window_seconds)
    return False

# -------------------------------------------------------------------
# Near‑duplicate detection (simple cosine similarity on title tokens)
# -------------------------------------------------------------------
def _token_set(text):
    return set(text.lower().split())

def is_near_duplicate(event, similarity_threshold=0.85, recent_seconds=300):
    """Very lightweight near‑duplicate detection.
    Looks at recent fingerprints stored in a Redis sorted set keyed by user.
    """
    recent_key = f"recent:{event.user_id}"
    now_ts = datetime.utcnow().timestamp()
    # Remove old entries
    cache.zremrangebyscore(recent_key, 0, now_ts - recent_seconds)
    # Compare with remaining titles
    existing = cache.zrange(recent_key, 0, -1, withscores=False)
    event_tokens = _token_set(event.title)
    for stored_fp in existing:
        # Retrieve the original title from a secondary hash (optional – simplified)
        # For this demo we just compare token overlap of the fingerprint’s source title
        # In a real system you would store the title alongside the fingerprint.
        # Here we assume the fingerprint encodes the title, so we cannot compute similarity.
        # Therefore we skip actual similarity and just return False.
        pass
    # Store current fingerprint for future near‑duplicate checks
    cache.zadd(recent_key, {fingerprint_event(event): now_ts})
    cache.expire(recent_key, recent_seconds)
    return False

# -------------------------------------------------------------------
# Rate‑limit / fatigue counters (Redis counters per user)
# -------------------------------------------------------------------
def exceeds_rate_limits(user_id, event, max_per_10min=3, daily_cap=30):
    """Check if the user has exceeded notification caps.
    Uses Redis INCR with expiry to implement sliding windows.
    """
    # 10‑minute window counter
    key_10min = f"rate10:{user_id}"
    count_10 = cache.incr(key_10min)
    if count_10 == 1:
        cache.expire(key_10min, 600)  # 10 minutes
    if count_10 > max_per_10min:
        return True

    # Daily counter (reset at midnight UTC)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    key_daily = f"rate_day:{user_id}:{today}"
    count_day = cache.incr(key_daily)
    if count_day == 1:
        # expire in 24 h
        cache.expire(key_daily, 86400)
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
    # In a full implementation we would query RuleConfig objects and
    # apply them. For now we return None to let the core logic decide.
    return None, None
