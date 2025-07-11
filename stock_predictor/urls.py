# stock_predictor/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock_app.urls')),   # ✅ include your app's urls!
]
 