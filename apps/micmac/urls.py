from django.conf.urls import url
from apps.micmac.views import *
urlpatterns = [

    url(r'^estudios_micmac',ListaEstudiosMicmac.as_view(), name='estudios_micmac'),
    url(r'^nuevo_estudios_micmac',Nuevo_estudio_Micmac.as_view(), name='crear_estudio'),
    url(r'^editar_estudios_micmac/(?P<pk>\d+)',MicmacUpdate.as_view(), name='editar_estudio'),
    url(r'^crear_variable/(?P<pk>\d+)', CrearVariable.as_view(), name='crear_variable'),
    url(r'^editar_variable/(?P<pk>\d+)', EditarVariable.as_view(), name='editar_variable'),
    url(r'^detalle_estudio/(?P<pk>\d+)', DetalleEstudioMicmac.as_view(), name='detalle_estudio'),
    url(r'^lista_variables/(?P<pk>\d+)', ListaVariables.as_view(), name='lista_variables'),
    url(r'^crear_sesion/(?P<pk>\d+)', CrearSesionVariable.as_view(), name='crear_sesion'),
    url(r'^crear_relacion/',RelacionCreate.as_view(), name='crear_relacion'),
    url(r'^micmac/matrix/relacion/crear/<int:pk>', RelacionUpdate.as_view(), name='editar_relacion'),
    url(r'^micmac/matrix/relacion/tabla', TableView.as_view(), name='tabla_relacion'),
    url(r'^micmac/matrix/mostrar/relacion_directa', MatrixListView.as_view(), name='matriz_directa'),
    url(r'^ micmac/matrix/relacion/directa/grafica', GraficaTemplate.as_view(), name='grafica_rdirecta'),
    url(r'^micmac/matrix/relacion/directa/grafica/json', get_json, name='json'),
    url(r'^micmac/matrix/relacion/directa/grafica/json/graph', grafica, name='grafica'),
    url(r'^micmac/matrix/relacion/directa/grafica/json/graph2', grafica_chartjs, name='grafica2')


]
