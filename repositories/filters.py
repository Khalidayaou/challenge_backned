import django_filters

from repositories.models import RepositoryFile


class RepositoryFileFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    language = django_filters.CharFilter(lookup_expr="iexact")
    file_type = django_filters.CharFilter(lookup_expr="iexact")
    type = django_filters.CharFilter(field_name="file_type", lookup_expr="iexact")

    class Meta:
        model = RepositoryFile
        fields = ["name", "language", "file_type", "type", "repository"]
