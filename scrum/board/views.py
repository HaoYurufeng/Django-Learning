import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets, authentication, permissions, filters
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer, UserSerializer
from .forms import TaskFilter, SprintFilter

# Create your views here.

User = get_user_model()

class DefaultsMixin(object):
    """Default settings for view authentication, permission, filtering and pagination."""
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )

    permissions_classes = (
        permissions.IsAuthenticated,
    )

    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

class UpdateHookMixin(object):
    """Mixin class to send update information to the websocket server."""
    def _build_hook_url(self, obj):
        if isinstance(obj, User):
            model = 'user'
        else:
            model = obj.__class__.__name__.lower()
        return '{}://{}/{}/{}'.format(
            'https' if settings.WATERCOOLER_SECURE else 'http',
            settings.WATERCOOLER_SERVER, model, obj.pk)

    def _send_hook_request(self, obj, method):
        url = self._build_hook_url(obj)
        try:
            response = requests.request(method, url, timeout=0.5)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            # Host could not be resolved or the connection was refused
            pass
        except requests.exceptions.Timeout:
            # Request timed out
            pass
        except requests.exceptions.RequestException:
            # Sever responsed with 4XX or 5XX status code
            pass

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._send_hook_request(serializer.instance, 'POST')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._send_hook_request(serializer.instance, 'PUT')

    def perform_destory(self, instance):
        self._send_hook_request(instance, 'DELETE')
        super().perform_destory(instance)

class SprintViewSet(DefaultsMixin, UpdateHookMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating sprints."""

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer

    filter_class = SprintFilter

    """将search_fields添加到视图，允许指定列表中的字段。"""
    search_fields = ('name',)

    """将ordering_fields添加到视图，可以根据需要按某些列排序。"""
    ordering_fields = ('end', 'name',)

class TaskViewSet(DefaultsMixin, UpdateHookMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating tasks."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    """引用一个过滤器，分配给视图中的filter_class, 对视图和过滤器建立连接"""
    filter_class = TaskFilter

    search_fields = ('name', 'description',)
    ordering_fields = ('name', 'order', 'started', 'due', 'completed',)

class UserViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint for listing users."""
    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = (User.USERNAME_FIELD,)
