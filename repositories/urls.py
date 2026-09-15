from rest_framework.routers import DefaultRouter

from repositories.views import FileViewSet, RepositoryViewSet

router = DefaultRouter()
router.register(r"repositories", RepositoryViewSet, basename="repository")
router.register(r"files", FileViewSet, basename="file")

urlpatterns = router.urls
