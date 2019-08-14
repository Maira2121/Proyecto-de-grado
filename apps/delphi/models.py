import datetime
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from apps.delphi.choices import *
from django.utils.timezone import now


# Create your models here.


class EstudioDelphi(models.Model):
    proyecto = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    objetivos = models.TextField()
    moderador = models.ForeignKey(User, verbose_name='moderador', related_name='delphi_moderador')
    coordinadores = models.ManyToManyField(User, verbose_name='coordinadores', related_name='coordinadores')
    participantes = models.ManyToManyField(User, verbose_name='participantes', related_name='participantes')
    fecha_inicio = models.DateField(default=now)
    fecha_final = models.DateField(default=now)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Estudios Delphi'
        verbose_name = 'Estudio Delphi'

    def get_coordinadores(self):
        return ",".join([str(p) for p in self.coordinadores.all()])

    def get_participantes(self):
        return ",".join([str(p) for p in self.participantes.all()])

    def __str__(self):
        return self.titulo


class CuestionarioDelphi(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    delphi = models.ForeignKey('EstudioDelphi', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='cuestionario_delphi')
    fecha_inicio = models.DateField(default=now)
    fecha_final = models.DateField()

    def get_absolute_url(self):
        return reverse('delphi:Detalle_estudio', args={self.delphi.id})

    def __str__(self):
        return self.nombre

    def preguntas_ordenadas(self):
        return self.pregunta_set.order_by('id')

    def cuestionario_terminado(self, user):
        preguntas = self.preguntas_ordenadas().values_list('id', flat=True)
        respuestas = RespuestasUsuarios.objects.filter(usuario=user, pregunta__id__in=preguntas)
        return respuestas.count() == len(preguntas)

    def abierto(self):
        return self.estado or self.fecha_final <= datetime.datetime.today()

    def __unicode__(self):
        return u'{0}'.format(self.nombre)


class SesionCuestionario(models.Model):
    cuestionario = models.ForeignKey('CuestionarioDelphi', verbose_name='cuestionario_delphi')
    codigo_sesion = models.IntegerField()
    nombre = models.CharField(max_length=100)
    permitir_preguntas = models.BooleanField(default=False, help_text='Dice si se pueden crear preguntas o no. '
                                                                      'y si esta desactivado se pueden votar por las preguntas ya creadas')
    estado = models.BooleanField(default=True, help_text='Dice si se pueden votar o no.')
    fecha = models.DateTimeField(default=now)
    fecha_inicio = models.DateField(default=now)
    fecha_final = models.DateField(default=now)

    class Meta:
        verbose_name = "Sesion cuestionario Delphi"
        verbose_name_plural = "Sesiones de cuestionario Delphi"
        unique_together = ('codigo_sesion', 'cuestionario')
        ordering = ('cuestionario', 'codigo_sesion',)

    def __str__(self):
        return u'Sesion {0} del cuestionario{0}'.format(self.codigo_sesion, self.cuestionario.nombre)

    def get_absolute_url(self):
        return reverse('delphi:detalle_cuestionario', args={self.cuestionario.id})


class Pregunta(models.Model):
    tipo_pregunta = models.CharField(max_length=10, choices=CHOICES_TIPO_PREGUNTA)
    enunciado_pregunta = models.TextField()
    de_control = models.BooleanField(default=False)
    votos_positivos = models.ManyToManyField(User, blank=True, related_name='votos_positivos')
    votos_negativos = models.ManyToManyField(User, blank=True, related_name='votos_negativos')
    autor = models.ForeignKey(User, verbose_name='autor', related_name='autor')
    sesion = models.ForeignKey('SesionCuestionario')
    cuestionario = models.ForeignKey('CuestionarioDelphi')


    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def get_absolute_url(self):
        if self.enunciado_pregunta == "":
            return reverse('delphi:completar_pregunta', args={self.id})
        elif self.tipo_pregunta != "texto" and self.enunciado_pregunta != "":
            return reverse('delphi:listaOpciones', args={self.id})
        else:
            return reverse('delphi:preguntas', args={self.sesion.id})

    def __unicode__(self):
        return u'{0}'.format(self.enunciado_pregunta)

    def get_votos(self):
        return ",".join([str(self.votos_positivos.all().count() + self.votos_negativos.all().count())])

    def __str__(self):
        return self.enunciado_pregunta




class OpcionRespuesta(models.Model):
    texto_opcion = models.CharField(max_length=200)
    pregunta = models.ForeignKey(Pregunta, null=True, on_delete=models.CASCADE)
    valor_inicio = models.IntegerField(default=0)  ## dependerá del tipo de pregunta el tipo de este campo
    valor_final = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Opcion'
        verbose_name_plural = 'Opciones'
        unique_together = [('texto_opcion', 'pregunta', 'valor_inicio', 'valor_final')]

    def __str__(self):
        return u'{0}'.format(self.texto_opcion)

    def get_absolute_url(self):
        return reverse('delphi:preguntas', args={self.pregunta.id})


class RespuestasUsuarios(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    respuesta_texto = models.TextField(blank=True, null=True)
    respuesta_numerica = models.IntegerField(default=0)
    opciones_seleccionadas = models.ManyToManyField(OpcionRespuesta)
    fecha = models.DateTimeField(default=now)
    usuario = models.ForeignKey(User)

    class Meta:
        unique_together = (
            'pregunta',
            'usuario'
        )

    def get_opciones_seleccinadas(self):
        return ",".join([str(p) for p in self.opciones_seleccionadas.all()])


class RondasDelphi(models.Model):
    numero_ronda = models.IntegerField()
    delphi = models.ForeignKey('EstudioDelphi', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='ronda_delphi')
    cuestionario = models.ForeignKey('CuestionarioDelphi', verbose_name='Cuestionario')
    descripcion = models.TextField()
    abierto = models.BooleanField(default=True, help_text='Dice si se pueden votar o no las preguntas.')
    numero_preguntas = models.IntegerField(default=1)
    fecha_inicio = models.DateField(default=now)
    fecha_final = models.DateField(default=now)

    class Meta:
        verbose_name = 'Ronda'
        verbose_name_plural = 'Rondas'
        unique_together = ('numero_ronda', 'cuestionario')

    def __str__(self):
        return u'Ronda {0} del cuestionario{0}'.format(self.numero_ronda, self.cuestionario.nombre)

    def get_absolute_url(self):
        return reverse('delphi:rondas', args={self.cuestionario.id})


class Comment(models.Model):
    pregunta = models.ForeignKey('Pregunta', related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text
