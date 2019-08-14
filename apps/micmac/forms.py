from django import forms
from apps.micmac.models import *


class MicmacForm(forms.ModelForm):

    def clean_titulo(self):
        mensaje = self.cleaned_data["titulo"]
        return mensaje

    class Meta:
        model = EstudioMicmac
        fields = (
            'proyecto',
            'titulo',
            'descripcion',
            'objetivos',
            'moderador',
            'coordinadores',
            'expertos',
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
            'expertos': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),
            'abierto': forms.CheckboxInput(),

        }

class VariableForm(forms.ModelForm):
    class Meta:
        model = Variable

        fields = ('nombre', 'nombre_corto', 'descripcion', 'estudio')

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_corto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': '3',
                                                 'placeholder': 'Ingrese aquí una descripción de la variable'}),
        }


class EditarVariableForm(forms.ModelForm):
    class Meta:
        model = Variable

        fields = ('nombre', 'nombre_corto', 'descripcion')

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_corto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': '3',
                                                 'placeholder': 'Ingrese aquí una descripción de la variable'}),
        }

class SesionVariablesForm(forms.ModelForm):
    class Meta:
        model = SesionVariables

        fields = ('codigo', 'estudio', 'nombre', 'estado', 'fecha_inicio', 'fecha_final',)

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(),
            'fecha_inicio': forms.DateInput(attrs={'class': 'datepiker'}),
            'fecha_final': forms.DateInput(attrs={'class': 'datepiker'}),


        }


class RelacionEditarForm(forms.ModelForm):
    class Meta:
        model = Relacion

        fields = ('de_variable',
                  'a_variable',
                  'valoracion',
                  'descripcion',
                  )

        widgets = {
            'de_variable': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'a_variable': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'valoracion': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }


class RelacionForm(forms.ModelForm):
    class Meta:
        model = Relacion

        fields = ('de_variable',
                  'a_variable',
                  'valoracion',
                  'descripcion',
                  )

        widgets = {
            'de_variable': forms.Select(attrs={'class': 'form-control', }),
            'a_variable': forms.Select(attrs={'class': 'form-control', }),
            'valoracion': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }
