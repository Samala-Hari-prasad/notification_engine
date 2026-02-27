from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('engine/', include('engine.urls')),
    path('rules/', include('rules.urls')),
    path('scheduler/', include('scheduler.urls')),
    path('audit/', include('audit.urls')),
    path('dashboard/', include('dashboard.urls')),
    # root URL redirects to dashboard home
    path('', include('dashboard.urls')),
]
