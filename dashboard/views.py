from django.shortcuts import render
from rules.models import RuleConfig
from audit.models import DecisionRecord
from scheduler.models import DeferredNotification

def dashboard_home(request):
    return render(request, 'dashboard/base.html')

def rule_list(request):
    rules = RuleConfig.objects.all()
    return render(request, 'dashboard/rule_list.html', {'rules': rules})

def audit_log(request):
    decisions = DecisionRecord.objects.select_related('event').order_by('-timestamp')[:100]
    return render(request, 'dashboard/audit_log.html', {'decisions': decisions})

def deferred_queue(request):
    pending = DeferredNotification.objects.filter(status='PENDING').order_by('scheduled_for')
    return render(request, 'dashboard/defer_queue.html', {'pending': pending})
