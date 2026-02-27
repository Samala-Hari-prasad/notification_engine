from django.urls import path
from . import views

urlpatterns = [
    path('records/', views.audit_list, name='audit-list'),
]
