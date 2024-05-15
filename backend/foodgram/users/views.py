from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, UpdateAPIView
# from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Value, BooleanField
from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer
from rest_framework.authtoken import views
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema

from users.models import User
from users.utils import send_confirmation_code

from foodgram.constants import PROHIBITED_USERNAME, SET_PASSWORD
from .permissions import IsAdmin
from .serializers import (
#    UserSerializer,
    SubscriptionsSerializer,
    SubscriptionSerializer,
#    SetPasswordSerializer
#    GetProfileSerializer
)


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


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet подписки."""

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)

    def get_author(self):
        return get_object_or_404(User, pk=self.kwargs.get('author_pk'))

    def get_queryset(self):
        author = self.get_author()
        return author.subscriber.annotate(
            recipes_count=Sum('recipes')
        ).all()

    def perform_create(self, serializer):
        author = self.get_author().annotate(
            is_subscribed=Value(True, output_field=BooleanField())
        )
        serializer.save(subscriber=self.request.user, author=author)


# class UserVerificationAPIView(GenericAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = UserVerificationSerializer
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.data['username']
#         confirmation_code = serializer.data['confirmation_code']
#         user = get_object_or_404(User, username=username)
#         if user.confirmation_code == confirmation_code:
#             user.save()
#             return Response(
#                 f'Token: {str(AccessToken.for_user(user))}',
#                 status=status.HTTP_200_OK
#             )
#         return Response(status=status.HTTP_400_BAD_REQUEST)


# class GetProfileViewSet(viewsets.ModelViewSet):

#    queryset = User.objects.all()
#    serializer_class = GetProfileSerializer
#    permission_classes = (AllowAny,)


class CustomUserViewSet(UserViewSet):
    """ViewSet пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    # http_method_names = ['get', 'post', 'patch', 'delete']
    # permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = LimitOffsetPagination
    # lookup_field = 'username'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    @action(
        ["get", "put", "patch", "delete"], detail=False,
        permission_classes=(IsAuthenticated, )
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

    # def get_object(self, queryset=None):
    #     return self.request.user

#    @action(
#        detail=False, permission_classes=(IsAuthenticated, ),
#        methods=['get', 'patch', ], url_path=PROHIBITED_USERNAME,
#    )
#    def me_user_view(self, request):
#        serializer = MeUserSerializer(
#            request.user, data=request.data, partial=True
#        )
#        serializer.is_valid(raise_exception=True)
#        if request.method == 'get':
#            return Response(serializer.data, status=status.HTTP_200_OK)
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_200_OK)

#    @action(
#        detail=True,
#        permission_classes=(IsAuthenticated, ),
#        methods=['post'],
#        url_path=SET_PASSWORD
#    )
#    def set_password(self, request, pk=None):
#        user = self.get_object()
#        serializer = SetPasswordSerializer(data=request.data)
#        if serializer.is_valid():
#            if not user.check_password(
#                serializer.data.get("current_password")
#            ):
#                return Response(
#                    {"current_password": ["Wrong password."]},
#                    status=status.HTTP_400_BAD_REQUEST
#                )
#            user.set_password(serializer.validated_data['new_password'])
#            user.save()
#            return Response(status=status.HTTP_204_NO_CONTENT)
#        else:
#            return Response(serializer.errors,
#                            status=status.HTTP_400_BAD_REQUEST)
