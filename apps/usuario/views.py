from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from apps.usuario.form import RegistroUsuario_form
from django.core.urlresolvers import reverse_lazy

# Create your views here.

class Registro_Usuario(CreateView):
    model = User
    template_name = "usuario/registro_usuario.html"
    form_class = RegistroUsuario_form
    success_url =  reverse_lazy('delphi:estudios_delphi')

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Usuaio ' + form.clean_username() + ' registrado con exito.')
        return super(Registro_Usuario, self).form_valid(form)

    def form_invalid(self, form):
        response = super(Registro_Usuario, self).form_invalid(form)
        messages.error(self.request, 'El usuario no pudo ser registrado. Verifique los datos ingresados.')
        return response