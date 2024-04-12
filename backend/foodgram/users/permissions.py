from rest_framework import permissions

from foodgram.constants import MESSAGE_NO_PERMISSION


class IsAdmin(permissions.BasePermission):

    MESSAGE_NO_PERMISSION

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin
        )
