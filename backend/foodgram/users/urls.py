from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
#    UserRegistrationAPIView,
#    UserVerificationAPIView,
#    GetProfileViewSet,
    SubscriptionsViewSet,
    SubscriptionViewSet,
    CustomUserViewSet
)

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register(
    'users/subscriptions/', SubscriptionsViewSet,
    basename='subscriptions'
)
router_v1.register(
    r'users/(?P<author_pk>\d+)/subscribe', SubscriptionViewSet,
    basename='subscription'
)
router_v1.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path(
        'auth/',
        include('djoser.urls.authtoken')
    ),
    path('', include(router_v1.urls)),
]
