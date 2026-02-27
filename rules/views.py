from django.http import JsonResponse
from .models import RuleConfig

def rule_list_json(request):
    data = {rc.key: rc.value for rc in RuleConfig.objects.all()}
    return JsonResponse(data, safe=False)
