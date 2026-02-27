from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('rules/', views.rule_list, name='rules'),
    path('audit/', views.audit_log, name='audit'),
    path('deferred/', views.deferred_queue, name='deferred'),
]
