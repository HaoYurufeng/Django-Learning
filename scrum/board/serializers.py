from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from datetime import date

from .models import Sprint, Task

User = get_user_model()

class SprintSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField()

    class Meta:
        model = Sprint
        fields = ('id', 'name', 'description', 'end', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        signer = TimestampSigner(settings.WATERCOOLER_SECRET)
        channel = signer.sign(obj.pk)
        return {
            'self': reverse('sprint-detail',
                            kwargs={'pk': obj.pk}, request=request),
            'tasks': reverse('task-list', request=request) + '?sprint={}'.format(obj.pk),
            'channel': '{proto}://{server}/{channel}'.format(
                proto='wss' if settings.WATERCOOLER_SECURE else 'ws',
                server=settings.WATERCOOLER_SERVER, channel=channel),
        }

    def validate_end(self, value):
        new = self.instance is None
        changed = self.instance and self.instance.end != value
        if (new or changed) and (value < date.today()):
            msg = _('End date cannot be in the past.')
            raise serializers.ValidationError(msg)
        return value

class TaskSerializer(serializers.ModelSerializer):

    assigned = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD, required=False, allow_null=True,
        queryset=User.objects.all()
    )
    status_display = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'sprint', 'status', 'status_display',
                  'order', 'assigned', 'started', 'due', 'completed', 'links',)

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('task-detail',
                            kwargs={'pk': obj.pk}, request=request),
            'sprint': None,
            'assigned': None,
        }
        if obj.sprint_id:
            links['sprint'] = reverse('sprint-detail',
                                      kwargs={'pk': obj.sprint_id}, request=request)

        """kwargs参数有误？现有的User为超级用户，当assigned选择为Admin时，
        可以通过数据库，但无法在浏览器页面查看，也无法查询？"""
        if obj.assigned:
            links['assigned'] = reverse('assigned-detail',
                                        kwargs={User.USERNAME_FIELD: obj.assigned}, request=request)
        return links

    def validate_sprint(self, value):
        """多个字段验证，确保sprint在任务完成前不被修改，且任务不会被分配给已完成的sprint."""
        '''value 指什么？'''
        if value.instance and self.instance.pk:
            if value != self.instance.sprint:
                if self.instance.status == Task.STATUS_DONE:
                    msg = _('Cannot change the sprint of a completed task.')
                    raise serializers.ValidationError(msg)
                if value and value.end < date.today():
                    msg = _('Cannot assign tasks to past sprints.')
                    raise serializers.ValidationError(msg)
        else:
            if value and value.end < date.today():
                msg = _('Cannot add tasks to past sprints.')
                raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        sprint = attrs.get('sprint')
        status = attrs.get('status', Task.STATUS_TODO)
        started = attrs.get('started')
        completed = attrs.get('completed')
        """验证任务状态和相应时间设置是否符合"""
        if not sprint and status != Task.STATUS_TODO:
            msg = _('Backlog tasks must have "Not Started" status.')
            raise serializers.ValidationError(msg)
        if started and status == Task.STATUS_TODO:
            msg = _('Started date cannot be set for not started task.')
            raise serializers.ValidationError(msg)
        if completed and status != Task.STATUS_DONE:
            msg = _('Completed date cannot be set for uncompleted task.')
            raise serializers.ValidationError(msg)
        return attrs

class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    links = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', User.USERNAME_FIELD, 'full_name', 'is_active', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        username = obj.get_username()
        return {
            'self': reverse('user-detail',
                            kwargs={User.USERNAME_FIELD: username}, request=request),
            'task': '{}?assigned={}'.format(
                reverse('task-list', request=request), username)
        }
