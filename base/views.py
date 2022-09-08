from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import UserRegisterForm, UserLoginForm, RoomForm, MessageCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message, Room, Topic
from django.db.models import Q
from django.core.mail import send_mail, EmailMessage
from stud2 import settings
from .token import generate_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode

# Create your views here.

def home(request):

    q = request.GET.get('q')

    if request.GET.get('q') is not None:

        rooms = Room.objects.filter(
            
                                    Q(topic__name__icontains = q) |
                                    Q(host__username__icontains = q) | 
                                    Q(description__icontains = q) |
                                    Q(name__icontains = q)
                                    
                                    )
    else:
        rooms = Room.objects.all()

    topics = Topic.objects.all()
    
    context = {
        'rooms' : rooms,
        'topics' :topics,
    }

    return render(request,'base/index.html', context)

def registerPage(request):

    page = 'register'

    if request.method == 'POST':

        if User.objects.filter(email = request.POST['email']):
            messages.error(request, 'Email already exist')
            return redirect('registerpage')

        if User.objects.filter(username = request.POST['username']):
            messages.error(request, 'Username already exist')
            return redirect('registerpage')

        if len(request.POST['password1']) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return redirect('registerpage')

        if request.POST['password1'] != request.POST['password2']:
            messages.error(request, 'Password Mismatch')
            return redirect('registerpage')

        form = UserRegisterForm(request.POST)
        user = form.save(commit=False)
        #user.username = user.username.upper()
        user.is_active = False
        user.save()

        #Welcome Email
        subject = 'Welcome to CryptChain'
        mail = 'Account Created successfully. We have sent you a confirmation email\nPlease confirm email to activate account'
        from_mail = settings.EMAIL_HOST_USER
        to_list = [user.email,]
        send_mail(subject, mail, from_mail, to_list, fail_silently=True)
       
        #Confirmation Email
        current_site = get_current_site(request)
        email_subject = 'Confirmation Email'
        message2 = render_to_string('base/email_confirmation.html',{

            'name' : user.first_name,
            'domain' : current_site,
            'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
            'token' : generate_token.make_token(user)

        }
        )

        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [user.email])
        email.send(fail_silently=True)
        messages.success(request,'Account Created successfully. We have sent you a confirmation email Please confirm email to activate account')
        return redirect('home')

    context = {

        'form' : UserRegisterForm,
        'page' : page,
    }

    return render(request, 'base/registerpage.html', context)


def activateAccount(request,uid64,token):
    
    try:

        uid = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk = uid)

    except(ValueError,TypeError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user,token):
        user.is_active = True
        user.save()
        return redirect('home')

    else:
        return render(request, 'base/activate.html')

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        #Authenticate if user records exist in the database
        user = authenticate(username = request.POST['username'], password = request.POST['password'] )

        #if an instance of the user is found in the database
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in succesfully')
            return redirect('home')

        else:
            messages.error(request, 'Incorrect Username or Password')
            return redirect('home')

    context = {

        'form' : UserLoginForm,
        'page' : page,
    }

    return render(request, 'base/registerpage.html', context)

def logoutPage(request):

    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('home')

def room(request, pk):

    room = Room.objects.get(pk = pk)
    room_messages = room.message_set.all()
    message_form = MessageCreationForm()
    room_participants = room.participants.all()

    context = {

        'room': room,
        'room_messages' : room_messages,
        'message_form' : message_form,
        'room_participants' : room_participants
    }

    return render(request, 'base/room.html', context)

#ROOM CRUD OPERATIONS
@login_required(login_url='loginpage')
def createRoom(request):

    if request.method == 'POST':

        form = RoomForm(request.POST)

        if form.is_valid():

            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {

        'form' : RoomForm,
    }
    return render(request,'base/create-room.html', context)

@login_required(login_url='loginpage')
def updateRoom(request, pk):

    room = Room.objects.get(pk = pk)

    if request.user != room.host:
        return HttpResponse('Permission Denied!!! You cannot update this room because you are not the room host')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()
            return redirect('home')

    context = {

        'form' : RoomForm(instance=room)
    }
    return render(request, 'base/update-room.html', context)

@login_required(login_url='loginpage')
def deleteRoom(request, pk):

    room = Room.objects.get(pk =  pk)

    if request.user != room.host:
        return HttpResponse('Permission Denied!!! You cannot delete this room because you not the room host')

    if request.method == "POST":
        room.delete()
        return redirect('home')


    return render(request, 'base/delete-room.html', {'obj':room})

#MESSAGE CRUD OPERATIONS
@login_required(login_url='loginpage')
def createMessage(request,pk):

    room = Room.objects.get(pk = pk)

    if request.method == 'POST':

        #form = MessageCreationForm(request.POST)
        #if form.is_valid():

        Message.objects.create(

            user = request.user,
            room = room,
            body = request.POST['body']

        )
        room.participants.add(request.user)

    return redirect('room', pk = room.id)

def deleteMessage(request,pk):

    message = Message.objects.get(pk = pk)
    room = message.room

    if request.method == "POST":

        message.delete()

        if room.message_set.filter(user__username = request.user).exists():
            pass

        else:
            room.participants.remove(request.user)

        return redirect('room', pk = room.id)

    return render(request, 'base/delete-room.html', {'obj':message})


def editMessage(request, pk):

    message = Message.objects.get(pk = pk)
    room = message.room
    page = 'edit'
    room_messages = room.message_set.all()
    room_participants = room.participants.all()

    if request.method == "POST":

        message_form = MessageCreationForm(request.POST, instance = message)
        message_form.save()
        return redirect('room', pk = room.id)

    context = {

        'message_form' : MessageCreationForm(instance = message),
        'page' : page,
        'room' : room,
        'room_messages' : room_messages,
        'room_participants' :room_participants,
    }

    return render(request, 'base/room.html', context)





