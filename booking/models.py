from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()


class Hotel(models.Model):
    name = models.CharField(max_length=100)


class Room(models.Model):
    ROOM_TYPES = [
        ('simple', 'Simple'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
    ]

    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='simple')
    capacity = models.IntegerField(default=1)
    price = models.FloatField()
    description = models.TextField(blank=True, default='')


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()


class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('es', 'Español'),
        ('en', 'English'),
    ]

    ROOM_PREFERENCES = [
        ('', 'Sin preferencia'),
        ('simple', 'Simple'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rut = models.CharField(max_length=12, blank=True, default='')
    address = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='es')
    preferred_room_type = models.CharField(max_length=10, choices=ROOM_PREFERENCES, blank=True, default='')

    def __str__(self):
        return f'Perfil de {self.user.username}'
