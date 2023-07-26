from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('register/',views.userlogin,name='userlogin'),
    path('index/',views.index,name='index'),
    path('',views.register,name='register'),
    path('logoutUser/',views.logoutUser,name='logoutUser'),
    path('vqa/',views.vqa,name='vqa'),
    path('bmi/',views.bmi_calculator,name='bmi_calculator'),
    path('blog/',views.blog,name='blog'),
    path('consultant/',views.consultant,name='consultant'),
    path('blooddonation/',views.blooddonation,name='blooddonation'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('stop_streaming', views.stop_streaming, name='stop_streaming'),
    path('uncapture', views.uncapture, name='uncapture'),
    path('video_feed1', views.video_feed1, name='video_feed1'),
    path('stop_streaming1', views.stop_streaming1, name='stop_streaming1'),
    path('uncapture1', views.uncapture1, name='uncapture1'),
    path('uncapture', views.uncapture, name='uncapture'),
    path('imagecreation/' , views.imagecreation , name='imagecreation'),
]