from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),
    path('', views.home, name='home'),
    path('room/<int:pk>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create_room'),
    path('update-room/<int:pk>/', views.update_room, name='update-room'),
    path('delete-room/<int:pk>', views.delete_room, name='delete-room'),
]
