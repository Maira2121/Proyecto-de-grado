from django.conf.urls import url
from  django.contrib.auth.decorators import login_required
from apps.delphi.views import *

urlpatterns = [
    url(r'^estudios_delphi/', login_required(ListaEstudiosDelphi.as_view()), name='estudios_delphi'),
    url(r'^detalle_estudio/(?P<pk>\d+)', login_required(DetalleEstudio.as_view()), name='Detalle_estudio'),
    url(r'^nuevo_estudio_delphi/', login_required(Nuevo_estudio_Delphi.as_view()), name='nuevo_estudio_delphi'),
    url(r'^editar_delphi/(?P<pk>\d+)/$', login_required(Editar_estudio_delphi.as_view()), name='editar_delphi'),
    url(r'^agregar_participante/', login_required(agregar_participante), name='agregar_participante'),
    url(r'^agregar_participante_estudio/(?P<pk>\d+)/$', login_required(agregar_participante_estudio), name='agregar_participante_estudio'),

    url(r'^lista_opciones/(?P<pk>\d+)/$', login_required(listaOpciones), name='listaOpciones'),
    url(r'^crear_opcion/(?P<pk>\d+)/$', login_required(crear_opcion_respuesta), name='crear_opcion'),
    url(r'^editar_opcion/(?P<pk>\d+)/$', login_required(editar_opcion_respuesta), name='editar_opcion'),
    url(r'^eliminar_opcion/(?P<pk>\d+)/$', login_required(eliminar_opcion), name='eliminar_opcion'),

    url(r'^crear_cuestionario/(?P<pk>\d+)/$', login_required(Crear_Cuestionario.as_view()), name='crear_cuestionario'),
    url(r'^detalle_cuestionario/(?P<pk>\d+)', login_required(ListaSesiones.as_view()), name='detalle_cuestionario'),
    url(r'^editar_cuestionario/(?P<pk>\d+)/$', login_required(EditarCuestionario.as_view()), name='editar_cuestionario'),
    url(r'^preguntas_cuestionario/(?P<pk>\d+)/$', login_required(GenerarCuestionario.as_view()), name='cuestionario'),
    url(r'^editar_sesion/(?P<pk>\d+)/$', login_required(EditarSesion.as_view()), name='editar_sesion'),
    url(r'^cerrar_sesion/(?P<pk>\d+)/$', login_required(cerrar_sesion), name='cerrar_sesion'),
    url(r'^sesion_cuestionario/(?P<pk>\d+)/$', login_required(NuevaSesion_cuestionario.as_view()), name='sesion_cuestionario'),
    url(r'^responder/(?P<pk>\d+)/$',responder_cuestionario,name='responder_cuestionario'),

    url(r'^editar_pregunta/(?P<pk>\d+)/$', login_required(EditarPregunta.as_view()), name='editar_pregunta'),
    url(r'^eliminar_pregunta/(?P<pk>\d+)/$', login_required(EliminarPregunta.as_view()), name='eliminar_pregunta'),
    url(r'^lista_preguntas/(?P<pk>\d+)/$', login_required(ListaPreguntas.as_view()), name='preguntas'),

    url(r'^completar_pregunta/(?P<pk>\d+)/$', login_required(CompletarPregunta.as_view()), name='completar_pregunta'),
    url(r'^detalle_pregunta/(?P<pk>\d+)', login_required(DetallePregunta.as_view()), name='detalle_pregunta'),

    url(r'^pregunta/votar_positivo/(?P<pk>\d+)/$', login_required(votar_positivo_pregunta), name='votar_positivo'),
    url(r'^pregunta/votar_negativo/(?P<pk>\d+)/$', login_required(votar_negativo_pregunta), name='votar_negativo'),
    url(r'^nueva_pregunta/(?P<pk>\d+)/$', login_required(NuevaPregunta.as_view()), name='nueva_pregunta'),
    url(r'^pregunta/estadisticas/(?P<pk>\d+)/$', login_required(EstadisticasPregunta.as_view()), name='estadisticas'),
    url(r'^inicio/', inicio, name="inicio"),


    url(r'^crear_ronda/(?P<pk>\d+)$', login_required(CrearRonda.as_view()), name='crear_ronda'),
    url(r'^lista_rondas/(\d+)/$', login_required(ListaRondas.as_view()), name='rondas'),
    url(r'^editar_ronda/(?P<pk>\d+)/$', login_required(EditarRondaDelphi.as_view()), name='editar_ronda'),
    url(r'^consultar_ronda/(?P<pk>\d+)/$', login_required(ConsultarRonda.as_view()), name='consultar_ronda'),

    url(r'^ver_resultados/(?P<id_cuestionario>\d+)/$', login_required(ver_resultados), name='ver_resultados'),

]