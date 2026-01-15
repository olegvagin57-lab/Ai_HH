import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  MoreVert as MoreVertIcon,
  Work as WorkIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vacanciesAPI } from '../../../api/api';
import LoadingState from '../../../shared/components/LoadingState';
import EmptyState from '../../../shared/components/EmptyState';
import VacancyForm from '../components/VacancyForm';

export default function VacancyDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentTab, setCurrentTab] = useState(0);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [editMode, setEditMode] = useState(false);

  const { data: vacancy, isLoading } = useQuery({
    queryKey: ['vacancy', id],
    queryFn: () => vacanciesAPI.get(id),
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status) => vacanciesAPI.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['vacancy', id]);
      queryClient.invalidateQueries(['vacancies']);
    },
  });

  const updateAutoMatchingMutation = useMutation({
    mutationFn: (settings) => vacanciesAPI.updateAutoMatching(id, settings),
    onSuccess: () => {
      queryClient.invalidateQueries(['vacancy', id]);
    },
  });

  const handleStatusChange = (newStatus) => {
    updateStatusMutation.mutate(newStatus);
    setMenuAnchor(null);
  };

  const handleAutoMatchingToggle = (enabled) => {
    updateAutoMatchingMutation.mutate({
      enabled,
      frequency: vacancy.auto_matching_frequency || 'daily',
      min_score: vacancy.auto_matching_min_score || 70,
      max_notifications: vacancy.auto_matching_max_notifications || 10,
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      active: 'success',
      paused: 'warning',
      closed: 'error',
      filled: 'info',
    };
    return colors[status] || 'default';
  };

  const getStatusLabel = (status) => {
    const labels = {
      draft: 'Черновик',
      active: 'Активна',
      paused: 'Приостановлена',
      closed: 'Закрыта',
      filled: 'Закрыта (найдена)',
    };
    return labels[status] || status;
  };

  if (isLoading) {
    return <LoadingState message="Загрузка вакансии..." />;
  }

  if (!vacancy) {
    return (
      <EmptyState
        icon={<WorkIcon sx={{ fontSize: 64, color: 'text.secondary' }} />}
        title="Вакансия не найдена"
        description="Вакансия с указанным ID не существует"
        action={
          <Button variant="contained" onClick={() => navigate('/vacancies')}>
            Вернуться к списку
          </Button>
        }
      />
    );
  }

  if (editMode) {
    return (
      <Box>
        <Box display="flex" alignItems="center" gap={2} mb={4}>
          <IconButton onClick={() => setEditMode(false)}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" fontWeight={600}>
            Редактирование вакансии
          </Typography>
        </Box>
        <Card>
          <CardContent>
            <VacancyForm
              vacancy={vacancy}
              onSuccess={() => {
                setEditMode(false);
                queryClient.invalidateQueries(['vacancy', id]);
              }}
              onCancel={() => setEditMode(false)}
            />
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={4}>
        <IconButton onClick={() => navigate('/vacancies')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" fontWeight={600} flex={1}>
          {vacancy.title}
        </Typography>
        <Chip
          label={getStatusLabel(vacancy.status)}
          color={getStatusColor(vacancy.status)}
          sx={{ mr: 2 }}
        />
        <IconButton onClick={(e) => setMenuAnchor(e.currentTarget)}>
          <MoreVertIcon />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} sx={{ mb: 3 }}>
                <Tab label="Описание" />
                <Tab label="Кандидаты" />
                <Tab label="Настройки" />
              </Tabs>

              {currentTab === 0 && (
                <Box>
                  <Box mb={3}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Описание
                    </Typography>
                    <Typography variant="body1">{vacancy.description || 'Нет описания'}</Typography>
                  </Box>

                  {vacancy.requirements && (
                    <Box mb={3}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Требования
                      </Typography>
                      <Typography variant="body1">{vacancy.requirements}</Typography>
                    </Box>
                  )}

                  <Divider sx={{ my: 3 }} />

                  <Grid container spacing={2}>
                    {vacancy.city && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Город
                        </Typography>
                        <Typography variant="body1">{vacancy.city}</Typography>
                      </Grid>
                    )}
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Удаленная работа
                      </Typography>
                      <Typography variant="body1">{vacancy.remote ? 'Да' : 'Нет'}</Typography>
                    </Grid>
                    {vacancy.salary_min && vacancy.salary_max && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Зарплата
                        </Typography>
                        <Typography variant="body1">
                          {vacancy.salary_min} - {vacancy.salary_max} {vacancy.currency || 'RUB'}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </Box>
              )}

              {currentTab === 1 && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Список кандидатов будет доступен после интеграции с системой кандидатов.
                  </Typography>
                  {vacancy.candidate_ids && vacancy.candidate_ids.length > 0 && (
                    <Box mt={2}>
                      <Typography variant="body2">
                        Кандидатов привязано: {vacancy.candidate_ids.length}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}

              {currentTab === 2 && (
                <Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={vacancy.auto_matching_enabled || false}
                        onChange={(e) => handleAutoMatchingToggle(e.target.checked)}
                      />
                    }
                    label="Автоматический подбор кандидатов"
                  />
                  {vacancy.auto_matching_enabled && (
                    <Box mt={3}>
                      <Typography variant="body2" color="text.secondary">
                        Частота: {vacancy.auto_matching_frequency || 'daily'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Минимальный score: {vacancy.auto_matching_min_score || 70}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Максимум уведомлений: {vacancy.auto_matching_max_notifications || 10}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Информация
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box mb={2}>
                <Typography variant="caption" color="text.secondary">
                  Создана
                </Typography>
                <Typography variant="body2">
                  {new Date(vacancy.created_at).toLocaleDateString('ru-RU')}
                </Typography>
              </Box>
              {vacancy.updated_at && (
                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    Обновлена
                  </Typography>
                  <Typography variant="body2">
                    {new Date(vacancy.updated_at).toLocaleDateString('ru-RU')}
                  </Typography>
                </Box>
              )}
              <Button
                fullWidth
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setEditMode(true)}
                sx={{ mt: 2 }}
              >
                Редактировать
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={() => setMenuAnchor(null)}>
        <MenuItem onClick={() => handleStatusChange('active')} disabled={vacancy.status === 'active'}>
          Активировать
        </MenuItem>
        <MenuItem onClick={() => handleStatusChange('paused')} disabled={vacancy.status === 'paused'}>
          Приостановить
        </MenuItem>
        <MenuItem onClick={() => handleStatusChange('closed')} disabled={vacancy.status === 'closed'}>
          Закрыть
        </MenuItem>
      </Menu>
    </Box>
  );
}
