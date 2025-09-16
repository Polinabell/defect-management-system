"""
Сериализаторы для отчётов и аналитики
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ReportTemplate, GeneratedReport, Dashboard, AnalyticsQuery
from apps.projects.models import Project

User = get_user_model()


class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    Сериализатор шаблона отчёта
    """
    report_type_display = serializers.ReadOnlyField(source='get_report_type_display')
    output_format_display = serializers.ReadOnlyField(source='get_output_format_display')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    reports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'report_type_display',
            'output_format', 'output_format_display', 'filter_config',
            'display_config', 'is_public', 'is_active', 'created_by',
            'created_by_name', 'reports_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_reports_count(self, obj):
        """Количество сгенерированных отчётов по этому шаблону"""
        return obj.generated_reports.count()
    
    def create(self, validated_data):
        """Создание шаблона отчёта"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class GeneratedReportSerializer(serializers.ModelSerializer):
    """
    Сериализатор сгенерированного отчёта
    """
    template_name = serializers.ReadOnlyField(source='template.name')
    template_type = serializers.ReadOnlyField(source='template.report_type')
    project_name = serializers.ReadOnlyField(source='project.name')
    generated_by_name = serializers.ReadOnlyField(source='generated_by.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    is_expired = serializers.ReadOnlyField()
    formatted_file_size = serializers.ReadOnlyField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'template', 'template_name', 'template_type', 'name',
            'description', 'project', 'project_name', 'date_from', 'date_to',
            'filter_params', 'status', 'status_display', 'file', 'file_url',
            'file_size', 'formatted_file_size', 'generated_by',
            'generated_by_name', 'generated_at', 'processing_time',
            'error_message', 'expires_at', 'is_expired', 'download_count',
            'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'file', 'file_size', 'generated_by',
            'generated_at', 'processing_time', 'error_message',
            'download_count', 'created_at'
        ]
    
    def get_file_url(self, obj):
        """Получает URL файла отчёта"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class GenerateReportSerializer(serializers.Serializer):
    """
    Сериализатор для генерации отчёта
    """
    template = serializers.PrimaryKeyRelatedField(
        queryset=ReportTemplate.objects.filter(is_active=True)
    )
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False,
        allow_null=True
    )
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    filter_params = serializers.JSONField(required=False, default=dict)
    
    def validate(self, attrs):
        """Валидация параметров генерации"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "Дата начала не может быть позже даты окончания"
            )
        
        return attrs


class DashboardSerializer(serializers.ModelSerializer):
    """
    Сериализатор дашборда
    """
    dashboard_type_display = serializers.ReadOnlyField(source='get_dashboard_type_display')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'dashboard_type',
            'dashboard_type_display', 'widgets_config', 'is_default',
            'is_public', 'allowed_roles', 'created_by', 'created_by_name',
            'can_edit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_can_edit(self, obj):
        """Проверка возможности редактирования дашборда"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Создатель может редактировать
        if obj.created_by == user:
            return True
        
        # Администратор может редактировать
        if user.is_admin:
            return True
        
        return False
    
    def create(self, validated_data):
        """Создание дашборда"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AnalyticsQuerySerializer(serializers.ModelSerializer):
    """
    Сериализатор аналитического запроса
    """
    query_type_display = serializers.ReadOnlyField(source='get_query_type_display')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsQuery
        fields = [
            'id', 'name', 'description', 'query_type', 'query_type_display',
            'sql_query', 'query_config', 'is_public', 'is_cached',
            'cache_duration', 'created_by', 'created_by_name', 'usage_count',
            'last_used_at', 'can_edit', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'usage_count', 'last_used_at',
            'created_at', 'updated_at'
        ]
    
    def get_can_edit(self, obj):
        """Проверка возможности редактирования запроса"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Создатель может редактировать
        if obj.created_by == user:
            return True
        
        # Администратор может редактировать
        if user.is_admin:
            return True
        
        return False
    
    def create(self, validated_data):
        """Создание запроса"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExecuteQuerySerializer(serializers.Serializer):
    """
    Сериализатор для выполнения аналитического запроса
    """
    query = serializers.PrimaryKeyRelatedField(
        queryset=AnalyticsQuery.objects.all()
    )
    parameters = serializers.JSONField(required=False, default=dict)
    
    def validate_query(self, value):
        """Валидация доступа к запросу"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Необходима аутентификация")
        
        user = request.user
        
        # Проверяем доступ к запросу
        if not value.is_public and value.created_by != user and not user.is_admin:
            raise serializers.ValidationError("Нет доступа к этому запросу")
        
        return value


class ProjectAnalyticsSerializer(serializers.Serializer):
    """
    Сериализатор аналитики по проекту
    """
    # Общая информация
    total_defects = serializers.IntegerField()
    defects_by_status = serializers.DictField()
    defects_by_priority = serializers.DictField()
    defects_by_category = serializers.DictField()
    
    # Временная аналитика
    defects_created_by_day = serializers.ListField()
    defects_closed_by_day = serializers.ListField()
    
    # Производительность
    average_resolution_time = serializers.FloatField()
    overdue_defects = serializers.IntegerField()
    defects_by_assignee = serializers.DictField()
    
    # Проектная информация
    project_progress = serializers.FloatField()
    stages_progress = serializers.ListField()
    
    # Качество
    defects_by_severity = serializers.DictField()
    reopened_defects = serializers.IntegerField()


class UserPerformanceSerializer(serializers.Serializer):
    """
    Сериализатор производительности пользователя
    """
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    
    # Дефекты
    defects_created = serializers.IntegerField()
    defects_assigned = serializers.IntegerField()
    defects_closed = serializers.IntegerField()
    
    # Время
    average_resolution_time = serializers.FloatField()
    overdue_defects = serializers.IntegerField()
    
    # Качество
    defects_reopened = serializers.IntegerField()
    quality_score = serializers.FloatField()
    
    # Активность
    comments_count = serializers.IntegerField()
    last_activity = serializers.DateTimeField()


class SystemAnalyticsSerializer(serializers.Serializer):
    """
    Сериализатор общей аналитики системы
    """
    # Общие показатели
    total_projects = serializers.IntegerField()
    total_defects = serializers.IntegerField()
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    
    # Статистика дефектов
    defects_by_status = serializers.DictField()
    defects_by_priority = serializers.DictField()
    defects_created_this_month = serializers.IntegerField()
    defects_closed_this_month = serializers.IntegerField()
    
    # Статистика проектов
    projects_by_status = serializers.DictField()
    overdue_projects = serializers.IntegerField()
    completed_projects_this_month = serializers.IntegerField()
    
    # Производительность
    average_resolution_time = serializers.FloatField()
    most_active_users = serializers.ListField()
    most_problematic_categories = serializers.ListField()
    
    # Тренды
    defects_trend = serializers.ListField()
    projects_trend = serializers.ListField()


class ExportDataSerializer(serializers.Serializer):
    """
    Сериализатор для экспорта данных
    """
    
    class DataType(serializers.ChoiceField):
        def __init__(self, **kwargs):
            choices = [
                ('defects', 'Дефекты'),
                ('projects', 'Проекты'),
                ('users', 'Пользователи'),
                ('comments', 'Комментарии'),
                ('files', 'Файлы'),
            ]
            super().__init__(choices=choices, **kwargs)
    
    class ExportFormat(serializers.ChoiceField):
        def __init__(self, **kwargs):
            choices = [
                ('csv', 'CSV'),
                ('excel', 'Excel'),
                ('json', 'JSON'),
            ]
            super().__init__(choices=choices, **kwargs)
    
    data_type = DataType()
    export_format = ExportFormat()
    filters = serializers.JSONField(required=False, default=dict)
    fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Список полей для экспорта"
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    
    def validate(self, attrs):
        """Валидация параметров экспорта"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "Дата начала не может быть позже даты окончания"
            )
        
        return attrs


class ChartDataSerializer(serializers.Serializer):
    """
    Сериализатор данных для графиков
    """
    
    class ChartType(serializers.ChoiceField):
        def __init__(self, **kwargs):
            choices = [
                ('line', 'Линейный график'),
                ('bar', 'Столбчатая диаграмма'),
                ('pie', 'Круговая диаграмма'),
                ('area', 'График с областями'),
                ('scatter', 'Точечная диаграмма'),
            ]
            super().__init__(choices=choices, **kwargs)
    
    chart_type = ChartType()
    title = serializers.CharField(max_length=200)
    data = serializers.JSONField()
    options = serializers.JSONField(required=False, default=dict)
    
    def validate_data(self, value):
        """Валидация данных графика"""
        if not isinstance(value, (list, dict)):
            raise serializers.ValidationError(
                "Данные должны быть списком или словарём"
            )
        
        return value
