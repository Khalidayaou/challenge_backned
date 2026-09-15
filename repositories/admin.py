from django.contrib import admin

from repositories.models import Repository, RepositoryFile


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner")


@admin.register(RepositoryFile)
class RepositoryFileAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "file_type", "language", "size_bytes", "repository")
    list_filter = ("file_type", "language")
    search_fields = ("name", "path")
