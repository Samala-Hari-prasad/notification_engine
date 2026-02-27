from django.http import JsonResponse
from .models import DecisionRecord

def audit_list(request):
    records = DecisionRecord.objects.select_related('event').order_by('-timestamp')[:50]
    data = [{
        'event_id': r.event.id,
        'user_id': r.event.user_id,
        'classification': r.classification,
        'explanation': r.explanation,
        'timestamp': r.timestamp.isoformat()
    } for r in records]
    return JsonResponse(data, safe=False)
