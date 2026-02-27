from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationEventViewSet

router = DefaultRouter()
router.register(r'events', NotificationEventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
