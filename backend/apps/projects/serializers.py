"""
Сериализаторы для управления проектами
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectMember, ProjectStage, ProjectTemplate, ProjectStageTemplate

User = get_user_model()


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Сериализатор участника проекта
    """
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_role = serializers.ReadOnlyField(source='user.role')
    role_display = serializers.ReadOnlyField(source='get_role_display')
    
    class Meta:
        model = ProjectMember
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_role',
            'role', 'role_display', 'joined_at', 'is_active'
        ]
        read_only_fields = ['id', 'joined_at']


class ProjectStageSerializer(serializers.ModelSerializer):
    """
    Сериализатор этапа проекта
    """
    responsible_name = serializers.ReadOnlyField(source='responsible.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    duration_planned = serializers.ReadOnlyField()
    duration_actual = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectStage
        fields = [
            'id', 'name', 'description', 'order',
            'start_date', 'end_date', 'actual_start_date', 'actual_end_date',
            'responsible', 'responsible_name', 'status', 'status_display',
            'estimated_hours', 'actual_hours', 'completion_percentage',
            'duration_planned', 'duration_actual', 'is_overdue', 'days_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Валидация данных этапа"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        completion_percentage = attrs.get('completion_percentage', 0)
        
        # Проверяем даты
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Дата начала не может быть позже даты завершения"
            )
        
        # Проверяем процент выполнения
        if completion_percentage < 0 or completion_percentage > 100:
            raise serializers.ValidationError(
                "Процент выполнения должен быть от 0 до 100"
            )
        
        return attrs


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор для списка проектов
    """
    manager_name = serializers.ReadOnlyField(source='manager.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    priority_display = serializers.ReadOnlyField(source='get_priority_display')
    progress_percentage = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    defects_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'status', 'status_display',
            'priority', 'priority_display', 'manager', 'manager_name',
            'start_date', 'end_date', 'progress_percentage',
            'is_overdue', 'days_remaining', 'defects_count', 'members_count',
            'created_at'
        ]
    
    def get_defects_count(self, obj):
        """Количество дефектов в проекте"""
        return obj.defects.count()
    
    def get_members_count(self, obj):
        """Количество участников проекта"""
        return obj.members.filter(project_memberships__is_active=True).count()


class ProjectSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор проекта
    """
    manager_name = serializers.ReadOnlyField(source='manager.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    priority_display = serializers.ReadOnlyField(source='get_priority_display')
    building_type_display = serializers.ReadOnlyField(source='get_building_type_display')
    
    # Вычисляемые поля
    duration_planned = serializers.ReadOnlyField()
    duration_actual = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    # Связанные объекты
    members = ProjectMemberSerializer(source='project_members', many=True, read_only=True)
    stages = ProjectStageSerializer(many=True, read_only=True)
    
    # Статистика
    defects_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'description', 'address',
            'coordinates_lat', 'coordinates_lng',
            'customer', 'customer_contact', 'customer_phone', 'customer_email',
            'contract_number', 'contract_date', 'contract_amount',
            'manager', 'manager_name',
            'start_date', 'end_date', 'actual_start_date', 'actual_end_date',
            'status', 'status_display', 'priority', 'priority_display',
            'total_area', 'building_type', 'building_type_display', 'floors_count',
            'notify_on_defect_creation', 'notify_on_status_change',
            'duration_planned', 'duration_actual', 'progress_percentage',
            'is_overdue', 'days_remaining',
            'members', 'stages', 'defects_stats',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_defects_stats(self, obj):
        """Статистика дефектов по проекту"""
        return obj.get_defects_stats()
    
    def validate(self, attrs):
        """Валидация данных проекта"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        actual_start_date = attrs.get('actual_start_date')
        actual_end_date = attrs.get('actual_end_date')
        manager = attrs.get('manager')
        
        # Проверяем плановые даты
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Дата начала не может быть позже даты завершения"
            )
        
        # Проверяем фактические даты
        if actual_start_date and actual_end_date and actual_start_date > actual_end_date:
            raise serializers.ValidationError(
                "Фактическая дата начала не может быть позже даты завершения"
            )
        
        # Проверяем роль менеджера
        if manager and manager.role not in ['admin', 'manager']:
            raise serializers.ValidationError(
                "Менеджером проекта может быть только пользователь с ролью 'Менеджер' или 'Администратор'"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Создание проекта"""
        # Создаём проект
        project = super().create(validated_data)
        
        # Автоматически добавляем менеджера как участника
        project.add_member(project.manager, role='manager')
        
        return project


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания проекта
    """
    template = serializers.PrimaryKeyRelatedField(
        queryset=ProjectTemplate.objects.filter(is_active=True),
        write_only=True,
        required=False,
        help_text="Шаблон для создания этапов проекта"
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'address',
            'coordinates_lat', 'coordinates_lng',
            'customer', 'customer_contact', 'customer_phone', 'customer_email',
            'contract_number', 'contract_date', 'contract_amount',
            'manager', 'start_date', 'end_date',
            'priority', 'total_area', 'building_type', 'floors_count',
            'notify_on_defect_creation', 'notify_on_status_change',
            'template'
        ]
    
    def create(self, validated_data):
        """Создание проекта с возможностью использования шаблона"""
        template = validated_data.pop('template', None)
        
        # Создаём проект
        project = super().create(validated_data)
        
        # Добавляем менеджера как участника
        project.add_member(project.manager, role='manager')
        
        # Если указан шаблон, создаём этапы на его основе
        if template:
            self._create_stages_from_template(project, template)
        
        return project
    
    def _create_stages_from_template(self, project, template):
        """Создание этапов проекта на основе шаблона"""
        stage_templates = template.stage_templates.all().order_by('order')
        current_date = project.start_date
        
        for stage_template in stage_templates:
            stage_start = current_date
            stage_end = current_date + timezone.timedelta(days=stage_template.estimated_days)
            
            # Проверяем, что этап не выходит за рамки проекта
            if stage_end > project.end_date:
                stage_end = project.end_date
            
            ProjectStage.objects.create(
                project=project,
                name=stage_template.name,
                description=stage_template.description,
                order=stage_template.order,
                start_date=stage_start,
                end_date=stage_end,
                estimated_hours=stage_template.estimated_hours
            )
            
            current_date = stage_end + timezone.timedelta(days=1)
            
            # Если достигли конца проекта, прекращаем создание этапов
            if current_date >= project.end_date:
                break


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления проекта
    """
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'address',
            'coordinates_lat', 'coordinates_lng',
            'customer', 'customer_contact', 'customer_phone', 'customer_email',
            'contract_number', 'contract_date', 'contract_amount',
            'start_date', 'end_date', 'actual_start_date', 'actual_end_date',
            'status', 'priority', 'total_area', 'building_type', 'floors_count',
            'notify_on_defect_creation', 'notify_on_status_change'
        ]
    
    def validate(self, attrs):
        """Валидация обновления проекта"""
        # Те же валидации что и в основном сериализаторе
        start_date = attrs.get('start_date', self.instance.start_date)
        end_date = attrs.get('end_date', self.instance.end_date)
        actual_start_date = attrs.get('actual_start_date')
        actual_end_date = attrs.get('actual_end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Дата начала не может быть позже даты завершения"
            )
        
        if actual_start_date and actual_end_date and actual_start_date > actual_end_date:
            raise serializers.ValidationError(
                "Фактическая дата начала не может быть позже даты завершения"
            )
        
        return attrs


class AddProjectMemberSerializer(serializers.Serializer):
    """
    Сериализатор для добавления участника в проект
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
    role = serializers.ChoiceField(
        choices=ProjectMember.Role.choices,
        default=ProjectMember.Role.ENGINEER
    )
    
    def validate_user(self, value):
        """Проверяем, что пользователь ещё не участвует в проекте"""
        project = self.context['project']
        if project.is_member(value):
            raise serializers.ValidationError(
                "Пользователь уже является участником проекта"
            )
        return value


class ProjectTemplateSerializer(serializers.ModelSerializer):
    """
    Сериализатор шаблона проекта
    """
    building_type_display = serializers.ReadOnlyField(source='get_building_type_display')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    stage_templates = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectTemplate
        fields = [
            'id', 'name', 'description', 'building_type', 'building_type_display',
            'is_active', 'created_by', 'created_by_name', 'stage_templates',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_stage_templates(self, obj):
        """Получаем шаблоны этапов"""
        return ProjectStageTemplateSerializer(
            obj.stage_templates.all().order_by('order'),
            many=True
        ).data


class ProjectStageTemplateSerializer(serializers.ModelSerializer):
    """
    Сериализатор шаблона этапа проекта
    """
    class Meta:
        model = ProjectStageTemplate
        fields = [
            'id', 'name', 'description', 'order',
            'estimated_days', 'estimated_hours'
        ]
        read_only_fields = ['id']


class ProjectStatsSerializer(serializers.Serializer):
    """
    Сериализатор статистики проектов
    """
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    overdue_projects = serializers.IntegerField()
    projects_by_status = serializers.DictField()
    projects_by_priority = serializers.DictField()
    average_duration = serializers.FloatField()
    total_defects = serializers.IntegerField()


class ProjectSearchSerializer(serializers.Serializer):
    """
    Сериализатор для поиска проектов
    """
    query = serializers.CharField(max_length=200, required=False)
    status = serializers.MultipleChoiceField(
        choices=Project.Status.choices,
        required=False
    )
    priority = serializers.MultipleChoiceField(
        choices=Project.Priority.choices,
        required=False
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['admin', 'manager']),
        required=False
    )
    building_type = serializers.ChoiceField(
        choices=[
            ('residential', 'Жилое'),
            ('commercial', 'Коммерческое'),
            ('industrial', 'Промышленное'),
            ('infrastructure', 'Инфраструктура'),
            ('other', 'Другое'),
        ],
        required=False
    )
    start_date_from = serializers.DateField(required=False)
    start_date_to = serializers.DateField(required=False)
    end_date_from = serializers.DateField(required=False)
    end_date_to = serializers.DateField(required=False)
    is_overdue = serializers.BooleanField(required=False)
