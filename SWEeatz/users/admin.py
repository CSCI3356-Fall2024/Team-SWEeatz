from django.contrib import admin
from .models import Campaign, Action, CompletedAction

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_at', 'points')
    search_fields = ('title',)
    list_filter = ('start_date', 'end_date')

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("name", "points", "is_active", "is_daily_challenge", "date")

@admin.register(CompletedAction)
class CompletedActionAdmin(admin.ModelAdmin):
    list_display = ("student", "action", "date_completed", "points_earned")