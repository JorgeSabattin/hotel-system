from django.shortcuts import render
from datetime import datetime
from .models import Room, Reservation


def home(request):
    return render(request, 'booking/home.html')


def search(request):
    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")

    # Validar que existan
    if not check_in or not check_out:
        return render(request, 'booking/results.html', {
            "rooms": [],
            "error": "Debes ingresar ambas fechas"
        })

    # Convertir a fecha
    try:
        check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
    except:
        return render(request, 'booking/results.html', {
            "rooms": [],
            "error": "Formato de fecha incorrecto"
        })

    # Validar lógica de fechas
    if check_out <= check_in:
        return render(request, 'booking/results.html', {
            "rooms": [],
            "error": "La fecha de salida debe ser mayor que la de entrada"
        })

    rooms = Room.objects.all()
    available_rooms = []

    for room in rooms:
        reservations = Reservation.objects.filter(room=room)

        is_available = True

        for r in reservations:
            # Verifica solapamiento de fechas
            if check_in < r.check_out and check_out > r.check_in:
                is_available = False
                break

        if is_available:
            available_rooms.append({
                "number": room.number,
                "price": room.price
            })

    return render(request, 'booking/results.html', {
        "rooms": available_rooms
    })