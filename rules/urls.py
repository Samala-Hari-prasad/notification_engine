from django.urls import path
from . import views

urlpatterns = [
    path('', views.rule_list_json, name='rule-list-json'),
]
