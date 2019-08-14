from datetime import date
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import json
from django.core import serializers
import numpy as np
from numpy import linalg as LA
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
# from apps.micmac.filters import RelacionFilter
from apps.micmac.forms import *
from apps.micmac.models import *
# Create your views here.
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, FormView, TemplateView, DetailView


def obtener_estudios_micmac_usuario(self):
    estudios = EstudioMicmac.objects.all().order_by('-estado', 'titulo')
    estudios_micmac_usuario = []

    for estudio in estudios:
        if estudio.moderador == self.request.user \
                or self.request.user in estudio.coordinadores.all() \
                or self.request.user in estudio.expertos.all():
            estudios_micmac_usuario.append(estudio)
    actualizar_estudios(estudios_micmac_usuario)

    return estudios_micmac_usuario


def actualizar_estudios(estudios_usuario):
    for estudio in estudios_usuario:
        if estudio.estado is True:
            if date.today() > estudio.fecha_final:
                estudio.estado = False
                estudio.save()


class ListaEstudiosMicmac(ListView):
    model = EstudioMicmac
    template_name = 'micmac/estudio/lista_estudio_micmac.html'

    def get_queryset(self):
        estudios = obtener_estudios_micmac_usuario(self)
        return estudios

    def get_context_data(self, **kwargs):
        context = super(ListaEstudiosMicmac, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context

    def post(self, request, **kwargs):
        mensaje = dict()
        if request.method == "POST":
            if "estudio_id" in request.POST:
                try:
                    estudio_id = self.request.POST['estudio_id']
                    p = EstudioMicmac.objects.get(pk=estudio_id)
                    mensaje = {'status':'True', 'estudio_id' :p.id}
                    p.delete()
                    return HttpResponse(json.dumps(mensaje), content_type='aplication/json')
                except:
                    mensaje = {'status': 'False'}
                    return HttpResponse(json.dumps(mensaje), contentype='aplication/json')


class Nuevo_estudio_Micmac(CreateView):
    form_class = MicmacForm
    template_name = 'micmac/estudio/NuevoEstudioMicmac.html'
    success_url = reverse_lazy('micmac:estudios_micmac')

    def get_context_data(self, **kwargs):
        context = super(Nuevo_estudio_Micmac, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Estudio ' + form.clean_titulo() + ' registrado con exito.')
        return super(Nuevo_estudio_Micmac, self).form_valid(form)

    def form_invalid(self, form):
        response = super(Nuevo_estudio_Micmac, self).form_invalid(form)
        messages.error(self.request, 'El estudio no pudo ser registrado, verifique los datos ingresados.')
        return response


class MicmacUpdate(UpdateView):
    model = EstudioMicmac
    form_class = MicmacForm
    template_name = 'micmac/estudio/micmac_form.html'
    success_url = reverse_lazy('micmac:listar_estudio')


class CrearVariable(CreateView):
    form_class = VariableForm
    template_name = 'micmac/variable/crearVariable.html'

    def get_context_data(self, **kwargs):
        estudio = EstudioMicmac.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'estudio': estudio})
        return super(CrearVariable, self).get_context_data(**kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.estudio = EstudioMicmac.objects.get(pk=self.kwargs.get('pk'))
        instance.autor = self.request.user
        return super(CrearVariable, self).form_valid(form=form)


class EditarVariable(UpdateView):
    model = Variable
    form_class = EditarVariableForm
    template_name = 'micmac/variable/editarVariable.html'

    def get_context_data(self, **kwargs):
        variable = get_object_or_404(Variable, id=self.kwargs['pk'])
        autor1 = variable.autor
        kwargs.update({'autor1': autor1})

        return super(EditarVariable, self).get_context_data(**kwargs)


def obtener_variables_micmac_usuario(self, estudio):
    variables = Variable.objects.filter(estudio=estudio).order_by('nombre_corto')
    variables_micmac_usuario = []

    for variable in variables:
        if variable.autor == self.request.user:
            variables_micmac_usuario.append(variable)
    return variables_micmac_usuario



class ListaVariables(DetailView):
    model = EstudioMicmac
    template_name = 'micmac/variable/listaVariablesMicmac.html'


    def post(self, request, **kwargs):
        if request.method == "POST":
            if "estudio_id" in request.POST:
                try:
                    varaible_id = self.request.POST['estudio_id']
                    p = Variable.objects.get(pk=varaible_id)
                    mensaje = {'status':'True', 'estudio_id' :p.id}
                    p.delete()
                    return HttpResponse(json.dumps(mensaje), content_type='aplication/json')
                except:
                    mensaje = {'status': 'False'}
                    return HttpResponse(json.dumps(mensaje), contentype='aplication/json')

    def get_context_data(self, **kwargs):
        variables = Variable.objects.filter(estudio=self.object)
        no_mis_variables = []
        mis_variables = obtener_variables_micmac_usuario(self, self.object)
        for variable in variables:
            if variable.autor != self.request.user:
                no_mis_variables.append(variable)

        kwargs.update({'variables': no_mis_variables,
                       'mis_variables': mis_variables,

                       }
                      )
        return super(ListaVariables, self).get_context_data(**kwargs)


class CrearSesionVariable(CreateView):
    form_class = SesionVariablesForm
    template_name = 'micmac/variable/sesionVariable.html'

    def get_context_data(self, **kwargs):
        context = super(CrearSesionVariable, self).get_context_data(**kwargs)
        estudio = EstudioMicmac.objects.get(pk=self.kwargs.get('pk'))
        sesion = SesionVariables.objects.filter(estudio=estudio.id).order_by('codigo')
        variables = Variable.objects.filter(estudio=estudio.id).count()

        if len(sesion) > 0:
            sesion_activa = sesion.filter(estado=True).count()
            context['cant_sesion_activa'] = sesion_activa
            context['codigo'] = sesion.last().codigo + 1
        else:
            context['cant_sesion_registradas'] = 0
            context['codigo'] = 1

        # Se verifica que existan preguntas registradas y una escala de likert que permita evaluarlas
        context['entradas_estudio'] = False
        if variables > 0:
            context['entradas_estudio'] = True

        context['estudio'] = estudio
        context['hoy'] = date.today()
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Sesión registrada con exito.')
        return super(CrearSesionVariable, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearSesionVariable, self).form_invalid(form)
        messages.error(self.request, 'La sesión no pudo ser registrada. Ingrese datos válidos')
        return response


def actualizar_sesiones(sesiones_list):
    for sesion in sesiones_list:
        if sesion.estado is True:
            if date.today() > sesion.fecha_final:
                sesion.estado = False
                sesion.save()


class DetalleEstudioMicmac(DetailView):
    model = EstudioMicmac
    template_name = 'micmac/estudio/detalleEstudioMicmac.html'
    success_url = reverse_lazy('micmac:estudios_micmac')

    def get_context_data(self, **kwargs):
        sesiones = SesionVariables.objects.filter(estudio=self.object)
        estudio = EstudioMicmac.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'sesiones': sesiones,
                       'estudio': estudio, }
                      )
        actualizar_sesiones(sesiones)
        return super(DetalleEstudioMicmac, self).get_context_data(**kwargs)


class RelacionCreate(CreateView):
    model = Relacion
    form_class = RelacionForm
    template_name = 'micmac/matriz/relacion_form.html'
    success_url = reverse_lazy('micmac:estudios_micmac')



class RelacionUpdate(UpdateView):
    model = Relacion
    form_class = RelacionEditarForm
    template_name = 'micmac/matriz/relacion_form.html'
    success_url = reverse_lazy('micmac:estudios_micmac')

    def get_object(self, queryset=Relacion.objects.all()):
        try:
            return super(RelacionUpdate, self).get_object(queryset)
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(RelacionUpdate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(request.POST)
        self.object = self.get_object()
        return super(RelacionUpdate, self).post(request, *args, **kwargs)



class TableView(ListView):
    model = Variable
    template_name = 'micmac/matriz/matriz_tabla.html'

    def get_context_data(self, **kwargs):

        for variable in Variable.objects.all():
            inf = 0
            dep = 0
            for relacion in Relacion.objects.all():
                if variable == relacion.de_variable:
                    inf = relacion.valoracion + inf
                if variable == relacion.a_variable:
                    dep = relacion.valoracion + dep
            variable.total_influencia = inf
            variable.total_dependencia = dep
            variable.save(update_fields=['total_influencia', 'total_dependencia'])
        return super(TableView, self).get_context_data(**kwargs)


class MatrixListView(ListView):
    model = Relacion
    template_name = 'micmac/matriz/matrizDirecta.html'


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['listado_relacion'] = sorted(list(Relacion.objects.all().values_list('de_variable', 'a_variable', 'valoracion')))
        nombres_variables = []
        # Agregar los nombres de las variables en una lista
        for elemento in Variable.objects.all():
            for relacion_var in Relacion.objects.all().values_list('de_variable'):
                if elemento.id == relacion_var[0]:
                    nombres_variables.append((elemento.nombre_corto, elemento.id))
            for relacion_var in Relacion.objects.all().values_list('a_variable'):
                if elemento.id == relacion_var[0]:
                    nombres_variables.append((elemento.nombre_corto, elemento.id))
        context['nom_var'] = sorted(set(nombres_variables))
        return context


class GraficaTemplate(TemplateView):
    template_name = 'micmac/graficas/grafica_base.html'


def get_json(request):
    return render(request, 'micmac/graficas/grafica_directa.html')


def grafica(request):
    queryset = Variable.objects.all()
    querylist = list(queryset)
    #Lista de influencias
    influencia = []
    dependencia = []
    for query in querylist:
        influencia.append(query.total_influencia)
        dependencia.append(query.total_dependencia)
    allValues = influencia + dependencia
    #JSON
    lista = list(map(lambda x: {'type': 'scatter', 'name': x.titulo_corto, 'data': [[x.total_dependencia, x.total_influencia]]}, querylist))
    areasmicmac = [
            {'type': 'polygon',
             'color': 'rgba(255, 255, 255, 0.2)',
             'name': 'Zona de Problemas Autonomos',
             'data': [[0, 0], [max(allValues)/2, 0], [max(allValues)/2, max(allValues)/2],[0, max(allValues)/2]]
             },
            {'type': 'polygon',
             'color': 'rgba(255, 255, 255, 0.2)',
             'name': 'Zona de Poder',
             'data': [[0, max(allValues)/2], [max(allValues)/2, max(allValues)/2], [max(allValues) / 2, max(allValues)], [0, max(allValues)]]},
            {'type': 'polygon',
             'color': 'rgba(255, 255, 255, 0.2)',
             'name': 'Zona de Salida',
             'data': [[max(allValues) / 2, 0], [max(allValues), 0], [max(allValues), max(allValues)/2], [max(allValues)/2, max(allValues)/2]]},
            {'type': 'polygon',
             'color': 'rgba(255, 255, 255, 0.2)',
             'name': 'Zona de Conflicto',
             'data': [[max(allValues) / 2, max(allValues) / 2], [max(allValues), max(allValues) / 2], [max(allValues), max(allValues)], [max(allValues) / 2, max(allValues)]]}
        ]

    data = {
        'title': {'text': 'Gráfica Relación Directa'},
        'xAxis': {'title': {'text': 'Dependencia'}, 'min': 0, 'max': max(allValues), \
                  'plotLines': [{'color': 'black', 'dashStyle': 'solid', 'value': max(allValues)/2, 'width': 1}]},
        'yAxis': {'title': {'text': 'Influencia'}, 'min': 0, 'max': max(allValues), \
                  'plotLines': [{'color': 'black', 'dashStyle': 'solid', 'value': max(allValues)/2, 'width': 1}]},
        'plotOptions': {'scatter':{'tooltip': {'pointFormat': 'Dependencia: {point.x}, Influencia: {point.y}'}}},
        'legend': {'enabled': False},
        'series': areasmicmac+lista,
    }
    return JsonResponse(data)


def grafica_chartjs (request):
    queryset = list(Variable.objects.all())
    matrizIndirecta = []
    index = 0
    for nomvar in list(Variable.objects.values_list('nombre_corto').order_by('nombre_corto')):
        matrizIndirecta.append([])
        lista = list(Relacion.objects.filter(de_variable__titulo_corto=nomvar[0]).values_list('valoracion').order_by(
                'a_variable__nombre_corto'))
        for valor in lista:
            matrizIndirecta[index].append(valor[0])
        index=index+1
    print(np.matrix(matrizIndirecta))
    print(len(matrizIndirecta))
    matrix_power = LA.matrix_power(matrizIndirecta, 9)
    print(matrix_power)
    data = {
        'matrix': matrix_power.tolist(),
    }
    return JsonResponse(data)
