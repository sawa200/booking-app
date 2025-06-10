from django.urls import path
from booking import views

urlpatterns = [
    path('', views.index, name='index'),
    path("rooms-list/", views.room_list, name="room_list"),
    path("booking-create/", views.booking_create, name="booking_create"),
    path("booking-success/<int:pk>/", views.booking_success, name="booking_success"),
]