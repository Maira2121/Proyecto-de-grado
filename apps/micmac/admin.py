from django.contrib import admin
from .models import *


# Register your models here.


@admin.register(Variable)
class AdminVariable(admin.ModelAdmin):
    list_display = ('pk', 'nombre_corto', 'descripcion', 'autor',)
    ordering = ('nombre_corto', )


@admin.register(Relacion)
class AdminRelacion(admin.ModelAdmin):
    list_display = ('pk', 'de_variable', 'a_variable', 'valoracion', 'descripcion',)
    ordering = ('de_variable__nombre_corto', 'a_variable__nombre_corto')

@admin.register(EstudioMicmac)
class AdminEstudioMicmac(admin.ModelAdmin):
    list_display = ('proyecto', 'titulo','moderador', 'get_coordinadores', 'get_expertos', 'fecha_inicio', 'fecha_final','estado')
    ordering = ('titulo',)

@admin.register(SesionVariables)
class AdminSesionvariable(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'estado', 'fecha_inicio', 'fecha_final')
    ordering = ('estado',)

