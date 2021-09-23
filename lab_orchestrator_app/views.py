"""
This module contains some example view sets that shows how the lab_orchestrator_lib_django_adapter could be used in
a django project. When using this library you probably need to implement the view sets by yourself, but this can be
used as a template.
"""
from typing import Optional

from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from lab_orchestrator_lib.controller.controller_collection import ControllerCollection
from rest_framework.viewsets import GenericViewSet

from lab_orchestrator_lib.model.model import LabInstanceKubernetes
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response

from lab_orchestrator_lib_django_adapter.controller_collection import get_default_cc
from lab_orchestrator_lib_django_adapter.models import LabInstanceModel, LabModel, DockerImageModel, LabDockerImageModel
from lab_orchestrator_lib_django_adapter.serializers import LabInstanceModelSerializer, LabInstanceKubernetesSerializer, \
    LabModelSerializer, DockerImageModelSerializer
from lab_orchestrator_lib_auth.auth import LabInstanceTokenParams, generate_auth_token
from lab_orchestrator_lib.controller.controller import LabInstanceController

from commons.permissions import IsAdminOrReadOnly
from lab_orchestrator import settings
from lab_orchestrator_app.serializers import LabDockerImageModelSerializer


class DockerImageViewSet(viewsets.ModelViewSet):
    """Example ViewSet for docker images.

    Only admins can edit and add docker images. Everyone (even not authenticated users) can use the list and retrieve
    methods.

    This doesn't need to use the docker image controller, because the controller has no special implementation of the
    create or delete methods and it's save to manipulate the database objects directly without the controller.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = DockerImageModel.objects.all()
    serializer_class = DockerImageModelSerializer


class LabDockerImageViewSet(viewsets.ModelViewSet):
    """Example ViewSet for lab docker images.

    Only admins can edit and add lab docker images. Everyone (even not authenticated users) can use the list and
    retrieve methods.

    This doesn't need to use the lab docker image controller, because the controller has no special implementation of
    the create or delete methods and it's save to manipulate the database objects directly without the controller.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = LabDockerImageModel.objects.all()
    serializer_class = LabDockerImageModelSerializer


class LabViewSet(viewsets.ModelViewSet):
    """Example ViewSet for labs.

    Only admins can edit and add labs. Everyone (even not authenticated users) can use the list and retrieve
    methods.

    This doesn't need to use the lab controller, because the controller has no special implementation of the
    create or delete methods and it's save to manipulate the database objects directly without the controller.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = LabModel.objects.all()
    serializer_class = LabModelSerializer


class LabInstanceViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """Example ViewSet for lab instances.

    Contains list, retrieve, create and delete method. Can't be updated because lab instances are immutable. If you are
    an admin you can see all lab instances. If you are authenticated and no admin you can only see your lab instances.
    If you are not authenticated you can see nothing.

    When you create a lab instance you will get a jwt token that can be used to access the VNC of the VMs that are
    started for this lab instance.

    This class uses the lab instance controller to create and delete lab instances, because the lab instance controller
    will also create other resources for example a kubernetes namespace and virtual machines. So it's needed to use the
    controller here.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = LabInstanceModel.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cc: Optional[ControllerCollection] = None

    def get_cc(self):
        if self.cc is None:
            self.cc = get_default_cc()
        return self.cc

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # admins can see all lab instances
        if not bool(self.request.user and self.request.user.is_staff):
            # filter my lab instances
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            # contains a special serializer
            return LabInstanceKubernetesSerializer
        return LabInstanceModelSerializer

    def serialize_lab_instance_kubernetes(self, lab_instance_kubernetes: LabInstanceKubernetes):
        """Serializes a lab instance kubernetes object."""
        # get lab object for serialisation
        lab: LabModel = LabModel.objects.get(pk=lab_instance_kubernetes.lab_id)
        user = get_user_model().objects.get(pk=lab_instance_kubernetes.user_id)
        all_lab_docker_images = lab.lab_docker_images.all()
        lab_docker_images = []
        for lab_docker_image in all_lab_docker_images:
            lab_docker_images.append({
                'id': lab_docker_image.id,
                'docker_image_id': lab_docker_image.docker_image.id,
                'docker_image_name': lab_docker_image.docker_image_name,
            })
        allowed_vmis_query = ",".join([elm.docker_image_name for elm in all_lab_docker_images])
        lab_vnc_path = f"{settings.LAB_VNC_PROTOCOL}://{settings.LAB_VNC_HOST}:{settings.LAB_VNC_PORT}/" \
                       f"{settings.LAB_VNC_PATH}?host={settings.WS_PROXY_HOST}&port={settings.WS_PROXY_PORT}" \
                       f"&path={settings.WS_PROXY_PATH_PREFIX}/" \
                       f"{lab_instance_kubernetes.jwt_token}/{lab_docker_images[0]['docker_image_name']}" \
                       f"&allowed_vmis={allowed_vmis_query}" \
                       f"&autoconnect=1"
        data = {
            'id': lab_instance_kubernetes.primary_key,
            'lab': {
                'id': lab.pk,
                'name': lab.name,
                'docker_images': lab_docker_images,
            },
            'lab_id': lab_instance_kubernetes.lab_id,
            'user': {
                'id': user.id,
                'email': user.email,
            },
            'user_id': self.request.user.id,
            'jwt_token': lab_instance_kubernetes.jwt_token,
            'lab_vnc_path': lab_vnc_path
        }
        return data

    @action(detail=True)
    def token(self, request, pk=None):
        """Creates a new JWT token for this lab instance.

        :return: The same response like when you start a new lab.
        """
        lab_instance = self.get_object()
        user_id = request.user.id
        if user_id != lab_instance.user_id:
            raise Exception("You are allowed to access this lab instance")
        lab = LabModel.objects.get(pk=lab_instance.lab_id)
        namespace_name = LabInstanceController.gen_namespace_name(lab, user_id, lab_instance.id)
        all_lab_docker_images = lab.lab_docker_images.all()
        allowed_vmi_names = [elm.docker_image_name for elm in all_lab_docker_images]
        lab_instance_token_params = LabInstanceTokenParams(lab_instance.lab_id, lab_instance.id, namespace_name,
                                                           allowed_vmi_names)
        jwt_token = generate_auth_token(user_id, lab_instance_token_params, settings.SECRET_KEY)
        lab_instance_kubernetes = LabInstanceKubernetes(lab_instance.id, lab_instance.lab_id, user_id, jwt_token,
                                                        allowed_vmi_names)
        data = self.serialize_lab_instance_kubernetes(lab_instance_kubernetes)
        return Response(data)

    def create(self, request, *args, **kwargs):
        """Creates a lab instance.

        This method starts a lab, including all its resources in Kuberenetes (namespace, network policies,
        virtual machines) and a specific jwt token that can be used to access the VNC of the virtual machines.
        """
        # get the post data with serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_id = serializer.data['lab']
        lab = self.get_cc().lab_ctrl.get(lab_id)
        if lab is None:
            raise Exception("Invalid lab id")
        # start lab with lab instance controller
        lab_instance_kubernetes = self.get_cc().lab_instance_ctrl.create(lab_id, request.user.id)
        # get serialisation
        data = self.serialize_lab_instance_kubernetes(lab_instance_kubernetes)
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Deletes the lab instance.

        This method removes the lab instance and deletes all its resources in Kubernetes.
        """
        mod = self.get_object()
        # convert database object to library object
        obj = self.get_cc().lab_instance_ctrl.adapter.to_obj(mod)
        # delete the lab instance with the controller
        self.get_cc().lab_instance_ctrl.delete(obj)
        return Response(None, status.HTTP_204_NO_CONTENT)
