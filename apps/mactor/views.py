import json
from .constants import VALOR_RELACION_NO_REGISTRADA, MATRIZ_COMPLETA, MATRIZ_INCOMPLETA
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse, request, Http404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from datetime import date, timedelta
from django.contrib import messages
from .models import *
from .forms import *
import xlwt

""" ----------------------------------------VIEWS MODELO ESTUDIO MACTOR---------------------------------"""


class ListaEstudios(ListView):

    model = EstudioMactor
    template_name = 'mactor/estudio/lista_estudios_mactor.html'
    context_object_name = 'estudios'
    paginate_by = 20

    def get_queryset(self):
        estudios = obtener_estudios_usuario(self)
        return estudios

    def get_context_data(self, **kwargs):
        context = super(ListaEstudios, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context


class CrearEstudio(CreateView):

    model = EstudioMactor
    form_class = FormEstudio
    template_name = 'mactor/estudio/crear_estudio_mactor.html'

    def get_context_data(self, **kwargs):
        context = super(CrearEstudio, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Estudio ' + form.clean_titulo() + ' registrado con exito.')
        return super(CrearEstudio, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearEstudio, self).form_invalid(form)
        messages.error(self.request, 'El estudio no pudo ser registrado. Verifique los datos ingresados.')
        return response


class ConsultarEstudio(DetailView):

    model = EstudioMactor
    template_name = 'mactor/estudio/consultar_estudio_mactor.html'
    context_object_name = 'estudio'

    def get_context_data(self, **kwargs):
        context = super(ConsultarEstudio, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context


class EditarEstudio(UpdateView):

    model = EstudioMactor
    form_class = FormEstudio
    template_name = 'mactor/estudio/editar_estudio_mactor.html'
    success_url = reverse_lazy('mactor:estudios_mactor')

    def get_context_data(self, **kwargs):
        context = super(EditarEstudio, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Estudio ' + form.clean_titulo() + ' actualizado con exito.')
        return super(EditarEstudio, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarEstudio, self).form_invalid(form)
        messages.error(self.request, 'El estudio no pudo ser actualizado. Verifique los datos ingresados.')
        return response


"""-------------------------------------------VIEWS MODELO ACTOR---------------------------------------"""


class ListaActores(ListView):

    model = Actor
    template_name = 'mactor/actor/lista_actores.html'
    context_object_name = 'actores'
    paginate_by = 15

    def get_queryset(self):
        self.estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        return Actor.objects.filter(idEstudio=self.estudio.id).order_by('nombreLargo')

    def get_context_data(self, **kwargs):
        context = super(ListaActores, self).get_context_data(**kwargs)
        context['estudio'] = self.estudio
        context['usuario'] = obtener_tipo_usuario(self.request, self.estudio.id)
        context['cant_actores'] = Actor.objects.filter(idEstudio=self.estudio.id).order_by('nombreLargo').count()
        return context


class CrearActor(CreateView):
    model = Actor
    form_class = FormActor
    template_name = 'mactor/actor/crear_actor.html'

    def get_context_data(self, **kwargs):
        context = super(CrearActor, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        context['estudio'] = estudio
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['cant_actores'] = Actor.objects.filter(idEstudio=estudio.id).order_by('nombreLargo').count()
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Actor ' + form.cleaned_data['nombreLargo'] + ' registrado con exito.')
        return super(CrearActor, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearActor, self).form_invalid(form)
        nombreLargo = form.cleaned_data["nombreLargo"]
        nombreCorto = form.cleaned_data["nombreCorto"]
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        actores_registrados = Actor.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        if actores_registrados.filter(nombreLargo=nombreLargo).count() > 0:
            messages.error(self.request, 'Ya existe un actor registrado con el nombre largo ' + nombreLargo)
        if actores_registrados.filter(nombreCorto=nombreCorto).count() > 0:
            messages.error(self.request, 'Ya existe un actor registrado con el nombre corto ' + nombreCorto)
        else:
            messages.error(self.request, 'El actor no pudo ser registrado. Verifique los datos ingresados.')
        return response


class EliminarActor(DeleteView):

    model = Actor
    template_name = 'mactor/actor/eliminar_actor.html'
    context_object_name = 'actor'
    success_message = "Actor eliminado con exito."

    def get_context_data(self, **kwargs):
        context = super(EliminarActor, self).get_context_data(**kwargs)
        actor = get_object_or_404(Actor, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=actor.idEstudio.id)
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarActor, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        actor = get_object_or_404(Actor, id=self.kwargs['pk'])
        return reverse('mactor:actores', args={actor.idEstudio.id})


class EditarActor(UpdateView):

    model = Actor
    form_class = FormActor
    template_name = 'mactor/actor/editar_actor.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super(EditarActor, self).get_context_data(**kwargs)
        actor = get_object_or_404(Actor, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, actor.idEstudio.id)
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Actor ' + form.cleaned_data['nombreLargo'] + ' actualizado con exito.')
        return super(EditarActor, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarActor, self).form_invalid(form)
        messages.error(self.request, 'El  registro del actor no pudo ser actulizado. Verifique los datos ingresados')
        return response


def consultar_actor(request):

    if request.is_ajax():
        id = request.GET.get('id')
        idEstudio = request.GET['idEstudio']

        # busqueda por nombre corto
        if id.count("mid") or id.count("caa") or id.count("daa"):
            id = id[3:]
            actor = get_object_or_404(Actor, nombreCorto=id, idEstudio=int(idEstudio))
        # busqueda por id con subcadena
        elif id.count("act") or id.count("ver"):
            id = id[3:]
            actor = get_object_or_404(Actor, id=id)
        # busqueda por id
        else:
            id = int(id)
            actor = get_object_or_404(Actor, id=id)

        response = JsonResponse(
            {'nombreCorto': actor.nombreCorto,
             'nombreLargo': actor.nombreLargo,
             'descripcion': actor.descripcion})
        return HttpResponse(response.content)
    else:
        return redirect('/')  # redirecciona a la misma pagina


""" -------------------------------------------VIEWS MODELO FICHA ACTOR-----------------------------------"""


class ListaFichas(ListView):

    model = Ficha
    template_name = 'mactor/ficha/lista_fichas.html'
    context_object_name = 'fichas'
    paginate_by = 20

    def get_queryset(self):
        self.estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        return Ficha.objects.filter(idActorY__idEstudio=self.estudio.id).order_by('idActorY', 'idActorX')

    def get_context_data(self, **kwargs):
        context = super(ListaFichas, self).get_context_data(**kwargs)
        context['estudio'] = self.estudio
        context['usuario'] = obtener_tipo_usuario(self.request, self.estudio.id)
        return context


class CrearFicha(CreateView):

    model = Ficha
    form_class = FormFicha
    template_name = 'mactor/ficha/nueva_ficha.html'

    def get_context_data(self, **kwargs):
        context = super(CrearFicha, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        context['estudio'] = estudio
        context['actores'] = actores
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['registrados_y'] = consultar_actores_eje_y_registrados(estudio.id, "ficha")
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Ficha de estrategias registrada con exito.')
        return super(CrearFicha, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearFicha, self).form_invalid(form)
        messages.error(self.request, 'La ficha de estrategias no pudo ser registrada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        return reverse('mactor:nueva_ficha', args=self.args[0])


class ConsultarFicha(DetailView):

    model = Ficha
    template_name = 'mactor/ficha/consultar_ficha.html'
    context_object_name = 'ficha'

    def get_context_data(self, **kwargs):
        context = super(ConsultarFicha, self).get_context_data(**kwargs)
        ficha = get_object_or_404(Ficha, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=ficha.idActorX.idEstudio.id)
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context


class EliminarFicha(DeleteView):

    model = Ficha
    template_name = 'mactor/ficha/eliminar_ficha.html'
    context_object_name = 'ficha'
    success_message = "Ficha de estrategias eliminada con exito."

    def get_context_data(self, **kwargs):
        context = super(EliminarFicha, self).get_context_data(**kwargs)
        ficha = get_object_or_404(Ficha, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=ficha.idActorX.idEstudio.id)
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarFicha, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        ficha = get_object_or_404(Ficha, id=self.kwargs['pk'])
        return reverse('mactor:fichas', args={ficha.idActorX.idEstudio.id})


class EditarFicha(UpdateView):

    model = Ficha
    form_class = FormFicha
    template_name = 'mactor/ficha/editar_ficha.html'
    context_object_name = 'ficha'

    def get_context_data(self, **kwargs):
        context = super(EditarFicha, self).get_context_data(**kwargs)
        ficha = get_object_or_404(Ficha, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, ficha.idActorX.idEstudio.id)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Ficha de estrategias actualizada con exito.')
        return super(EditarFicha, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarFicha, self).form_invalid(form)
        messages.error(self.request, 'La ficha de estrategias no pudo ser actualizada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        ficha = get_object_or_404(Ficha, id=self.kwargs['pk'])
        return reverse('mactor:fichas', args={ficha.idActorX.idEstudio.id})


# Obtiene la ficha de estrategias del par de actores seleccionado en el formulario de influencias mid
def consultar_ficha_mid(request):

    if request.is_ajax():
        response = JsonResponse({'estrategia': ""})
        if request.GET['id'] == "" or request.GET['id2'] == "":
            response = JsonResponse({'estrategia': "Seleccione el par de actores a consultar"})
            return HttpResponse(response.content)
        else:
            actorX = int(request.GET['id'])
            actorY = int(request.GET['id2'])
            idEstudio = int(request.GET['idEstudio'])
            filtro = Ficha.objects.filter(idActorX=actorX, idActorY=actorY, idActorY__idEstudio=idEstudio).count()

            if filtro > 0:
                ficha = get_object_or_404(Ficha, idActorX=actorX, idActorY=actorY, idActorY__idEstudio=idEstudio)
                if ficha.estrategia != "":
                    response = JsonResponse({'estrategia': ficha.estrategia})
            else:
                response = JsonResponse({'estrategia': "No se ha registrado la ficha de estrategias para el par de"
                                                       " actores seleccionado"})
            return HttpResponse(response.content)
    else:
        return redirect('/')


"""--------------------------------------------------------VIEWS MODELO OBJETIVO------------------------------"""


class ListaObjetivos(ListView):

    model = Objetivo
    template_name = 'mactor/objetivo/lista_objetivos.html'
    context_object_name = 'objetivos'
    paginate_by = 15

    def get_queryset(self):
        self.estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        return Objetivo.objects.filter(idEstudio=self.estudio.id).order_by('nombreLargo')

    def get_context_data(self, **kwargs):
        context = super(ListaObjetivos, self).get_context_data(**kwargs)
        context['estudio'] = self.estudio
        context['usuario'] = obtener_tipo_usuario(self.request, self.estudio.id)
        context['cant_objetivos'] = Objetivo.objects.filter(idEstudio=self.estudio.id).order_by('nombreLargo').count()
        return context


class CrearObjetivo(CreateView):

    model = Objetivo
    form_class = FormObjetivo
    template_name = 'mactor/objetivo/crear_objetivo.html'

    def get_context_data(self, **kwargs):
        context = super(CrearObjetivo, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        context['estudio'] = estudio
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['cant_objetivos'] = Objetivo.objects.filter(idEstudio=estudio.id).order_by('nombreLargo').count()
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Objetivo ' + form.cleaned_data['nombreLargo'] + ' registrado con exito.')
        return super(CrearObjetivo, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearObjetivo, self).form_invalid(form)
        nombreLargo = form.cleaned_data["nombreLargo"]
        nombreCorto = form.cleaned_data["nombreCorto"]
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        objetivos_registrados = Objetivo.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        if objetivos_registrados.filter(nombreLargo=nombreLargo).count() > 0:
            messages.error(self.request, 'Ya existe un objetivo registrado con el nombre largo ' + nombreLargo)
        if objetivos_registrados.filter(nombreCorto=nombreCorto).count() > 0:
            messages.error(self.request, 'Ya existe un objetivo registrado con el nombre corto ' + nombreCorto)
        else:
            messages.error(self.request, 'El objetivo no pudo ser registrado. Verifique los datos ingresados.')
        return response


class EliminarObjetivo(DeleteView):

    model = Objetivo
    template_name = 'mactor/objetivo/eliminar_objetivo.html'
    context_object_name = 'objetivo'
    success_message = "Objetivo eliminado con exito."

    def get_context_data(self, **kwargs):
        context = super(EliminarObjetivo, self).get_context_data(**kwargs)
        objetivo = get_object_or_404(Objetivo, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=objetivo.idEstudio.id)
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarObjetivo, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        objetivo = get_object_or_404(Objetivo, id=self.kwargs['pk'])
        return reverse('mactor:objetivos', args={objetivo.idEstudio.id})


class EditarObjetivo(UpdateView):

    model = Objetivo
    form_class = FormObjetivo
    template_name = 'mactor/objetivo/editar_objetivo.html'
    context_object_name = 'objetivo'

    def get_context_data(self, **kwargs):
        context = super(EditarObjetivo, self).get_context_data(**kwargs)
        objetivo = get_object_or_404(Objetivo, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, objetivo.idEstudio.id)
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Objetivo ' + form.cleaned_data['nombreLargo'] + ' actualizado con exito.')
        return super(EditarObjetivo, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarObjetivo, self).form_invalid(form)
        messages.error(self.request, 'El objetivo no pudo ser actulizado. Verifique los datos ingresados')
        return response


def consultar_objetivo(request):

    if request.is_ajax():
        id = request.GET.get('id')
        objetivo = get_object_or_404(Objetivo, id=int(id))
        response = JsonResponse({'nombreCorto': objetivo.nombreCorto, 'nombreLargo': objetivo.nombreLargo,
                                 'descripcion': objetivo.descripcion})
        return HttpResponse(response.content)
    else:
        return redirect('/')


"""-----------------------------------------VIEWS MODELO RELACION_MID-----------------------------------------"""


class ListaInfluenciasMID(ListView):

    model = RelacionMID
    template_name = 'mactor/mid/influenciasMID.html'
    context_object_name = 'influenciasMID'
    paginate_by = 14

    def get_queryset(self):
        self.estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        self.usuario = obtener_tipo_usuario(self.request, self.estudio.id)

        if self.usuario != 'COORDINADOR':
            influencias = RelacionMID.objects.filter(idExperto=self.request.user,
                                                     idActorY__idEstudio=self.estudio.id).order_by('idActorY', 'idActorX')
        else:
            influencias = RelacionMID.objects.filter(idActorY__idEstudio=self.estudio.id).order_by('idActorY', 'idActorX')

        # se excluyen las auto influencias ingresadas para hacer la matriz cuadrada
        for mid in influencias:
            if mid.idActorY == mid.idActorX:
                auxiliar = influencias.exclude(idActorY=mid.idActorX, idActorX=mid.idActorY)
                influencias = auxiliar
        return influencias

    def get_context_data(self, **kwargs):
        context = super(ListaInfluenciasMID, self).get_context_data(**kwargs)
        context['estudio'] = self.estudio
        context['usuario'] = obtener_tipo_usuario(self.request, self.estudio.id)
        context['porcentaje'] = calcular_porcentaje(self.request, self.estudio.id, "MID")
        context['hoy'] = date.today()
        return context


class CrearInfluenciaMID(CreateView):

    model = RelacionMID
    form_class = FormMID
    template_name = 'mactor/mid/nueva_influencia.html'

    def get_context_data(self, **kwargs):
        context = super(CrearInfluenciaMID, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        context['estudio'] = estudio
        context['actores'] = actores
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['porcentaje'] = calcular_porcentaje(self.request, estudio.id, "MID")
        context['registrados_y'] = consultar_actores_eje_y_registrados(estudio.id, "mid")
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Relación de influencia registrada con exito.')
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        crear_auto_influencia(self.request, estudio.id)
        return super(CrearInfluenciaMID, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearInfluenciaMID, self).form_invalid(form)
        messages.error(
            self.request, 'La relación de influencias no pudo ser registrada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        return reverse('mactor:nueva_mid', args=self.args[0])


class ConsultarInfluenciaMID(DetailView):

    model = RelacionMID
    template_name = 'mactor/mid/consultar_influencia.html'
    context_object_name = 'influencia'

    def get_context_data(self, **kwargs):
        context = super(ConsultarInfluenciaMID, self).get_context_data(**kwargs)
        mid = get_object_or_404(RelacionMID, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=mid.idActorX.idEstudio.id)
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context


class EditarInfluenciaMID(UpdateView):

    model = RelacionMID
    form_class = FormMID
    template_name = 'mactor/mid/editar_influencia.html'
    context_object_name = 'mid'

    def get_context_data(self, **kwargs):
        context = super(EditarInfluenciaMID, self).get_context_data(**kwargs)
        mid = get_object_or_404(RelacionMID, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, mid.idActorX.idEstudio.id)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Relación de influencia directa actualizada con exito.')
        return super(EditarInfluenciaMID, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarInfluenciaMID, self).form_invalid(form)
        messages.error(
            self.request, 'La relación de influencia directa no pudo ser actualizada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        mid = get_object_or_404(RelacionMID, id=self.kwargs['pk'])
        return reverse('mactor:influenciasMID', args={mid.idActorX.idEstudio.id})


# Genera la matriz mid
def generar_matriz_mid(request, idEstudio):  #  recibe idEstudio tipo str() para verificar consenso

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    usuario = obtener_tipo_usuario(request, estudio.id)
    tamano_matriz_completa = len(actores) ** 2
    influencias = []
    cantidad_expertos = 0  # expertos que han finalizado la matriz y por tanto estan en el consenso
    porcentaje = 0

    # si se esta accediendo al consenso de la matriz mid
    if consenso is True:
        influencias = calcular_consenso_mid(estudio.id)
        cantidad_expertos = influencias['num_expertos']
        influencias = influencias['consenso']
        if len(influencias) > 1:
            porcentaje = 100

    # si se esta accediendo a la matriz del usuario
    elif usuario != "COORDINADOR":
        influencias = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                                 idExperto=request.user.id).order_by('idActorY', 'idActorX')

    # si la matriz esta totalmente diligenciada o se esta accediendo al consenso
    if len(influencias) == tamano_matriz_completa and tamano_matriz_completa > 0 or consenso is True:
        valores_mid = establecer_valores_mid(estudio.id, influencias)
        if consenso is False:
            porcentaje = calcular_porcentaje(request, estudio.id, "MID")
        contexto = {'actores': actores, 'matriz': valores_mid, 'porcentaje': porcentaje, 'expertos': cantidad_expertos,
                    'estudio': estudio, 'usuario': usuario, 'consenso': consenso, 'estado_matriz': MATRIZ_COMPLETA}

    # si la matriz esta incompleta
    elif len(influencias) != tamano_matriz_completa and tamano_matriz_completa != 0:
        valores_mid = generar_mid_incompleta(request, estudio.id)
        porcentaje = calcular_porcentaje(request, estudio.id, "MID")
        contexto = {'actores': actores, 'porcentaje': porcentaje, 'matriz': valores_mid, 'estudio': estudio,
                    'usuario': usuario, 'consenso': consenso, 'estado_matriz': MATRIZ_INCOMPLETA}

    # si no se han registrado actores
    else:
        contexto = {'estudio': estudio, 'usuario': usuario}

    return render(request, 'mactor/mid/matrices/matriz_mid.html', contexto)


# Genera la matriz de influencias directas e indirectas
def generar_matriz_midi(request, idEstudio):  # idEstudio tipo str()

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    tamano_matriz_completa = len(actores) ** 2
    usuario = obtener_tipo_usuario(request, estudio.id)
    influencias_registradas = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                             idExperto=request.user.id).order_by('idActorY', 'idActorX').count()

    # si la matriz esta completa o el consenso esta activo
    if influencias_registradas == tamano_matriz_completa and tamano_matriz_completa > 0 or consenso is True:
        valores_midi = calcular_midi(request, idEstudio)
        cantidad_expertos = 0

        if consenso is True:
            influencias_consenso = calcular_consenso_mid(estudio.id)
            cantidad_expertos = influencias_consenso['num_expertos']

        contexto = {'actores': actores, 'matriz': valores_midi, 'expertos': cantidad_expertos, 'estudio': estudio,
                    'usuario': usuario, 'consenso': consenso}
    else:
        contexto = {'estudio': estudio, 'usuario': usuario}

    return render(request, 'mactor/mid/matrices/matriz_midi.html', contexto)


# Genera la matriz maxima de influencias directas e indirectas
def generar_matriz_maxima(request, idEstudio):  # idEstudio tipo str()

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    tamano_matriz_completa = len(actores) ** 2
    usuario = obtener_tipo_usuario(request, estudio.id)
    influencias = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                             idExperto=request.user.id).order_by('idActorY', 'idActorX')

    if len(influencias) == tamano_matriz_completa and tamano_matriz_completa > 0 or consenso is True:
        valores_maximos = calcular_maxima_influencia(request, idEstudio)
        cantidad_expertos = 0

        if consenso is True:
            influencias_consenso = calcular_consenso_mid(estudio.id)
            cantidad_expertos = influencias_consenso['num_expertos']

        contexto = {'actores': actores, 'valores_maximos': valores_maximos, 'expertos': cantidad_expertos,
                    'estudio': estudio, 'usuario': usuario, 'consenso': consenso}
    else:
        contexto = {'estudio': estudio, 'usuario': usuario}

    return render(request, 'mactor/mid/matrices/matriz_maxima.html', contexto)


# Genera la matriz de balance liquido
def generar_matriz_balance(request, idEstudio):  # idEstudio tipo str()

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    influencias = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                             idExperto=request.user.id).order_by('idActorY', 'idActorX')
    tamano_matriz_completa = len(actores) ** 2
    tipo_usuario = obtener_tipo_usuario(request, estudio.id)

    if len(influencias) == tamano_matriz_completa and tamano_matriz_completa > 0 or consenso is True:
        valores_balance = calcular_balance_liquido(request, idEstudio)
        cantidad_expertos = 0
        if consenso is True:
            influencias_mid = calcular_consenso_mid(estudio.id)
            cantidad_expertos = influencias_mid['num_expertos']
        contexto = {'actores': actores, 'valores_balance': valores_balance, 'expertos': cantidad_expertos,
                    'estudio': estudio, 'usuario': tipo_usuario, 'consenso': consenso}
    else:
        contexto = {'estudio': estudio, 'usuario': tipo_usuario}

    return render(request, 'mactor/mid/matrices/matriz_balance.html', contexto)


# Genera la matriz de coeficientes de fuerza Ri
def generar_matriz_ri(request, idEstudio):

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    valores_ri = calcular_ri(request, idEstudio)
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    usuario = obtener_tipo_usuario(request, estudio.id)

    matriz_ri = []
    fila = []
    for i in range(len(valores_ri)):
        fila.append(ValorPosicion(posicion=0, valor=actores[i].nombreCorto, descripcion=actores[i].nombreLargo))
        fila.append(ValorPosicion(posicion=1, valor=round(valores_ri[i], 2), descripcion=round(valores_ri[i], 2)))
        matriz_ri.append(fila)
        fila = []

    cantidad_expertos = 0
    if consenso is True:
        influencias_mid = calcular_consenso_mid(estudio.id)
        cantidad_expertos = influencias_mid['num_expertos']

    contexto = {'lista_contexto': matriz_ri, 'expertos': cantidad_expertos, 'estudio': estudio,
                'usuario': usuario, 'consenso': consenso}

    return render(request, 'mactor/mid/matrices/matriz_ri.html', contexto)


# Genera el indicador de estabilidad H
def generar_indicador_estabilidad(request, idEstudio):  # idEstudio tipo str()

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    indicador = calcular_estabilidad(request, idEstudio)
    tipo_usuario = obtener_tipo_usuario(request, estudio.id)

    cantidad_expertos = 0
    if consenso is True:
        influencias_mid = calcular_consenso_mid(estudio.id)
        cantidad_expertos = influencias_mid['num_expertos']

    contexto = {'indicador': indicador, 'expertos': cantidad_expertos, 'estudio': estudio,
                'usuario': tipo_usuario, 'consenso': consenso}

    return render(request, 'mactor/mid/matrices/indicador_estabilidad.html', contexto)


"""-----------------------------------------VIEWS MODELO RELACION_MAO----------------------------------"""


class ListaRelacionesMAO(ListView):

    model = RelacionMAO
    template_name = 'mactor/mao/relacionesMAO.html'
    context_object_name = 'relacionesMAO'
    paginate_by = 15

    def get_queryset(self):
        self.estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        influencias = RelacionMAO.objects.filter(idExperto=self.request.user,
                                                 idActorY__idEstudio=self.estudio.id,
                                                 tipo=int(self.args[1])).order_by('idActorY', 'idObjetivoX')
        return influencias

    def get_context_data(self, **kwargs):
        context = super(ListaRelacionesMAO, self).get_context_data(**kwargs)
        context['estudio'] = self.estudio
        context['usuario'] = obtener_tipo_usuario(self.request, self.estudio.id)
        context['tipo'] = self.args[1]
        if self.args[1] == "1":
            context['porcentaje'] = calcular_porcentaje(self.request, self.estudio.id, "1MAO")
        else:
            context['porcentaje'] = calcular_porcentaje(self.request, self.estudio.id, "2MAO")
        return context


class CrearRelacion1MAO(CreateView):

    model = RelacionMAO
    form_class = Form1mao
    template_name = 'mactor/mao/nueva_relacion.html'

    def get_context_data(self, **kwargs):
        context = super(CrearRelacion1MAO, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        objetivos = Objetivo.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        context['estudio'] = estudio
        context['actores'] = actores
        context['objetivos'] = objetivos
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['porcentaje'] = calcular_porcentaje(self.request, estudio.id, "1MAO")
        context['tipo'] = 1
        context['registrados_y'] = consultar_actores_eje_y_registrados(estudio.id, "1mao")
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Relación 1MAO registrada con exito.')
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        crear_auto_influencia(self.request, estudio.id)
        return super(CrearRelacion1MAO, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearRelacion1MAO, self).form_invalid(form)
        messages.error(self.request, 'La relación no pudo ser registrada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        return reverse('mactor:1MAO', args=self.args[0])


class CrearRelacion2MAO(CreateView):

    model = RelacionMAO
    form_class = Form2mao
    template_name = 'mactor/mao/nueva_relacion.html'

    def get_context_data(self, **kwargs):
        context = super(CrearRelacion2MAO, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        objetivos = Objetivo.objects.filter(idEstudio=estudio.id).order_by('nombreLargo')
        context['estudio'] = estudio
        context['actores'] = actores
        context['objetivos'] = objetivos
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['porcentaje'] = calcular_porcentaje(self.request, estudio.id, "2MAO")
        context['tipo'] = 2
        context['registrados_y'] = consultar_actores_eje_y_registrados(estudio.id, "2mao")
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Relación 2MAO registrada con exito.')
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        crear_auto_influencia(self.request, estudio.id)
        return super(CrearRelacion2MAO, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearRelacion2MAO, self).form_invalid(form)
        messages.error(self.request, 'La relación no pudo ser registrada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        return reverse('mactor:2MAO', args=self.args[0])


class ConsultarRelacionMAO(DetailView):

    model = RelacionMAO
    template_name = 'mactor/mao/consultar_relacion.html'
    context_object_name = 'relacion'

    def get_context_data(self, **kwargs):
        context = super(ConsultarRelacionMAO, self).get_context_data(**kwargs)
        mao = get_object_or_404(RelacionMAO, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=mao.idActorY.idEstudio.id)
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        return context


class EditarRelacion1MAO(UpdateView):

    model = RelacionMAO
    form_class = Form1mao
    template_name = 'mactor/mao/editar_relacion.html'
    context_object_name = 'mao'

    def get_context_data(self, **kwargs):
        context = super(EditarRelacion1MAO, self).get_context_data(**kwargs)
        mao = get_object_or_404(RelacionMAO, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, mao.idActorY.idEstudio.id)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Relación 1MAO actualizada con exito.')
        return super(EditarRelacion1MAO, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarRelacion1MAO, self).form_invalid(form)
        messages.error(self.request, 'La relación no pudo ser actualizada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        mao = get_object_or_404(RelacionMAO, id=self.kwargs['pk'])
        return reverse('mactor:relacionesMAO', args=[mao.idActorY.idEstudio.id, 1])


class EditarRelacion2MAO(UpdateView):

    model = RelacionMAO
    form_class = Form2mao
    template_name = 'mactor/mao/editar_relacion.html'
    context_object_name = 'mao'

    def get_context_data(self, **kwargs):
        context = super(EditarRelacion2MAO, self).get_context_data(**kwargs)
        mao = get_object_or_404(RelacionMAO, id=self.kwargs['pk'])
        context['usuario'] = obtener_tipo_usuario(self.request, mao.idActorY.idEstudio.id)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Relación 2MAO actualizada con exito.')
        return super(EditarRelacion2MAO, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarRelacion2MAO, self).form_invalid(form)
        messages.error(self.request, 'La relación no pudo ser actualizada. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        mao = get_object_or_404(RelacionMAO, id=self.kwargs['pk'])
        return reverse('mactor:relacionesMAO', args=[mao.idActorY.idEstudio.id, 2])


# Genera las matrices actores x objetivos
def generar_matriz_mao(request, idEstudio, numero_matriz):  # idEstudio tipo str

    contexto = crear_contexto_mao(request, idEstudio, int(numero_matriz))

    if int(numero_matriz) in [1, 2, 3]:
        return render(request, 'mactor/mao/matrices/matriz_mao.html', contexto)
    else:
        raise Http404("Error: Esta vista no existe")


# Calcula el porcentaje diligenciamiento de la matriz pasada como argumento
def calcular_porcentaje(request, idEstudio, matriz):

    estudio = EstudioMactor.objects.get(id=idEstudio)
    actores = Actor.objects.filter(idEstudio=estudio.id).count()
    porcentaje = 0

    if matriz == "MID":
        influencias_total = (actores ** 2) - actores    # total de influencias que se deben registrar exc diagonal
        influencias_registradas = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                                             idExperto=request.user.id)

        # Se excluyen los valores de la diagonal
        cont = 0
        for inf in influencias_registradas:
            if inf.idActorY != inf.idActorX:
                cont += 1

        if cont > 0:
            porcentaje = round((100 / influencias_total) * cont, 2)

    elif matriz == "1MAO":

        objetivos = Objetivo.objects.filter(idEstudio=estudio.id).count()
        relaciones_total = actores * objetivos
        relaciones_registradas = len(RelacionMAO.objects.filter(idActorY__idEstudio=estudio.id,
                                                                idExperto=request.user.id, tipo=1))
        if relaciones_registradas > 0:
            porcentaje = round((100 / relaciones_total) * relaciones_registradas, 2)

    else:
        objetivos = Objetivo.objects.filter(idEstudio=estudio.id).count()
        relaciones_total = actores * objetivos
        relaciones_registradas = len(RelacionMAO.objects.filter(idActorY__idEstudio=estudio.id,
                                                                idExperto=request.user.id, tipo=2))
        if relaciones_registradas > 0:
            porcentaje = round((100 / relaciones_total) * relaciones_registradas, 2)

    return porcentaje


# Genera las matrices convergencia y divergencia
def generar_matrices_caa_daa(request, idEstudio, numero_matriz):

    consenso = verificar_consenso(request, idEstudio)
    numero_matriz = int(numero_matriz)
    valores_mao = []

    if numero_matriz in [1, 2, 3]:
        estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
        usuario = obtener_tipo_usuario(request, estudio.id)
        contexto_mao = crear_contexto_mao(request, idEstudio, numero_matriz)
        if contexto_mao['estado_matriz'] == MATRIZ_COMPLETA:
            valores_mao = contexto_mao['valores_mao']

        num_expertos = 0
        if consenso is True:
            if numero_matriz == 3:
                num_expertos = calcular_consenso_mao(request, estudio.id,
                                                     numero_matriz - 1)['expertos']  # porque 3mao se calcula apartir de 2mao
            else:
                num_expertos = calcular_consenso_mao(request, estudio.id, numero_matriz)['expertos']

        if contexto_mao['estado_matriz'] == MATRIZ_COMPLETA:
            valores_caa = calcular_caa(idEstudio, valores_mao)
            valores_daa = calcular_daa(idEstudio, valores_mao)

            contexto = {'actores': actores, 'valores_caa': valores_caa, 'valores_daa': valores_daa, 'estudio': estudio,
                        'numero_matriz': numero_matriz, 'usuario': usuario, 'expertos': num_expertos,
                        'consenso': consenso}

        else:
            contexto = {'estudio': estudio, 'numero_matriz': numero_matriz, 'usuario': usuario,
                        'expertos': num_expertos, 'consenso': consenso}

        return render(request, 'mactor/mao/matrices/matrices_caa_daa.html', contexto)
    else:
        raise Http404("Error: Esta vista no existe")


"""-------------------------------------------------CLASES AUXILIARES------------------------------------------------"""


# Clase auxiliar para la generacion de matrices, se asigna una posicion a un respectivo valor
class ValorPosicion:
    def __init__(self, posicion, valor, descripcion):
        self.posicion = posicion
        self.valor = valor
        self.descripcion = descripcion


# Clase auxiliar para la generacion de matrices, se asigna una posicion a un respectivo valor
class ValorPareja:
    def __init__(self, x, y, valor):
        self.x = x
        self.y = y
        self.valor = valor


"""---------------------------------------------FUNCIONES AUXILIARES MATRICES MID-----------------------------------"""


# Crea los 0 de la diagonal de la matriz mid, para que la matriz sea cuadrada
def crear_auto_influencia(request, idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    influencias = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                             idExperto=request.user.id).order_by('idActorY', 'idActorX')
    lista_registrados = []

    # se verifica si estas influencias ya existen
    for actor in actores:
        for inf in influencias:
            if len(influencias) > 0 and inf.idActorX.id == actor.id and inf.idActorY.id == actor.id:
                lista_registrados.append(actor.id)

    # se agregan las autoinfluencias restantes
    for actor in actores:
        if actor.id not in lista_registrados:
            a = RelacionMID()
            a.idActorY = actor
            a.idActorX = actor
            a.valor = 0
            a.justificacion = "auto_influencia"
            a.idExperto = request.user
            a.save()


# Genera las filas de la matriz mid
def establecer_valores_mid(idEstudio, influencias):

    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    matriz_mid = []
    fila = []
    sumaFila = 0
    cont = 1

    for i in influencias:
        # se inserta el valor del eje Y (nombre corto del actor)
        if len(fila) == 0:
            fila.append(ValorPosicion(posicion=0, valor=actores[len(matriz_mid)].nombreCorto,
                                      descripcion=actores[len(matriz_mid)].nombreLargo))

        # se insertan los valores de influencias directas del actor
        descripcion = obtener_descripcion_mid(i.valor)
        fila.append(ValorPosicion(posicion=cont, valor=i.valor, descripcion=descripcion))
        cont += 1

        # se calcula el valor de influencia directa del actor
        if i.valor != VALOR_RELACION_NO_REGISTRADA:
            sumaFila += i.valor

        # se ingresa la fila a la matriz
        if len(fila) == (actores.count() + 1):
            fila.append(ValorPosicion(posicion=cont, valor=sumaFila, descripcion=sumaFila))
            matriz_mid.append(fila)
            fila = []
            sumaFila = 0
            cont = 1

    # Se calculan las dependencias directas D.D (suma de columnas)
    cont = 1
    fila.append(ValorPosicion(posicion=0, valor="D.D", descripcion="DEPENDENCIA DIRECTA"))
    sumaColumna = 0
    sumaTotal = 0

    while cont <= actores.count():
        for fil in matriz_mid:
            for celda in fil:
                if celda.posicion == cont:
                    if celda.valor != VALOR_RELACION_NO_REGISTRADA:
                        sumaColumna += celda.valor
                        sumaTotal += celda.valor
        fila.append(ValorPosicion(posicion=cont, valor=sumaColumna, descripcion=sumaColumna))
        sumaColumna = 0
        cont += 1

    fila.append(ValorPosicion(posicion=cont, valor=sumaTotal, descripcion=sumaTotal))
    matriz_mid.append(fila)

    return matriz_mid


# Genera la matriz mid con los valores actualmente registrados, destacando los que hacen falta
def generar_mid_incompleta(request, idEstudio):

    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    mid = RelacionMID.objects.filter(idActorY__idEstudio=idEstudio, idExperto=request.user.id).order_by('idActorY',
                                                                                                        'idActorX')
    lista_ejes_incompletos = []
    lista_ejes_ordenados = []

    # se obtiene el orden en que deben ir los actores en la matriz (ejes Y y X) estructura correcta de la matriz
    for i in actores:
        for j in actores:
            lista_ejes_ordenados.append(ValorPareja(y=i.id, x=j.id, valor=""))

    # se obtienen las parejas de ejes, actualmente registradas y su valor correspondiente
    for inf in mid:
        lista_ejes_incompletos.append(ValorPareja(y=inf.idActorY.id, x=inf.idActorX.id, valor=inf.valor))

    # se ingresan a la lista de ejes incompletos, valores relleno que facilitan la comparacion con la de ejes ordenados
    cont = 0
    while len(lista_ejes_incompletos) != len(lista_ejes_ordenados):
        lista_ejes_incompletos.append(ValorPareja(y=0, x=0, valor=0))
        cont += 1

    # se detectan los ejes faltantes y se ingresan en esas posiciones el valor 100 para indicar la falta del registro
    for j in range(len(lista_ejes_ordenados)):
        eje_y = lista_ejes_ordenados[j].y
        eje_x = lista_ejes_ordenados[j].x
        if lista_ejes_incompletos[j].y != eje_y or lista_ejes_incompletos[j].x != eje_x:
            lista_ejes_incompletos.insert(j, ValorPareja(y=eje_y, x=eje_x, valor=VALOR_RELACION_NO_REGISTRADA))

    # se eliminan de la lista de ejes incompletos los valores relleno inicialmente ingresados para comparar
    while cont != 0:
        lista_ejes_incompletos.pop()
        cont -= 1

    lista_contexto = establecer_valores_mid(idEstudio, lista_ejes_incompletos)
    return lista_contexto


# Devuelve el significado de cada valor de la matriz mid
def obtener_descripcion_mid(valor):

    descripcion = ""

    if valor == 0:
        descripcion = "Sin influencia"
    elif valor == 1:
        descripcion = "Procesos"
    elif valor == 2:
        descripcion = "Proyectos"
    elif valor == 3:
        descripcion = "Misión"
    elif valor == 4:
        descripcion = "Existencia"

    return descripcion


# Calcula los valores de la matriz MIDI
def calcular_midi(request, idEstudio):

    estudio = int(idEstudio)
    actores = Actor.objects.filter(idEstudio=estudio).order_by('id')
    lista_comparacion_minimo = []  # contiene las sublistas de valores minimos por cada actor Y
    lista_suma = []                # contiene lista_comparacion_minimo concatenado
    matriz_midi = []

    if verificar_consenso(request, idEstudio):  # se trabaja con la lista mid de consenso
        influencias_mid = calcular_consenso_mid(estudio)
        influencias_mid = influencias_mid['consenso']
    else:
        influencias_mid = RelacionMID.objects.filter(idActorY__idEstudio=estudio, idExperto=request.user.id).order_by(
            'idActorY', 'idActorX')  # se trabaja con la lista mid del usuario en sesion

    # Si Mid esta completamente diligenciada
    if len(influencias_mid) == (len(actores) ** 2):
        # se agrega la sublista de valores minimos correspondiente al actorY a lista_comparacion_minimo
        for actor in range(len(influencias_mid)):
            if influencias_mid[actor].idActorY == influencias_mid[actor].idActorX:
                # cada valor de actor permite el calculo de la suma de sus valores minimos
                lista_comparacion_minimo.append(sumar_valores_minimos(request, actorY=actor, idEstudio=idEstudio))

        # concatenacion de lista_minimo para facilitar la suma con las influencias correspondientes (igual longitud)
        for minimo in lista_comparacion_minimo:
            lista_suma += minimo

        fila = []
        sumaFila = 0
        cont = 1

        if len(influencias_mid) > 0:
            for i in range(len(influencias_mid)):
                # se ingresa el encabezado de la fila (nombre corto del actor)
                if len(fila) == 0:
                    fila.append(
                        ValorPosicion(posicion=0, valor=actores[len(matriz_midi)].nombreCorto,
                                      descripcion=actores[len(matriz_midi)].nombreLargo))

                # se calcula e ingresa a la fila cada valor midi
                valor_midi = influencias_mid[i].valor + lista_suma[i]
                fila.append(ValorPosicion(posicion=cont, valor=valor_midi, descripcion=valor_midi))
                sumaFila += valor_midi
                cont += 1

                # se calcula e ingresa la suma de la fila
                if len(fila) == (actores.count() + 1):
                    sumaFila -= fila[len(matriz_midi) + 1].valor  # se resta la inf direc del actor sobre si mismo
                    fila.append(ValorPosicion(posicion=cont, valor=sumaFila, descripcion=sumaFila))
                    matriz_midi.append(fila)   # construida la fila se ingresa a la matriz
                    fila = []
                    sumaFila = 0
                    cont = 1

            # se calcula e ingresa la fila de las dependencias (ultima fila de la matriz)
            cont = 1
            fila.append(ValorPosicion(posicion=0, valor="D.DI", descripcion="DEPENDENCIA DIRECTA E INDIRECTA"))
            sumaColumna = 0
            sumaTotal = 0

            while cont <= actores.count():
                for fil in matriz_midi:
                    for celda in fil:
                        if celda.posicion == cont and fil[0].valor != actores[cont - 1].nombreCorto:
                            sumaColumna += celda.valor
                            sumaTotal += celda.valor
                fila.append(ValorPosicion(posicion=cont, valor=sumaColumna, descripcion=sumaColumna))
                sumaColumna = 0
                cont += 1

            fila.append(ValorPosicion(posicion=cont, valor=sumaTotal, descripcion=sumaTotal))
            matriz_midi.append(fila)

    return matriz_midi


# Suma de valores minimos (lado derecho formula midi), idEstudio tipo str
def sumar_valores_minimos(request, actorY, idEstudio):

    estudio = int(idEstudio)
    actores = Actor.objects.filter(idEstudio=estudio).order_by('id')

    if verificar_consenso(request, idEstudio):
        mid = calcular_consenso_mid(estudio)
        mid = mid['consenso']
    else:
        mid = RelacionMID.objects.filter(idActorY__idEstudio=estudio, idExperto=request.user.id).order_by('idActorY',
                                                                                                          'idActorX')

    lista_suma = [0] * len(mid)     # contiene la suma de los valores minimos establecidos al comparar
    valores_minimos = obtener_valores_minimos(request, idEstudio, actorY)
    inicio_sublista = 0             # indica el punto inicial de la sublista
    fin_sublista = actores.count()  # indica el punto final de la sublista

    # la lista valores_minimos es divida y sumada
    for i in range(fin_sublista):
        if i < actores.count() - 1:
            lista_suma = map(sum, zip(lista_suma, valores_minimos[inicio_sublista:fin_sublista]))
            inicio_sublista = fin_sublista
            fin_sublista = fin_sublista + actores.count()

    return lista_suma


# Calcula los valores de la matriz maxima
def calcular_maxima_influencia(request, idEstudio):

    estudio = int(idEstudio)
    actores = Actor.objects.filter(idEstudio=estudio).order_by('id')
    lista_comparacion_minimo = []  # contiene las sublistas de valores minimos por cada actores Y
    lista_maximos = []             # contiene lista_comparacion_minimo concatenado (sin sublista)

    if verificar_consenso(request, idEstudio):
        influencias_mid = calcular_consenso_mid(estudio)
        influencias_mid = influencias_mid['consenso']
    else:
        influencias_mid = RelacionMID.objects.filter(idActorY__idEstudio=estudio,
                                                     idExperto=request.user.id).order_by('idActorY', 'idActorX')

    # se agrega la sublista de valores minimos correspondiente al actorY a lista_comparacion_minimo
    for inf in range(len(influencias_mid)):
        if influencias_mid[inf].idActorY == influencias_mid[inf].idActorX:
            # cada valor de actorY permite el calculo de una fila de la matriz
            lista_comparacion_minimo.append(mayor_valores_minimos(request, actorY=inf, idEstudio=idEstudio))

    # concatenacion de lista_minimo para facilitar la suma con las influencias correspondientes (igual longitud)
    for i in lista_comparacion_minimo:
        lista_maximos += i

    matriz_maxima = []
    fila = []
    sumaFila = 0
    cont = 1

    if len(influencias_mid) > 0:
        for i in range(len(influencias_mid)):
            # se ingresa el encabezado de la fila (nombre corto del actor)
            if len(fila) == 0:
                fila.append(
                    ValorPosicion(posicion=0, valor=actores[len(matriz_maxima)].nombreCorto,
                                  descripcion=actores[len(matriz_maxima)].nombreLargo))

            if influencias_mid[i].idActorY != influencias_mid[i].idActorX:
                # se calcula e ingresa a la fila cada valor maximo
                maximo = max(influencias_mid[i].valor, lista_maximos[i])
                fila.append(ValorPosicion(posicion=cont, valor=maximo, descripcion=maximo))
                sumaFila += maximo
                cont += 1
            else:
                fila.append(ValorPosicion(posicion=cont, valor=0, descripcion=0))
                cont += 1

            # se calcula e ingresa la suma de la fila
            if len(fila) == (actores.count() + 1):
                sumaFila -= fila[len(matriz_maxima) + 1].valor  # se resta la inf directa e ind del actor sobre si mismo
                fila.append(ValorPosicion(posicion=cont, valor=sumaFila, descripcion=sumaFila))
                matriz_maxima.append(fila)  # construida la fila se ingresa a la matriz
                fila = []
                sumaFila = 0
                cont = 1

        # se calcula e ingresa la fila de las dependencias maximas (ultima fila de la matriz)
        cont = 1
        fila.append(ValorPosicion(posicion=0, valor="D.DI", descripcion="DEPENDENCIA DIRECTA E INDIRECTA"))
        sumaColumna = 0
        sumaTotal = 0

        while cont <= actores.count():
            for fil in matriz_maxima:
                for celda in fil:
                    if celda.posicion == cont and fil[0].valor != actores[cont - 1].nombreCorto:
                        sumaColumna += celda.valor
                        sumaTotal += celda.valor
            fila.append(ValorPosicion(posicion=cont, valor=sumaColumna, descripcion=sumaColumna))
            sumaColumna = 0
            cont += 1

        fila.append(ValorPosicion(posicion=cont, valor=sumaTotal, descripcion=sumaTotal))
        matriz_maxima.append(fila)

    return matriz_maxima


# Determina de valores minimos mayores, (lado derecho formula maxima) idEstudio tipo str
def mayor_valores_minimos(request, actorY, idEstudio):

    actores = Actor.objects.filter(idEstudio=int(idEstudio)).order_by('id')
    lista_minimos = obtener_valores_minimos(request, idEstudio, actorY)
    lista_comparar = []
    lista_mayores = []

    # Se asigna una posicion a los valores minimos para facilitar la comparacion y posterior visualizacion
    contador = 0
    for minimo in lista_minimos:
        if contador < actores.count():
            lista_comparar.append(ValorPosicion(posicion=contador, valor=minimo, descripcion=""))
            contador += 1
        if contador + 1 > actores.count():
            contador = 0

    # Se determinan el valor mayor dentro de la lista de valores minimos por cada pareja ij
    posicion = 0
    while posicion < actores.count():
        mayor = 0
        for i in lista_comparar:
            if i.posicion == posicion and i.valor > mayor:
                mayor = i.valor
        lista_mayores.append(mayor)
        posicion += 1

    return lista_mayores


# Obtiene los valores minimos, necesarios para midi y maxima, idEstudio tipo str
def obtener_valores_minimos(request, idEstudio, actorY):

    estudio = int(idEstudio)
    actores = Actor.objects.filter(idEstudio=estudio).order_by('id')
    valores_izquierdos = []  # contiene los valores izquierdos a comparar
    valores_derechos = []  # contiene los valores derechos a comparar
    valores_minimos = []  # contiene los valores minimos establecidos al comparar valores_izquierdos vs derechos

    if verificar_consenso(request, idEstudio):
        mid = calcular_consenso_mid(estudio)
        mid = mid['consenso']
    else:
        mid = RelacionMID.objects.filter(idActorY__idEstudio=estudio, idExperto=request.user.id).order_by('idActorY',
                                                                                                          'idActorX')
    if len(mid) == (len(actores) ** 2):
        # Valores_derechos: influencias de los actores influenciados por Y sobre el actor X excepto Y
        indice = 1
        aux = 0
        for i in range(len(mid)):
            # se verifica si en el registro actual (i), el campo idActorY no corresponde al actorY recibido
            if mid[i].idActorY != mid[actorY].idActorY:
                valores_derechos.append(ValorPosicion(posicion=indice, valor=mid[i].valor, descripcion=""))
                aux += 1
                if aux == actores.count():
                    indice += 1
                    aux = 0

        # Valores_izquierdos: influencias del actorY recibido, sobre los demas.
        indice = 0
        for i in range(len(mid)):
            longitud = len(valores_izquierdos)
            cantidad_actores = actores.count() - 1
            eje_y = mid[i].idActorY
            eje_x = mid[i].idActorX
            # para que no tenga en cuenta la influencia sobre si mismo
            if mid[actorY].idActorY != eje_x and eje_y == mid[actorY].idActorY and longitud < cantidad_actores:
                valores_izquierdos.append(ValorPosicion(posicion=indice + 1, valor=mid[i].valor, descripcion=""))
                indice += 1

        # se establece el minimo entre cada pareja izquierdo[i] - derecho[i]
        indice = 0
        for i in range(len(valores_derechos)):
            if valores_izquierdos[indice].posicion == valores_derechos[i].posicion and indice < actores.count():
                minimo = min(valores_izquierdos[indice].valor, valores_derechos[i].valor)
                valores_minimos.append(minimo)
            else:
                indice += 1
                if valores_izquierdos[indice].posicion == valores_derechos[i].posicion:
                    minimo = min(valores_izquierdos[indice].valor, valores_derechos[i].valor)
                    valores_minimos.append(minimo)
    return valores_minimos


# Calcular balance liquido idEstudio tipo str
def calcular_balance_liquido(request, idEstudio):

    valores_midi = calcular_midi(request, idEstudio)
    cant_actores = Actor.objects.filter(idEstudio=int(idEstudio)).order_by('id').count()
    lista_balance = []

    if len(valores_midi) > 1:
        valores_midi.pop(cant_actores)                   # Elimino fila de dependencias de la matriz midi
        lista_inversa = list(zip(*valores_midi.copy()))  # Invierto la matriz (filas a columnas)
        lista_inversa.pop(0)                             # Elimino la fila de las cabeceras

        # Obtengo solo los valores
        lista_inversa_valores = []
        for fila in lista_inversa:
            for celda in fila:
                lista_inversa_valores.append(celda.valor)

        # Calculo el balance líquido
        cont = 0
        suma_fila = 0
        for fila in valores_midi:
            for celda in fila:
                if celda.posicion in range(1, cant_actores + 1):
                    celda.valor -= lista_inversa_valores[cont]
                    suma_fila += celda.valor
                    cont += 1
                elif celda.posicion == cant_actores + 1:
                    celda.valor = suma_fila
                    suma_fila = 0

        lista_balance = valores_midi

    return lista_balance


# Calcula los valores de la matriz Ri
def calcular_ri(request, idEstudio):

    cant_actor = Actor.objects.filter(idEstudio=int(idEstudio)).count()
    valores_midi = calcular_midi(request, idEstudio)
    valores_diagonal = []  # valores de la diagonal de la matriz midi
    valores_Ii = []  # valores Ii de midi
    valores_Di = []  # valores Di de midi
    valores_ri = []  # valores ri calculados

    if len(valores_midi) > 1:
        # Obtengo los valores de la diagonal midi
        for fila in valores_midi:
            if len(valores_diagonal) < cant_actor:
                celda = fila[len(valores_diagonal) + 1]
                valores_diagonal.append(celda.valor)

        # Obtengo los valores de influencias directas e indirectas (ultima columna de midi)
        for fila in valores_midi:
            for celda in fila:
                if celda.posicion == cant_actor + 1 and len(valores_Ii) < cant_actor:
                    valores_Ii.append(celda.valor)

        # Obtendo los valores de dependencias directas e indirectas a graficar
        fila_dependencias = valores_midi[cant_actor]  # fila de valores de dependencia de la matriz
        fila_dependencias.pop(0)                      # se elimina la cabecera de la fila (D.D)

        for celda in fila_dependencias:
            valores_Di.append(celda.valor)

        # se calcula el valor ri de cada actor
        suma_ri = 0
        for i in range(len(valores_diagonal)):
            a = valores_Ii[i]
            b = valores_diagonal[i]
            c = valores_Di[cant_actor]
            d = valores_Di[i]
            ri = ((a - b) / (c * 1.0)) * (a / ((a + d) * 1.0))
            valores_ri.append(ri)
            suma_ri += ri
        # se calcula el promedio de los valores ri
        ri_prom = suma_ri / cant_actor

        # se obtiene el valor ri promedio de cada actor
        for i in range(len(valores_ri)):
            res = valores_ri[i] / ri_prom
            valores_ri[i] = res

    return valores_ri


# Calcula el indicador de estabilidad del estudio, idEstudio tipo str
def calcular_estabilidad(request, idEstudio):

    cant_actores = Actor.objects.filter(idEstudio=int(idEstudio)).count()
    valores_midi = calcular_midi(request, idEstudio)
    lista_influencias = []
    lista_dependencias = []
    estabilidad = 0

    if len(valores_midi) > 1:
        # Obtengo las influencias directas e indirectas (ultima columna de midi)
        for fila in valores_midi:
            for celda in fila:
                if celda.posicion == (cant_actores + 1) and len(lista_influencias) < cant_actores:
                    lista_influencias.append(celda.valor)

        # Obtengo las dependencias directas e indirectas (ultima fila de midi)
        fila_dependencias = valores_midi[cant_actores]
        fila_dependencias.pop(0)
        total = fila_dependencias.pop(cant_actores).valor

        for celda in fila_dependencias:
            lista_dependencias.append(celda.valor)

        # Calculo el indicador de estabilidad H
        for inf in range(len(lista_influencias)):
            estabilidad += abs(lista_influencias[inf] - lista_dependencias[inf])

        estabilidad = round((estabilidad / (2 * total)) * 100, 2)

    return estabilidad


"""---------------------------------------------FUNCIONES AUXILIARES MATRICES MAO-----------------------------------"""


# Crea el contexto a enviar al template de mao
def crear_contexto_mao(request, idEstudio, numero_matriz):

    consenso = verificar_consenso(request, idEstudio)
    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    tipo_usuario = obtener_tipo_usuario(request, estudio.id)
    objetivos = Objetivo.objects.filter(idEstudio=estudio.id).order_by('id')
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    tamano_matriz_completa = len(actores) * len(objetivos)
    lista_mao = []
    num_expertos = []

    contexto = {'objetivos': objetivos, 'estudio': estudio, 'usuario': tipo_usuario, 'consenso': consenso,
                'tipo': numero_matriz}

    # Se determina que valores se va a mostrar (los del usuario o el consenso) y que numero de matriz 1mao, 2mao 0 3mao
    if numero_matriz < 3:  # para la matriz 1mao y 2mao
        if consenso is True:
            lista_mao = calcular_consenso_mao(request, estudio.id, numero_matriz)
            num_expertos = lista_mao['expertos']
            lista_mao = lista_mao['consenso']
        else:
            lista_mao = RelacionMAO.objects.filter(idActorY__idEstudio=estudio.id, tipo=numero_matriz,
                                                   idExperto=request.user.id).order_by('idActorY', 'idObjetivoX')
    else:  # para la matriz 3mao por ser calculada
        if consenso is True:
            lista_mao = calcular_consenso_mao(request, estudio.id, numero_matriz)
            num_expertos = calcular_consenso_mao(request, estudio.id, 2)
            num_expertos = num_expertos['expertos']
            lista_mao = lista_mao['consenso']
        else:
            estado_mao3 = verificar_mid_mao2(request, estudio.id) # se verifica que mid y 2mao esten diligenciadas
            if estado_mao3:
                lista_mao = calcular_valores_3mao(request, estudio.id)

    # Si la matriz esta completa
    if len(lista_mao) == tamano_matriz_completa and tamano_matriz_completa > 0:
        valores_mao = calcular_valores_mao(estudio.id, lista_mao, numero_matriz)

        contexto['valores_mao'] = valores_mao
        contexto['estado_matriz'] = MATRIZ_COMPLETA
        contexto['expertos'] = num_expertos

        # Controla el acceso al informe final (muestra la vista de creacion o edicion del informe)
        if numero_matriz == 3 and InformeFinal.objects.filter(idEstudio=estudio.id).exists() is True:
            contexto['informe'] = InformeFinal.objects.get(idEstudio=estudio.id)

    # Si la matriz es 1mao o 2mao y esta incompleta
    elif len(lista_mao) != tamano_matriz_completa or len(lista_mao) == 0 and numero_matriz != 3:
        valores_mao = generar_mao_incompleta(idEstudio, lista_mao, numero_matriz)

        contexto['valores_mao'] = valores_mao
        contexto['estado_matriz'] = MATRIZ_INCOMPLETA

    # si no se han registrado actores u objetivos
    else:
        contexto = {'estudio': estudio, 'usuario': tipo_usuario, 'estado_matriz': MATRIZ_INCOMPLETA}

    return contexto


# Calcula los valores de la matriz mao
def calcular_valores_mao(idEstudio, mao, numero_matriz):

    objetivos = Objetivo.objects.filter(idEstudio=idEstudio).order_by('id').count()
    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    suma_positivos = 0  # sumatoria de los valores positivos de implicacion
    suma_negativos = 0  # sumatoria de los valores negativos de implicacion

    matriz_mao = []
    fila = []
    cont = 1
    for i in mao:
        # se inserta el valor del eje Y (nombre corto del actor)
        if len(fila) == 0:
            fila.append(ValorPosicion(posicion=0, valor=actores[len(matriz_mao)].nombreCorto,
                                      descripcion=actores[len(matriz_mao)].nombreLargo))

        # Se inserta el valor de las relaciones mao
        descripcion = obtener_descripcion_mao(i.valor, numero_matriz)
        fila.append(ValorPosicion(posicion=cont, valor=i.valor, descripcion=descripcion))
        cont += 1
        if i.valor != VALOR_RELACION_NO_REGISTRADA:
            if i.valor > 0:
                suma_positivos += i.valor       # Implicaciones positivas
            else:
                suma_negativos += abs(i.valor)  # Implicaciones negativas

        # Se insertan los valores de implicacion negativa y positiva
        if len(fila) == (objetivos + 1):
            total_fila = round(suma_positivos + suma_negativos, 1)
            fila.append(ValorPosicion(posicion=cont, valor=round(suma_positivos, 1), descripcion=round(suma_positivos, 1)))
            fila.append(ValorPosicion(posicion=cont+1, valor=round(suma_negativos, 1), descripcion=round(suma_negativos, 1)))
            fila.append(ValorPosicion(posicion=cont+2, valor=total_fila, descripcion=total_fila))
            matriz_mao.append(fila)
            fila = []
            cont = 1
            suma_positivos = 0
            suma_negativos = 0

    # Se calculan los valores de movilizacion positiva y negativa (suma de columnas)
    cont = 1
    fila_pos = [ValorPosicion(posicion=0, valor="+", descripcion=u"MOVILIZACIÓN POSITIVA")]
    fila_neg = [ValorPosicion(posicion=0, valor="-", descripcion=u"MOVILIZACIÓN NEGATIVA")]
    fila_total = [ValorPosicion(posicion=0, valor="Mov.", descripcion=u"MOVILIZACIÓN")]

    while cont <= objetivos:
        for fil in matriz_mao:
            for celda in fil:
                if celda.posicion == cont and celda.valor != VALOR_RELACION_NO_REGISTRADA:
                    if celda.valor > 0:
                        suma_positivos += celda.valor       # Movilizaciones positivas
                    else:
                        suma_negativos += abs(celda.valor)  # Movilizaciones negativas
        total_columna = round(suma_positivos + suma_negativos, 1)
        fila_pos.append(ValorPosicion(posicion=cont, valor=round(suma_positivos, 1), descripcion=round(suma_positivos, 1)))
        fila_neg.append(ValorPosicion(posicion=cont, valor=round(suma_negativos, 1), descripcion=round(suma_negativos, 1)))
        fila_total.append(ValorPosicion(posicion=cont, valor=total_columna, descripcion=total_columna))
        suma_negativos = 0
        suma_positivos = 0
        cont += 1

    matriz_mao.append(fila_pos)    # Ingreso fila movilizaciones positivas a la matriz
    matriz_mao.append(fila_neg)    # Ingreso fila movilizaciones negativas a la matriz
    matriz_mao.append(fila_total)  # Ingreso fila movilizaciones totales a la matriz

    return matriz_mao


# Devuelve la descripcion de los valores de las matrices mao
def obtener_descripcion_mao(valor, numero_matriz):

    descripcion = ""
    if numero_matriz == 1:
        if valor == 0:
            descripcion = "Neutro"
        elif valor == 1:
            descripcion = "A favor"
        elif valor == -1:
            descripcion = "En contra"
    elif numero_matriz == 2:
        if valor == 0:
            descripcion = "Neutro"
        elif valor > 0:
            descripcion = "Acuerdo"
        else:
            descripcion = "Desacuerdo"
    else:
        descripcion = valor

    return descripcion


# Calculo de los valores 3mao = 2mao * ri, idEstudio tipo str
def calcular_valores_3mao(request, idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    cant_objetivos = Objetivo.objects.filter(idEstudio=estudio.id).order_by('id').count()
    valores_ri = calcular_ri(request, idEstudio)
    valores_3mao = []

    if verificar_consenso(request, idEstudio):
        mao = calcular_consenso_mao(request, estudio.id, 2)
        mao = mao['consenso']
    else:
        mao = RelacionMAO.objects.filter(idActorY__idEstudio=estudio.id, tipo=2,
                                         idExperto=request.user.id).order_by('idActorY', 'idObjetivoX')
    # Multiplicacion de los valores 2mao por los valores ri para calcular los valores 3mao
    cont = 0
    cont2 = 0
    for i in mao:
        if cont2 < cant_objetivos:
            valor = i.valor * valores_ri[cont]
            valores_3mao.append(ValorPosicion(posicion=cont2 + 1, valor=round(valor, 1), descripcion=round(valor, 1)))
            cont2 += 1
            if cont2 == cant_objetivos:
                cont2 = 0
                cont += 1

    return valores_3mao


# Genera la matriz mao en caso de que este incompleta, solo 1mao y 2mao
def generar_mao_incompleta(idEstudio, mao, numero_matriz):

    objetivos = Objetivo.objects.filter(idEstudio=idEstudio).order_by('id')
    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    lista_mao_incompleta = []  # contiene los valores de la matriz mao incompleta
    actores_objetivos = []     # contiene el orden de los ejes de la matriz

    # se obtiene el orden de los ejes
    for i in actores:
        for j in objetivos:
            actores_objetivos.append(ValorPareja(y=i.id, x=j.id, valor=""))

    # se obtienen las influencias mao actualmente registradas
    for i in mao:
        lista_mao_incompleta.append(ValorPareja(y=i.idActorY.id, x=i.idObjetivoX.id, valor=i.valor))

    # ingreso de valores de relleno en la matriz mao para permitir la comparacion con el orden ideal (igual longitud)
    registros_relleno = 0
    while len(lista_mao_incompleta) != len(actores_objetivos):
        lista_mao_incompleta.append(ValorPareja(y=0, x=0, valor=0))
        registros_relleno += 1

    # al detectar ejes diferentes al ideal se inserta en esa posicion un registro de relleno con los ejes adecucados
    for j in range(len(actores_objetivos)):
        eje_y = actores_objetivos[j].y
        eje_x = actores_objetivos[j].x
        if lista_mao_incompleta[j].y != eje_y or lista_mao_incompleta[j].x != eje_x:
            lista_mao_incompleta.insert(j, ValorPareja(y=eje_y, x=eje_x, valor=VALOR_RELACION_NO_REGISTRADA))

    # se eliminan los registros de relleno ingresados
    while registros_relleno != 0:
        lista_mao_incompleta.pop()
        registros_relleno -= 1

    lista_contexto = calcular_valores_mao(idEstudio, lista_mao_incompleta, numero_matriz)

    return lista_contexto


# Verifica si las matrices MID y 2MAO estan totalmente diligenciadas para proceder al calculo de la matriz 3mao
def verificar_mid_mao2(request, idEstudio):

    objetivos = Objetivo.objects.filter(idEstudio=idEstudio).count()
    actores = Actor.objects.filter(idEstudio=idEstudio).count()
    mid = RelacionMID.objects.filter(idActorY__idEstudio=idEstudio, idExperto=request.user.id).count()
    mao2 = RelacionMAO.objects.filter(tipo=2, idActorY__idEstudio=idEstudio, idExperto=request.user.id).count()
    tamano_mid = actores * actores
    tamano_2mao = actores * objetivos
    estado_3mao = False

    if mid == tamano_mid and mao2 == tamano_2mao:
        estado_3mao = True

    return estado_3mao


# Calcula los valores de la matriz de convergencias
def calcular_caa(idEstudio, lista_mao):

    cant_objetivos = Objetivo.objects.filter(idEstudio=idEstudio).order_by('id').count()
    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    matriz_caa = []

    # Elimino las tres ultimas filas (filas de movilizaciones)
    lista_mao.pop()
    lista_mao.pop()
    lista_mao.pop()

    def obtener_fila_caa(numero_fila, fila_base):

        valor = 0
        # Inserto la cabecera de la fila
        fila_matriz = [ValorPosicion(posicion=0, valor=actores[len(matriz_caa)].nombreCorto,
                                     descripcion=actores[len(matriz_caa)].nombreLargo)]
        for fila in lista_mao:
            for celda in range(len(fila)):
                if fila[0].valor != fila_base[0].valor:
                    if fila[celda].posicion in range(1, cant_objetivos + 1):
                        if (fila[celda].valor * fila_base[celda].valor) > 0:
                            valor += (abs(fila[celda].valor) + abs(fila_base[celda].valor)) / 2.0

                        if fila[celda].posicion == cant_objetivos:
                            fila_matriz.append(ValorPosicion(posicion="", valor=round(valor, 1),
                                                             descripcion=round(valor, 1)))
                            valor = 0
        # Inserto el 0 de la diagonal
        fila_matriz.insert(numero_fila + 1, ValorPosicion(posicion="", valor=0, descripcion=0))

        # Asigno las posiciones de cada valor(columna de la matriz)
        for i in range(actores.count() + 1):
            fila_matriz[i].posicion = i

        return fila_matriz

    aux = 0
    while aux < actores.count():
        fila_base = lista_mao[aux]   # fila que se envia para comparar y calcular las caa o daa
        matriz_caa.append(obtener_fila_caa(aux, fila_base))
        aux += 1

    fila_suma_columna = obtener_fila_suma_columnas(matriz_caa, actores)
    fila_suma_columna.insert(0, ValorPosicion(posicion=0, valor="Ci", descripcion="CONVERGENCIA"))
    matriz_caa.append(fila_suma_columna)
    return matriz_caa


# Calcula los valores de la matriz de divergencias
def calcular_daa(idEstudio, lista_mao):

    cant_objetivos = Objetivo.objects.filter(idEstudio=idEstudio).order_by('id').count()
    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    matriz_daa = []

    def obtener_fila_daa(numero_fila, fila_base):

        valor = 0
        # Inserto la cabecera de la fila
        fila_matriz = [ValorPosicion(posicion=0, valor=actores[len(matriz_daa)].nombreCorto,
                                     descripcion=actores[len(matriz_daa)].nombreLargo)]
        for fila in lista_mao:
            for celda in range(len(fila)):
                if fila[0].valor != fila_base[0].valor:
                    if fila[celda].posicion in range(1, cant_objetivos + 1):
                        if (fila[celda].valor * fila_base[celda].valor) < 0:
                            valor += (abs(fila[celda].valor) + abs(fila_base[celda].valor)) / 2.0

                        if fila[celda].posicion == cant_objetivos:
                            fila_matriz.append(ValorPosicion(posicion="", valor=round(valor, 1), descripcion=round(valor, 1)))
                            valor = 0
        # Inserto el 0 de la diagonal
        fila_matriz.insert(numero_fila + 1, ValorPosicion(posicion="", valor=0, descripcion=0))

        # Asigno las posiciones de cada valor(columna de la matriz)
        for i in range(actores.count() + 1):
            fila_matriz[i].posicion = i

        return fila_matriz

    aux = 0
    while aux < actores.count():
        fila_base = lista_mao[aux]   # fila que se envia para comparar y calcular daa
        matriz_daa.append(obtener_fila_daa(aux, fila_base))
        aux += 1

    fila_suma_columna = obtener_fila_suma_columnas(matriz_daa, actores)
    fila_suma_columna.insert(0, ValorPosicion(posicion=0, valor="Di", descripcion="DIVERGENCIA"))
    matriz_daa.append(fila_suma_columna)

    return matriz_daa


# Devuelve la fila correspondiente a la suma de las columnas
def obtener_fila_suma_columnas(matriz, actores):

    fila_suma_columna = []
    cont = 0
    suma_columna = 0
    while cont < actores.count():
        for fila in matriz:
            for celda in fila:
                if celda.posicion == (cont + 1):
                    suma_columna += celda.valor
        suma_columna = round(suma_columna, 2)
        fila_suma_columna.append(ValorPosicion(posicion=cont+1, valor=suma_columna, descripcion=suma_columna))
        suma_columna = 0
        cont += 1

    return fila_suma_columna


"""----------------------------CONTROL OPTIONS SELECTS FORMULARIOS ESTRATEGIAS, MID, MAO----------------------------"""


# Devuelve la lista de actores que no se han registrado en la lista de fichas de estrategia o matriz mid
def consultar_actores_faltantes(request):

    if request.is_ajax():
        id = request.GET['id']
        idEstudio = int(request.GET['estudio'])
        tipo = request.GET['tipo']
        actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
        lista_registrados = []
        lista_id = []
        lista_valores = []

        # si se esta registrando una influencia mid
        if tipo == "form_mid":
            mid = RelacionMID.objects.filter(idActorY__idEstudio=idEstudio).order_by('idActorY', 'idActorX')
            # se obtienen los id de los actores ya registrados en la matriz mid
            for i in mid:
                if i.idActorY.id == int(id) and i.idExperto == request.user:
                    lista_registrados.append(i.idActorX.id)
                    lista_valores.append(i.valor)
            # para desactivar la opcion correspondiente a autoinfluencia se agrega el id como registrado
            if id not in lista_registrados:
                lista_registrados.append(id)
                lista_valores.append(0)

        # si se esta registrando una ficha de estrategias
        if tipo == "form_ficha":
            fichas = Ficha.objects.filter(idActorY__idEstudio=idEstudio).order_by('idActorY', 'idActorX')
            for ficha in fichas:
                if ficha.idActorY.id == int(id):
                    lista_registrados.append(ficha.idActorX.id)

        # se obtiene la lista de id de los actores del estudio
        for actor in actores:
            lista_id.append(actor.id)

        response = JsonResponse({'actores': lista_id, 'lista': lista_registrados, 'valores': lista_valores})
        return HttpResponse(response.content)


# Devuelve la lista de objetivos que no se han registrado en determinada matriz mao
def consultar_objetivos_faltantes(request):

    if request.is_ajax():
        id = request.GET['id']
        idEstudio = int(request.GET['estudio'])
        tipo = request.GET['tipo']
        objetivos = Objetivo.objects.all().order_by('id')
        lista_registrados = []
        lista_valores = []
        lista_id = []

        # si se esta registrando una influencia 1mao
        if tipo == "form_1mao":
            mao = RelacionMAO.objects.filter(tipo=1, idActorY__idEstudio=idEstudio,
                                             idExperto=request.user.id).order_by('idActorY', 'idObjetivoX')
            # se obtienen los id de los objetivos ya registrados en la matriz mao con ese actor Y
            for i in mao:
                if i.idActorY.id == int(id) and i.idExperto == request.user:
                    lista_registrados.append(i.idObjetivoX.id)
                    lista_valores.append(i.valor)

        # si se esta registrando una influencia 2mao
        elif tipo == "form_2mao":
            mao = RelacionMAO.objects.all().filter(tipo=2, idActorY__idEstudio=idEstudio,
                                                   idExperto=request.user.id).order_by('idActorY', 'idObjetivoX')
            for i in mao:
                if i.idActorY.id == int(id):
                    lista_registrados.append(i.idObjetivoX.id)
                    lista_valores.append(i.valor)

        # se obtiene la lista de id de los objetivos del estudio
        for objetivo in objetivos:
            lista_id.append(objetivo.id)

        response = JsonResponse({'objetivos': lista_id, 'lista': lista_registrados, 'valores': lista_valores})
        return HttpResponse(response.content)


# Obtiene la lista de actores cuyas relaciones ya estan totalmente registradas (primer select ficha, mid y mao)
def consultar_actores_eje_y_registrados(idEstudio, tipo):

    registrados = []
    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    if tipo == "ficha":
        relaciones = Ficha.objects.filter(idActorY__idEstudio=idEstudio).order_by('idActorY', 'idActorX')
    elif tipo == "mid":
        relaciones = RelacionMID.objects.filter(idActorY__idEstudio=idEstudio).order_by('idActorY', 'idActorX')
    elif tipo == "1mao":
        relaciones = RelacionMAO.objects.filter(idActorY__idEstudio=idEstudio, tipo=1).order_by('idActorY', 'idObjetivoX')
    else:
        relaciones = RelacionMAO.objects.filter(idActorY__idEstudio=idEstudio, tipo=2).order_by('idActorY', 'idObjetivoX')

    if tipo != "1mao" and tipo != "2mao" and len(relaciones) > 0:
        for actor in actores:
            if relaciones.filter(idActorY=actor).count() == actores.count():
                registrados.append(actor.id)
    else:
        objetivos = Objetivo.objects.filter(idEstudio=idEstudio).order_by('id')
        for actor in actores:
            if relaciones.filter(idActorY=actor).count() == objetivos.count():
                registrados.append(actor.id)

    return registrados

""" ----------------------------------------HISTOGRAMAS--------------------------------------------------------"""


# Genera el histograma de la matriz de influencias directas, idEstudio tipo str
def histograma_mid(request, idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        influencias_mid = calcular_consenso_mid(estudio.id)
        cantidad_expertos = influencias_mid['num_expertos']
        contexto = {'estudio': estudio, 'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'usuario': usuario}

    return render(request, 'mactor/mid/graficos/histograma_mid.html', contexto)


# Devuelve los datos a representar en el histograma mid
def datos_histograma_mid(request):

    if request.is_ajax():
        estudio = get_object_or_404(EstudioMactor, id=int(request.GET['estudio']))
        usuario = obtener_tipo_usuario(request, estudio.id)
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
        lista_nombres = []
        lista_influencias = []
        lista_dependencias = []

        valores_mid = []
        if verificar_consenso(request, request.GET['estudio']):  # histograma consenso
            valores_mid = calcular_consenso_mid(estudio.id)
            valores_mid = valores_mid['consenso']
        elif usuario != "COORDINADOR":  # histograma del experto
            valores_mid = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                                     idExperto=request.user.id).order_by('idActorY', 'idActorX')
        valores_mid = establecer_valores_mid(estudio.id, valores_mid)

        if len(valores_mid) == (actores.count() + 1):
            # se obtienen los valores de influencia a graficar
            for fila in valores_mid:
                for celda in fila:
                    if celda.posicion == actores.count() + 1:
                        lista_influencias.append(celda.valor)

            fila_dependencias = valores_mid[actores.count()]  # fila de valores de dependencia de la matriz
            fila_dependencias.pop(0)                          # se elimina la cabecera de la fila (D.D)
            fila_dependencias.pop(actores.count())            # se elimina la sumatoria total

            # se obtienen los valores de dependencia a graficar
            for celda in fila_dependencias:
                lista_dependencias.append(celda.valor)

            # Etiquetas del histograma
            for actor in actores:
                lista_nombres.append(actor.nombreCorto)

        data = {'labels': lista_nombres, 'influencias': lista_influencias, 'dependencias': lista_dependencias}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


# Genera el histograma del coeficiente Ri, idEstudio tipo str
def histograma_ri(request, idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        influencias_mid = calcular_consenso_mid(estudio.id)
        cantidad_expertos = influencias_mid['num_expertos']
        contexto = {'estudio': estudio, 'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'usuario': usuario}

    return render(request, 'mactor/mid/graficos/histograma_ri.html', contexto)


# Devuelve los datos a representar en el histograma ri
def datos_histograma_ri(request):

    if request.is_ajax():
        valores_ri = calcular_ri(request, request.GET['estudio'])  # str para que verifique si es consenso
        estudio = int(request.GET['estudio'])
        actores = Actor.objects.filter(idEstudio=estudio).order_by('id')
        lista_nombres = []

        # Etiquetas del histograma
        for actor in actores:
            lista_nombres.append(actor.nombreCorto)

        # Valores a graficar
        for i in range(len(valores_ri)):
            valores_ri[i] = round(valores_ri[i], 2)

        data = {'labels': lista_nombres, 'valores_ri': valores_ri}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


# Genera el histograma de implicacion, idEstudio tipo str
def histograma_implicacion(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)
    matriz = int(numero_matriz)

    if verificar_consenso(request, idEstudio):
        if matriz != 3:
            consenso_mao = calcular_consenso_mao(request, estudio.id, matriz)
            cantidad_expertos = consenso_mao['expertos']
        else:
            consenso_mao = calcular_consenso_mao(request, estudio.id, 2)
            cantidad_expertos = consenso_mao['expertos']

        contexto = {'estudio': estudio, 'numero_matriz': matriz, 'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': matriz, 'usuario': usuario}

    return render(request, 'mactor/mao/graficos/histograma_implicacion.html', contexto)


# Genera el histograma de movilizacion, idEstudio tipo str
def histograma_movilizacion(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)
    matriz = int(numero_matriz)

    if verificar_consenso(request, idEstudio):
        if matriz != 3:
            consenso_mao = calcular_consenso_mao(request, estudio.id, matriz)
            cantidad_expertos = consenso_mao['expertos']
        else:
            consenso_mao = calcular_consenso_mao(request, estudio.id, 2)
            cantidad_expertos = consenso_mao['expertos']

        contexto = {'estudio': estudio, 'numero_matriz': matriz, 'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': matriz, 'usuario': usuario}

    return render(request, 'mactor/mao/graficos/histograma_movilizacion.html', contexto)


# Devuelve los datos a representar en los histogramas de implicacion y movilizacion
def datos_histogramas_mao(request):

    if request.is_ajax():
        idEstudio = request.GET['estudio']
        numero_matriz = int(request.GET['numero_matriz'])
        tipo = request.GET['tipo']
        estudio = get_object_or_404(EstudioMactor, id=int(request.GET['estudio']))
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
        cant_objetivos = Objetivo.objects.filter(idEstudio=estudio.id).count()
        lista_nombres = []

        valores_mao = crear_contexto_mao(request, idEstudio, numero_matriz)
        valores_mao = valores_mao['valores_mao']
        valores_positivos = []
        valores_negativos = []

        if tipo == "IMPLICACION":
            labels = actores
            for fila in valores_mao:
                for celda in fila:
                    if celda.posicion == cant_objetivos + 1:
                        valores_positivos.append(celda.valor)
                    elif celda.posicion == cant_objetivos + 2:
                        valores_negativos.append(celda.valor)
        # si se trata de los valores de movilizacion
        else:
            labels = Objetivo.objects.filter(idEstudio=estudio.id).order_by('id')
            fila_movilizaciones_pos = valores_mao[actores.count()]
            fila_movilizaciones_neg = valores_mao[actores.count() + 1]

            # Obtengo los valores de movilizacion positiva
            for celda in fila_movilizaciones_pos:
                if celda.posicion > 0:
                    valores_positivos.append(celda.valor)

            # Obtengo los valores de movilizacion negativa
            for celda in fila_movilizaciones_neg:
                if celda.posicion > 0:
                    valores_negativos.append(celda.valor)

        for i in labels:
            lista_nombres.append(i.nombreCorto)

        data = {'labels': lista_nombres, 'valores_positivos': valores_positivos, 'valores_negativos': valores_negativos}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


# Genera el histograma de convergencias y divergencias, idEstudio tipo str
def histograma_caa_daa(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)
    num_expertos = 0

    if verificar_consenso(request, idEstudio):
        mao = crear_contexto_mao(request, idEstudio, int(numero_matriz))
        if mao['estado_matriz'] == MATRIZ_COMPLETA:
            num_expertos = mao['expertos']
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz), 'expertos': num_expertos,
                    'usuario': usuario}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz), 'usuario': usuario}

    return render(request, 'mactor/mao/graficos/histograma_caa_daa.html', contexto)


# Devuelve los datos a representar en el histograma de convergencias y divergencias
def datos_histograma_caa_daa(request):

    if request.is_ajax():
        numero_matriz = int(request.GET['numero_matriz'])
        estudio = get_object_or_404(EstudioMactor, id=int(request.GET['estudio']))
        labels = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
        lista_nombres = []
        valores_caa = []
        valores_daa = []

        mao = crear_contexto_mao(request, request.GET['estudio'], numero_matriz)
        if mao['estado_matriz'] == MATRIZ_COMPLETA:
            valores_caa = calcular_caa(int(request.GET['estudio']), mao['valores_mao'])[labels.count()]
            valores_daa = calcular_daa(int(request.GET['estudio']), mao['valores_mao'])[labels.count()]

        datos_caa = []
        datos_daa = []

        # Obtengo los valores de convergencia y divergergencia
        for celda in range(len(valores_caa)):
            if valores_caa[celda].posicion > 0:
                datos_caa.append(valores_caa[celda].valor)
                datos_daa.append(valores_daa[celda].valor)

        for actor in labels:
            lista_nombres.append(actor.nombreCorto)

        data = {'labels': lista_nombres, 'caa': datos_caa, 'daa': datos_daa}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


""" ----------------------------------------PLANOS CARTESIANOS-----------------------------------------------------"""


# genera el plano cartesiano de los actores en la matriz midi, idEstudio tipo str
def generar_mapa_midi(request, idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        influencias_mid = calcular_consenso_mid(estudio.id)
        cantidad_expertos = influencias_mid['num_expertos']
        contexto = {'estudio': estudio, 'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'usuario': usuario}

    return render(request, 'mactor/mid/graficos/mapa_actores.html', contexto)


# devuelve los datos a representar en el plano cartesiano de los actores
def datos_mapa_midi(request):

    if request.is_ajax():
        valores_midi = calcular_midi(request, request.GET['estudio'])
        lista_nombres = []
        valores_ejeX = []
        valores_ejeY = []
        actores = Actor.objects.filter(idEstudio=int(request.GET['estudio'])).order_by('id')

        if len(valores_midi) > 1:
            # Etiquetas del grafico
            for actor in actores:
                lista_nombres.append(actor.nombreCorto)

            # se obtienen los valores de influencia a graficar
            for fila in valores_midi:
                for celda in fila:
                    if celda.posicion == actores.count() + 1 and len(valores_ejeX) < actores.count():
                        valores_ejeX.append(celda.valor)

            fila_dependencias = valores_midi[actores.count()]  # fila de valores de dependencia de la matriz
            fila_dependencias.pop(0)  # se elimina la cabecera de la fila (D.D)
            fila_dependencias.pop(actores.count())  # se elimina la sumatoria total

            # se obtienen los valores de dependencia a graficar
            for celda in fila_dependencias:
                valores_ejeY.append(celda.valor)

            for i in range(len(valores_ejeX)):
                x = valores_ejeX[i]
                y = valores_ejeY[i]
                diferencia = x - y
                if abs(diferencia) > 2:
                    if x > y:
                        valores_ejeY[i] = y * -1
                    else:
                        valores_ejeX[i] = x * -1

        data = {'labels': lista_nombres, 'valores_ejeX': valores_ejeX, 'valores_ejeY': valores_ejeY}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


# genera el plano cartesiano de convergencias y divergencias, idEstudio tipo str
def generar_mapa_caa_daa(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        if numero_matriz < 3:
            cantidad_expertos = calcular_consenso_mao(request, estudio.id, int(numero_matriz))['expertos']
        else:
            cantidad_expertos = calcular_consenso_mao(request, estudio.id, 2)['expertos']

        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz),
                    'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz), 'usuario': usuario}

    return render(request, 'mactor/mao/graficos/mapa_caa_daa.html', contexto)


# devuelve los datos a representar en el mapa de convergencias y divergencias
def datos_mapa_caa_daa(request):

    if request.is_ajax():
        numero_matriz = int(request.GET['numero_matriz'])
        labels = Actor.objects.filter(idEstudio=int(request.GET['estudio'])).order_by('id')
        lista_nombres = []
        valores_caa = []
        valores_daa = []

        mao = crear_contexto_mao(request, request.GET['estudio'], numero_matriz)
        if mao['estado_matriz'] == MATRIZ_COMPLETA:
            valores_caa = calcular_caa(int(request.GET['estudio']), mao['valores_mao'])[labels.count()]
            valores_daa = calcular_daa(int(request.GET['estudio']), mao['valores_mao'])[labels.count()]

        valores_ejeX = []
        valores_ejeY = []

        # Obtengo los valores de convergencia y divergencia
        for celda in range(len(valores_caa)):
            if valores_caa[celda].posicion > 0:
                valores_ejeY.append(valores_caa[celda].valor)
                valores_ejeX.append(valores_daa[celda].valor)

        # Obtengo las etiquetas de cada actor
        for actor in labels:
            lista_nombres.append(actor.nombreCorto)

        data = {'labels': lista_nombres, 'valores_ejeX': valores_ejeX, 'valores_ejeY': valores_ejeY}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


"""-------------------------------------------GRAFOS-----------------------------------------------------------"""


# Genera el grafo de convergencias, idEstudio tipo str
def generar_grafo_caa(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        if numero_matriz < 3:
            mao = calcular_consenso_mao(request, estudio.id, int(numero_matriz))
        else:
            mao = calcular_consenso_mao(request, estudio.id, 2)

        cantidad_expertos = mao['expertos']
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz),
                    'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz), 'usuario': usuario}

    return render(request, 'mactor/mao/graficos/grafo_caa.html', contexto)


# Devuelve los datos a representar en el grafo de convergencias
def datos_grafo_caa(request):

    if request.is_ajax():
        estudio = get_object_or_404(EstudioMactor, id=int(request.GET['estudio']))
        numero_matriz = int(request.GET['numero_matriz'])
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
        mao = crear_contexto_mao(request, request.GET['estudio'], numero_matriz)
        valores_caa = []
        if mao['estado_matriz'] == MATRIZ_COMPLETA:
            valores_caa = calcular_caa(estudio.id, mao['valores_mao'])
            valores_caa.pop()  # Elimino la ultima fila(Sumatorias de columna)
        coordenadas = []
        nodos_id = []
        nodos_labels = []
        destinos_edge = []
        origenes_edge = []
        labels_edge = []

        if len(valores_caa) > 0:
            # Excluyo los valores de las cabeceras de las filas
            lista_limpia = []
            for fila in valores_caa:
                for celda in fila:
                    if celda.posicion > 0:
                        lista_limpia.append(celda.valor)

            valores_caa = lista_limpia

            # se asigna a cada valor el eje X y Y que le corresponde (actor x, actor y)
            contador = 0
            for i in actores:
                nodos_id.append(i.id)
                nodos_labels.append(i.nombreCorto)
                for j in actores:
                    coordenadas.append(ValorPosicion(posicion=i, valor=valores_caa[contador], descripcion=j))
                    contador += 1

            # eliminacion de los valores o en la diagonal
            contador = 0
            for i in range(len(coordenadas)):
                if i != contador:
                    origenes_edge.append(coordenadas[i].posicion.id)
                    destinos_edge.append(coordenadas[i].descripcion.id)
                    labels_edge.append(str(coordenadas[i].valor))
                else:
                    contador += actores.count() + 1

        data = {'nodos_id': nodos_id, 'nodos_labels': nodos_labels, 'edge_origenes': origenes_edge,
                'edge_destinos': destinos_edge, 'edge_labels': labels_edge}

        json_data = json.dumps(data)
        return HttpResponse(json_data)


# Genera el grafo de divergencias, idEstudio tipo str
def generar_grafo_daa(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        if numero_matriz < 3:
            mao = calcular_consenso_mao(request, estudio.id, int(numero_matriz))
        else:
            mao = calcular_consenso_mao(request, estudio.id, 2)
        cantidad_expertos = mao['expertos']
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz),
                    'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz), 'usuario': usuario}

    return render(request, 'mactor/mao/graficos/grafo_daa.html', contexto)


# Devuelve los datos a representar en el grafo de divergencias
def datos_grafo_daa(request):

    if request.is_ajax():
        estudio = get_object_or_404(EstudioMactor, id=int(request.GET['estudio']))
        numero_matriz = int(request.GET['numero_matriz'])
        actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
        mao = crear_contexto_mao(request, request.GET['estudio'], numero_matriz)
        valores_daa = []
        if mao['estado_matriz'] == MATRIZ_COMPLETA:
            valores_daa = calcular_daa(estudio.id, mao['valores_mao'])
            valores_daa.pop()
        coordenadas = []
        nodos_id = []
        nodos_labels = []
        destinos_edge = []
        origenes_edge = []
        labels_edge = []

        if len(valores_daa) > 0:
            # Excluyo los valores de las cabeceras de las filas
            lista_limpia = []
            for fila in valores_daa:
                for celda in fila:
                    if celda.posicion != "" and celda.posicion > 0:
                        lista_limpia.append(celda.valor)

            valores_daa = lista_limpia

            # se asigna a cada valor el eje x y y que le corresponde (actor x, actor y)
            contador = 0
            for i in actores:
                nodos_id.append(i.id)
                nodos_labels.append(i.nombreCorto)
                for j in actores:
                    coordenadas.append(ValorPosicion(posicion=i, valor=valores_daa[contador], descripcion=j))
                    contador += 1

            # eliminacion de los valores o en la diagonal
            contador = 0
            for i in range(len(coordenadas)):
                if i != contador:
                    origenes_edge.append(coordenadas[i].posicion.id)
                    destinos_edge.append(coordenadas[i].descripcion.id)
                    labels_edge.append(str(coordenadas[i].valor))
                else:
                    contador += actores.count() + 1

        data = {'nodos_id': nodos_id, 'nodos_labels': nodos_labels, 'edge_origenes': origenes_edge,
                'edge_destinos': destinos_edge, 'edge_labels': labels_edge}

        json_data = json.dumps(data)
        return HttpResponse(json_data)

"""----------------------------------TABLA DE CONVERGENCIAS Y DIVERGENCIAS DESCENDENTE------------------------------"""


# Genera la tabla de convergencias y divergencias en orden descendente
def generar_lista_descendiente(request, idEstudio, numero_matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    usuario = obtener_tipo_usuario(request, estudio.id)

    if verificar_consenso(request, idEstudio):
        if numero_matriz < 3:
            mao = calcular_consenso_mao(request, estudio.id, int(numero_matriz))
        else:
            mao = calcular_consenso_mao(request, estudio.id, 2)

        cantidad_expertos = mao['expertos']
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz),
                    'usuario': usuario, 'expertos': cantidad_expertos}
    else:
        contexto = {'estudio': estudio, 'numero_matriz': int(numero_matriz), 'usuario': usuario}

    mao = crear_contexto_mao(request, idEstudio, int(numero_matriz))
    if mao['estado_matriz'] == MATRIZ_COMPLETA:
        valores_caa = calcular_caa(estudio.id, mao['valores_mao'])
        valores_daa = calcular_daa(estudio.id, mao['valores_mao'])
        contexto['descendientes_caa'] = ordenar_descendentemente(estudio.id, valores_caa)
        contexto['descendientes_daa'] = ordenar_descendentemente(estudio.id, valores_daa)

    return render(request, 'mactor/mao/matrices/lista_descendientes.html', contexto)


# Retorna los valores de convergencia y divergencia en orden descendentemente
def ordenar_descendentemente(idEstudio, matriz):

    actores = Actor.objects.filter(idEstudio=idEstudio).order_by('id')
    matriz.pop()  # Elimino la fila de las sumatorias

    # Reemplazo los valores de posicion y descripcion de las celdas de la matriz por los nombres largos de los actores
    cont = 0
    cont2 = 0
    while cont < actores.count():
        fila_base = matriz[cont]
        cabecera = fila_base[0].descripcion
        for celda in fila_base:
            if celda.posicion > 0:
                celda.posicion = cabecera
                celda.descripcion = actores[cont2].nombreLargo
                matriz.pop(cont)
                matriz.insert(cont, fila_base)
                cont2 += 1
        cont += 1
        cont2 = 0

    # Excluyo la columna 0 (Cabeceras de fila)
    for fila in matriz:
        for celda in fila:
            if celda.posicion == 0:
                fila.remove(celda)

    # Excluyo los valores de la diagonal
    for fila in matriz:
        for celda in fila:
            if celda.posicion == celda.descripcion:
                fila.remove(celda)

    # Obtengo las celdas de cada fila como una sola lista
    celdas = []
    for fila in matriz:
        for celda in fila:
            celdas.append(celda)

    lista_sin_duplicados = []

    # Retorna true si se encuentra el registro equivalente para que no sea agregado a la lista a mostrar
    def verificar(celd):

        flag = False
        for i in lista_sin_duplicados:
            if i.posicion == celd.descripcion and i.descripcion == celd.posicion:
                flag = True
        return flag

    # Excluyo el registro equivalente (X, valor, Y) = (Y, valor, X)
    for celda in celdas:
        flag = verificar(celda)
        if flag is False:
            lista_sin_duplicados.append(celda)

    # Ordeno descendente los valores
    lista_sin_duplicados.sort(key=lambda valorposicion: valorposicion.valor, reverse=True)

    return lista_sin_duplicados

"""-------------------------------------------CONSENSOS----------------------------------------------------------"""


# Verifica si se debe mostrar el consenso, idEstudio tipo str
def verificar_consenso(request, idEstudio):

    consenso = False
    tipo_usuario = obtener_tipo_usuario(request, int(idEstudio))
    if tipo_usuario == "COORDINADOR" or type(idEstudio) == str and idEstudio[0] == '0':
        consenso = True
    return consenso


# Activa el consenso para las matrices y graficos de las influencias mid, idEstudio tipo str
def activar_consenso_mid(request, idEstudio, matriz):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    idEstudio = "0" + str(estudio.id)
    tipo = int(matriz)

    if tipo == 1:
        return generar_matriz_mid(request, idEstudio)
    elif tipo == 2:
        return generar_matriz_midi(request, idEstudio)
    elif tipo == 3:
        return generar_matriz_maxima(request, idEstudio)
    elif tipo == 4:
        return generar_matriz_balance(request, idEstudio)
    elif tipo == 5:
        return generar_matriz_ri(request, idEstudio)
    elif tipo == 6:
        return generar_indicador_estabilidad(request, idEstudio)
    elif tipo == 7:
        return histograma_mid(request, idEstudio)
    elif tipo == 8:
        return generar_mapa_midi(request, idEstudio)
    elif tipo == 9:
        return histograma_ri(request, idEstudio)
    else:
        raise Http404("Error: Esta vista no existe")


# Calcula el consenso de la matriz mid
def calcular_consenso_mid(idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=idEstudio)
    lista_expertos = estudio.idExpertos.all()
    actores = Actor.objects.filter(idEstudio=estudio.id).order_by('id')
    tamano_matriz_completa = len(actores) ** 2
    lista_consenso = []
    contador = 0

    for experto in lista_expertos:
        consulta = RelacionMID.objects.filter(idActorY__idEstudio=estudio.id,
                                              idExperto=experto.id).order_by('idActorY', 'idActorX')
        if len(consulta) == tamano_matriz_completa and len(lista_consenso) == 0:
            lista_consenso = consulta
            contador += 1
        elif len(consulta) == tamano_matriz_completa:
            contador += 1
            for i in range(len(lista_consenso)):
                lista_consenso[i].valor += consulta[i].valor

    if len(lista_consenso) > 0:
        for i in lista_consenso:
            i.valor = round(i.valor / contador)

    calculo = {'consenso': lista_consenso, 'num_expertos': str(contador) + "/" + str(len(lista_expertos))}

    return calculo


# Activa el consenso de las matrices y graficos de las matrices mao, idEstudio tipo str
def activar_consenso_mao(request, idEstudio, matriz, tipo):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    idEstudio = "0" + str(estudio.id)
    matriz = int(matriz)
    tipo = int(tipo)

    if matriz in [1, 2, 3] and tipo == 0:
        return generar_matriz_mao(request, idEstudio, matriz)
    elif tipo == 4:
        return histograma_implicacion(request, idEstudio, str(matriz))
    elif tipo == 5:
        return histograma_movilizacion(request, idEstudio, str(matriz))
    else:
        raise Http404("Error: Esta vista no existe")


# Activa el consenso de matrices de convergencia y divergencia, idEstudio tipo str
def activar_consenso_caa_daa(request, idEstudio, matriz, tipo):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    idEstudio = "0" + str(estudio.id)
    tipo = int(tipo)
    matriz = int(matriz)

    if tipo == 1:
        return generar_matrices_caa_daa(request, idEstudio, matriz)
    elif tipo == 2:
        return generar_mapa_caa_daa(request, idEstudio, matriz)
    elif tipo == 3:
        return histograma_caa_daa(request, idEstudio, matriz)
    elif tipo == 4:
        return generar_grafo_caa(request, idEstudio, matriz)
    elif tipo == 5:
        return generar_grafo_daa(request, idEstudio, matriz)
    elif tipo == 6:
        return generar_lista_descendiente(request, idEstudio, matriz)
    else:
        raise Http404("Error: Esta vista no existe")


# Calcula el consenso de las matrices 1mao y 2mao
def calcular_consenso_mao(request, idEstudio, num_matriz):

    estudio = get_object_or_404(EstudioMactor, id=idEstudio)
    lista_expertos = estudio.idExpertos.all()
    actores = Actor.objects.filter(idEstudio=estudio.id)
    objetivos = Objetivo.objects.filter(idEstudio=estudio.id)
    tamano_matriz_completa = len(actores) * len(objetivos)
    contador = 0
    lista_sublistas = []

    cont1 = 0
    while cont1 < tamano_matriz_completa:
        lista_sublistas.append([])
        cont1 += 1

    consulta_base = []
    if num_matriz < 3:
        for experto in lista_expertos:
            consulta = RelacionMAO.objects.filter(
                idActorY__idEstudio=estudio.id, idExperto=experto.id, tipo=num_matriz).order_by('idActorY',
                                                                                                'idObjetivoX')

            if len(consulta) == tamano_matriz_completa and len(consulta) > 0:
                consulta_base = consulta
                contador += 1
                for i in range(len(consulta)):
                    sublista = lista_sublistas[i]
                    sublista.append(consulta[i].valor)
                    lista_sublistas[i] = sublista
    else:
        idEstudio = "0" + str(estudio.id)
        consulta_base = calcular_valores_3mao(request, idEstudio)

    if num_matriz == 1 and len(consulta_base) > 0:
        for i in range(len(lista_sublistas)):  # se cuentan las veces en que aparecen cada uno de los valores del rango
            cont_uno_pos = lista_sublistas[i].count(1)
            cont_cero = lista_sublistas[i].count(0)
            cont_uno_neg = lista_sublistas[i].count(-1)

            if cont_uno_pos > max(cont_cero, cont_uno_neg):
                consulta_base[i].valor = 1
            elif cont_cero >= cont_uno_pos and cont_cero > cont_uno_neg:
                consulta_base[i].valor = 0
            elif cont_uno_neg >= max(cont_uno_pos, cont_cero):
                consulta_base[i].valor = -1

    elif num_matriz == 2 and len(consulta_base) > 0:
        for i in range(len(lista_sublistas)):  # se cuentan las veces en que aparecen cada uno de los valores del rango
            cont_4 = lista_sublistas[i].count(-4)
            cont_3 = lista_sublistas[i].count(-3)
            cont_2 = lista_sublistas[i].count(-2)
            cont_1 = lista_sublistas[i].count(-1)
            cont0 = lista_sublistas[i].count(0)
            cont1 = lista_sublistas[i].count(1)
            cont2 = lista_sublistas[i].count(2)
            cont3 = lista_sublistas[i].count(3)
            cont4 = lista_sublistas[i].count(4)

            if cont_4 >= max(cont_3, cont_2, cont_1, cont0, cont1, cont2, cont3, cont4):
                consulta_base[i].valor = -4
            elif cont_3 >= max(cont_2, cont_1, cont0, cont1, cont2, cont3, cont4):
                consulta_base[i].valor = -3
            elif cont_2 >= max(cont_1, cont0, cont1, cont2, cont3, cont4):
                consulta_base[i].valor = -2
            elif cont_1 >= max(cont0, cont1, cont2, cont3, cont4):
                consulta_base[i].valor = -1
            elif cont0 >= max(cont1, cont2, cont3, cont4):
                consulta_base[i].valor = 0
            elif cont1 >= max(cont2, cont3, cont4):
                consulta_base[i].valor = 1
            elif cont2 >= max(cont3, cont4):
                consulta_base[i].valor = 2
            elif cont3 >= cont4:
                consulta_base[i].valor = 3
            else:
                consulta_base[i].valor = 4

    cantidad = str(contador) + "/" + str(len(lista_expertos))
    resultado = {'consenso': consulta_base, 'expertos': cantidad}

    return resultado


"""------------------------------------------VIEWS MODELO INFORME FINAL---------------------------------------------"""


class CrearInformeFinal(CreateView):

    model = InformeFinal
    form_class = FormInforme
    template_name = 'mactor/informe/redactar_informe.html'

    def get_context_data(self, **kwargs):
        context = super(CrearInformeFinal, self).get_context_data(**kwargs)
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        context['estudio'] = estudio
        context['usuario'] = obtener_tipo_usuario(self.request, estudio.id)
        context['fecha_edicion'] = estudio.fecha_final + timedelta(days=5)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Informe final registrado con exito.')
        return super(CrearInformeFinal, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CrearInformeFinal, self).form_invalid(form)
        messages.error(self.request, 'El informe final no pudo ser registrado. Verifique los datos ingresados. ')
        return response

    def get_success_url(self):
        estudio = get_object_or_404(EstudioMactor, id=self.args[0])
        informe = get_object_or_404(InformeFinal, idEstudio=estudio.id)
        return reverse('mactor:editar_informe', args=[informe.id])


class EditarInformeFinal(UpdateView):

    model = InformeFinal
    form_class = FormInforme
    template_name = 'mactor/informe/editar_informe.html'
    context_object_name = 'informe'

    def get_context_data(self, **kwargs):
        context = super(EditarInformeFinal, self).get_context_data(**kwargs)
        informe = get_object_or_404(InformeFinal, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioMactor, id=informe.idEstudio.id)
        context['estudio'] = estudio
        context['usuario'] = obtener_tipo_usuario(self.request, informe.idEstudio.id)
        context['hoy'] = date.today()
        context['fecha_edicion'] = estudio.fecha_final + timedelta(days=5)
        obtener_estudios_usuario(self)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Informe final actualizado con exito.')
        return super(EditarInformeFinal, self).form_valid(form)

    def form_invalid(self, form):
        response = super(EditarInformeFinal, self).form_invalid(form)
        messages.error(self.request, 'El informe final no pudo ser actualizado. Verifique los datos ingresados.')
        return response

    def get_success_url(self):
        return reverse('mactor:editar_informe', args=self.kwargs['pk'])


"""---------------------------------------------FUNCIONES DE CONTROL Y ACTUALIZACION--------------------------------"""


# Determina el rol que ocupa el usuario en sesión en el estudio
def obtener_tipo_usuario(request, idEstudio):

    estudio = EstudioMactor.objects.get(id=idEstudio)
    lista_expertos = estudio.idExpertos.all()
    tipo = ""

    if request.user == estudio.idAdministrador or request.user == estudio.idCoordinador:
        tipo = "COORDINADOR"
    if request.user in lista_expertos and tipo == "COORDINADOR":
        tipo = "COORDINADOR_EXPERTO"
    elif request.user in lista_expertos:
        tipo = "EXPERTO"
    return tipo


# Retorna la lista de estudios Entrevista del usuario en sesión
def obtener_estudios_usuario(self):

    estudios = EstudioMactor.objects.all().order_by('-estado', 'titulo')
    estudios_usuario = []

    for estudio in estudios:
        if estudio.idAdministrador == self. \
                request.user or estudio.idCoordinador == self. \
                request.user or self.request.user in estudio.idExpertos.all():
            estudios_usuario.append(estudio)

    actualizar_estudios(estudios_usuario)
    return estudios_usuario


# Actualiza el estado de los estudios del usuario a medida que este se desarrolla
def actualizar_estudios(estudios_usuario):

    for estudio in estudios_usuario:
        if estudio.estado is True:
            if date.today() > estudio.fecha_final:
                estudio.estado = False
                estudio.save()
    actualizar_informes(estudios_usuario)


# Actualiza el estado de los estudios del usuario a medida que este se desarrolla
def actualizar_informes(estudios_usuario):

    for estudio in estudios_usuario:
        informe = InformeFinal.objects.filter(idEstudio=estudio.id).exists()
        if informe is True:
            informe = InformeFinal.objects.get(idEstudio=estudio.id)
            if informe.estado is False:
                if date.today() > (estudio.fecha_final + timedelta(days=5)):
                    informe.estado = True
                    informe.save()


"""---------------------------------------EXPORTACION A EXCEL-------------------------------------------------------"""


# Exporta a excel los datos basicos del estudio y sus respectivas entradas
def exportar_estudio_xls(request, idEstudio):

    estudio = get_object_or_404(EstudioMactor, id=int(idEstudio))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + estudio.titulo + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    hoja_actores = wb.add_sheet('Actores')
    hoja_fichas = wb.add_sheet('Estrategias')
    hoja_objetivos = wb.add_sheet('Objetivos')
    hoja_mid = wb.add_sheet('MID')
    hoja_1mao = wb.add_sheet('1MAO')
    hoja_2mao = wb.add_sheet('2MAO')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns1 = ['Nombre Largo', 'Nombre Corto', 'Descripción']
    columns2 = ['Estrategias del actor', 'Sobre el actor', 'Estrategias']
    columns3 = ['Influencia del actor', 'Sobre el actor', 'Valor', 'Justificación']
    columns4 = ['Posicion del actor', 'Ante el objetivo', 'Valor', 'Justificación']

    for col_num in range(len(columns1)):
        hoja_actores.write(row_num, col_num, columns1[col_num], font_style)

    for col_num in range(len(columns2)):
        hoja_fichas.write(row_num, col_num, columns2[col_num], font_style)

    for col_num in range(len(columns1)):
        hoja_objetivos.write(row_num, col_num, columns1[col_num], font_style)

    for col_num in range(len(columns3)):
        hoja_mid.write(row_num, col_num, columns3[col_num], font_style)

    for col_num in range(len(columns4)):
        hoja_1mao.write(row_num, col_num, columns4[col_num], font_style)
        hoja_2mao.write(row_num, col_num, columns4[col_num], font_style)

    font_style = xlwt.XFStyle()
    filas = obtener_datos_estudio(request, estudio.id)

    for row in filas['actores']:
        row_num += 1
        for col_num in range(len(row)):
            hoja_actores.write(row_num, col_num, row[col_num], font_style)
    row_num = 0
    for row in filas['fichas']:
        row_num += 1
        for col_num in range(len(row)):
            hoja_fichas.write(row_num, col_num, row[col_num], font_style)
    row_num = 0
    for row in filas['objetivos']:
        row_num += 1
        for col_num in range(len(row)):
            hoja_objetivos.write(row_num, col_num, row[col_num], font_style)
    row_num = 0
    for row in filas['mid']:
        row_num += 1
        for col_num in range(len(row)):
            hoja_mid.write(row_num, col_num, row[col_num], font_style)
    row_num = 0
    for row in filas['1mao']:
        row_num += 1
        for col_num in range(len(row)):
            hoja_1mao.write(row_num, col_num, row[col_num], font_style)
    row_num = 0
    for row in filas['2mao']:
        row_num += 1
        for col_num in range(len(row)):
            hoja_2mao.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# Devuelve los datos a exportar a excel
def obtener_datos_estudio(request, idEstudio):

    usuario = obtener_tipo_usuario(request, idEstudio)
    filas_actores = Actor.objects.filter(idEstudio=idEstudio).values_list('nombreLargo', 'nombreCorto', 'descripcion')
    filas_fichas = Ficha.objects.filter(idActorY__idEstudio=idEstudio).values_list(
        'idActorY__nombreLargo', 'idActorX__nombreLargo', 'estrategia')
    filas_objetivos = Objetivo.objects.filter(idEstudio=idEstudio).values_list(
        'nombreLargo', 'nombreCorto', 'descripcion')

    if usuario != "EXPERTO":
        filas_mid = RelacionMID.objects.filter(idActorY__idEstudio=idEstudio).values_list(
            'idActorY__nombreLargo', 'idActorX__nombreLargo', 'valor', 'justificacion').order_by('idActorY', 'idActorX')
        filas_1mao = RelacionMAO.objects.filter(idActorY__idEstudio=idEstudio, tipo=1).values_list(
            'idActorY__nombreLargo', 'idObjetivoX__nombreLargo', 'valor', 'justificacion').order_by('idActorY',
                                                                                                    'idObjetivoX')
        filas_2mao = RelacionMAO.objects.filter(idActorY__idEstudio=idEstudio, tipo=2).values_list(
            'idActorY__nombreLargo', 'idObjetivoX__nombreLargo', 'valor', 'justificacion').order_by('idActorY',
                                                                                                    'idObjetivoX')
    else:
        filas_mid = RelacionMID.objects.filter(idActorY__idEstudio=idEstudio, idExperto=request.user.id).values_list(
            'idActorY__nombreLargo', 'idActorX__nombreLargo', 'valor', 'justificacion').order_by('idActorY', 'idActorX')
        filas_1mao = RelacionMAO.objects.filter(idActorY__idEstudio=idEstudio, tipo=1,
                                                idExperto=request.user.id).values_list(
            'idActorY__nombreLargo', 'idObjetivoX__nombreLargo', 'valor', 'justificacion').order_by('idActorY',
                                                                                                    'idObjetivoX')
        filas_2mao = RelacionMAO.objects.filter(idActorY__idEstudio=idEstudio, tipo=2,
                                                idExperto=request.user.id).values_list(
            'idActorY__nombreLargo', 'idObjetivoX__nombreLargo', 'valor', 'justificacion').order_by('idActorY',
                                                                                                    'idObjetivoX')

    filas = {'actores': filas_actores, 'fichas': filas_fichas, 'objetivos': filas_objetivos,
             'mid': filas_mid, '1mao': filas_1mao, '2mao': filas_2mao}

    return filas