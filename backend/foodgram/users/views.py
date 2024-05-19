from djoser.conf import settings

from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Value, BooleanField
from djoser.views import UserViewSet

from users.models import User, Subscription
from foodgram.constants import PROHIBITED_USERNAME, SET_PASSWORD
from .serializers import (
    SubscriptionsSerializer,
    SubscriptionSerializer,
)
from api.paginations import LimitPageNumberPagination


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """ViewSet списка подписок."""

    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        return self.request.user.author.annotate(
            recipes_count=Sum('recipes'),
            is_subscribed=Value(True, output_field=BooleanField())
        ).all()


# class SubscriptionViewSet(viewsets.ModelViewSet):
#     """ViewSet подписки."""

#     serializer_class = SubscriptionSerializer
#     permission_classes = (IsAuthenticated,)
#     # filter_backends = (filters.SearchFilter,)

#     def get_author(self):
#         return get_object_or_404(User, pk=self.kwargs.get('author_pk'))

#     def get_queryset(self):
#         author = self.get_author()
#         return author.subscriber.annotate(
#             recipes_count=Sum('recipes')
#         ).all()

#     def perform_create(self, serializer):
#         author = self.get_author().annotate(
#             is_subscribed=Value(True, output_field=BooleanField())
#         )
#         serializer.save(subscriber=self.request.user, author=author)


class CustomUserViewSet(UserViewSet):
    """ViewSet пользователя."""

    queryset = User.objects.all()
    # http_method_names = ['get', 'post', 'patch', 'delete']
    # permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = LimitOffsetPagination
    # lookup_field = 'username'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

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
        # queryset = User.objects.filter(authors__user=self.request.user)
        queryset = self.request.user.authors.all()
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
