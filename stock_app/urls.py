# stock_app/urls.py

from django.urls import path
from . import views
app_name = 'stock_app'   # ✅ THIS is very important
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('download_chart/', views.download_chart, name='download_chart'),
]
