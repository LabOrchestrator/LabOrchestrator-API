from rest_framework import viewsets

from commons.permissions import IsAdminOrReadOnly

from instructions.models import InstructionPageModel
from instructions.serializers import InstructionPageModelSerializer


class InstructionPageViewSet(viewsets.ModelViewSet):
    """Example ViewSet for instruction pages.

    Only admins can edit and add instruction pages. Everyone (even not authenticated users) can use the list and
    retrieve methods.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = InstructionPageModel.objects.all()
    serializer_class = InstructionPageModelSerializer
    filterset_fields = {
        'lab_id': ['exact'],
    }
    search_fields = ['title', 'content']
