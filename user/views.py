import rules
from rest_framework import viewsets, permissions

from commons.permissions import RuleBasedPermission, is_admin, is_true
from user.models import User
from user.serializers import UserSerializer


@rules.predicate
def is_user(request, obj):
    return bool(request.user == obj)


class UserPermission(RuleBasedPermission):
    message = "You don't have the correct permissions on this user."
    safe_rules = [is_admin, is_user]
    post_rules = [is_true]
    change_rules = [is_admin, is_user]
    delete_rules = [is_admin, is_user]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, UserPermission]
    filterset_fields = {
        'email': ['icontains'],
        'first_name': ['icontains'],
        'last_name': ['icontains'],
        'is_staff': ['exact'],
        'is_active': ['exact'],
        'is_superuser': ['exact'],
    }
    ordering_fields = ['id', 'email', 'first_name', 'last_name', 'date_joined']
    ordering = ['id']
    search_fields = ['email', 'first_name', 'last_name']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if is_admin(self.request):
            return queryset
        return queryset.filter(id=self.request.user.id)
