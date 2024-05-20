from djoser.conf import settings

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.models import User, Subscription
from foodgram.constants import PROHIBITED_USERNAME, SET_PASSWORD
from .serializers import SubscriptionSerializer
from api.paginations import LimitPageNumberPagination


class CustomUserViewSet(UserViewSet):
    """ViewSet пользователя."""

    @action(
        ["get", "put", "patch", "delete"], detail=False,
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
       methods=['post', 'delete'], pagination_class=None,
    )
    def subscribe(self, request, id):
        if not User.objects.filter(pk=id).exists():
            return Response(
                {'error': f'Пользователь с ID:{id} не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        author = User.objects.get(pk=id)
        subscriber = request.user
        if request.method == 'POST':
            if subscriber == author:
                return Response(
                    {'error': 'Нельзя подписываться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                subscriber=subscriber, author=author
            ).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(subscriber=subscriber, author=author)
            serializer = SubscriptionSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                subscriber=subscriber, author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=('GET',),
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
