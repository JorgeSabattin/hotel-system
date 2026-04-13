from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('reserve/', views.reserve, name='reserve'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('register/', views.register, name='register'),
    path('catalog/', views.catalog, name='catalog'),
    path('add-room/', views.add_room, name='add_room'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
]
