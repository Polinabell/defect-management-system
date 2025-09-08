"""
Views для управления дефектами
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Defect, DefectCategory, DefectFile, DefectComment, DefectHistory
from .serializers import (
    DefectSerializer, DefectListSerializer, DefectCreateSerializer,
    DefectUpdateSerializer, DefectCategorySerializer, DefectFileSerializer,
    DefectCommentSerializer, DefectStatusChangeSerializer,
    DefectAssignmentSerializer, DefectHistorySerializer,
    DefectSearchSerializer, DefectStatsSerializer
)
from apps.common.permissions import (
    IsProjectMember, IsDefectAssigneeOrAuthor, CanChangeDefectStatus,
    CanAssignDefects
)
from apps.common.utils import get_client_ip


class DefectCategoryListView(generics.ListCreateAPIView):
    """
    Список категорий дефектов и создание новой категории
    """
    queryset = DefectCategory.objects.filter(is_active=True)
    serializer_class = DefectCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['order', 'name']
    
    def get_permissions(self):
        """Создавать категории могут только администраторы и менеджеры"""
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated]
            # Дополнительная проверка в perform_create
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Создание категории"""
        user = self.request.user
        if not (user.is_admin or user.role == 'manager'):
            raise ValidationError("Недостаточно прав для создания категории")
        serializer.save()


class DefectCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление категории дефектов
    """
    queryset = DefectCategory.objects.all()
    serializer_class = DefectCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Изменять категории могут только администраторы и менеджеры"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated]
            # Дополнительная проверка в методах
        return super().get_permissions()
    
    def perform_update(self, serializer):
        """Обновление категории"""
        user = self.request.user
        if not (user.is_admin or user.role == 'manager'):
            raise ValidationError("Недостаточно прав для изменения категории")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Мягкое удаление категории"""
        user = self.request.user
        if not (user.is_admin or user.role == 'manager'):
            raise ValidationError("Недостаточно прав для удаления категории")
        
        # Проверяем, что категория не используется
        if instance.defects.exists():
            raise ValidationError("Нельзя удалить категорию, которая используется в дефектах")
        
        instance.is_active = False
        instance.save()


class DefectListCreateView(generics.ListCreateAPIView):
    """
    Список дефектов и создание нового дефекта
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'location', 'defect_number']
    filterset_fields = [
        'project', 'category', 'status', 'priority', 'severity',
        'assignee', 'author'
    ]
    ordering_fields = [
        'created_at', 'updated_at', 'due_date', 'priority',
        'status', 'defect_number'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.request.method == 'POST':
            return DefectCreateSerializer
        return DefectListSerializer
    
    def get_queryset(self):
        """Фильтрация дефектов по правам доступа пользователя"""
        queryset = Defect.objects.select_related(
            'project', 'category', 'author', 'assignee', 'stage'
        ).prefetch_related('files', 'comments')
        
        user = self.request.user
        
        # Администраторы видят все дефекты
        if user.is_admin:
            return queryset
        
        # Получаем проекты, к которым пользователь имеет доступ
        user_projects = user.projects.all()
        managed_projects = user.managed_projects.all() if user.is_manager else []
        
        # Объединяем проекты
        all_projects = user_projects.union(managed_projects) if managed_projects else user_projects
        
        return queryset.filter(project__in=all_projects)
    
    def perform_create(self, serializer):
        """Создание дефекта"""
        # Проверяем права на создание дефекта в проекте
        project = serializer.validated_data['project']
        user = self.request.user
        
        if not (project.is_member(user) or user.is_admin):
            raise ValidationError("Нет прав для создания дефекта в этом проекте")
        
        serializer.save()


class DefectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление дефекта
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    def get_serializer_class(self):
        """Выбор сериализатора"""
        if self.request.method in ['PUT', 'PATCH']:
            return DefectUpdateSerializer
        return DefectSerializer
    
    def get_queryset(self):
        """Queryset с оптимизацией"""
        return Defect.objects.select_related(
            'project', 'stage', 'category', 'author', 'assignee', 'reviewer'
        ).prefetch_related(
            'files', 'comments__author', 'history'
        )
    
    def get_permissions(self):
        """Права доступа в зависимости от действия"""
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsDefectAssigneeOrAuthor
            ]
        elif self.request.method == 'DELETE':
            # Удалять могут только автор, менеджер проекта или админ
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsDefectAssigneeOrAuthor
            ]
        return super().get_permissions()


class DefectStatusChangeView(APIView):
    """
    Изменение статуса дефекта
    """
    permission_classes = [permissions.IsAuthenticated, CanChangeDefectStatus]
    
    def post(self, request, defect_id):
        """Изменение статуса дефекта"""
        try:
            defect = Defect.objects.get(id=defect_id)
        except Defect.DoesNotExist:
            return Response(
                {"error": "Дефект не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем права доступа к проекту
        if not (defect.project.is_member(request.user) or request.user.is_admin):
            return Response(
                {"error": "Нет доступа к этому дефекту"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DefectStatusChangeSerializer(
            data=request.data,
            context={'defect': defect, 'request': request}
        )
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            comment = serializer.validated_data.get('comment', '')
            
            try:
                defect.change_status(new_status, request.user, comment)
                
                # Логируем изменение
                DefectHistory.objects.create(
                    defect=defect,
                    user=request.user,
                    action='status_changed',
                    field_name='status',
                    old_value=defect.status,
                    new_value=new_status,
                    ip_address=get_client_ip(request)
                )
                
                return Response(
                    DefectSerializer(defect, context={'request': request}).data,
                    status=status.HTTP_200_OK
                )
            except ValidationError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class DefectAssignmentView(APIView):
    """
    Назначение исполнителя дефекта
    """
    permission_classes = [permissions.IsAuthenticated, CanAssignDefects]
    
    def post(self, request, defect_id):
        """Назначение исполнителя"""
        try:
            defect = Defect.objects.get(id=defect_id)
        except Defect.DoesNotExist:
            return Response(
                {"error": "Дефект не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем права на назначение
        user = request.user
        if not (defect.project.manager == user or user.is_admin):
            return Response(
                {"error": "Недостаточно прав для назначения исполнителя"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DefectAssignmentSerializer(
            data=request.data,
            context={'defect': defect, 'request': request}
        )
        
        if serializer.is_valid():
            assignee = serializer.validated_data['assignee']
            due_date = serializer.validated_data.get('due_date')
            comment = serializer.validated_data.get('comment', '')
            
            try:
                defect.assign_to(assignee, due_date, user)
                
                # Логируем назначение
                DefectHistory.objects.create(
                    defect=defect,
                    user=user,
                    action='assigned',
                    field_name='assignee',
                    old_value=str(defect.assignee) if defect.assignee else '',
                    new_value=str(assignee),
                    ip_address=get_client_ip(request)
                )
                
                return Response(
                    DefectSerializer(defect, context={'request': request}).data,
                    status=status.HTTP_200_OK
                )
            except ValidationError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class DefectFilesView(generics.ListCreateAPIView):
    """
    Список файлов дефекта и загрузка новых файлов
    """
    serializer_class = DefectFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    def get_queryset(self):
        """Получаем файлы конкретного дефекта"""
        defect_id = self.kwargs.get('defect_pk')
        return DefectFile.objects.filter(
            defect_id=defect_id
        ).select_related('uploaded_by').order_by('-is_main', 'created_at')
    
    def perform_create(self, serializer):
        """Создание файла"""
        defect_id = self.kwargs.get('defect_pk')
        serializer.save(defect_id=defect_id)


class DefectFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление файла дефекта
    """
    serializer_class = DefectFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    def get_queryset(self):
        """Queryset для файлов дефекта"""
        defect_id = self.kwargs.get('defect_pk')
        return DefectFile.objects.filter(defect_id=defect_id)
    
    def get_permissions(self):
        """Права доступа"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Изменять/удалять файлы может автор файла, автор дефекта, менеджер проекта или админ
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsDefectAssigneeOrAuthor
            ]
        return super().get_permissions()


class DefectCommentsView(generics.ListCreateAPIView):
    """
    Список комментариев дефекта и создание нового комментария
    """
    serializer_class = DefectCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    ordering = ['created_at']
    
    def get_queryset(self):
        """Получаем комментарии конкретного дефекта"""
        defect_id = self.kwargs.get('defect_pk')
        return DefectComment.objects.filter(
            defect_id=defect_id,
            reply_to__isnull=True  # Только родительские комментарии
        ).select_related('author').prefetch_related(
            'replies__author'
        )
    
    def perform_create(self, serializer):
        """Создание комментария"""
        defect_id = self.kwargs.get('defect_pk')
        serializer.save(defect_id=defect_id)


class DefectCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление комментария к дефекту
    """
    serializer_class = DefectCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Queryset для комментариев дефекта"""
        defect_id = self.kwargs.get('defect_pk')
        return DefectComment.objects.filter(defect_id=defect_id)
    
    def get_permissions(self):
        """Права доступа"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Редактировать/удалять может автор комментария, менеджер проекта или админ
            self.permission_classes = [
                permissions.IsAuthenticated,
                # Дополнительная проверка в методах
            ]
        return super().get_permissions()
    
    def perform_update(self, serializer):
        """Обновление комментария"""
        comment = self.get_object()
        user = self.request.user
        
        # Проверяем права
        if not (comment.author == user or 
                comment.defect.project.manager == user or 
                user.is_admin):
            raise ValidationError("Недостаточно прав для редактирования комментария")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Удаление комментария"""
        user = self.request.user
        
        # Проверяем права
        if not (instance.author == user or 
                instance.defect.project.manager == user or 
                user.is_admin):
            raise ValidationError("Недостаточно прав для удаления комментария")
        
        instance.delete()


class DefectHistoryView(generics.ListAPIView):
    """
    История изменений дефекта
    """
    serializer_class = DefectHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Получаем историю конкретного дефекта"""
        defect_id = self.kwargs.get('defect_pk')
        return DefectHistory.objects.filter(
            defect_id=defect_id
        ).select_related('user')


class DefectSearchView(APIView):
    """
    Расширенный поиск дефектов
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Поиск дефектов по критериям"""
        serializer = DefectSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Базовый queryset с учётом прав доступа
        queryset = self._get_user_defects(request.user)
        
        # Применяем фильтры
        queryset = self._apply_search_filters(queryset, serializer.validated_data)
        
        # Сериализуем результаты
        results = DefectListSerializer(
            queryset[:100],  # Ограничиваем результаты для производительности
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': queryset.count(),
            'results': results.data
        })
    
    def _get_user_defects(self, user):
        """Получение дефектов с учётом прав пользователя"""
        queryset = Defect.objects.select_related(
            'project', 'category', 'author', 'assignee'
        )
        
        if user.is_admin:
            return queryset
        
        # Получаем проекты пользователя
        user_projects = user.projects.all()
        managed_projects = user.managed_projects.all() if user.is_manager else []
        all_projects = user_projects.union(managed_projects) if managed_projects else user_projects
        
        return queryset.filter(project__in=all_projects)
    
    def _apply_search_filters(self, queryset, filters):
        """Применение фильтров поиска"""
        query = filters.get('query')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(defect_number__icontains=query)
            )
        
        project = filters.get('project')
        if project:
            queryset = queryset.filter(project=project)
        
        category = filters.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        status_list = filters.get('status')
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        
        priority_list = filters.get('priority')
        if priority_list:
            queryset = queryset.filter(priority__in=priority_list)
        
        severity_list = filters.get('severity')
        if severity_list:
            queryset = queryset.filter(severity__in=severity_list)
        
        assignee = filters.get('assignee')
        if assignee:
            queryset = queryset.filter(assignee=assignee)
        
        author = filters.get('author')
        if author:
            queryset = queryset.filter(author=author)
        
        created_from = filters.get('created_from')
        if created_from:
            queryset = queryset.filter(created_at__date__gte=created_from)
        
        created_to = filters.get('created_to')
        if created_to:
            queryset = queryset.filter(created_at__date__lte=created_to)
        
        due_date_from = filters.get('due_date_from')
        if due_date_from:
            queryset = queryset.filter(due_date__gte=due_date_from)
        
        due_date_to = filters.get('due_date_to')
        if due_date_to:
            queryset = queryset.filter(due_date__lte=due_date_to)
        
        is_overdue = filters.get('is_overdue')
        if is_overdue is not None:
            today = timezone.now().date()
            if is_overdue:
                queryset = queryset.filter(
                    due_date__lt=today,
                    status__in=['new', 'in_progress', 'review']
                )
            else:
                queryset = queryset.exclude(
                    due_date__lt=today,
                    status__in=['new', 'in_progress', 'review']
                )
        
        has_files = filters.get('has_files')
        if has_files is not None:
            if has_files:
                queryset = queryset.filter(files__isnull=False).distinct()
            else:
                queryset = queryset.filter(files__isnull=True)
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def defect_stats(request):
    """
    Статистика дефектов
    """
    # Получаем дефекты с учётом прав доступа
    user = request.user
    
    if user.is_admin:
        defects = Defect.objects.all()
    else:
        user_projects = user.projects.all()
        managed_projects = user.managed_projects.all() if user.is_manager else []
        all_projects = user_projects.union(managed_projects) if managed_projects else user_projects
        defects = Defect.objects.filter(project__in=all_projects)
    
    # Базовая статистика
    total_defects = defects.count()
    
    # Статистика по статусам
    defects_by_status = {}
    for status_choice in Defect.Status.choices:
        status_code = status_choice[0]
        count = defects.filter(status=status_code).count()
        defects_by_status[status_code] = count
    
    # Статистика по приоритетам
    defects_by_priority = {}
    for priority_choice in Defect.Priority.choices:
        priority_code = priority_choice[0]
        count = defects.filter(priority=priority_code).count()
        defects_by_priority[priority_code] = count
    
    # Статистика по категориям
    defects_by_category = {}
    categories = DefectCategory.objects.filter(is_active=True)
    for category in categories:
        count = defects.filter(category=category).count()
        defects_by_category[category.name] = count
    
    # Просроченные дефекты
    today = timezone.now().date()
    overdue_defects = defects.filter(
        due_date__lt=today,
        status__in=['new', 'in_progress', 'review']
    ).count()
    
    # Среднее время решения
    closed_defects = defects.filter(
        status='closed',
        closed_at__isnull=False
    )
    
    if closed_defects.exists():
        resolution_times = []
        for defect in closed_defects:
            if defect.resolution_time:
                resolution_times.append(defect.resolution_time)
        
        average_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    else:
        average_resolution_time = 0
    
    # Дефекты за сегодня
    defects_created_today = defects.filter(created_at__date=today).count()
    defects_closed_today = defects.filter(closed_at__date=today).count()
    
    stats = {
        'total_defects': total_defects,
        'defects_by_status': defects_by_status,
        'defects_by_priority': defects_by_priority,
        'defects_by_category': defects_by_category,
        'overdue_defects': overdue_defects,
        'average_resolution_time': round(average_resolution_time, 1),
        'defects_created_today': defects_created_today,
        'defects_closed_today': defects_closed_today,
    }
    
    serializer = DefectStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_defects(request):
    """
    Массовое обновление дефектов
    """
    defect_ids = request.data.get('defect_ids', [])
    action = request.data.get('action')
    value = request.data.get('value')
    
    if not defect_ids or not action:
        return Response(
            {"error": "Не указаны дефекты или действие"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Получаем дефекты с проверкой прав доступа
    user = request.user
    defects = Defect.objects.filter(id__in=defect_ids)
    
    # Фильтруем по правам доступа
    if not user.is_admin:
        user_projects = user.projects.all()
        managed_projects = user.managed_projects.all() if user.is_manager else []
        all_projects = user_projects.union(managed_projects) if managed_projects else user_projects
        defects = defects.filter(project__in=all_projects)
    
    updated_count = 0
    errors = []
    
    for defect in defects:
        try:
            if action == 'change_status':
                can_change, error_msg = defect.can_transition_to(value, user)
                if can_change:
                    defect.change_status(value, user)
                    updated_count += 1
                else:
                    errors.append(f"Дефект {defect.defect_number}: {error_msg}")
            
            elif action == 'assign':
                try:
                    assignee = User.objects.get(id=value)
                    if defect.project.is_member(assignee):
                        defect.assign_to(assignee, user=user)
                        updated_count += 1
                    else:
                        errors.append(f"Дефект {defect.defect_number}: Исполнитель не является участником проекта")
                except User.DoesNotExist:
                    errors.append(f"Дефект {defect.defect_number}: Пользователь не найден")
            
            elif action == 'change_priority':
                defect.priority = value
                defect.save()
                updated_count += 1
            
            else:
                errors.append(f"Неизвестное действие: {action}")
        
        except Exception as e:
            errors.append(f"Дефект {defect.defect_number}: {str(e)}")
    
    return Response({
        'updated_count': updated_count,
        'errors': errors
    }, status=status.HTTP_200_OK)
