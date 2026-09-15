from django.db.models import Count, Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from repositories.filters import RepositoryFileFilter
from repositories.models import Repository, RepositoryFile
from repositories.serializers import (
    NestedRepositoryFileSerializer,
    RepositoryDetailSerializer,
    RepositoryFileSerializer,
    RepositorySerializer,
)
from repositories.services import is_critical


class RepositoryViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    filterset_fields = ["owner"]
    search_fields = ["name", "description", "owner"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        files = Prefetch("files", queryset=RepositoryFile.objects.all())
        return (
            Repository.objects.annotate(files_count=Count("files"))
            .prefetch_related(files)
            .order_by("name")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RepositoryDetailSerializer
        return RepositorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        items = page if page is not None else queryset
        payload = []
        for repository in items:
            data = RepositorySerializer(repository).data
            data["critical_files_count"] = sum(1 for f in repository.files.all() if is_critical(f))
            payload.append(data)
        if page is not None:
            return self.get_paginated_response(payload)
        return Response(payload)

    def retrieve(self, request, *args, **kwargs):
        repository = self.get_object()
        data = RepositoryDetailSerializer(repository).data
        data["files_count"] = repository.files.count()
        data["critical_files_count"] = sum(1 for f in repository.files.all() if is_critical(f))
        return Response(data)

    @action(detail=True, methods=["get", "post"], url_path="files")
    def files(self, request, pk=None):
        repository = self.get_object()
        if request.method == "POST":
            serializer = NestedRepositoryFileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(repository=repository)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        queryset = repository.files.all()
        serializer = NestedRepositoryFileSerializer(queryset, many=True)
        return Response(serializer.data)


class FileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RepositoryFile.objects.select_related("repository")
    serializer_class = RepositoryFileSerializer
    filterset_class = RepositoryFileFilter
    search_fields = ["name", "path", "language"]
    ordering_fields = ["name", "size_bytes", "added_at"]

    @action(detail=False, methods=["get"], url_path="critical")
    def critical(self, request):
        files = [f for f in self.filter_queryset(self.get_queryset()) if is_critical(f)]
        page = self.paginate_queryset(files)
        serializer = self.get_serializer(page if page is not None else files, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
