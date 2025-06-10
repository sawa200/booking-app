from django.db import models
from django.db.models import Q, Model  
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Location(models.Model):
    title = models.CharField(max_length=100,unique=True)
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ['title']

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='bookings', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        super().clean()
        if self.start_date > self.end_date:
            raise ValidationError(_('Дата початку не може бути пізніше дати закінчення.'))

        if Booking.objects.filter(location=self.location).exclude(pk=self.pk).filter(
            Q(start_date__lte=self.end_date) & Q(end_date__gte=self.start_date)
        ).exists():
            raise ValidationError(_('ці дати вже зайняті для локації.'))


def seve(self, *args, **kwargs):
    self.clean()
    super().save(*args, **kwargs)