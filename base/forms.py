from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Message, Room

class UserRegisterForm(UserCreationForm):

    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    email = forms.EmailField()

    class Meta:

        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class UserLoginForm(forms.Form):

    username = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput)

class RoomForm(forms.ModelForm):

    class Meta:

        model = Room
        fields = '__all__'

        exclude = ['host', 'participants']


class MessageCreationForm(forms.ModelForm):

    class Meta:

        model = Message
        fields = ['body']