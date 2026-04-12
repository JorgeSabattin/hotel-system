from django.contrib import admin
from .models import Customer, Hotel, Room, Reservation

admin.site.register(Customer)
admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Reservation)