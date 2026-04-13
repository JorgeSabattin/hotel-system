from django.shortcuts import render, redirect
from .models import Room, Reservation, UserProfile
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django import forms


# ────────────────────────────────────────────
# FORMULARIO DE REGISTRO
# ────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Nombre')
    last_name = forms.CharField(max_length=50, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    rut = forms.CharField(max_length=12, required=True, label='RUT')
    address = forms.CharField(max_length=200, required=True, label='Dirección')
    phone = forms.CharField(max_length=20, required=True, label='Teléfono')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# ────────────────────────────────────────────
# FORMULARIO DE PERFIL
# ────────────────────────────────────────────
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='Nombre')
    last_name = forms.CharField(max_length=30, required=False, label='Apellido')
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = UserProfile
        fields = ['rut', 'address', 'phone', 'photo', 'language', 'preferred_room_type']
        labels = {
            'rut': 'RUT',
            'address': 'Dirección',
            'phone': 'Teléfono',
            'photo': 'Foto de perfil',
            'language': 'Idioma preferido',
            'preferred_room_type': 'Tipo de habitación favorita',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


# ────────────────────────────────────────────
# HOME
# ────────────────────────────────────────────
def home(request):
    return render(request, 'booking/home.html')


# ────────────────────────────────────────────
# BUSCAR HABITACIONES
# ────────────────────────────────────────────
def search(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if not check_in or not check_out:
        return render(request, 'booking/home.html')

    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

    nights = (check_out_date - check_in_date).days

    overlapping_reservations = Reservation.objects.filter(
        check_in__lt=check_out_date,
        check_out__gt=check_in_date
    )
    occupied_room_ids = overlapping_reservations.values_list('room_id', flat=True)
    available_rooms = Room.objects.exclude(id__in=occupied_room_ids)

    return render(request, 'booking/results.html', {
        'rooms': available_rooms,
        'check_in': check_in,
        'check_out': check_out,
        'nights': nights
    })


# ────────────────────────────────────────────
# RESERVAR
# ────────────────────────────────────────────
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


# ────────────────────────────────────────────
# MIS RESERVAS
# ────────────────────────────────────────────
@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'booking/my_reservations.html', {
        'reservations': reservations
    })


# ────────────────────────────────────────────
# CANCELAR RESERVA
# ────────────────────────────────────────────
@login_required
def cancel_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    if reservation.user == request.user:
        reservation.delete()
    return redirect('/my-reservations/')


# ────────────────────────────────────────────
# ADMIN CHECK
# ────────────────────────────────────────────
def is_admin(user):
    return user.is_staff


# ────────────────────────────────────────────
# AGREGAR HABITACIÓN
# ────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/')
def add_room(request):
    if request.method == 'POST':
        Room.objects.create(
            room_type=request.POST.get('room_type'),
            capacity=request.POST.get('capacity'),
            price=request.POST.get('price'),
            description=request.POST.get('description')
        )
        from django.contrib import messages
        messages.success(request, '✅ Habitación creada correctamente.')
        return redirect('/add-room/')
    return render(request, 'booking/add_room.html')


# ────────────────────────────────────────────
# PANEL ADMIN
# ────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/')
def admin_panel(request):
    reservations = Reservation.objects.select_related('user', 'room').order_by('-check_in')
    rooms = Room.objects.all()
    return render(request, 'booking/admin_panel.html', {
        'reservations': reservations,
        'rooms': rooms,
    })


# ────────────────────────────────────────────
# ELIMINAR HABITACIÓN
# ────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/')
def delete_room(request, room_id):
    Room.objects.filter(id=room_id).delete()
    return redirect('/admin-panel/')


# ────────────────────────────────────────────
# PERFIL DE USUARIO
# ────────────────────────────────────────────
@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    reservations = Reservation.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'booking/profile.html', {
        'profile': profile_obj,
        'reservations': reservations,
    })


@login_required
def edit_profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)

    return render(request, 'booking/edit_profile.html', {'form': form})

# 📋 CATÁLOGO DE HABITACIONES

# 📋 CATÁLOGO DE HABITACIONES
def catalog(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if check_in and check_out:
        from datetime import datetime
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

        # Excluir habitaciones ocupadas en esas fechas
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

# ────────────────────────────────────────────
# REGISTRO
# ────────────────────────────────────────────
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            UserProfile.objects.create(
                user=user,
                rut=form.cleaned_data['rut'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
            )
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'booking/login.html', {
                'register_form': form,
                'register_error': True
            })
    return redirect('/login/')


# ────────────────────────────────────────────
# DESPEDIDA
# ────────────────────────────────────────────
def goodbye(request):
    return render(request, 'booking/goodbye.html')
