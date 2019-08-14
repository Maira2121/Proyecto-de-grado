from django.contrib.auth.models import User
from django.db import models
from enum import IntEnum


# Create your models here.
from django.urls import reverse
from django.utils.timezone import now


class SesionVariables(models.Model):
    nombre = models.CharField(max_length=50)
    estudio = models.ForeignKey('EstudioMicmac', verbose_name='estudio_micmac')
    codigo = models.PositiveIntegerField()
    estado = models.BooleanField(default=True, help_text='Dice si se pueden votar o no.')
    fecha_inicio = models.DateField(default=now)
    fecha_final = models.DateField(default=now)
    class Meta:
        verbose_name = "Sesion de creacion de variables Micmac"
        verbose_name_plural = "Sesiones de creacion de variables"
        unique_together = ('codigo', 'estudio')
        ordering = ('estudio', 'codigo',)
    def __str__(self):
        return u'Sesion {0} del cuestionario{0}'.format(self.codigo, self.estudio.titulo)
    def get_absolute_url(self):
        return reverse('micmac:detalle_estudio', args={self.estudio.id})



class EstudioMicmac(models.Model):

    proyecto = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    objetivos = models.TextField()
    moderador = models.ForeignKey(User, verbose_name='moderador', related_name='micmac_moderador')
    coordinadores = models.ManyToManyField(User, verbose_name='coordinadores', related_name='micmac_coordinadores')
    expertos = models.ManyToManyField(User, verbose_name='expertos', related_name='micmac_expertos')
    fecha_inicio = models.DateField(default=now)
    fecha_final = models.DateField(default=now)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Estudios Micmac'
        verbose_name = 'Estudio Micmac'

    def get_coordinadores(self):
        return ",".join([str(p) for p in self.coordinadores.all()])

    def get_expertos(self):
        return ",".join([str(p) for p in self.expertos.all()])

    def __str__(self):
        return self.titulo


class Valor(IntEnum):
    NULA = 0
    DEBIL = 1
    MODERADA = 2
    FUERTE = 3
    POTENCIAL = 4

    @classmethod
    def choice(cls):
        return tuple((val.name, val.value) for val in cls)



class Variable(models.Model):
    nombre = models.CharField(max_length=500)
    nombre_corto = models.CharField(max_length=10)
    descripcion = models.TextField()
    total_influencia = models.PositiveIntegerField(default=0)
    total_dependencia = models.PositiveIntegerField(default=0)
    relacion = models.ManyToManyField('self', through='Relacion', symmetrical=False)
    autor = models.ForeignKey(User, verbose_name='autor', related_name='autor_variable')
    estudio = models.ForeignKey('EstudioMicmac')
    votos_positivos = models.ManyToManyField(User, verbose_name='votante_positivo',
                                           related_name='votante_positivo_variable', default=None)
    votos_negativos = models.ManyToManyField(User, verbose_name='votante_negativo',
                                           related_name='votante_negativo_variable', default=None)

    def get_votos_positivos(self):
        return ",".join([str(p) for p in self.votos_positivos.all()])

    def get_votos_negativos(self):
        return ",".join([str(p) for p in self.votos_negativos.all()])

    class Meta:
        verbose_name = 'Variable'
        verbose_name_plural = 'Variables'

    def get_absolute_url(self):
        return reverse('micmac:lista_variables', args={self.estudio.id})

    def __unicode__(self):
        return u'{0}'.format(self.nombre)

    def __str__(self):
        return self.nombre_corto


class Relacion(models.Model):
    VALORACION = (
        (0, 'NULA'),
        (1, 'DÉBIL'),
        (2, 'MODERADA'),
        (3, 'FUERTE'),
        (4, 'POTENCIAL')
    )
    valoracion = models.IntegerField(choices=VALORACION)
    descripcion = models.TextField(default='')
    de_variable = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='de_variable')
    a_variable = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='a_variable')

    class Meta:
        unique_together = ('de_variable', 'a_variable',)

    def __str__(self):
        return 'Relacion entre {self.de_variable} y {self.a_variable}'



'''
class Influencia(models.Model):
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='lista_variable_influencia')
    valor_influencia = models.IntegerField()


class Dependencia(models.Model):
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='lista_variable_dependencia')
    valor_dependencia = models.IntegerField()
'''