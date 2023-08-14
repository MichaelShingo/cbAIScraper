from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.opps_list_create_view),
    path('testcreate/', views.test_model_creation),
    path('delete/<int:pk>/', views.delete_view),
    path('scrapeComposer/', views.composer_scrape_view),
    path('scrapeCapital/', views.capital_scrape_view),
    path('scrapeAsian/', views.asian_arts_scrape_view),
    path('scrapeHyper/', views.hyper_scrape_view),
    path('thismonth/', views.opps_list_month_view),
    path('formatLocation/', views.format_location_view),
    path('generateTitles/', views.generate_titles_view),
    path('getToday/', views.list_today_view),
]
