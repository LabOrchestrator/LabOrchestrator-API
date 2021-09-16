from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


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