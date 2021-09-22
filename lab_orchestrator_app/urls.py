from rest_framework.routers import DefaultRouter

from .views import LabInstanceViewSet, DockerImageViewSet, LabViewSet

app_name = 'lab_orchestrator_app'

router = DefaultRouter()
router.register('docker_images', DockerImageViewSet, basename='docker_image')
router.register('labs', LabViewSet, basename='lab')
router.register('lab_instances', LabInstanceViewSet, basename='lab_instance')

urlpatterns = router.urls
