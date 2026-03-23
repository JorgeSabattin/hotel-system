from django.http import JsonResponse
from .models import Room, Reservation

def availability(request):

    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")

    rooms = Room.objects.all()
    available_rooms = []

    for room in rooms:

        reservations = Reservation.objects.filter(room=room)

        is_available = True

        for r in reservations:
            if check_in < str(r.check_out) and check_out > str(r.check_in):
                is_available = False
                break

        if is_available:
            available_rooms.append({
                "room": room.number,
                "price": float(room.price)
            })

    return JsonResponse(available_rooms, safe=False)