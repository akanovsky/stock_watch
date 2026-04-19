"""
URL configuration for stock_project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('stock_app.urls')),
]
