from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from .forms import RoomForm, UserForm
from .models import Topic, Room, Message, User
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
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    rooms_count = len(rooms)
    topics = Topic.objects.all()
    context = {'rooms':rooms, 'topics':topics, 'rooms_count':rooms_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk): 
    # room = None
    # for i in rooms:
    #     if i['id'] == pk:
    #         room = i
    rooms = Room.objects.get(id=pk)
    room_messages = rooms.message_set.all().order_by('-created')


    participants = rooms.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=rooms,
            body=request.POST.get('body')
        )
        rooms.participants.add(request.user)
        return redirect('room', pk=rooms.id)

    return render(request, "base/room.html", {'room':rooms, 'room_messages':room_messages, 'participants':participants})

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    print(rooms)
    topics = Topic.objects.all()

    context = {'topics':topics, 'room_messages':room_messages, 'rooms':rooms, 'user':user}
    return render(request, 'base/profile_component.html', context)

@login_required(login_url='login')
def updateUser(request):
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', request.user.id)
    context = {'form':form}
    return render(request, 'base/update_user.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        name = request.POST.get('name')
        description = request.POST.get('description')

        topic, created = Topic.objects.get_or_create(name=topic_name)
        room  = Room.objects.create(
            topic=topic,
            host=request.user,
            name=name,
            description=description
        )
        return redirect('home')
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here !")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        name = request.POST.get('name')
        description = request.POST.get('description')

        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = name
        room.description = description
        room.save()
        return redirect('home')
    
    context = {'form':form, 'topics':topics, 'room':room}
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

def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here !")
    
    if request.method=='POST':
        message.delete()
        return redirect('room', message.room.id)

    return render(request, 'base/delete_room.html', {'room':message})


def topics(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(Q(name__icontains=q))
    context = {'topics':topics}
    return render(request, 'base/topic.html', context)


def activity(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html', context)