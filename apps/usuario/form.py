from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegistroUsuario_form(UserCreationForm):

    class Meta:
        model= User
        fields = [
            'username',
            'email',
        ]
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',

        }