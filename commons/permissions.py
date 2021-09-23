import rules as rules
from rest_framework.permissions import BasePermission, SAFE_METHODS


@rules.predicate
def is_false(_request):
    return False


@rules.predicate
def is_true(_request):
    return True


class RuleBasedPermission(BasePermission):
    safe_rules = []
    post_rules = []
    change_rules = []
    delete_rules = []

    @staticmethod
    def _merge_rules(all_rules):
        if len(all_rules) == 0:
            return is_false
        rule = None
        for part in all_rules:
            if rule is None:
                rule = part
            else:
                rule |= part
        return rule

    def has_permission(self, request, view):
        if is_post_method(request):
            rule = RuleBasedPermission._merge_rules(self.post_rules)
            return rule(request)
        return True

    def has_object_permission(self, request, view, obj):
        safe_rule = RuleBasedPermission._merge_rules(self.safe_rules) & is_safe_method
        change_rule = RuleBasedPermission._merge_rules(self.change_rules) & is_change_method
        delete_rule = RuleBasedPermission._merge_rules(self.delete_rules) & is_delete_method
        rule = safe_rule | delete_rule | change_rule
        return rule(request, obj)


@rules.predicate
def is_authenticated(request):
    return bool(request and request.is_authenticated)


@rules.predicate
def is_post_method(request):
    return bool(request.method == 'POST')


@rules.predicate
def is_put_method(request):
    return bool(request.method == 'PUT')


@rules.predicate
def is_patch_method(request):
    return bool(request.method == 'PATCH')


@rules.predicate
def is_change_method(request):
    return bool(request.method == 'PUT' or request.method == 'PATCH')


@rules.predicate
def is_delete_method(request):
    return bool(request.method == 'DELETE')


@rules.predicate
def is_safe_method(request):
    return request.method in SAFE_METHODS


@rules.predicate
def is_admin(request):
    return bool(request.user and request.user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as an admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or (request.user and request.user.is_staff))