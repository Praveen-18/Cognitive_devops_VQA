from django.contrib import admin
from .models import Registration, Question, BloodDonation, Doctor_register, Consultant, Appointment_status, Blog, Feedback, User_Wallet

# Register your models here.

admin.site.register(Registration)
admin.site.register(Question)
admin.site.register(BloodDonation)
admin.site.register(Doctor_register)
admin.site.register(Consultant)
admin.site.register(Appointment_status)
admin.site.register(Blog)
admin.site.register(Feedback)
admin.site.register(User_Wallet)
