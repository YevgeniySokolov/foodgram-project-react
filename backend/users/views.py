from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404

from users.models import User, Subscription
from .serializers import SubscriptionSerializer, WriteSubscriptionSerializer
from api.paginations import LimitPageNumberPagination


class FoodgramUserViewSet(UserViewSet):
    """ViewSet пользователя."""

    @action(
        ("GET", "PUT", "PATCH", "DELETE", ), detail=False,
        permission_classes=(IsAuthenticated, ),
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)

    @action(
        detail=True, permission_classes=(IsAuthenticated, ),
        methods=('POST', ), pagination_class=None,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        serializer = WriteSubscriptionSerializer(
            data={'subscriber': request.user.pk, 'author': author.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(
            subscriber=request.user, author=author
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, methods=('GET', ),
        pagination_class=LimitPageNumberPagination,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(authors__subscriber=self.request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
