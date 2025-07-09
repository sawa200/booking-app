from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:pk>/', views.location_detail, name='location_detail'),
    path('booking/<int:pk>/create/', views.booking_create, name='booking_create'),
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),
    path('profile/', views.profile, name='profile'),
]
