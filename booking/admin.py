from django.contrib import admin
from .models import Hotel, Room, Customer, Reservation

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Reservation)