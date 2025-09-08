"""
Views для управления проектами
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Project, ProjectMember, ProjectStage, ProjectTemplate
from .serializers import (
    ProjectSerializer, ProjectListSerializer, ProjectCreateSerializer,
    ProjectUpdateSerializer, ProjectMemberSerializer, ProjectStageSerializer,
    AddProjectMemberSerializer, ProjectTemplateSerializer,
    ProjectStatsSerializer, ProjectSearchSerializer
)
from apps.common.permissions import (
    IsProjectMember, IsProjectManagerOrReadOnly, CanManageUsers
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    Список проектов и создание нового проекта
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'customer', 'address']
    filterset_fields = ['status', 'priority', 'manager', 'building_type']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectListSerializer
    
    def get_queryset(self):
        """Фильтрация проектов по правам доступа пользователя"""
        queryset = Project.objects.select_related('manager').prefetch_related(
            'members', 'defects'
        )
        
        user = self.request.user
        
        # Администраторы видят все проекты
        if user.is_admin:
            return queryset
        
        # Менеджеры видят проекты, которыми управляют, и в которых участвуют
        if user.is_manager:
            return queryset.filter(
                Q(manager=user) | Q(members=user)
            ).distinct()
        
        # Инженеры и наблюдатели видят только проекты, в которых участвуют
        return queryset.filter(members=user).distinct()
    
    def perform_create(self, serializer):
        """Создание проекта"""
        # Если менеджер не указан, назначаем текущего пользователя
        if not serializer.validated_data.get('manager'):
            if self.request.user.role in ['admin', 'manager']:
                serializer.save(manager=self.request.user)
            else:
                # Ошибка: обычный пользователь не может создавать проекты
                raise ValidationError("Недостаточно прав для создания проекта")
        else:
            serializer.save()


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление проекта
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    def get_serializer_class(self):
        """Выбор сериализатора"""
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectUpdateSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        """Queryset с оптимизацией"""
        return Project.objects.select_related('manager').prefetch_related(
            'members', 'stages', 'project_members__user', 'defects'
        )
    
    def get_permissions(self):
        """Права доступа в зависимости от действия"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsProjectManagerOrReadOnly
            ]
        return super().get_permissions()


class ProjectMembersView(generics.ListAPIView):
    """
    Список участников проекта
    """
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    def get_queryset(self):
        """Получаем участников конкретного проекта"""
        project_id = self.kwargs.get('project_pk')
        return ProjectMember.objects.filter(
            project_id=project_id,
            is_active=True
        ).select_related('user', 'project')


class AddProjectMemberView(APIView):
    """
    Добавление участника в проект
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrReadOnly]
    
    def post(self, request, project_pk):
        """Добавление участника"""
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(
                {"error": "Проект не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем права доступа к проекту
        if not project.is_member(request.user) and not request.user.is_admin:
            if project.manager != request.user:
                return Response(
                    {"error": "Недостаточно прав"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = AddProjectMemberSerializer(
            data=request.data,
            context={'project': project}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            role = serializer.validated_data['role']
            
            member, created = project.add_member(user, role)
            
            if created:
                return Response(
                    ProjectMemberSerializer(member).data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": "Пользователь уже является участником проекта"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class RemoveProjectMemberView(APIView):
    """
    Удаление участника из проекта
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrReadOnly]
    
    def delete(self, request, project_pk, user_pk):
        """Удаление участника"""
        try:
            project = Project.objects.get(pk=project_pk)
            member = ProjectMember.objects.get(
                project=project,
                user_id=user_pk,
                is_active=True
            )
        except (Project.DoesNotExist, ProjectMember.DoesNotExist):
            return Response(
                {"error": "Проект или участник не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Нельзя удалить менеджера проекта
        if member.user == project.manager:
            return Response(
                {"error": "Нельзя удалить менеджера проекта"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.is_active = False
        member.save()
        
        return Response(
            {"message": "Участник удалён из проекта"},
            status=status.HTTP_200_OK
        )


class ProjectStagesView(generics.ListCreateAPIView):
    """
    Список этапов проекта и создание нового этапа
    """
    serializer_class = ProjectStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    def get_queryset(self):
        """Получаем этапы конкретного проекта"""
        project_id = self.kwargs.get('project_pk')
        return ProjectStage.objects.filter(
            project_id=project_id
        ).select_related('responsible', 'project').order_by('order', 'start_date')
    
    def perform_create(self, serializer):
        """Создание этапа"""
        project_id = self.kwargs.get('project_pk')
        serializer.save(project_id=project_id)


class ProjectStageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление этапа проекта
    """
    serializer_class = ProjectStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrReadOnly]
    
    def get_queryset(self):
        """Queryset для этапов проекта"""
        project_id = self.kwargs.get('project_pk')
        return ProjectStage.objects.filter(
            project_id=project_id
        ).select_related('responsible', 'project')


class ProjectTemplatesView(generics.ListCreateAPIView):
    """
    Список шаблонов проектов и создание нового шаблона
    """
    queryset = ProjectTemplate.objects.filter(is_active=True)
    serializer_class = ProjectTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_permissions(self):
        """Создавать шаблоны могут только администраторы и менеджеры"""
        if self.request.method == 'POST':
            self.permission_classes = [CanManageUsers]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Создание шаблона"""
        serializer.save(created_by=self.request.user)


class ProjectTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление шаблона проекта
    """
    queryset = ProjectTemplate.objects.all()
    serializer_class = ProjectTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]


class ProjectSearchView(APIView):
    """
    Расширенный поиск проектов
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Поиск проектов по критериям"""
        serializer = ProjectSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Базовый queryset с учётом прав доступа
        queryset = self._get_user_projects(request.user)
        
        # Применяем фильтры
        queryset = self._apply_search_filters(queryset, serializer.validated_data)
        
        # Сериализуем результаты
        results = ProjectListSerializer(queryset, many=True, context={'request': request})
        
        return Response({
            'count': queryset.count(),
            'results': results.data
        })
    
    def _get_user_projects(self, user):
        """Получение проектов с учётом прав пользователя"""
        queryset = Project.objects.select_related('manager').prefetch_related('members')
        
        if user.is_admin:
            return queryset
        elif user.is_manager:
            return queryset.filter(
                Q(manager=user) | Q(members=user)
            ).distinct()
        else:
            return queryset.filter(members=user).distinct()
    
    def _apply_search_filters(self, queryset, filters):
        """Применение фильтров поиска"""
        query = filters.get('query')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(customer__icontains=query) |
                Q(address__icontains=query)
            )
        
        status_list = filters.get('status')
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        
        priority_list = filters.get('priority')
        if priority_list:
            queryset = queryset.filter(priority__in=priority_list)
        
        manager = filters.get('manager')
        if manager:
            queryset = queryset.filter(manager=manager)
        
        building_type = filters.get('building_type')
        if building_type:
            queryset = queryset.filter(building_type=building_type)
        
        start_date_from = filters.get('start_date_from')
        if start_date_from:
            queryset = queryset.filter(start_date__gte=start_date_from)
        
        start_date_to = filters.get('start_date_to')
        if start_date_to:
            queryset = queryset.filter(start_date__lte=start_date_to)
        
        end_date_from = filters.get('end_date_from')
        if end_date_from:
            queryset = queryset.filter(end_date__gte=end_date_from)
        
        end_date_to = filters.get('end_date_to')
        if end_date_to:
            queryset = queryset.filter(end_date__lte=end_date_to)
        
        is_overdue = filters.get('is_overdue')
        if is_overdue is not None:
            today = timezone.now().date()
            if is_overdue:
                queryset = queryset.filter(
                    end_date__lt=today,
                    status__in=['planning', 'in_progress', 'on_hold']
                )
            else:
                queryset = queryset.exclude(
                    end_date__lt=today,
                    status__in=['planning', 'in_progress', 'on_hold']
                )
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_stats(request):
    """
    Статистика проектов
    """
    # Получаем проекты с учётом прав доступа
    if request.user.is_admin:
        projects = Project.objects.all()
    elif request.user.is_manager:
        projects = Project.objects.filter(
            Q(manager=request.user) | Q(members=request.user)
        ).distinct()
    else:
        projects = Project.objects.filter(members=request.user)
    
    # Базовая статистика
    total_projects = projects.count()
    active_projects = projects.filter(
        status__in=['planning', 'in_progress']
    ).count()
    completed_projects = projects.filter(status='completed').count()
    
    # Просроченные проекты
    today = timezone.now().date()
    overdue_projects = projects.filter(
        end_date__lt=today,
        status__in=['planning', 'in_progress', 'on_hold']
    ).count()
    
    # Статистика по статусам
    projects_by_status = {}
    for status_choice in Project.Status.choices:
        status_code = status_choice[0]
        count = projects.filter(status=status_code).count()
        projects_by_status[status_code] = count
    
    # Статистика по приоритетам
    projects_by_priority = {}
    for priority_choice in Project.Priority.choices:
        priority_code = priority_choice[0]
        count = projects.filter(priority=priority_code).count()
        projects_by_priority[priority_code] = count
    
    # Средняя продолжительность проектов
    completed_with_duration = projects.filter(
        status='completed',
        actual_start_date__isnull=False,
        actual_end_date__isnull=False
    )
    
    average_duration = 0
    if completed_with_duration.exists():
        durations = [
            (p.actual_end_date - p.actual_start_date).days
            for p in completed_with_duration
        ]
        average_duration = sum(durations) / len(durations)
    
    # Общее количество дефектов
    total_defects = sum(p.defects.count() for p in projects)
    
    stats = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'projects_by_status': projects_by_status,
        'projects_by_priority': projects_by_priority,
        'average_duration': round(average_duration, 1),
        'total_defects': total_defects,
    }
    
    serializer = ProjectStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clone_project(request, project_pk):
    """
    Клонирование проекта
    """
    try:
        original_project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return Response(
            {"error": "Проект не найден"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Проверяем права доступа
    if not original_project.is_member(request.user) and not request.user.is_admin:
        if original_project.manager != request.user:
            return Response(
                {"error": "Недостаточно прав"},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Получаем данные для нового проекта
    new_name = request.data.get('name', f"Копия {original_project.name}")
    new_start_date = request.data.get('start_date')
    new_end_date = request.data.get('end_date')
    
    if not new_start_date or not new_end_date:
        return Response(
            {"error": "Необходимо указать новые даты начала и завершения"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Создаём копию проекта
    new_project = Project.objects.create(
        name=new_name,
        description=original_project.description,
        address=original_project.address,
        coordinates_lat=original_project.coordinates_lat,
        coordinates_lng=original_project.coordinates_lng,
        customer=original_project.customer,
        customer_contact=original_project.customer_contact,
        customer_phone=original_project.customer_phone,
        customer_email=original_project.customer_email,
        manager=request.user,  # Текущий пользователь становится менеджером
        start_date=new_start_date,
        end_date=new_end_date,
        priority=original_project.priority,
        total_area=original_project.total_area,
        building_type=original_project.building_type,
        floors_count=original_project.floors_count,
    )
    
    # Копируем этапы проекта
    original_stages = original_project.stages.all().order_by('order')
    if original_stages.exists():
        # Вычисляем новые даты для этапов пропорционально
        original_duration = (original_project.end_date - original_project.start_date).days
        new_duration = (new_project.end_date - new_project.start_date).days
        scale_factor = new_duration / original_duration if original_duration > 0 else 1
        
        for stage in original_stages:
            stage_start_offset = (stage.start_date - original_project.start_date).days
            stage_duration = (stage.end_date - stage.start_date).days
            
            new_stage_start = new_project.start_date + timezone.timedelta(
                days=int(stage_start_offset * scale_factor)
            )
            new_stage_end = new_stage_start + timezone.timedelta(
                days=int(stage_duration * scale_factor)
            )
            
            ProjectStage.objects.create(
                project=new_project,
                name=stage.name,
                description=stage.description,
                order=stage.order,
                start_date=new_stage_start,
                end_date=new_stage_end,
                estimated_hours=stage.estimated_hours,
            )
    
    # Добавляем создателя как участника
    new_project.add_member(request.user, role='manager')
    
    serializer = ProjectSerializer(new_project, context={'request': request})
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )
