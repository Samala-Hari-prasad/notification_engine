from django.contrib import admin
from .models import RuleConfig

@admin.register(RuleConfig)
class RuleConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')
    search_fields = ('key',)
