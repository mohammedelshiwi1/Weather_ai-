from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from .views import login_view,register_view,home_view,fetch_weather_data,user_readings_csv
from django.conf.urls.static import static
urlpatterns = [
    path('', login_view,name='login'),
    path('register/',register_view,name='register'),
    path('home/',home_view,name='home'),
    path("weather/", fetch_weather_data, name="fetch_weather"),
    path('download_csv/', user_readings_csv, name='user_readings_csv')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
