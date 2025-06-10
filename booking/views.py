from django. shortcuts import render, redirect
from booking.models import Location , Booking
from django.http import HttpResponse

def index(request):
    context = {
        "render_string": "Hello, world!"
    }
    return render(request, template_name="index.html", context=context)


def room_list(request):
    rooms = Location.objects.all()
    context = {
        "rooms": rooms
    }
    return render(request, template_name="room_list.html", context=context)

def booking_create(request): 
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        
        try:
            room = Location.objects.get(number=room_number)
        except ValueError:
            return HttpResponse(
                "Invalid room number. Please try again.",
                status=400
            )
        except Location.DoesNotExist:
            return HttpResponse(
                "Room not found. Please try again.",
                status=404
            )
        
        booking = Booking.objects.create(
            user=request.user,  
            room=room,
            start_time=start_time,
            end_time=end_time
        )
        return redirect("booking_success", pk=booking.id)
    else:
        return render(request, template_name="booking_form.html")

def booking_success(request, pk):
    try:
        booking = Booking.objects.get(id=pk)
    except Booking.DoesNotExist:
        return HttpResponse("Booking not found.", status=404)

    context = {
        "booking": booking
    }
    return render(request, template_name="booking_success.html", context=context)
