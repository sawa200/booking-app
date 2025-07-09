from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
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

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # пока не активирован
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            message = render_to_string('activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            send_mail(
                'Активация аккаунта',
                message,
                None,
                [user.email],
                fail_silently=False,
            )

            return HttpResponse('Проверьте вашу почту для активации аккаунта.')
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
        return HttpResponse('Аккаунт успешно активирован. Теперь вы можете войти.')
    else:
        return HttpResponse('Ссылка для активации недействительна.')


def room_list(request):
    rooms = Location.objects.all()
    return render(request, "room_list.html", {"rooms_list": rooms})


def booking_create(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Для бронювання потрібно увійти в акаунт.")
        return redirect('login')

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

        confirmation_message = render_to_string('booking_confirmation_email.html', {
            'user': request.user,
            'booking': booking,
        })

        send_mail(
            subject='Підтвердження бронювання',
            message=confirmation_message,
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        messages.success(request, "Бронювання успішно створено! Лист підтвердження відправлено на вашу пошту.")
        return redirect("booking_success", pk=booking.id)

    # Если GET-запрос, то просто перенаправляем на страницу комнаты
    return redirect('location_detail', pk=pk)



def booking_success(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    return render(request, "booking-success.html", {"booking": booking})


def location_detail(request, pk):
    room = get_object_or_404(Location, pk=pk)
    return render(request, "location_detail.html", {"room": room})


def index(request):
    return render(request, 'index.html')

