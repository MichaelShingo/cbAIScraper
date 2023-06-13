from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.opps_list_create_view),
    path('testcreate/', views.test_model_creation),
    path('composerscrape/', views.composer_scrape_view),
    path('delete/<int:pk>/', views.delete_view),
    path('scrapecapital/', views.capital_scrape_view)
]
