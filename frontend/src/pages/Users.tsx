/**
 * Страница управления пользователями (только для администраторов)
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  IconButton,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Card,
  CardContent,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Switch,
  FormControlLabel,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Person as PersonIcon,
  PersonAdd as PersonAddIcon,
  Group as GroupIcon,
  Security as SecurityIcon,
  Block as BlockIcon,
  CheckCircle as ActiveIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  AccessTime as LastSeenIcon,
  Badge as BadgeIcon
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '../store/index';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'manager' | 'engineer' | 'observer';
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login?: string;
  phone?: string;
  department?: string;
  position?: string;
  avatar?: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`users-tabpanel-${index}`}
      aria-labelledby={`users-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const Users: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user: currentUser, hasPermission } = useAuth();
  const { showSuccess, showError } = useNotification();

  // Состояние
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [tabValue, setTabValue] = useState(0);
  
  // Диалоги
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  
  // Меню
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Форма пользователя
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'engineer' as User['role'],
    password: '',
    phone: '',
    department: '',
    position: '',
    is_active: true,
    is_staff: false
  });

  // Проверка прав доступа
  if (!hasPermission('manage_users')) {
    return (
      <Alert severity="error">
        У вас нет прав доступа к управлению пользователями
      </Alert>
    );
  }

  // Загрузка пользователей
  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      // Здесь должен быть запрос к API
      // const response = await usersAPI.getUsers();
      // setUsers(response.results);
      
      // Мок данные
      const mockUsers: User[] = [
        {
          id: 1,
          username: 'admin',
          email: 'admin@company.com',
          first_name: 'Администратор',
          last_name: 'Системы',
          role: 'manager',
          is_active: true,
          is_staff: true,
          date_joined: '2024-01-01T00:00:00Z',
          last_login: '2024-09-12T10:00:00Z',
          department: 'IT',
          position: 'Системный администратор'
        },
        {
          id: 2,
          username: 'engineer1',
          email: 'engineer1@company.com',
          first_name: 'Иван',
          last_name: 'Инженеров',
          role: 'engineer',
          is_active: true,
          is_staff: false,
          date_joined: '2024-02-01T00:00:00Z',
          last_login: '2024-09-12T09:30:00Z',
          department: 'Строительный отдел',
          position: 'Инженер-строитель'
        },
        {
          id: 3,
          username: 'observer1',
          email: 'observer1@company.com',
          first_name: 'Мария',
          last_name: 'Наблюдатель',
          role: 'observer',
          is_active: true,
          is_staff: false,
          date_joined: '2024-03-01T00:00:00Z',
          last_login: '2024-09-11T16:45:00Z',
          department: 'Контроль качества',
          position: 'Инспектор'
        }
      ];
      
      setUsers(mockUsers);
    } catch (error) {
      showError('Ошибка загрузки пользователей');
    } finally {
      setLoading(false);
    }
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>, user: User) => {
    setAnchorEl(event.currentTarget);
    setSelectedUser(user);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
    setSelectedUser(null);
  };

  const handleOpenUserDialog = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setUserForm({
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        role: user.role,
        password: '',
        phone: user.phone || '',
        department: user.department || '',
        position: user.position || '',
        is_active: user.is_active,
        is_staff: user.is_staff
      });
    } else {
      setEditingUser(null);
      setUserForm({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        role: 'engineer',
        password: '',
        phone: '',
        department: '',
        position: '',
        is_active: true,
        is_staff: false
      });
    }
    setUserDialogOpen(true);
    handleUserMenuClose();
  };

  const handleCloseUserDialog = () => {
    setUserDialogOpen(false);
    setEditingUser(null);
  };

  const handleSaveUser = async () => {
    try {
      if (editingUser) {
        // Обновление пользователя
        // await usersAPI.updateUser(editingUser.id, userForm);
        showSuccess('Пользователь обновлен');
      } else {
        // Создание нового пользователя
        // await usersAPI.createUser(userForm);
        showSuccess('Пользователь создан');
      }
      
      handleCloseUserDialog();
      loadUsers();
    } catch (error) {
      showError('Ошибка сохранения пользователя');
    }
  };

  const handleDeleteUser = async () => {
    if (!userToDelete) return;
    
    try {
      // await usersAPI.deleteUser(userToDelete.id);
      showSuccess('Пользователь удален');
      setDeleteDialogOpen(false);
      setUserToDelete(null);
      loadUsers();
    } catch (error) {
      showError('Ошибка удаления пользователя');
    }
  };

  const handleToggleUserStatus = async (user: User) => {
    try {
      // await usersAPI.updateUser(user.id, { is_active: !user.is_active });
      showSuccess(`Пользователь ${!user.is_active ? 'активирован' : 'деактивирован'}`);
      loadUsers();
    } catch (error) {
      showError('Ошибка изменения статуса пользователя');
    }
  };

  const getRoleLabel = (role: string) => {
    const labels = {
      'manager': 'Менеджер',
      'engineer': 'Инженер',
      'observer': 'Наблюдатель'
    };
    return labels[role as keyof typeof labels] || role;
  };

  const getRoleColor = (role: string) => {
    const colors = {
      'manager': 'error',
      'engineer': 'primary',
      'observer': 'info'
    };
    return colors[role as keyof typeof colors] || 'default';
  };

  const activeUsers = users.filter(u => u.is_active);
  const inactiveUsers = users.filter(u => !u.is_active);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Заголовок */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Управление пользователями
        </Typography>
        <Button
          variant="contained"
          startIcon={<PersonAddIcon />}
          onClick={() => handleOpenUserDialog()}
        >
          Добавить пользователя
        </Button>
      </Box>

      {/* Статистика */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="primary.main">
                    {users.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Всего пользователей
                  </Typography>
                </Box>
                <GroupIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {activeUsers.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Активные
                  </Typography>
                </Box>
                <ActiveIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="error.main">
                    {users.filter(u => u.role === 'manager').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Менеджеры
                  </Typography>
                </Box>
                <SecurityIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="info.main">
                    {users.filter(u => u.role === 'engineer').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Инженеры
                  </Typography>
                </Box>
                <BadgeIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Вкладки */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab icon={<GroupIcon />} label="Все пользователи" />
          <Tab icon={<ActiveIcon />} label="Активные" />
          <Tab icon={<BlockIcon />} label="Неактивные" />
        </Tabs>
      </Box>

      {/* Таблица пользователей */}
      <TabPanel value={tabValue} index={0}>
        <UserTable 
          users={users} 
          onUserMenuOpen={handleUserMenuOpen}
          onToggleStatus={handleToggleUserStatus}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={setPage}
          onRowsPerPageChange={setRowsPerPage}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <UserTable 
          users={activeUsers} 
          onUserMenuOpen={handleUserMenuOpen}
          onToggleStatus={handleToggleUserStatus}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={setPage}
          onRowsPerPageChange={setRowsPerPage}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <UserTable 
          users={inactiveUsers} 
          onUserMenuOpen={handleUserMenuOpen}
          onToggleStatus={handleToggleUserStatus}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={setPage}
          onRowsPerPageChange={setRowsPerPage}
        />
      </TabPanel>

      {/* Меню действий */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleUserMenuClose}
      >
        <MenuItem onClick={() => handleOpenUserDialog(selectedUser!)}>
          <EditIcon sx={{ mr: 1 }} />
          Редактировать
        </MenuItem>
        <MenuItem onClick={() => handleToggleUserStatus(selectedUser!)}>
          {selectedUser?.is_active ? <BlockIcon sx={{ mr: 1 }} /> : <ActiveIcon sx={{ mr: 1 }} />}
          {selectedUser?.is_active ? 'Деактивировать' : 'Активировать'}
        </MenuItem>
        <MenuItem 
          onClick={() => {
            setUserToDelete(selectedUser);
            setDeleteDialogOpen(true);
            handleUserMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Удалить
        </MenuItem>
      </Menu>

      {/* Диалог создания/редактирования пользователя */}
      <Dialog 
        open={userDialogOpen} 
        onClose={handleCloseUserDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingUser ? 'Редактирование пользователя' : 'Создание нового пользователя'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Имя пользователя"
                value={userForm.username}
                onChange={(e) => setUserForm(prev => ({ ...prev, username: e.target.value }))}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                label="Email"
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm(prev => ({ ...prev, email: e.target.value }))}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                label="Имя"
                value={userForm.first_name}
                onChange={(e) => setUserForm(prev => ({ ...prev, first_name: e.target.value }))}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                label="Фамилия"
                value={userForm.last_name}
                onChange={(e) => setUserForm(prev => ({ ...prev, last_name: e.target.value }))}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Роль</InputLabel>
                <Select
                  value={userForm.role}
                  onChange={(e) => setUserForm(prev => ({ ...prev, role: e.target.value as User['role'] }))}
                  label="Роль"
                >
                  <MenuItem value="manager">Менеджер</MenuItem>
                  <MenuItem value="engineer">Инженер</MenuItem>
                  <MenuItem value="observer">Наблюдатель</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {!editingUser && (
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Пароль"
                  type="password"
                  value={userForm.password}
                  onChange={(e) => setUserForm(prev => ({ ...prev, password: e.target.value }))}
                  fullWidth
                  required
                />
              </Grid>
            )}
            
            <Grid item xs={12} sm={6}>
              <TextField
                label="Телефон"
                value={userForm.phone}
                onChange={(e) => setUserForm(prev => ({ ...prev, phone: e.target.value }))}
                fullWidth
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                label="Отдел"
                value={userForm.department}
                onChange={(e) => setUserForm(prev => ({ ...prev, department: e.target.value }))}
                fullWidth
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                label="Должность"
                value={userForm.position}
                onChange={(e) => setUserForm(prev => ({ ...prev, position: e.target.value }))}
                fullWidth
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box display="flex" gap={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={userForm.is_active}
                      onChange={(e) => setUserForm(prev => ({ ...prev, is_active: e.target.checked }))}
                    />
                  }
                  label="Активный пользователь"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={userForm.is_staff}
                      onChange={(e) => setUserForm(prev => ({ ...prev, is_staff: e.target.checked }))}
                    />
                  }
                  label="Администратор"
                />
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUserDialog}>Отмена</Button>
          <Button onClick={handleSaveUser} variant="contained">
            {editingUser ? 'Сохранить' : 'Создать'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог подтверждения удаления */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Подтверждение удаления</DialogTitle>
        <DialogContent>
          <Typography>
            Вы уверены, что хотите удалить пользователя {userToDelete?.first_name} {userToDelete?.last_name}?
            Это действие нельзя отменить.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleDeleteUser} color="error" variant="contained">
            Удалить
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Компонент таблицы пользователей
interface UserTableProps {
  users: User[];
  onUserMenuOpen: (event: React.MouseEvent<HTMLElement>, user: User) => void;
  onToggleStatus: (user: User) => void;
  page: number;
  rowsPerPage: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (rowsPerPage: number) => void;
}

const UserTable: React.FC<UserTableProps> = ({
  users,
  onUserMenuOpen,
  onToggleStatus,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange
}) => {
  const getRoleLabel = (role: string) => {
    const labels = {
      'manager': 'Менеджер',
      'engineer': 'Инженер',
      'observer': 'Наблюдатель'
    };
    return labels[role as keyof typeof labels] || role;
  };

  const getRoleColor = (role: string) => {
    const colors = {
      'manager': 'error',
      'engineer': 'primary',
      'observer': 'info'
    };
    return colors[role as keyof typeof colors] || 'default';
  };

  return (
    <Paper>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Пользователь</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Роль</TableCell>
              <TableCell>Отдел</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Последний вход</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((user) => (
                <TableRow key={user.id} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar>
                        <PersonIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {user.first_name} {user.last_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          @{user.username}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  
                  <TableCell>{user.email}</TableCell>
                  
                  <TableCell>
                    <Chip
                      label={getRoleLabel(user.role)}
                      color={getRoleColor(user.role) as any}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  
                  <TableCell>
                    {user.department && (
                      <Box>
                        <Typography variant="body2">{user.department}</Typography>
                        {user.position && (
                          <Typography variant="caption" color="text.secondary">
                            {user.position}
                          </Typography>
                        )}
                      </Box>
                    )}
                  </TableCell>
                  
                  <TableCell>
                    <Chip
                      label={user.is_active ? 'Активен' : 'Неактивен'}
                      color={user.is_active ? 'success' : 'error'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  
                  <TableCell>
                    {user.last_login ? (
                      <Typography variant="body2" color="text.secondary">
                        {new Date(user.last_login).toLocaleDateString('ru-RU')}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Никогда
                      </Typography>
                    )}
                  </TableCell>
                  
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Tooltip title={user.is_active ? 'Деактивировать' : 'Активировать'}>
                        <Switch
                          checked={user.is_active}
                          onChange={() => onToggleStatus(user)}
                          size="small"
                        />
                      </Tooltip>
                      
                      <IconButton
                        size="small"
                        onClick={(e) => onUserMenuOpen(e, user)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        component="div"
        count={users.length}
        page={page}
        onPageChange={(_, newPage) => onPageChange(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => onRowsPerPageChange(parseInt(e.target.value, 10))}
        labelRowsPerPage="Строк на странице:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
      />
    </Paper>
  );
};
