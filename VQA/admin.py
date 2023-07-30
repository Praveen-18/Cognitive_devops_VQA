from django.contrib import admin
from .models import Registration, Question, BloodDonation

# Register your models here.

admin.site.register(Registration)
admin.site.register(Question)
admin.site.register(BloodDonation)
