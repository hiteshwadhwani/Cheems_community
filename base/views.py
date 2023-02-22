from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from .forms import RoomForm
from .models import Topic
from .models import Room
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# rooms = [
#     {'id':1, 'name':'hello join me'},
#     {'id':2, 'name':'hello join me'},
#     {'id':3, 'name':'hello join me'},
#     {'id':4, 'name':'hello join me'},
#     {'id':5, 'name':'hello join me'}
#     ]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exists')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password does not exists')
    return render(request, 'base/login_register.html', {'page':page})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error occured during registration')
    return render(request, 'base/login_register.html', {'form':form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(Q(topic__name__contains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    rooms_count = len(rooms)
    topics = Topic.objects.all()
    context = {'rooms':rooms, 'topics':topics, 'rooms_count':rooms_count}
    return render(request, 'base/home.html', context)

def room(request, pk): 
    # room = None
    # for i in rooms:
    #     if i['id'] == pk:
    #         room = i
    rooms = Room.objects.get(id=pk)
    return render(request, "base/room.html", {'room':rooms})

@login_required(login_url='login')
def create_room(request):
    form = RoomForm

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed here !")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here !")
    
    if request.method=='POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete_room.html', {'room':room})