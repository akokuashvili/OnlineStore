from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.account_type == 'SELLER' and
                request.user.seller.is_approved) or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user.seller or request.user.is_staff


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff


