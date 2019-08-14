from django.contrib import admin

# Register your models here.
from apps.delphi.models import *

class Nuevo_estudio_delphi_Admin(admin.ModelAdmin):

    list_display = ('id', 'proyecto', 'titulo', 'descripcion',
            'objetivos', 'fecha_inicio', 'fecha_final', 'estado', 'moderador', 'get_coordinadores', 'get_participantes')

admin.site.register(EstudioDelphi, Nuevo_estudio_delphi_Admin)

class Pregunta_delphi_Admin(admin.ModelAdmin):
    list_display = ('enunciado_pregunta', 'sesion','tipo_pregunta', 'cuestionario', 'autor', 'de_control', 'get_votos')
    ordering = ('cuestionario', 'sesion')

admin.site.register(Pregunta, Pregunta_delphi_Admin)



class Cuestionario_delphi_Admin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'estado', 'delphi', 'fecha_inicio','fecha_final',)
    ordering = ('delphi',)

admin.site.register(CuestionarioDelphi, Cuestionario_delphi_Admin)


class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ('texto_opcion', 'pregunta', 'valor_inicio', 'valor_final')


admin.site.register(OpcionRespuesta, OpcionRespuestaAdmin)

class RespuestasUsuariosAdmin(admin.ModelAdmin):
    list_display = ('pregunta', 'respuesta_texto', 'get_opciones_seleccinadas', 'usuario')


admin.site.register(RespuestasUsuarios, RespuestasUsuariosAdmin)

class RondasAdmin(admin.ModelAdmin):
    list_display = ('cuestionario', 'delphi', 'fecha_inicio', 'fecha_final', 'abierto')


admin.site.register(RondasDelphi, RondasAdmin)

class SesionAdmin(admin.ModelAdmin):
    list_display = ('cuestionario', 'codigo_sesion', 'nombre', 'permitir_preguntas', 'fecha_inicio', 'fecha_final', 'estado')
admin.site.register(SesionCuestionario, SesionAdmin)