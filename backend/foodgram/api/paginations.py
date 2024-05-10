from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class LimitPageNumberPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    page_size_query_param = 'limit'
