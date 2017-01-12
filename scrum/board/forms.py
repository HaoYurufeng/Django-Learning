import django_filters
from django.contrib.auth import get_user_model
from .models import Task, Sprint

User = get_user_model()

class NullFilter(django_filters.BooleanFilter):
    """筛选未设置为空或非空的字段"""

    def filter(self, qs, value):
        if value is not None:
            return qs.filter(**{'%__isnull' % self.name: value})
        return qs

class TaskFilter(django_filters.FilterSet):
    """基于模型定义创建过滤器"""

    backlog = NullFilter(name='sprint')

    class Meta:
        model = Task
        fields = ('sprint', 'status', 'assigned', 'backlog',)

    """更新assigned字段，使用User.USERNAME——FIELD而不是默认的pk作为字段引用"""
    """那views.py文件中的这一参数是不是问题就在这？
        if obj.assigned:
            links['assigned'] = reverse('assigned-detail',
                                        kwargs={User.USERNAME_FIELD: obj.assigned}, request=request)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['assigned'].extra.update(
            {'to_field_name': User.USERNAME_FIELD}
        )

class SprintFilter(django_filters.FilterSet):
    end_min = django_filters.DateFilter(name='end', lookup_type='gte')
    end_max = django_filters.DateFilter(name='end', lookup_type='gte')

    class Meta:
        model = Sprint
        fields = ('end_min', 'end_max', )
