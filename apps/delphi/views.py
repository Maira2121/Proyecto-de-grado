import json
from collections import OrderedDict
from datetime import timedelta
from urllib import request

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from apps.delphi.forms import *
from django.forms.models import model_to_dict
from apps.delphi.models import *
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, RedirectView, TemplateView
from django.http import JsonResponse
from django.template.loader import render_to_string

# Create your views here.
from apps.usuario.form import *


def obtener_tipo_usuario(request, estudio_delphi):
    estudio = EstudioDelphi.objects.get(id=estudio_delphi.id)
    lista_coordinadores = estudio.coordinadores.all()
    lista_participantes = estudio.participantes.all()
    tipo = ""
    if request.user == estudio.moderador:
        tipo = "MODERADOR"
    if request.user in lista_coordinadores:
        tipo = "COORDINADOR"
    elif request.user in lista_participantes:
        tipo = "PARTICIPANTES"

    return tipo


# Retorna la lista de estudios Delphi del usuario en sesión
def obtener_estudios_delphi_usuario(self):
    estudios = EstudioDelphi.objects.all().order_by('-estado', 'titulo')
    estudios_delphi_usuario = []

    for estudio in estudios:
        if estudio.moderador == self.request.user \
                or self.request.user in estudio.coordinadores.all() \
                or self.request.user in estudio.participantes.all():
            estudios_delphi_usuario.append(estudio)
    actualizar_estudios(estudios_delphi_usuario)

    return estudios_delphi_usuario


def obtener_preguntas_delphi_usuario(self, sesion):
    preguntas = Pregunta.objects.filter(sesion=sesion).order_by('enunciado_pregunta')
    preguntas_delphi_usuario = []

    for pregunta in preguntas:
        if pregunta.autor == self.request.user:
            preguntas_delphi_usuario.append(pregunta)
    return preguntas_delphi_usuario


# Actualiza el estado de los estudios del usuario a medida que este se desarrolla
def actualizar_estudios(estudios_usuario):
    for estudio in estudios_usuario:
        if estudio.estado is True:
            if date.today() > estudio.fecha_final:
                estudio.estado = False
                estudio.save()


def cerrar_sesion(request, pk):
    sesion = get_object_or_404(SesionCuestionario, id=pk)
    preguntas = Pregunta.objects.filter(sesion=sesion)
    sesion.estado = False
    sesion.save()
    if sesion.estado is False :
        for pregunta in preguntas:
            coordina = pregunta.sesion.cuestionario.delphi.coordinadores.all()
            if pregunta.votos_positivos.count()<= (coordina.count() / 2):
                pregunta.delete()

    return redirect('delphi:detalle_cuestionario', sesion.cuestionario.id)




def actualizar_cuestionarios(cuestionarios_list):
    for cuestionario in cuestionarios_list:
        if cuestionario.abierto is True:
            if date.today() > cuestionario.fecha_final:
                cuestionario.abierto = False
                cuestionario.save()


class Nuevo_estudio_Delphi(CreateView):
    form_class = DelphiForm
    template_name = 'delphi/estudios_delphi/addEstudioDelphi.html'
    success_url = reverse_lazy('delphi:estudios_delphi')

    def get_context_data(self, **kwargs):
        context = super(Nuevo_estudio_Delphi, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS, 'Estudio ' + form.clean_titulo() + ' registrado con exito.')
        return super(Nuevo_estudio_Delphi, self).form_valid(form)

    def form_invalid(self, form):
        response = super(Nuevo_estudio_Delphi, self).form_invalid(form)
        messages.error(self.request, 'El estudio no pudo ser registrado, verifique los datos ingresados.')
        return response


def inicio(request):
    template_name = 'inicio.html'
    return render(request, template_name)


class ListaEstudiosDelphi(ListView):
    model = EstudioDelphi
    template_name = 'delphi/estudios_delphi/lista_estudio_delphi.html'

    def get_queryset(self):
        estudios = obtener_estudios_delphi_usuario(self)
        return estudios

    def get_context_data(self, **kwargs):
        context = super(ListaEstudiosDelphi, self).get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context

    def post(self, request, **kwargs):
        mensaje = dict()
        if request.method == "POST":
            if "estudio_id" in request.POST:
                try:
                    estudio_id = self.request.POST['estudio_id']
                    p = EstudioDelphi.objects.get(pk=estudio_id)
                    mensaje = {'status': 'True', 'estudio_id': p.id}
                    p.delete()
                    return HttpResponse(json.dumps(mensaje), content_type='aplication/json')
                except:
                    mensaje = {'status': 'False'}
                    return HttpResponse(json.dumps(mensaje), content_type='aplication/json')


class Editar_estudio_delphi(UpdateView):
    model = EstudioDelphi
    form_class = DelphiForm
    template_name = 'delphi/editarEstudioDelphi.html'
    success_url = reverse_lazy('delphi:estudios_delphi')


def agregar_participante(request):
    if request.method == 'POST':
        form = RegistroUsuario_form(request.POST)
    else:
        form = RegistroUsuario_form()
    return guardar_participante_estudio(request, form, 'delphi/estudios_delphi/agregar_participante.html')


def guardar_participante_estudio(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            context = {
                'form': form,

            }
            data['opcion_list'] = render_to_string(
                'usuario/lista_participantes.html', context)
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


class DetalleEstudio(DetailView):
    model = EstudioDelphi
    template_name = 'delphi/estudios_delphi/detalleEstudioDelphi.html'
    success_url = reverse_lazy('delphi:estudios_delphi')

    def get_context_data(self, **kwargs):
        cuestionarios_activos = 0
        cant_rondas_activas = 0
        delphi = EstudioDelphi.objects.get(pk=self.kwargs.get('pk'))
        cuestionarios = CuestionarioDelphi.objects.filter(delphi=delphi)
        rondas = RondasDelphi.objects.filter(cuestionario=cuestionarios)
        sesiones = SesionCuestionario.objects.filter(cuestionario=cuestionarios)

        if len(cuestionarios) > 0:
            cuestionarios_activos = cuestionarios.filter(estado=True).count()

        if len(rondas) > 0:
            cant_rondas_activas = rondas.filter(abierto=True).count()

        kwargs.update({'cuestionarios': cuestionarios,
                       'delphi': delphi,
                       'rondas': rondas,
                       'sesiones': sesiones,
                       'cant_cuestionarios_activos':cuestionarios_activos,
                       ' cant_rondas_activas': cant_rondas_activas
                       }
                      )
        actualizar_cuestionarios(cuestionarios)
        return super(DetalleEstudio, self).get_context_data(**kwargs)

    # ---------------------------------------------------------------


class EditarCuestionario(UpdateView):
    model = CuestionarioDelphi
    form_class = EditarCuestionarioForm
    template_name = 'delphi/cuestionario/editarCuestionarioDelphi.html'


def agregar_participante_estudio(request, pk):
    estudio = get_object_or_404(EstudioDelphi, id=pk)
    cuestionario = get_object_or_404(CuestionarioDelphi, delphi=pk)
    if request.method == 'POST':

        content = request.POST['content']
        content = json.loads(content)
        print(type(content))
        for p in content:
            print(type(p))
            usuario = get_object_or_404(User, username=p)
            print(usuario.email)
            estudio.participantes.add(usuario)
            estudio.save()
            url = '/delphi/crear_ronda/' + pk
            data = {
                'url': url,
            }
        return JsonResponse(data)
    else:
        data = {
            'is_taken': False
        }
    return JsonResponse(data)


class GenerarCuestionario(DetailView):
    model = SesionCuestionario
    template_name = 'delphi/cuestionario/generar_cuestionario.html'

    def get_context_data(self, **kwargs):
        session = get_object_or_404(SesionCuestionario, id=self.kwargs['pk'])
        lista_preguntas = []
        preguntas = Pregunta.objects.filter(sesion=session)
        usuarios = User.objects.all()
        for pregunta in preguntas:
            coordina = pregunta.sesion.cuestionario.delphi.coordinadores.all()
            if pregunta.votos_positivos.count() > (coordina.count() / 2):
                lista_preguntas.append(pregunta)
        opciones = OpcionRespuesta.objects.all()

        kwargs.update({'preguntas': lista_preguntas,
                       'opciones': opciones,
                       'participantes': usuarios,
                       'sesion': self.object}
                      )
        return super(GenerarCuestionario, self).get_context_data(**kwargs)


class Crear_Cuestionario(CreateView):
    model = CuestionarioDelphi
    template_name = 'delphi/cuestionario/addCuestionarioDelphi.html'
    form_class = CuestionarioForm

    def get_context_data(self, **kwargs):
        context = super(Crear_Cuestionario, self).get_context_data(**kwargs)
        delphi = EstudioDelphi.objects.get(pk=self.kwargs.get('pk'))
        cuestionarios = CuestionarioDelphi.objects.filter(delphi=delphi)
        rondas = RondasDelphi.objects.filter(delphi=delphi).order_by('numero_ronda')
        if len(rondas) > 0:
            rondas_activas = rondas.filter(abierto=True).count()
            context['cant_rondas_activas'] = rondas_activas

        if len(cuestionarios) > 0:
            cuestionarios_activos = cuestionarios.filter(estado=True).count()
            print(cuestionarios_activos)
            context['cant_cuestionarios_activos'] = cuestionarios_activos
        else:
            context['cant_cuestionarios_activos'] = 0
            context['cant_rondas_activas'] = 0
        context['delphi'] = delphi
        # Se verifica que existan preguntas registradas y una escala de likert que permita evaluarlas

        return context

    def form_valid(self, form):
        delphi = EstudioDelphi.objects.get(pk=self.kwargs.get('pk'))
        instance = form.save(commit=False)
        instance.delphi = delphi
        form.save()
        print(instance)
        return super(Crear_Cuestionario, self).form_valid(form=form)


class NuevaSesion_cuestionario(CreateView):
    form_class = SesionCuestionarioForm
    template_name = 'delphi/sesion/addSesion_cuestionario.html'

    def get_context_data(self, **kwargs):
        context = super(NuevaSesion_cuestionario, self).get_context_data(**kwargs)
        cuestionario = CuestionarioDelphi.objects.get(pk=self.kwargs.get('pk'))
        sesiones = SesionCuestionario.objects.filter(cuestionario=cuestionario.id).order_by('codigo_sesion')
        if len(sesiones) > 0:
            sesiones_activas = sesiones.filter(estado=True).count()
            context['cant_sessiones_activas'] = sesiones_activas
            context['delphi'] = cuestionario.delphi
            context['cuestionario'] = cuestionario
            context['hoy'] = date.today()
            context['codigo_sesion'] = sesiones.last().codigo_sesion + 1
        else:
            context['cant_sesiones_resgistradas'] = 0
            context['cuestionario'] = cuestionario
            context['hoy'] = date.today()
            context['codigo_sesion'] = 1
            context['delphi'] = cuestionario.delphi
        return context

    def form_valid(self, form):
        cuestionario = CuestionarioDelphi.objects.get(pk=self.kwargs.get('pk'))
        sesiones = SesionCuestionario.objects.filter(cuestionario=cuestionario).order_by('codigo_sesion')
        if len(sesiones) > 0:
            sesiones_activas = sesiones.filter(estado=True).count()
            cant_sesiones_activas = sesiones_activas
            codigo_sesion = sesiones.last().codigo_sesion + 1
        else:
            cant_rondas_registradas = 0
            codigo_sesion = 1

        instance = form.save(commit=False)
        instance.codigo_sesion = codigo_sesion
        instance.cuestionario = cuestionario
        form.save()
        print(instance)
        return super(NuevaSesion_cuestionario, self).form_valid(form=form)


class EditarSesion(UpdateView):
    model = SesionCuestionario
    form_class = EditarSesionForm
    template_name = 'delphi/sesion/editarSesion_cuestionario.html'

    def get_context_data(self, **kwargs):
        context = super(EditarSesion, self).get_context_data(**kwargs)
        cuestionario = CuestionarioDelphi.objects.get(pk=self.kwargs.get('pk'))
        context['delphi'] = cuestionario.delphi
        context['cuestionario'] = cuestionario
        return context


# ------------- Rondas ----------------------------------------

class CrearRonda(CreateView):
    model = RondasDelphi
    template_name = 'delphi/ronda/nueva_ronda.html'
    form_class = RondasForm
    success_url = reverse_lazy('delphi:estudios_delphi')

    def get_context_data(self, **kwargs):
        lista_preguntas = []
        context = super(CrearRonda, self).get_context_data(**kwargs)
        cuestionario = CuestionarioDelphi.objects.get(pk=self.kwargs.get('pk'))
        sesion = SesionCuestionario.objects.filter(cuestionario=cuestionario)
        rondas = RondasDelphi.objects.filter(cuestionario=cuestionario.id).order_by('numero_ronda')
        print(sesion)
        preguntas = Pregunta.objects.filter(sesion=sesion)
        for pregunta in preguntas:
            coordina = pregunta.sesion.cuestionario.delphi.coordinadores.all()
            if pregunta.votos_positivos.count() > (coordina.count() / 2):
                lista_preguntas.append(pregunta)

        if len(sesion)> 0:
            sesion_activa = sesion.filter(estado=True).count()
            context['cant_sessiones_activas'] = sesion_activa
        else:
            context['cant_sessiones_activas'] = 0


        if len(rondas) > 0:
            rondas_activa = rondas.filter(abierto=True).count()
            context['cant_rondas_activa'] = rondas_activa
            context['num_ronda'] = rondas.last().numero_ronda + 1
        else:
            context['cant_rondas_registradas'] = 0
            context['num_ronda'] = 1

        # Se verifica que existan preguntas registradas y una escala de likert que permita evaluarlas
        context['entradas_estudio'] = False
        if len(lista_preguntas) > 0:
            context['entradas_estudio'] = True

        context['cuestionario'] = cuestionario
        context['num_preguntas'] = len(lista_preguntas)
        context['hoy'] = date.today()
        return context

    def form_valid(self, form):
        cuestionario = CuestionarioDelphi.objects.get(pk=self.kwargs.get('pk'))
        rondas = RondasDelphi.objects.filter(cuestionario=cuestionario).order_by('numero_ronda')
        if len(rondas) > 0:
            rondas_activa = rondas.filter(abierto=True).count()
            cant_rondas_activa = rondas_activa
            num_ronda = rondas.last().numero_ronda + 1
        else:
            cant_rondas_registradas = 0
            num_ronda = 1

        instance = form.save(commit=False)
        instance.numero_ronda = num_ronda
        instance.cuestionario = cuestionario
        instance.delphi = cuestionario.delphi
        form.save()
        print(instance)
        return super(CrearRonda, self).form_valid(form=form)


def actualizar_rondas(cuestionario_id):
    cuestionario = get_object_or_404(CuestionarioDelphi, id=cuestionario_id)
    rondas = RondasDelphi.objects.filter(cuestionario=cuestionario).order_by('numero_ronda')

    for ronda in rondas:
        # si se cumplio el tiempo de la ronda
        if ronda.abierto is True and date.today() > ronda.fecha_final:
            ronda.abierto = False
            ronda.save()
        # si el estudio esta cerrado o se desactiva la ronda y se crea otra, se cierra la anterior
        if cuestionario.abierto is False or ronda.abierto is False \
                and rondas.exclude(id=ronda.id).filter(abierto=True).count() > 0:
            if ronda.fecha_final >= date.today():
                ronda.fecha_final = date.today() - timedelta(days=1)
                ronda.abierto = False
                ronda.save()
        registrar_coeficiente(ronda)


def registrar_coeficiente(ronda):
    estudio = get_object_or_404(EstudioDelphi, id=ronda.delphi.id)
    cant_preguntas = ronda.numero_preguntas
    # matriz_juicios = calcular_matriz_juicios(estudio, ronda, "")
    # valor = calcular_coeficiente(ronda, matriz_juicios, "")
    # ver_coeficiente = CoeficienteAlfa.objects.filter(idRonda=ronda.id).exists()

    # cantidad de expertos que finalizaron la ronda
    cont = 0


def actualizar_sesiones(cuestionario_id):
    cuestionario = get_object_or_404(CuestionarioDelphi, id=cuestionario_id)
    sesiones = SesionCuestionario.objects.filter(cuestionario=cuestionario).order_by('codigo_sesion')

    for sesion in sesiones:
        # si se cumplio el tiempo de la ronda
        if sesion.estado is True and date.today() > sesion.fecha_final:
            sesion.estado = False
            sesion.save()
        if sesion.estado is False or date.today() > sesion.fecha_final:
            sesion.permitir_preguntas = False
            sesion.save()
        # si el estudio esta cerrado o se desactiva la ronda y se crea otra, se cierra la anterior
        if cuestionario.estado is False or sesion.estado is False \
                and sesiones.exclude(id=sesion.id).filter(estado=True).count() > 0:
            if sesion.fecha_final >= date.today():
                sesion.fecha_final = date.today() - timedelta(days=1)
                sesion.abierto = False

                sesion.save()


class ListaSesiones(ListView):
    model = SesionCuestionario
    template_name = 'delphi/cuestionario/detalleCuestionario.html'
    context_object_name = 'sesiones'

    def get_queryset(self, **kwargs):
        self.cuestionario = get_object_or_404(CuestionarioDelphi, id=self.kwargs['pk'])
        print(self.cuestionario)
        actualizar_sesiones(self.cuestionario.id)
        return SesionCuestionario.objects.filter(cuestionario=self.cuestionario.id).order_by('codigo_sesion')

    def get_context_data(self, **kwargs):
        cuestionario = self.cuestionario
        context = super(ListaSesiones, self).get_context_data(**kwargs)
        context['cuestionario'] = cuestionario
        context['hoy'] = date.today()
        context['sesiones_activas'] = SesionCuestionario.objects.filter(cuestionario=cuestionario.id,
                                                                        estado=True).count()
        actualizar_sesiones(self.cuestionario.id)
        return context


class ListaRondas(ListView):
    model = RondasDelphi
    template_name = 'delphi/ronda/lista_ronda.html'
    context_object_name = 'rondas'

    def get_queryset(self):
        self.cuestionario = get_object_or_404(CuestionarioDelphi, id=self.args[0])
        actualizar_rondas(self.cuestionario.id)
        return RondasDelphi.objects.filter(cuestionario=self.cuestionario.id).order_by('numero_ronda')

    def get_context_data(self, **kwargs):
        context = super(ListaRondas, self).get_context_data(**kwargs)
        context['cuestionario'] = self.cuestionario
        #   context['usuario'] = obtener_tipo_usuario(self, self.cuestionario.delphi)
        context['hoy'] = date.today()
        context['rondas_activas'] = RondasDelphi.objects.filter(cuestionario=self.cuestionario.id, abierto=True).count()
        actualizar_rondas(self.cuestionario.id)
        return context


class EditarRondaDelphi(UpdateView):
    model = RondasDelphi
    form_class = RondasForm
    template_name = 'delphi/editarRondasDelphi.html'

    def get_context_data(self, **kwargs):
        ronda = get_object_or_404(RondasDelphi, id=self.kwargs['pk'])
        context = super(EditarRondaDelphi, self).get_context_data(**kwargs)
        cuestionario = ronda.cuestionario
        context['delphi'] = cuestionario.delphi
        context['cuestionario'] = cuestionario
        return context


class ConsultarRonda(DetailView):
    model = RondasDelphi
    template_name = 'delphi/ronda/consultar_ronda.html'
    context_object_name = 'ronda'

    def get_context_data(self, **kwargs):
        context = super(ConsultarRonda, self).get_context_data(**kwargs)
        ronda = get_object_or_404(RondasDelphi, id=self.kwargs['pk'])
        estudio = get_object_or_404(EstudioDelphi, id=ronda.delphi.id)
        # context['usuario'] = obtener_tipo_usuario(self, estudio)
        return context


# -------------------------- Preguntas -----------------------------

class ListaPreguntas(DetailView):
    model = SesionCuestionario
    template_name = 'delphi/pregunta/listaPreguntasCuestionarioDelphi.html'

    def get_context_data(self, **kwargs):
        preguntas = Pregunta.objects.filter(sesion=self.object)
        no_mis_preguntas = []
        for pregunta in preguntas:
            if pregunta.enunciado_pregunta == "":
                pregunta.delete()
        mis_preguntas = obtener_preguntas_delphi_usuario(self, self.object)
        kwargs.update({'preguntas': preguntas,
                       'mis_preguntas': mis_preguntas,
                       }
                      )
        return super(ListaPreguntas, self).get_context_data(**kwargs)


class NuevaPregunta(CreateView):
    form_class = FormPregunta
    template_name = 'delphi/pregunta/nuevaPregunta.html'

    def get_context_data(self, **kwargs):
        sesion = SesionCuestionario.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'sesion': sesion})
        return super(NuevaPregunta, self).get_context_data(**kwargs)

    def form_valid(self, form):
        sesion = SesionCuestionario.objects.get(pk=self.kwargs.get('pk'))
        instance = form.save(commit=False)
        instance.sesion = sesion
        instance.cuestionario = sesion.cuestionario
        instance.enunciado_pregunta = ""
        return super(NuevaPregunta, self).form_valid(form=form)


class DetallePregunta(DetailView):
    model = Pregunta
    form_class = FormPregunta
    template_name = 'delphi/pregunta/Pregunta.html'

    def get_context_data(self, **kwargs):
        opciones = OpcionRespuesta.objects.filter(pregunta=self.object)
        numero_opciones = len(opciones)
        kwargs.update({'opciones': opciones,
                       'numero_opciones': numero_opciones,
                       })

        return super(DetallePregunta, self).get_context_data(**kwargs)


class EliminarPregunta(DeleteView):
    model = Pregunta
    context_object_name = 'pregunta'
    success_message = "Pregunta eliminada del cuestionario."
    template_name = 'delphi/pregunta/eliminar_pregunta.html'

    def get_context_data(self, **kwargs):
        context = super(EliminarPregunta, self).get_context_data(**kwargs)
        pregunta = get_object_or_404(Pregunta, id=self.kwargs['pk'])
        context['autor'] = pregunta.autor
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarPregunta, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        pregunta = get_object_or_404(Pregunta, id=self.kwargs['pk'])
        return reverse('delphi:preguntas', args={pregunta.cuestionario.id})


class CompletarPregunta(UpdateView):
    model = Pregunta
    form_class = PreguntaForm
    template_name = 'delphi/pregunta/completarPregunta.html'


class EditarPregunta(UpdateView):
    model = Pregunta
    form_class = FormEditarPregunta
    template_name = 'delphi/pregunta/editarPregunta.html'

    def get_context_data(self, **kwargs):
        pregunta = get_object_or_404(Pregunta, id=self.kwargs['pk'])
        autor1 = pregunta.autor
        kwargs.update({'autor1': autor1})

        return super(EditarPregunta, self).get_context_data(**kwargs)


# ---------------- Opciones de respuestas --------------

def listaOpciones(request, pk):
    pregunta = Pregunta.objects.get(pk=pk)
    opciones = OpcionRespuesta.objects.filter(pregunta=pregunta.id)
    context = {
        'opciones': opciones,
        'pregunta': pregunta,
    }
    if pregunta.tipo_pregunta == "escala":

        return render(request, 'delphi/pregunta/opciones/opciones_Likert/listaOpciones_Likert.html', context)

    elif pregunta.tipo_pregunta == "numerica":

        return render(request, 'delphi/pregunta/opciones/opciones_numerica/lista_opciones_escala_numerica.html',
                      context)

    else:
        return render(request, 'delphi/pregunta/opciones/listaOpciones.html', context)


def guardar_opciones(request, form, template_name, pregunta):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            context = {
                'form': form,
                'pregunta': pregunta,
                'opciones': OpcionRespuesta.objects.filter(pregunta=pregunta.id)
            }
            data['opcion_list'] = render_to_string('delphi/pregunta/opciones/listaOpcion2.html', context)
        else:
            data['form_is_valid'] = False
    context = {
        'form': form,
        'pregunta': pregunta
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def guardar_opcion_escala_numerica(request, form, template_name, pregunta):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            context = {
                'form': form,
                'pregunta': pregunta,
                'opciones': OpcionRespuesta.objects.filter(pregunta=pregunta.id)
            }
            data['opcion_list'] = render_to_string(
                'delphi/pregunta/opciones/opciones_numerica/lista_opcion2_escala_numerica.html', context)
        else:
            data['form_is_valid'] = False
    context = {
        'form': form,
        'pregunta': pregunta
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def guardar_opcion_escala_Likert(request, form, template_name, pregunta):
    data = dict()
    valores_rango = [5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5]
    valores_registrados = OpcionRespuesta.objects.filter(pregunta=pregunta.id).order_by('-valor_inicio')
    # Se eliminan los puntajes que ya estan en la escala para evitar duplicados.
    for i in valores_registrados:
        valores_rango.remove(i.valor_inicio)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            context = {
                'form': form,
                'pregunta': pregunta,
                'valores': valores_rango,
                'opciones': OpcionRespuesta.objects.filter(pregunta=pregunta.id)
            }
            data['opcion_list'] = render_to_string('delphi/pregunta/opciones/opciones_Likert/listaOpcion2_Likert.html',
                                                   context)
        else:
            data['form_is_valid'] = False
    context = {
        'form': form,
        'pregunta': pregunta,
        'valores': valores_rango
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def crear_opcion_respuesta(request, pk):
    pregunta = get_object_or_404(Pregunta, id=pk)

    if pregunta.tipo_pregunta == "escala":
        if request.method == 'POST':
            form = Form_opcion_escala_Likert(request.POST)
        else:
            form = Form_opcion_escala_Likert()
        return guardar_opcion_escala_Likert(request, form,
                                            'delphi/pregunta/opciones/opciones_Likert/crearOpciones_escala_Likert.html',
                                            pregunta)

    elif pregunta.tipo_pregunta == "numerica":
        if request.method == 'POST':
            form = Form_opcion_escala_numerica(request.POST)
        else:
            form = Form_opcion_escala_numerica()
        return guardar_opcion_escala_numerica(request, form,
                                              'delphi/pregunta/opciones/opciones_numerica/crear_opciones_escala_numerica.html',
                                              pregunta)

    else:
        if request.method == 'POST':
            form = Form_crear_opciones(request.POST)
        else:
            form = Form_crear_opciones()
        return guardar_opciones(request, form, 'delphi/pregunta/opciones/crearOpciones.html', pregunta)


def editar_opcion_respuesta(request, pk):
    opcion = get_object_or_404(OpcionRespuesta, id=pk)
    pregunta = Pregunta.objects.get(pk=opcion.pregunta.pk)

    if pregunta.tipo_pregunta == "numerica":
        if request.method == 'POST':
            form = Form_opcion_escala_numerica(request.POST, instance=opcion)
        else:
            form = Form_opcion_escala_numerica(instance=opcion)
        return guardar_opcion_escala_numerica(request, form,
                                              'delphi/pregunta/opciones/opciones_numerica/editar_opcion_numerica.html',
                                              pregunta)

    if pregunta.tipo_pregunta == "escala":
        if request.method == 'POST':
            form = Form_opcion_escala_Likert(request.POST, instance=opcion)
        else:
            form = Form_opcion_escala_Likert(instance=opcion)
        return guardar_opcion_escala_Likert(request, form,
                                            'delphi/pregunta/opciones/opciones_Likert/editar_opcion_Likert.html',
                                            pregunta)
    else:
        if request.method == 'POST':
            form = Form_crear_opciones(request.POST, instance=opcion)
        else:
            form = Form_crear_opciones(instance=opcion)
        return guardar_opciones(request, form, 'delphi/pregunta/opciones/editar_opcion.html', pregunta)


def eliminar_opcion(request, pk):
    data = dict()
    opcion = get_object_or_404(OpcionRespuesta, id=pk)
    pregunta = opcion.pregunta
    if request.method == "POST":
        opcion.delete()
        data['form_is_valid'] = True
        opciones = OpcionRespuesta.objects.filter(pregunta=pregunta.id)
        context = {
            'opciones': opciones,
            'pregunta': pregunta,
            'opcion': opcion
        }
        if pregunta.tipo_pregunta != "escala":

            data['opcion_list'] = render_to_string('delphi/pregunta/opciones/listaOpcion2.html', context)
        else:
            data['opcion_list'] = render_to_string('delphi/pregunta/opciones/opciones_Likert/listaOpcion2_Likert.html',
                                                   context)
    else:
        context = {'pregunta': pregunta.id,
                   'opcion': opcion}
        if pregunta.tipo_pregunta != "escala":
            data['html_form'] = render_to_string('delphi/pregunta/opciones/eliminar_opcion.html', context,
                                                 request=request)
        else:
            data['html_form'] = render_to_string('delphi/pregunta/opciones/opciones_Likert/eliminar_opcion_Likert.html',
                                                 context, request=request)

    return JsonResponse(data)


def votar_positivo_pregunta(request, pk):
    pregunta = get_object_or_404(Pregunta, id=pk)
    coordinadores = pregunta.sesion.cuestionario.delphi.coordinadores.all()
    user = request.user
    if request.user in coordinadores:
        if request.user in pregunta.votos_positivos.all():
            pregunta.votos_positivos.remove(user)
        else:
            pregunta.votos_positivos.add(user)
            if request.user in pregunta.votos_negativos.all():
                pregunta.votos_negativos.remove(user)
    else:
        data = {
            'data': "usted no puede votar"
        }
        return redirect('delphi:preguntas', pregunta.sesion.id)
    contador = pregunta.votos_positivos.count()
    print(contador)
    data = {
        'data': contador
    }
    return redirect('delphi:preguntas', pregunta.sesion.id)


def votar_negativo_pregunta(request, pk):
    pregunta = get_object_or_404(Pregunta, id=pk)
    coordinadores = pregunta.sesion.cuestionario.delphi.coordinadores.all()
    user = request.user
    if request.user in coordinadores:
        if request.user in pregunta.votos_negativos.all():
            pregunta.votos_negativos.remove(user)
        else:
            pregunta.votos_negativos.add(user)
            if request.user in pregunta.votos_positivos.all():
                pregunta.votos_positivos.remove(user)
    else:
        data = {
            'data': "usted no puede votar"
        }
        return redirect('delphi:preguntas', pregunta.sesion.id)
    contador = pregunta.votos_negativos.count()
    print(contador)
    data = {
        'data': contador
    }
    return redirect('delphi:preguntas', pregunta.sesion.id)


def Lanzar_cuestionario():
    return HttpResponse("Hola")


class EstadisticasPregunta(DetailView):
    model = Pregunta
    template_name = 'delphi/pregunta/estadisticas.html'


class ResponderCuestionario(TemplateView):
    template_name = 'delphi/respuesta/responder_cuestionario.html'

    def dispatch(self, request, *args, **kwargs):
        self.cuestionario = get_object_or_404(CuestionarioDelphi, pk=kwargs.get('pk', 0))
        return super(ResponderCuestionario, self).dispatch(request, *args, **kwargs)

    @csrf_exempt
    def get_context_data(self, **kwargs):
        data = super(ResponderCuestionario, self).get_context_data(**kwargs)
        forms = OrderedDict()
        for pregunta in self.cuestionario.preguntas_ordenadas():
            if pregunta.respuestasusuarios_set.filter(usuario=self.request.user).exists():
                forms.update({pregunta.id: ['Ha respondido satisfactoriamente esta pregunta',
                                            [
                                                resp.respuesta_texto if pregunta.tipo_pregunta == 'texto'
                                                else [r.texto_opcion for r in resp.opciones_seleccionadas.all()]
                                                for resp in
                                                pregunta.respuestasusuarios_set.filter(usuario=self.request.user).all()
                                            ]
                                            ]})

            else:
                forms.update({pregunta.id: ResponderForm(pregunta=pregunta)})

        data.update({
            'forms': forms,
            'preguntas': self.cuestionario.preguntas_ordenadas,
            'cuestionario': self.cuestionario,
            'finalizado': self.cuestionario.cuestionario_terminado(self.request.user)
        })
        print(self.cuestionario.cuestionario_terminado(self.request.user))
        return data

    def post(self, request, *args, **kwargs):

        pregunta = get_object_or_404(Pregunta, pk=request.POST.get('pregunta', 0))
        if pregunta.tipo_pregunta == 'unica' or pregunta.tipo_pregunta == 'texto' or pregunta.tipo_pregunta == 'escala':
            respuesta = request.POST.get('pregunta_{0}'.format(pregunta.id))
            if not respuesta:
                return JsonResponse(data={'done': False, 'id': pregunta.id, })
        else:
            respuesta = request.POST.getlist('pregunta_{0}'.format(pregunta.id))
            if not respuesta:
                return JsonResponse(data={'done': False, 'id': pregunta.id, })
        respuesta_usuario = RespuestasUsuarios()
        respuesta_usuario.pregunta = pregunta

        if pregunta.tipo_pregunta == 'texto':
            respuesta_usuario.respuesta_texto = respuesta

        respuesta_usuario.usuario = request.user
        respuesta_usuario.save()

        if pregunta.tipo_pregunta == 'multi':
            respuesta_usuario.opciones_seleccionadas.add(*respuesta)

        if pregunta.tipo_pregunta == 'unica':
            respuesta_usuario.opciones_seleccionadas.add(respuesta)

        if pregunta.tipo_pregunta == 'escala':
            respuesta_usuario.opciones_seleccionadas.add(respuesta)

        respuesta_usuario.save()

        return JsonResponse(data={'done': True, 'id': pregunta.id,
                                  'tipo': pregunta.tipo_pregunta,
                                  'respuestas': [
                                      resp.respuesta_texto if pregunta.tipo_pregunta == 'texto' else \
                                          [r.texto_opcion for r in resp.opciones_seleccionadas.all()] for resp
                                      in \
                                      pregunta.respuestasusuarios_set.filter(usuario=self.request.user).all()
                                  ],
                                  'finalizado': self.cuestionario.cuestionario_terminado(self.request.user)
                                  }, safe=False)


responder_cuestionario = ResponderCuestionario.as_view()


def ver_resultados(request, id_cuestionario):
    cuestionario = get_object_or_404(CuestionarioDelphi, id=id_cuestionario)

    preguntas = cuestionario.pregunta_set.all()

    resultado_preguntas = []
    for pregunta in preguntas:
        resultado_respuestas = []
        resultado_json = ''
        if pregunta.tipo_pregunta in ('multi', 'unica', 'escala'):
            cantidad_respuestas_totales = RespuestasUsuarios.objects.filter(
                opciones_seleccionadas__pregunta=pregunta).count()

            for opcion in pregunta.opcionrespuesta_set.all():
                cantidad = RespuestasUsuarios.objects.filter(pregunta=pregunta,
                                                             opciones_seleccionadas=opcion).count()
                if cantidad > 0:
                    porcentaje = float(cantidad) / float(cantidad_respuestas_totales) * float(100)
                else:
                    porcentaje = 0
                resultado = {
                    'label': opcion.texto_opcion,
                    'data': cantidad,
                    'respuesta': opcion.texto_opcion,
                    'cantidad': cantidad,
                    'porcentaje': porcentaje
                }
                resultado_respuestas.append(resultado)
            resultado_json = json.dumps(resultado_respuestas)

        else:
            for opcion in RespuestasUsuarios.objects.filter(pregunta=pregunta):
                resultado = {
                    'respuesta': opcion,
                }
                resultado_respuestas.append(resultado)

        r_pregunta = {
            'pregunta': pregunta,
            'resultados': resultado_respuestas,
            'resultado_json': resultado_json
        }
        resultado_preguntas.append(r_pregunta)

    context = {
        'resultados_preguntas': resultado_preguntas,
        'cuestionario': cuestionario
    }
    return render(request, 'delphi/cuestionario/ver_resultados.html', context)


def eliminar_cuestionario(request, pk):
    data = dict()
    cuestionario = get_object_or_404(CuestionarioDelphi, id=pk)
    delphi = cuestionario.delphi
    if request.method == "POST":
        cuestionario.delete()
        data['form_is_valid'] = True
        cuestionarios = CuestionarioDelphi.objects.filter(delphi=delphi.id)
        context = {
            'cuestionarios': cuestionarios,
            'delphi': delphi,
            'cuestionario': cuestionario
        }

        data['opcion_list'] = render_to_string('delphi/pregunta/opciones/listaOpcion2.html', context)
    else:
        context = {'delphi': delphi.id,
                   'cuestionario': cuestionario}
        data['html_form'] = render_to_string('delphi/pregunta/opciones/opciones_Likert/eliminar_opcion_Likert.html',
                                             context, request=request)

    return JsonResponse(data)
