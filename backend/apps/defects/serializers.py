"""
Сериализаторы для управления дефектами
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Defect, DefectCategory, DefectFile, DefectComment, DefectHistory
from apps.projects.models import Project, ProjectStage
from apps.common.models import Priority
from apps.common.utils import FileUploadHandler

User = get_user_model()


class DefectCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории дефектов
    """
    defects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DefectCategory
        fields = [
            'id', 'name', 'description', 'color', 'icon',
            'is_active', 'order', 'defects_count'
        ]
        read_only_fields = ['id']
    
    def get_defects_count(self, obj):
        """Количество дефектов в категории"""
        return obj.defects.count()


class DefectFileSerializer(serializers.ModelSerializer):
    """
    Сериализатор файла дефекта
    """
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')
    file_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = DefectFile
        fields = [
            'id', 'file', 'file_url', 'filename', 'file_type',
            'file_size', 'file_size_formatted', 'mime_type',
            'description', 'uploaded_by', 'uploaded_by_name',
            'is_main', 'created_at'
        ]
        read_only_fields = ['id', 'file_size', 'mime_type', 'created_at']
    
    def get_file_url(self, obj):
        """Получает URL файла"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_formatted(self, obj):
        """Форматированный размер файла"""
        from apps.common.utils import format_file_size
        return format_file_size(obj.file_size)
    
    def validate_file(self, value):
        """Валидация загружаемого файла"""
        # Определяем тип файла по расширению
        filename = value.name.lower()
        
        if any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            validation_result = FileUploadHandler.validate_image(value)
        elif any(filename.endswith(ext) for ext in ['.pdf', '.doc', '.docx']):
            validation_result = FileUploadHandler.validate_document(value)
        else:
            raise serializers.ValidationError("Неподдерживаемый тип файла")
        
        if not validation_result['valid']:
            raise serializers.ValidationError(validation_result['errors'])
        
        return value
    
    def create(self, validated_data):
        """Создание файла дефекта"""
        # Устанавливаем пользователя, загрузившего файл
        validated_data['uploaded_by'] = self.context['request'].user
        
        # Если это первое изображение, делаем его основным
        defect = validated_data['defect']
        if validated_data.get('file_type') == DefectFile.FileType.IMAGE:
            if not defect.files.filter(file_type=DefectFile.FileType.IMAGE, is_main=True).exists():
                validated_data['is_main'] = True
        
        return super().create(validated_data)


class DefectCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор комментария к дефекту
    """
    author_name = serializers.ReadOnlyField(source='author.get_full_name')
    comment_type_display = serializers.ReadOnlyField(source='get_comment_type_display')
    replies = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = DefectComment
        fields = [
            'id', 'content', 'comment_type', 'comment_type_display',
            'is_internal', 'author', 'author_name', 'reply_to',
            'replies', 'can_edit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Получаем ответы на комментарий"""
        if obj.replies.exists():
            return DefectCommentSerializer(
                obj.replies.all(),
                many=True,
                context=self.context
            ).data
        return []
    
    def get_can_edit(self, obj):
        """Проверка возможности редактирования комментария"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Автор может редактировать в течение 15 минут
        if obj.author == request.user:
            time_limit = timezone.now() - timezone.timedelta(minutes=15)
            return obj.created_at > time_limit
        
        # Админы и менеджеры проекта могут редактировать всегда
        return (
            request.user.is_admin or 
            obj.defect.project.manager == request.user
        )
    
    def create(self, validated_data):
        """Создание комментария"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class DefectListSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор для списка дефектов
    """
    project_name = serializers.ReadOnlyField(source='project.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    category_color = serializers.ReadOnlyField(source='category.color')
    author_name = serializers.ReadOnlyField(source='author.get_full_name')
    assignee_name = serializers.ReadOnlyField(source='assignee.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    priority_display = serializers.ReadOnlyField(source='get_priority_display')
    severity_display = serializers.ReadOnlyField(source='get_severity_display')
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    main_image = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Defect
        fields = [
            'id', 'defect_number', 'title', 'project', 'project_name',
            'category', 'category_name', 'category_color',
            'priority', 'priority_display', 'severity', 'severity_display',
            'status', 'status_display', 'author', 'author_name',
            'assignee', 'assignee_name', 'due_date', 'is_overdue',
            'days_remaining', 'main_image', 'comments_count', 'created_at'
        ]
    
    def get_main_image(self, obj):
        """Основное изображение дефекта"""
        main_image = obj.files.filter(
            file_type=DefectFile.FileType.IMAGE,
            is_main=True
        ).first()
        
        if main_image:
            return DefectFileSerializer(main_image, context=self.context).data
        
        # Если основного нет, берём первое изображение
        first_image = obj.files.filter(file_type=DefectFile.FileType.IMAGE).first()
        if first_image:
            return DefectFileSerializer(first_image, context=self.context).data
        
        return None
    
    def get_comments_count(self, obj):
        """Количество комментариев"""
        return obj.comments.count()


class DefectSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор дефекта
    """
    project_name = serializers.ReadOnlyField(source='project.name')
    stage_name = serializers.ReadOnlyField(source='stage.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    category_color = serializers.ReadOnlyField(source='category.color')
    author_name = serializers.ReadOnlyField(source='author.get_full_name')
    assignee_name = serializers.ReadOnlyField(source='assignee.get_full_name')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.get_full_name')
    
    # Отображаемые значения
    status_display = serializers.ReadOnlyField(source='get_status_display')
    priority_display = serializers.ReadOnlyField(source='get_priority_display')
    severity_display = serializers.ReadOnlyField(source='get_severity_display')
    
    # Вычисляемые поля
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    resolution_time = serializers.ReadOnlyField()
    
    # Связанные объекты
    files = DefectFileSerializer(many=True, read_only=True)
    comments = DefectCommentSerializer(many=True, read_only=True)
    
    # Права доступа
    can_edit = serializers.SerializerMethodField()
    can_assign = serializers.SerializerMethodField()
    can_change_status = serializers.SerializerMethodField()
    available_statuses = serializers.SerializerMethodField()
    
    class Meta:
        model = Defect
        fields = [
            'id', 'defect_number', 'title', 'description',
            'project', 'project_name', 'stage', 'stage_name',
            'category', 'category_name', 'category_color',
            'priority', 'priority_display', 'severity', 'severity_display',
            'location', 'floor', 'room', 'coordinates_x', 'coordinates_y',
            'author', 'author_name', 'assignee', 'assignee_name',
            'reviewer', 'reviewer_name', 'status', 'status_display',
            'due_date', 'assigned_at', 'started_at', 'completed_at', 'closed_at',
            'estimated_cost', 'actual_cost', 'resolution_description',
            'prevention_measures', 'external_id',
            'is_overdue', 'days_remaining', 'resolution_time',
            'files', 'comments', 'can_edit', 'can_assign',
            'can_change_status', 'available_statuses',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'defect_number', 'author', 'assigned_at',
            'started_at', 'completed_at', 'closed_at', 'created_at', 'updated_at'
        ]
    
    def get_can_edit(self, obj):
        """Проверка возможности редактирования дефекта"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Автор может редактировать
        if obj.author == user:
            return True
        
        # Менеджер проекта может редактировать
        if obj.project.manager == user:
            return True
        
        # Администратор может редактировать
        if user.is_admin:
            return True
        
        return False
    
    def get_can_assign(self, obj):
        """Проверка возможности назначения исполнителя"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Менеджер проекта может назначать
        if obj.project.manager == user:
            return True
        
        # Администратор может назначать
        if user.is_admin:
            return True
        
        return False
    
    def get_can_change_status(self, obj):
        """Проверка возможности изменения статуса"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Проверяем для каждого статуса отдельно
        for status in Defect.Status.choices:
            can_change, _ = obj.can_transition_to(status[0], user)
            if can_change:
                return True
        
        return False
    
    def get_available_statuses(self, obj):
        """Доступные статусы для изменения"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        
        user = request.user
        available = []
        
        for status_code, status_name in Defect.Status.choices:
            if status_code != obj.status:
                can_change, _ = obj.can_transition_to(status_code, user)
                if can_change:
                    available.append({
                        'code': status_code,
                        'name': status_name
                    })
        
        return available
    
    def validate(self, attrs):
        """Валидация данных дефекта"""
        project = attrs.get('project')
        stage = attrs.get('stage')
        assignee = attrs.get('assignee')
        
        # Проверяем, что этап принадлежит проекту
        if stage and project and stage.project != project:
            raise serializers.ValidationError(
                "Этап должен принадлежать выбранному проекту"
            )
        
        # Проверяем, что исполнитель является участником проекта
        if assignee and project and not project.is_member(assignee):
            raise serializers.ValidationError(
                "Исполнитель должен быть участником проекта"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Создание дефекта"""
        # Устанавливаем автора
        validated_data['author'] = self.context['request'].user
        
        return super().create(validated_data)


class DefectCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания дефекта
    """
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        help_text="Список файлов для загрузки"
    )
    
    class Meta:
        model = Defect
        fields = [
            'title', 'description', 'project', 'stage', 'category',
            'priority', 'severity', 'location', 'floor', 'room',
            'coordinates_x', 'coordinates_y', 'assignee', 'due_date',
            'estimated_cost', 'external_id', 'files'
        ]
    
    def create(self, validated_data):
        """Создание дефекта с файлами"""
        files_data = validated_data.pop('files', [])
        
        # Создаём дефект
        defect = super().create(validated_data)
        
        # Добавляем файлы
        for i, file_data in enumerate(files_data):
            DefectFile.objects.create(
                defect=defect,
                file=file_data,
                filename=file_data.name,
                uploaded_by=self.context['request'].user,
                is_main=(i == 0)  # Первый файл делаем основным
            )
        
        return defect


class DefectUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления дефекта
    """
    class Meta:
        model = Defect
        fields = [
            'title', 'description', 'category', 'priority', 'severity',
            'location', 'floor', 'room', 'coordinates_x', 'coordinates_y',
            'due_date', 'estimated_cost', 'actual_cost',
            'resolution_description', 'prevention_measures'
        ]


class DefectStatusChangeSerializer(serializers.Serializer):
    """
    Сериализатор для изменения статуса дефекта
    """
    status = serializers.ChoiceField(choices=Defect.Status.choices)
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Валидация нового статуса"""
        defect = self.context['defect']
        user = self.context['request'].user
        
        can_change, error_message = defect.can_transition_to(value, user)
        if not can_change:
            raise serializers.ValidationError(error_message)
        
        return value


class DefectAssignmentSerializer(serializers.Serializer):
    """
    Сериализатор для назначения исполнителя
    """
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    due_date = serializers.DateField(required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def validate_assignee(self, value):
        """Валидация исполнителя"""
        defect = self.context['defect']
        
        if not defect.project.is_member(value):
            raise serializers.ValidationError(
                "Исполнитель должен быть участником проекта"
            )
        
        return value
    
    def validate_due_date(self, value):
        """Валидация срока выполнения"""
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "Срок выполнения не может быть в прошлом"
            )
        
        return value


class DefectHistorySerializer(serializers.ModelSerializer):
    """
    Сериализатор истории изменений дефекта
    """
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    
    class Meta:
        model = DefectHistory
        fields = [
            'id', 'action', 'field_name', 'old_value', 'new_value',
            'user', 'user_name', 'timestamp', 'ip_address'
        ]


class DefectSearchSerializer(serializers.Serializer):
    """
    Сериализатор для поиска дефектов
    """
    query = serializers.CharField(max_length=200, required=False)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=DefectCategory.objects.filter(is_active=True),
        required=False
    )
    status = serializers.MultipleChoiceField(
        choices=Defect.Status.choices,
        required=False
    )
    priority = serializers.MultipleChoiceField(
        choices=Priority.choices,
        required=False
    )
    severity = serializers.MultipleChoiceField(
        choices=[
            ('cosmetic', 'Косметический'),
            ('minor', 'Незначительный'),
            ('major', 'Значительный'),
            ('critical', 'Критический'),
            ('blocking', 'Блокирующий'),
        ],
        required=False
    )
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False
    )
    created_from = serializers.DateField(required=False)
    created_to = serializers.DateField(required=False)
    due_date_from = serializers.DateField(required=False)
    due_date_to = serializers.DateField(required=False)
    is_overdue = serializers.BooleanField(required=False)
    has_files = serializers.BooleanField(required=False)


class DefectStatsSerializer(serializers.Serializer):
    """
    Сериализатор статистики дефектов
    """
    total_defects = serializers.IntegerField()
    defects_by_status = serializers.DictField()
    defects_by_priority = serializers.DictField()
    defects_by_category = serializers.DictField()
    overdue_defects = serializers.IntegerField()
    average_resolution_time = serializers.FloatField()
    defects_created_today = serializers.IntegerField()
    defects_closed_today = serializers.IntegerField()
