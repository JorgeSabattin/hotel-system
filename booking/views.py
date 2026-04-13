from django.shortcuts import render, redirect
from .models import Room, Reservation
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied


# ── Helper: verificar si el usuario es Administrador ──
def es_administrador(user):
    return user.groups.filter(name='Administradores').exists()


# 🏠 HOME
def home(request):
    if request.user.is_authenticated:
        grupos = list(request.user.groups.values_list('name', flat=True))
        print("GRUPOS DEL USUARIO:", grupos)
    return render(request, 'booking/home.html')


# 🔍 BUSCAR HABITACIONES
def search(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if not check_in or not check_out:
        return render(request, 'booking/home.html')

    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

    overlapping_reservations = Reservation.objects.filter(
        check_in__lt=check_out_date,
        check_out__gt=check_in_date
    )

    occupied_room_ids = overlapping_reservations.values_list('room_id', flat=True)
    available_rooms = Room.objects.exclude(id__in=occupied_room_ids)

    return render(request, 'booking/results.html', {
        'rooms': available_rooms,
        'check_in': check_in,
        'check_out': check_out
    })


# 🛏️ RESERVAR
@login_required
def reserve(request):
    room_id = request.GET.get('room_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    room = Room.objects.get(id=room_id)

    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

    conflict = Reservation.objects.filter(
        room=room,
        check_in__lt=check_out_date,
        check_out__gt=check_in_date
    ).exists()

    if conflict:
        return render(request, 'booking/error.html', {
            'message': '❌ Esta habitación ya está reservada en esas fechas'
        })

    Reservation.objects.create(
        user=request.user,
        room=room,
        check_in=check_in_date,
        check_out=check_out_date
    )

    return redirect('/my-reservations/')


# 📖 MIS RESERVAS
@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)

    return render(request, 'booking/my_reservations.html', {
        'reservations': reservations
    })


# ❌ CANCELAR RESERVA
@login_required
def cancel_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)

    if reservation.user == request.user:
        reservation.delete()

    return redirect('/my-reservations/')


# ➕ AGREGAR HABITACIÓN (solo Administradores)
@login_required
def add_room(request):
    if not es_administrador(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        room_type = request.POST.get('room_type')
        capacity = request.POST.get('capacity')
        price = request.POST.get('price')
        description = request.POST.get('description')

        Room.objects.create(
            room_type=room_type,
            capacity=int(capacity),
            price=float(price),
            description=description
        )

        return redirect('/admin-panel/')

    return render(request, 'booking/add_room.html')


# 🛠️ PANEL ADMINISTRADOR (solo Administradores)
@login_required
def admin_panel(request):
    if not es_administrador(request.user):
        raise PermissionDenied

    rooms = Room.objects.all().order_by('room_type')
    reservations = Reservation.objects.all().order_by('-check_in')

    return render(request, 'booking/admin_panel.html', {
        'rooms': rooms,
        'reservations': reservations,
    })


# 📋 CATÁLOGO DE HABITACIONES
def catalog(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if check_in and check_out:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

        occupied = Reservation.objects.filter(
            check_in__lt=check_out_date,
            check_out__gt=check_in_date
        ).values_list('room_id', flat=True)

        rooms = Room.objects.exclude(id__in=occupied).order_by('room_type')
    else:
        rooms = Room.objects.all().order_by('room_type')

    return render(request, 'booking/catalog.html', {
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out
    })


# 👤 REGISTRO DE USUARIO
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'booking/register.html', {'form': form})
# 🗑️ ELIMINAR HABITACIÓN (solo Administradores)
@login_required
def delete_room(request, room_id):
    if not es_administrador(request.user):
        raise PermissionDenied
    room = Room.objects.get(id=room_id)
    room.delete()
    return redirect('/admin-panel/')
