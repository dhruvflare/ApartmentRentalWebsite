# permissions.py - Custom Permissions for Django REST Framework

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # All permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsInquirerOrOwner(permissions.BasePermission):
    """
    Custom permission for inquiries - allow inquirer to view their own inquiries
    and property owners to view inquiries for their properties.
    """

    def has_object_permission(self, request, view, obj):
        # Allow inquirer to see their own inquiries
        if hasattr(obj, 'inquirer') and obj.inquirer == request.user:
            return True

        # Allow property owner to see inquiries for their properties
        if hasattr(obj, 'property') and obj.property.owner == request.user:
            return True

        return False


class IsReviewerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for reviews - allow reviewers to edit their own reviews
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the reviewer
        return obj.reviewer == request.user