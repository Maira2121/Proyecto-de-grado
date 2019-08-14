from apps.micmac.models import Relacion
import django_filters


class RelacionFilter(django_filters.FilterSet):
    class Meta:
        model = Relacion
        fields = ['de_variable', 'a_variable', 'valoracion']