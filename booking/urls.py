from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
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
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),


    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
