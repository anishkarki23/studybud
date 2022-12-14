
from email import contentmanager
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

#rooms = [
#   {'id':1, 'name':'Python'},
#    {'id':2, 'name':'Java'},
#    {'id':3, 'name':'C++'},
#]
def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method== 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password did not match')



    context = {'page':page}
    return render(request, 'base/login_register.html', context )

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    
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
            messages.error(request, 'An error occured during registration')


    return render (request, 'base/login_register.html', {'form': form})

def home(request): 
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms , 'topics' : topics, 'room_count': room_count }
    return render(request, 'base/home.html', context )

def room(request,pk):

    #pk parameter will pass the id value in the room 
    #room = None
    #for i in rooms:
    #    if i['id'] == int(pk):
    #        room = i


    room = Room.objects.get(id=pk)
    context = {'room':room}
    return render(request, 'base/room.html', context )

@login_required(login_url = 'login')
def createroom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')


    context ={'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def updateroom(request, pk):
    room = Room.objects.get (id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("Your are not allowed to to update the information")


    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')


    context = {'form':form}
    return render (request, 'base/room_form.html' ,context) 

@login_required(login_url = 'login')
def delete(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed to to delete the information")

    if request.method == 'POST':
        room.delete()
        return redirect('home')


    return render(request, 'base/delete.html', {'obj':room})

