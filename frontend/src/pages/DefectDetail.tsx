/**
 * Страница детального просмотра дефекта
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  IconButton,
  Button,
  Breadcrumbs,
  Link,
  Divider,
  Card,
  CardContent,
  Avatar,
  Tab,
  Tabs,
  TabPanel,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack,
  Edit,
  Delete,
  CalendarToday,
  Person,
  Category,
  LocationOn,
  Priority,
  Schedule,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '../store';
import { defectsAPI, commentsAPI } from '../services/api';
import { Defect } from '../types';
import DefectWorkflow from '../components/defects/DefectWorkflow';
import DefectComments from '../components/defects/DefectComments';
import { EditDefectDialog } from '../components/defects/DefectDialogs';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`defect-tabpanel-${index}`}
      aria-labelledby={`defect-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export const DefectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const { user, hasPermission } = useAppSelector(state => state.auth);
  
  const [defect, setDefect] = useState<Defect | null>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const canManageDefects = hasPermission('update_defect');
  const canViewInternalComments = hasPermission('view_internal_comments');

  useEffect(() => {
    loadDefectData();
  }, [id]);

  const loadDefectData = async () => {
    if (!id) return;
    
    setLoading(true);
    try {
      const [defectData, commentsData] = await Promise.all([
        defectsAPI.getDefect(parseInt(id)),
        commentsAPI.getDefectComments(parseInt(id))
      ]);
      
      setDefect(defectData);
      setComments(commentsData);
    } catch (error) {
      console.error('Ошибка загрузки данных дефекта:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (defectId: number, newStatus: string) => {
    try {
      const updatedDefect = await defectsAPI.changeStatus(defectId, newStatus);
      setDefect(updatedDefect);
    } catch (error) {
      console.error('Ошибка изменения статуса:', error);
    }
  };

  const handleAddComment = async (content: string, isInternal: boolean, files?: FileList) => {
    if (!defect) return;
    
    try {
      const newComment = await commentsAPI.addComment(defect.id, content, isInternal, files);
      setComments(prev => [...prev, newComment]);
    } catch (error) {
      console.error('Ошибка добавления комментария:', error);
    }
  };

  const handleEditComment = async (commentId: number, content: string) => {
    try {
      const updatedComment = await commentsAPI.updateComment(commentId, content);
      setComments(prev => prev.map(c => c.id === commentId ? updatedComment : c));
    } catch (error) {
      console.error('Ошибка редактирования комментария:', error);
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    try {
      await commentsAPI.deleteComment(commentId);
      setComments(prev => prev.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Ошибка удаления комментария:', error);
    }
  };

  const handleEditDefect = async (data: any) => {
    if (!defect) return;
    
    try {
      const updatedDefect = await defectsAPI.updateDefect(defect.id, data);
      setDefect(updatedDefect);
      setEditDialogOpen(false);
    } catch (error) {
      console.error('Ошибка обновления дефекта:', error);
    }
  };

  const getStatusColor = (status: string) => {
    const statusColors = {
      new: 'info',
      in_progress: 'primary',
      review: 'warning',
      closed: 'success',
      cancelled: 'error',
    };
    return statusColors[status as keyof typeof statusColors] || 'default';
  };

  const getPriorityColor = (priority: string) => {
    const priorityColors = {
      low: 'success',
      medium: 'warning',
      high: 'error',
      critical: 'error',
    };
    return priorityColors[priority as keyof typeof priorityColors] || 'default';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!defect) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h6">Дефект не найден</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs и навигация */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/defects')} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Breadcrumbs>
          <Link
            component="button"
            variant="body1"
            onClick={() => navigate('/defects')}
            sx={{ textDecoration: 'none' }}
          >
            Дефекты
          </Link>
          <Typography color="text.primary">
            {defect.defect_number}
          </Typography>
        </Breadcrumbs>
      </Box>

      {/* Заголовок */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {defect.title}
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {defect.defect_number}
            </Typography>
          </Box>
          
          {canManageDefects && (
            <Box display="flex" gap={1}>
              <Button
                startIcon={<Edit />}
                variant="outlined"
                onClick={() => setEditDialogOpen(true)}
              >
                Редактировать
              </Button>
            </Box>
          )}
        </Box>

        {/* Статус и приоритет */}
        <Box display="flex" gap={2} mb={2}>
          <Chip
            label={defect.status}
            color={getStatusColor(defect.status) as any}
            variant="filled"
          />
          <Chip
            label={`Приоритет: ${defect.priority}`}
            color={getPriorityColor(defect.priority) as any}
            variant="outlined"
          />
          <Chip
            label={`Серьезность: ${defect.severity}`}
            variant="outlined"
          />
        </Box>

        {/* Основная информация */}
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="body1" paragraph>
              {defect.description}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Информация о дефекте
                </Typography>
                
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <Person fontSize="small" />
                  <Typography variant="body2">
                    Автор: {defect.author.first_name} {defect.author.last_name}
                  </Typography>
                </Box>

                {defect.assignee && (
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <Person fontSize="small" color="primary" />
                    <Typography variant="body2">
                      Исполнитель: {defect.assignee.first_name} {defect.assignee.last_name}
                    </Typography>
                  </Box>
                )}

                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <Category fontSize="small" />
                  <Typography variant="body2">
                    Категория: {defect.category.name}
                  </Typography>
                </Box>

                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <LocationOn fontSize="small" />
                  <Typography variant="body2">
                    Локация: {defect.location}
                    {defect.floor && `, этаж ${defect.floor}`}
                    {defect.room && `, ${defect.room}`}
                  </Typography>
                </Box>

                {defect.due_date && (
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <Schedule fontSize="small" color={defect.is_overdue ? 'error' : 'default'} />
                    <Typography variant="body2" color={defect.is_overdue ? 'error' : 'default'}>
                      Срок: {new Date(defect.due_date).toLocaleDateString()}
                      {defect.is_overdue && ' (просрочено)'}
                    </Typography>
                  </Box>
                )}

                <Box display="flex" alignItems="center" gap={1}>
                  <CalendarToday fontSize="small" />
                  <Typography variant="body2">
                    Создан: {new Date(defect.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Изображение дефекта */}
        {defect.main_image && (
          <Box mt={2}>
            <img
              src={defect.main_image.file_url}
              alt="Фото дефекта"
              style={{
                maxWidth: '100%',
                maxHeight: 400,
                objectFit: 'contain',
                borderRadius: 8
              }}
            />
          </Box>
        )}
      </Paper>

      {/* Табы */}
      <Paper elevation={2}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          aria-label="defect detail tabs"
        >
          <Tab label="Workflow" />
          <Tab label={`Комментарии (${comments.length})`} />
        </Tabs>

        <CustomTabPanel value={activeTab} index={0}>
          <DefectWorkflow
            defect={defect}
            onStatusChange={handleStatusChange}
            canManageDefects={canManageDefects}
          />
        </CustomTabPanel>

        <CustomTabPanel value={activeTab} index={1}>
          <DefectComments
            defectId={defect.id}
            comments={comments}
            onAddComment={handleAddComment}
            onEditComment={handleEditComment}
            onDeleteComment={handleDeleteComment}
            currentUserId={user?.id || 0}
            canViewInternal={canViewInternalComments}
          />
        </CustomTabPanel>
      </Paper>

      {/* Диалог редактирования */}
      <EditDefectDialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        onSubmit={handleEditDefect}
        defect={defect}
      />
    </Container>
  );
};

export default DefectDetail;