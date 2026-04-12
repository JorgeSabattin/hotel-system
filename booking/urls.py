from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('reserve/', views.reserve, name='reserve'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
