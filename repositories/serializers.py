from rest_framework import serializers

from repositories.models import Repository, RepositoryFile
from repositories.services import assess_file


class RepositoryFileSerializer(serializers.ModelSerializer):
    is_critical = serializers.SerializerMethodField()
    critical_reasons = serializers.SerializerMethodField()

    class Meta:
        model = RepositoryFile
        fields = [
            "id",
            "repository",
            "name",
            "path",
            "file_type",
            "language",
            "size_bytes",
            "description",
            "added_at",
            "is_critical",
            "critical_reasons",
        ]
        read_only_fields = ["id", "added_at", "is_critical", "critical_reasons"]

    def _assessment(self, obj):
        cached = getattr(obj, "_critical_assessment", None)
        if cached is None:
            cached = assess_file(obj)
            obj._critical_assessment = cached
        return cached

    def get_is_critical(self, obj):
        return self._assessment(obj)["is_critical"]

    def get_critical_reasons(self, obj):
        return self._assessment(obj)["critical_reasons"]


class NestedRepositoryFileSerializer(RepositoryFileSerializer):
    class Meta(RepositoryFileSerializer.Meta):
        extra_kwargs = {"repository": {"read_only": True}}


class RepositorySerializer(serializers.ModelSerializer):
    files_count = serializers.IntegerField(read_only=True)
    critical_files_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Repository
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "created_at",
            "updated_at",
            "files_count",
            "critical_files_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RepositoryDetailSerializer(RepositorySerializer):
    files = RepositoryFileSerializer(many=True, read_only=True)

    class Meta(RepositorySerializer.Meta):
        fields = RepositorySerializer.Meta.fields + ["files"]
