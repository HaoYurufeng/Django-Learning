from django.shortcuts import render
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

class SprintViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and creating sprints."""

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer

    filter_class = SprintFilter

    """将search_fields添加到视图，允许指定列表中的字段。"""
    search_fields = ('name',)

    """将ordering_fields添加到视图，可以根据需要按某些列排序。"""
    ordering_fields = ('end', 'name',)

class TaskViewSet(DefaultsMixin, viewsets.ModelViewSet):
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
