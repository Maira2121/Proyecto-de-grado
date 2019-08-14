from django.conf.urls import url
from apps.usuario.views import Registro_Usuario



urlpatterns = [
    url(r'^registro_usuario', Registro_Usuario.as_view(), name="registro_usuario"),

]