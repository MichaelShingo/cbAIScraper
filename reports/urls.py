from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_list_view),
    path('today/', views.reports_today_view),
    path('email/', views.reports_email_view),
]