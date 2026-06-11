import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Stack,
  Card,
  CardContent,
} from '@mui/material';
import {
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Delete as DeleteIcon,
  DoneAll as DoneAllIcon,
  CheckCircle as CheckCircleIcon,
  Lock as LockIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useAuth } from '../../auth/contexts/AuthContext';
import { usersAPI, notificationsAPI } from '../../../api/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ pt: 3 }}>{children}</Box> : null;
}

function ProfileTab({ user }) {
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    company_name: user?.company_name || '',
    position: user?.position || '',
  });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: (data) => usersAPI.update(user.id, data),
    onSuccess: () => {
      setSuccess(true);
      setError('');
      setTimeout(() => setSuccess(false), 3000);
    },
    onError: (err) => {
      setError(err.response?.data?.detail || err.response?.data?.message || 'Ошибка сохранения');
    },
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setSuccess(false);
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('ru-RU', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <Stack spacing={3}>
      <Card variant="outlined">
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <Avatar
              sx={{ width: 64, height: 64, bgcolor: 'primary.main', fontSize: '1.75rem', fontWeight: 700 }}
            >
              {(user?.username || user?.email || 'U').charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                {user?.full_name || user?.username || '—'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {user?.email}
              </Typography>
              <Box display="flex" gap={0.5} mt={0.5} flexWrap="wrap">
                {user?.role_names?.map((role) => (
                  <Chip key={role} label={role} size="small" color="primary" variant="outlined"
                    sx={{ height: 20, fontSize: '0.65rem' }} />
                ))}
                {user?.is_verified && (
                  <Chip label="Верифицирован" size="small" color="success" variant="outlined"
                    icon={<CheckCircleIcon />} sx={{ height: 20, fontSize: '0.65rem' }} />
                )}
              </Box>
            </Box>
          </Box>
          <Divider sx={{ mb: 3 }} />
          <Typography variant="subtitle2" fontWeight={600} gutterBottom color="text.secondary">
            РЕДАКТИРОВАТЬ ПРОФИЛЬ
          </Typography>
          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
              Профиль обновлён
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}
          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Полное имя"
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                variant="outlined"
                size="small"
              />
              <TextField
                fullWidth
                label="Компания"
                name="company_name"
                value={form.company_name}
                onChange={handleChange}
                variant="outlined"
                size="small"
              />
              <TextField
                fullWidth
                label="Должность"
                name="position"
                value={form.position}
                onChange={handleChange}
                variant="outlined"
                size="small"
              />
              <Button
                type="submit"
                variant="contained"
                disabled={mutation.isPending}
                sx={{ alignSelf: 'flex-start' }}
              >
                {mutation.isPending ? <CircularProgress size={20} color="inherit" /> : 'Сохранить'}
              </Button>
            </Stack>
          </Box>
        </CardContent>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom color="text.secondary">
            ИНФОРМАЦИЯ ОБ АККАУНТЕ
          </Typography>
          <Stack spacing={1.5} mt={1}>
            {[
              { label: 'Имя пользователя', value: user?.username || '—' },
              { label: 'Email', value: user?.email || '—' },
              { label: 'Статус', value: user?.is_active ? 'Активен' : 'Неактивен' },
              { label: 'Дата регистрации', value: formatDate(user?.created_at) },
              { label: 'Последний вход', value: formatDate(user?.last_login) },
            ].map(({ label, value }) => (
              <Box key={label} display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2" color="text.secondary">{label}</Typography>
                <Typography variant="body2" fontWeight={500}>{value}</Typography>
              </Box>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}

function NotificationsTab() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', 'settings', filter],
    queryFn: () => notificationsAPI.getNotifications(filter, 1, 50),
  });

  const markAllMutation = useMutation({
    mutationFn: notificationsAPI.markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: notificationsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
    },
  });

  const markReadMutation = useMutation({
    mutationFn: notificationsAPI.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
    },
  });

  const notifications = data?.notifications || [];
  const unreadCount = data?.unread_count || 0;

  return (
    <Stack spacing={2}>
      <Card variant="outlined">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="subtitle2" fontWeight={600} color="text.secondary">
                УВЕДОМЛЕНИЯ
              </Typography>
              {unreadCount > 0 && (
                <Typography variant="caption" color="text.secondary">
                  {unreadCount} непрочитанных
                </Typography>
              )}
            </Box>
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant={filter ? 'contained' : 'outlined'}
                onClick={() => setFilter(!filter)}
              >
                {filter ? 'Все' : 'Непрочитанные'}
              </Button>
              {unreadCount > 0 && (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<DoneAllIcon />}
                  onClick={() => markAllMutation.mutate()}
                  disabled={markAllMutation.isPending}
                >
                  Прочитать все
                </Button>
              )}
            </Box>
          </Box>
          {isLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={32} />
            </Box>
          ) : notifications.length === 0 ? (
            <Box textAlign="center" py={4} color="text.secondary">
              <NotificationsIcon sx={{ fontSize: 48, opacity: 0.3, mb: 1 }} />
              <Typography variant="body2">Нет уведомлений</Typography>
            </Box>
          ) : (
            <List disablePadding>
              {notifications.map((n, idx) => (
                <React.Fragment key={n.id}>
                  {idx > 0 && <Divider />}
                  <ListItem
                    alignItems="flex-start"
                    sx={{
                      px: 0,
                      bgcolor: n.is_read ? 'transparent' : 'action.hover',
                      borderRadius: 1,
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2" fontWeight={n.is_read ? 400 : 600}>
                            {n.title || n.message}
                          </Typography>
                          {!n.is_read && (
                            <Chip label="Новое" size="small" color="primary"
                              sx={{ height: 18, fontSize: '0.6rem' }} />
                          )}
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {n.title ? n.message : ''}
                          {n.created_at
                            ? ` · ${new Date(n.created_at).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}`
                            : ''}
                        </Typography>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box display="flex" gap={0.5}>
                        {!n.is_read && (
                          <IconButton
                            size="small"
                            title="Отметить прочитанным"
                            onClick={() => markReadMutation.mutate(n.id)}
                          >
                            <CheckCircleIcon fontSize="small" />
                          </IconButton>
                        )}
                        <IconButton
                          size="small"
                          title="Удалить"
                          onClick={() => deleteMutation.mutate(n.id)}
                          color="error"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}

function SecurityTab({ user }) {
  return (
    <Stack spacing={2}>
      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom color="text.secondary">
            БЕЗОПАСНОСТЬ
          </Typography>
          <Stack spacing={2} mt={1}>
            <Box display="flex" alignItems="center" gap={1.5} p={2}
              sx={{ bgcolor: 'action.hover', borderRadius: 2 }}>
              <LockIcon color="action" />
              <Box flex={1}>
                <Typography variant="body2" fontWeight={600}>Смена пароля</Typography>
                <Typography variant="caption" color="text.secondary">
                  Изменение пароля недоступно через интерфейс — обратитесь к администратору системы
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1.5} p={2}
              sx={{ bgcolor: 'action.hover', borderRadius: 2 }}>
              <InfoIcon color="action" />
              <Box flex={1}>
                <Typography variant="body2" fontWeight={600}>Верификация аккаунта</Typography>
                <Typography variant="caption" color="text.secondary">
                  Статус: {user?.is_verified ? 'Аккаунт верифицирован' : 'Аккаунт не верифицирован'}
                </Typography>
              </Box>
              {user?.is_verified && (
                <CheckCircleIcon color="success" />
              )}
            </Box>
            <Box display="flex" alignItems="center" gap={1.5} p={2}
              sx={{ bgcolor: 'action.hover', borderRadius: 2 }}>
              <SecurityIcon color="action" />
              <Box flex={1}>
                <Typography variant="body2" fontWeight={600}>Роли и права</Typography>
                <Box display="flex" gap={0.5} mt={0.5} flexWrap="wrap">
                  {user?.role_names?.length > 0
                    ? user.role_names.map((role) => (
                        <Chip key={role} label={role} size="small" variant="outlined"
                          sx={{ height: 20, fontSize: '0.65rem' }} />
                      ))
                    : <Typography variant="caption" color="text.secondary">Нет назначенных ролей</Typography>
                  }
                </Box>
              </Box>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState(0);

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Настройки
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Управление профилем, уведомлениями и безопасностью аккаунта
      </Typography>

      <Paper variant="outlined" sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          sx={{
            px: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Tab label="Профиль" icon={<PersonIcon />} iconPosition="start" sx={{ minHeight: 56 }} />
          <Tab label="Уведомления" icon={<NotificationsIcon />} iconPosition="start" sx={{ minHeight: 56 }} />
          <Tab label="Безопасность" icon={<SecurityIcon />} iconPosition="start" sx={{ minHeight: 56 }} />
        </Tabs>
        <Box sx={{ p: 3 }}>
          <TabPanel value={tab} index={0}>
            <ProfileTab user={user} />
          </TabPanel>
          <TabPanel value={tab} index={1}>
            <NotificationsTab />
          </TabPanel>
          <TabPanel value={tab} index={2}>
            <SecurityTab user={user} />
          </TabPanel>
        </Box>
      </Paper>
    </Box>
  );
}
