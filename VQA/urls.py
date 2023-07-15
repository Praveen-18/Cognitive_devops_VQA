from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',views.userlogin,name='userlogin'),
    path('index/',views.index,name='index'),
    path('register/',views.register,name='register'),
    path('logoutUser/',views.logoutUser,name='logoutUser'),
    path('vqa/',views.vqa,name='vqa'),
    # path('',views.index,name='index'),

]