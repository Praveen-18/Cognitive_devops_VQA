from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Registration(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.username

class Question(models.Model):
    question = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    def __str__(self):
        if self.question:
            return self.question
        return "No question available"