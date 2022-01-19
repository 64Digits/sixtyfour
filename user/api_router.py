"""
    Provides the Router bindings for API endpoints
"""
from django.urls import path
from .api_views import RecentActivity

api_routes = [
    path('api/recent_activity/get', RecentActivity.as_view({'get':'list'}), name="recent_activity")
]