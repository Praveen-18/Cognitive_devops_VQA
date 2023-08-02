from django.contrib import admin
from .models import Registration, Question, BloodDonation, Doctor_register

# Register your models here.

admin.site.register(Registration)
admin.site.register(Question)
admin.site.register(BloodDonation)
admin.site.register(Doctor_register)
