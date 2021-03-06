"""softprosp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^delphi/', include('apps.delphi.urls', namespace="delphi")),
    url(r'^entrevista/', include('apps.entrevista.urls', namespace="entrevista")),
    url(r'^usuario/', include('apps.usuario.urls', namespace="usuario")),
    url(r'^mactor/', include('apps.mactor.urls', namespace="mactor")),
    url(r'^micmac/', include('apps.micmac.urls', namespace="micmac")),
    url(r'^$', LoginView.as_view(template_name='usuario/login.html'), name= "login"),
    url(r'^logout/', LogoutView.as_view(), name= "logout"),
]
