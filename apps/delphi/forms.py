# coding: utf-8
from django.contrib.auth.models import User
from django.forms import RadioSelect
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple

from apps.delphi.models import *
from django import forms


class DelphiForm(forms.ModelForm):
    def clean_titulo(self):
        mensaje = self.cleaned_data["titulo"]
        return mensaje

    class Meta:
        model = EstudioDelphi
        fields = (
            'proyecto',
            'titulo',
            'descripcion',
            'objetivos',
            'moderador',
            'coordinadores',
            'participantes',
            'fecha_inicio',
            'fecha_final',
            'estado',

        )

        widgets = {
            'proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': '3',
                                                 'placeholder': 'Ingrese aquí una descripción del estudio'}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': '3',
                                               'placeholder': 'Ingresar los objetivos iniciales del estudio'}),
            'coordinadores': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'participantes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),
            'abierto': forms.CheckboxInput(),

        }


class CuestionarioForm(forms.ModelForm):
    class Meta:
        model = CuestionarioDelphi
        fields = ('nombre', 'estado', 'fecha_inicio', 'fecha_final',)

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),
        }


class SesionCuestionarioForm(forms.ModelForm):
    class Meta:
        model = SesionCuestionario
        fields = ('permitir_preguntas', 'nombre', 'estado', 'fecha_inicio', 'fecha_final',)

        widgets = {
            'permitir_preguntas': forms.CheckboxInput(),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),
        }
class EditarSesionForm(forms.ModelForm):
    class Meta:
        model = SesionCuestionario
        fields = ('permitir_preguntas', 'nombre', 'estado', 'fecha_inicio', 'fecha_final',)

        widgets = {
            'permitir_preguntas': forms.CheckboxInput(),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),
        }


class EditarCuestionarioForm(forms.ModelForm):
    class Meta:
        model = CuestionarioDelphi
        fields = ('nombre', 'estado', 'fecha_inicio', 'fecha_final',)

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),
        }

class RondasForm(forms.ModelForm):
    class Meta:
        model = RondasDelphi
        fields = (
            'descripcion',
            'fecha_inicio',
            'fecha_final',
            'abierto',

        )
        widgets = {
            'abierto': forms.CheckboxInput(),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control'}),
            'fecha_final': forms.DateInput(attrs={'class': 'form-control'}),

        }


class FormPregunta(forms.ModelForm):
    class Meta:
        model = Pregunta

        fields = (
            'tipo_pregunta',
            'sesion',
            'autor',
            'de_control',
        )

        widgets = {
            'tipo_pregunta': forms.Select(attrs={'class': 'form-control select2'}),
            'de_control': forms.CheckboxInput(),

        }


class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta

        fields = (
            'enunciado_pregunta',

        )

        widgets = {
            'enunciado_pregunta': forms.TextInput(attrs={'class': 'form-control'}),

        }


class FormEditarPregunta(forms.ModelForm):
    class Meta:
        model = Pregunta

        fields = (
            'tipo_pregunta',
            'enunciado_pregunta',
            'de_control',
            'autor',
        )

        widgets = {
            'tipo_pregunta': forms.Select(attrs={'class': 'form-control select2'}),
            'enunciado_pregunta': forms.TextInput(attrs={'class': 'form-control'}),
            'de_control': forms.CheckboxInput(),
            'autor': forms.TextInput(attrs={'class': 'form-conol'}),

        }


class FormRespuestaNumerica(forms.ModelForm):
    class Meta:
        model = RespuestasUsuarios

        fields = (
            'pregunta',
            'respuesta_numerica',
        )

        widgets = {
            'pregunta': forms.CharField(max_length=100),
            'respuesta_numerica': forms.IntegerField(),

        }


class Form_crear_opciones(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ('texto_opcion', 'pregunta')

        widgets = {
            'texto_opcion': forms.TextInput(attrs={'class': 'form-control'}),
            'pregunta': forms.Select(attrs={'class': 'form-control'}),
        }


class Form_opcion_escala_Likert(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ('texto_opcion', 'pregunta', 'valor_inicio')
        widgets = {
            'texto_opcion': forms.TextInput(attrs={'class': 'form-control'}),
            'pregunta': forms.Select(attrs={'class': 'form-control'}),
            'valor_inicio': forms.Select(attrs={'class': 'form-control'}),
        }


class Form_opcion_escala_numerica(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ('texto_opcion', 'pregunta', 'valor_inicio', 'valor_final',)

        widgets = {
            'texto_opcion': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_inicio': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_final': forms.TextInput(attrs={'class': 'form-control'}),
            'pregunta': forms.Select(attrs={'class': 'form-control'}),
        }


class Form_agregar_particioante(forms.ModelForm):
    class Meta:
        model = EstudioDelphi
        fields = ('participantes',)

        widgets = {
            'participantes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }


class RespuestaRadioFieldRenderer(RadioSelect):
    choice_input_class = RadioSelect
    outer_html = '<ul class="task" {id_attr}>{content}</ul>'
    inner_html = '<li>{opcion_value}{sub_widgets}</li>'


class RespuestaOrdenable(CheckboxSelectMultiple):

    outer_html = '<ul class="q_sortable ui-sortable" {id_attr}>{content}</ul>'
    inner_html = '<li class = ui-sortable-handle ui-accordion>{opcion_value}{sub_widgets}</li>'


class RespuestaRadioSelect(RadioSelect):
    renderer = RespuestaRadioFieldRenderer
    _empty_value = ''

class RespuestaNumericaRenderer(RadioSelect):
    choice_input_class = RadioSelect
    outer_html = '<ul class="task" {id_attr}>{content}</ul>'
    inner_html = '<li>{opcion_value}{sub_widgets}</li>'


class RespuestaNumerica():
    renderer = RespuestaRadioFieldRenderer

class ResponderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        pregunta = kwargs.pop('pregunta', None)
        super(ResponderForm, self).__init__(*args, **kwargs)
        if pregunta:
            field = u'pregunta_{0}'.format(pregunta.id)
            if pregunta.tipo_pregunta == 'unica':
                self.fields[field] = forms.ModelChoiceField(
                    label='',
                    queryset=OpcionRespuesta.objects.filter(pregunta=pregunta),
                    widget=RespuestaRadioSelect(),
                    required=True
                )
            elif pregunta.tipo_pregunta == 'multi':
                self.fields[field] = forms.ModelMultipleChoiceField(
                    label='',
                    queryset=OpcionRespuesta.objects.filter(pregunta=pregunta),
                    widget=CheckboxSelectMultiple(),
                    required=True
                )
            elif pregunta.tipo_pregunta == 'texto':
                self.fields[field] = forms.CharField(
                    label='',
                    widget=forms.Textarea(attrs={'rows': '3'}),
                    required=True
                )
            elif pregunta.tipo_pregunta == 'escala':
                self.fields[field] = forms.ModelChoiceField(
                    label='',
                    queryset=OpcionRespuesta.objects.filter(pregunta=pregunta),
                    widget=RespuestaRadioSelect(),
                    required=True
                )
            elif pregunta.tipo_pregunta == 'ranking':
                self.fields[field] = forms.ModelChoiceField(
                    label='',
                    queryset=OpcionRespuesta.objects.filter(pregunta=pregunta),
                    widget=RespuestaOrdenable(),
                    required=True
                )

        else:
            print('passed')


