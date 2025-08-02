import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date

from booking.models import Location, Booking
from .forms import UserRegisterForm


@login_required
def profile(request):
    user = request.user
    active_bookings = user.bookings.filter(end_date__gte=date.today()).select_related('location')
    past_bookings = user.bookings.filter(end_date__lt=date.today()).select_related('location')

    context = {
        'user': user,
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'profile.html', context)


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == "POST":
        booking.delete()
        messages.success(request, "Бронювання скасовано.")
        return redirect('profile')

    return render(request, 'cancel_booking_confirm.html', {'booking': booking})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            html_message = render_to_string('activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            email = EmailMessage(
                subject='Активація акаунта',
                body=html_message,
                from_email=None,
                to=[user.email],
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)

            messages.success(request, 'Перевірте вашу пошту для активації акаунта.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Акаунт активовано. Тепер ви можете увійти.')
        return redirect('login')
    else:
        messages.error(request, 'Посилання для активації недійсне.')
        return redirect('register')


def room_list(request):
    rooms = Location.objects.all()
    return render(request, "room_list.html", {"rooms_list": rooms})


@login_required
def booking_create(request, pk):
    room = get_object_or_404(Location, pk=pk)

    if request.method == "POST":
        start_date_str = request.POST.get("start_time")
        end_date_str = request.POST.get("end_time")

        if not start_date_str or not end_date_str:
            messages.error(request, "Будь ласка, виберіть дату заїзду та виїзду.")
            context = {"room": room, "start_time": start_date_str, "end_time": end_date_str}
            return render(request, "location_detail.html", context)

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date or not end_date or start_date > end_date:
            messages.error(request, "Некоректний діапазон дат.")
            context = {"room": room, "start_time": start_date_str, "end_time": end_date_str}
            return render(request, "location_detail.html", context)

        overlapping_bookings = Booking.objects.filter(
            location=room,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if overlapping_bookings.exists():
            messages.error(request, "Ця кімната вже заброньована на вибраний період.")
            context = {"room": room, "start_time": start_date_str, "end_time": end_date_str}
            return render(request, "location_detail.html", context)

        booking = Booking.objects.create(
            user=request.user,
            location=room,
            start_date=start_date,
            end_date=end_date
        )

        html_message = render_to_string('booking_confirmation_email.html', {
            'user': request.user,
            'booking': booking,
        })

        email = EmailMessage(
            subject='Підтвердження бронювання',
            body=html_message,
            from_email=None,
            to=[request.user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        messages.success(request, "Бронювання успішно створено! Підтвердження надіслано на вашу пошту.")
        return redirect("booking_success", pk=booking.id)

    return redirect('location_detail', pk=pk)


def booking_success(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    return render(request, "booking_success.html")


def location_detail(request, pk):
    room = get_object_or_404(Location, pk=pk)

    bookings = room.bookings.filter(end_date__gte=date.today())

    busy_dates = []
    for booking in bookings:
        current_date = booking.start_date
        while current_date <= booking.end_date:
            busy_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)

    busy_dates_json = json.dumps(busy_dates, cls=DjangoJSONEncoder)

    return render(request, "location_detail.html", {
        "room": room,
        "bookings": bookings,
        "busy_dates_json": busy_dates_json,
    })


def index(request):
    return render(request, 'index.html')