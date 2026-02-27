import hashlib
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from .utils import fingerprint_event, is_exact_duplicate, is_near_duplicate, exceeds_rate_limits, evaluate_rules
from api.models import NotificationEvent
from audit.models import DecisionRecord


def decide_notification(event: NotificationEvent):
    """Core decision function returning (classification, explanation)."""
    # 1️⃣ Fingerprint / dedupe
    fp = fingerprint_event(event)
    if is_exact_duplicate(fp):
        explanation = "Exact duplicate within configured window."
        classification = "NEVER"
        _log_decision(event, classification, explanation, duplicate='exact')
        return classification, explanation

    if is_near_duplicate(event):
        explanation = "Near‑duplicate detected (similar title/content)."
        classification = "NEVER"
        _log_decision(event, classification, explanation, duplicate='near')
        return classification, explanation

    # 2️⃣ Fatigue / rate‑limit counters (cached per user)
    if exceeds_rate_limits(event.user_id, event):
        explanation = "Rate‑limit exceeded (max notifications per interval)."
        classification = "NEVER"
        _log_decision(event, classification, explanation, duplicate=None)
        return classification, explanation

    # 3️⃣ Priority hint / business rules
    if event.priority_hint and event.priority_hint.lower() == 'critical':
        explanation = "Critical hint – forced immediate delivery."
        classification = "NOW"
        _log_decision(event, classification, explanation)
        return classification, explanation

    # 4️⃣ Evaluate dynamic rules (stored in RuleConfig model)
    rule_action, rule_desc = evaluate_rules(event)
    if rule_action:
        explanation = f"Rule triggered: {rule_desc}"
        classification = rule_action
        _log_decision(event, classification, explanation)
        return classification, explanation

    # 5️⃣ Default fallback – send now
    explanation = "No rule matched – default to immediate delivery."
    classification = "NOW"
    _log_decision(event, classification, explanation)
    return classification, explanation


def _log_decision(event, classification, explanation, duplicate=None):
    """Persist a DecisionRecord for audit and explainability."""
    DecisionRecord.objects.create(
        event=event,
        classification=classification,
        explanation=explanation,
        duplicate_result=duplicate,
        timestamp=datetime.utcnow()
    )
