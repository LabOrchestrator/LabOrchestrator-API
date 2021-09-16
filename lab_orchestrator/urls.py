from django.contrib import admin
from django.views.generic import TemplateView
from django.conf.urls import url
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.schemas import get_schema_view
import lab_orchestrator


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'docker_image': reverse('lab_orchestrator:docker_image-list', request=request, format=format),
        'lab': reverse('lab_orchestrator:lab-list', request=request, format=format),
        'lab_instances': reverse('lab_orchestrator:lab_instance-list', request=request, format=format),
    })


@api_view(['GET'])
def root(request, format=None):
    return Response({
        'api': reverse('api_root', request=request, format=format),
        'openapi-schema': reverse('openapi-schema', request=request, format=format),
        'swagger': reverse('swagger-ui', request=request, format=format),
    })


urlpatterns = [
    path('', root, name='root'),
    path('api/', api_root, name='api_root'),
    path('api/', include('lab_orchestrator_lib_django_adapter.urls')),
]

urlpatterns += [
    path('admin/', admin.site.urls),                    # contains the admin web-ui
    path('api-auth/', include('rest_framework.urls')),  # contains login and logout for the api web-ui
]

urlpatterns += [
    url(r'^openapi-schema/', get_schema_view(
        title="Lab Orchestrator API",
        version=lab_orchestrator.__version__,
        public=True,
    ), name='openapi-schema'),
    url(r'swagger/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]