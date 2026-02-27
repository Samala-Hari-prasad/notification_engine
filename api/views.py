from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import NotificationEvent
from .serializers import NotificationEventSerializer
from engine.services import decide_notification

class NotificationEventViewSet(viewsets.ModelViewSet):
    queryset = NotificationEvent.objects.all()
    serializer_class = NotificationEventSerializer

    @action(detail=False, methods=['post'], url_path='evaluate')
    def evaluate(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        # Run the prioritization engine
        classification, explanation = decide_notification(event)
        return Response({
            'classification': classification,
            'explanation': explanation,
            'event_id': event.id
        }, status=status.HTTP_200_OK)
