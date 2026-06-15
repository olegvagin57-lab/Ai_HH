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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  MoreVert as MoreVertIcon,
  Work as WorkIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  OpenInNew as OpenInNewIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vacanciesAPI } from '../../../api/api';
import LoadingState from '../../../shared/components/LoadingState';
import EmptyState from '../../../shared/components/EmptyState';
import VacancyForm from '../components/VacancyForm';

const ScoreBadge = ({ score }) => {
  const color = score >= 8 ? 'success' : score >= 6 ? 'warning' : 'error';
  return <Chip label={`${score}/10`} color={color} size="small" sx={{ fontWeight: 600 }} />;
};

const MatchBar = ({ pct }) => {
  const color = pct >= 80 ? 'success' : pct >= 60 ? 'warning' : 'error';
  return (
    <Box display="flex" alignItems="center" gap={1}>
      <Typography variant="body2" fontWeight={600} minWidth={45}>{pct?.toFixed(1)}%</Typography>
      <LinearProgress variant="determinate" value={pct} color={color} sx={{ flex: 1, height: 8, borderRadius: 4 }} />
    </Box>
  );
};

export default function VacancyDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentTab, setCurrentTab] = useState(0);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const { data: vacancy, isLoading } = useQuery({
    queryKey: ['vacancy', id],
    queryFn: () => vacanciesAPI.get(id),
    enabled: !!id,
  });

  const { data: candidatesData, isLoading: candidatesLoading } = useQuery({
    queryKey: ['vacancy', id, 'candidates'],
    queryFn: () => vacanciesAPI.getCandidates(id, 1, 100, 'ai_score', 'desc'),
    enabled: !!id && currentTab === 1,
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
                  {candidatesLoading ? (
                    <Box display="flex" justifyContent="center" p={4}><LinearProgress sx={{ width: '100%' }} /></Box>
                  ) : !candidatesData?.resumes?.length ? (
                    <Box p={3} textAlign="center">
                      <Typography color="text.secondary">Кандидаты не найдены. Активируйте автоматический подбор во вкладке «Настройки».</Typography>
                    </Box>
                  ) : (
                    <>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          Подобрано кандидатов: {candidatesData.total}
                        </Typography>
                      </Box>
                      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                        <Table size="small">
                          <TableHead>
                            <TableRow sx={{ bgcolor: 'primary.main', '& .MuiTableCell-head': { color: 'white', fontWeight: 700, fontSize: '0.8rem', textTransform: 'uppercase' } }}>
                              <TableCell>Должность / Кандидат</TableCell>
                              <TableCell>Город</TableCell>
                              <TableCell>Зарплата</TableCell>
                              <TableCell>AI Score</TableCell>
                              <TableCell>Совпадение</TableCell>
                              <TableCell align="center">Действия</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {candidatesData.resumes.map((r) => (
                              <TableRow key={r.id} hover sx={{ '&:nth-of-type(even)': { bgcolor: 'action.hover' }, cursor: 'pointer' }}
                                onClick={() => setSelectedCandidate(r)}>
                                <TableCell>
                                  <Typography variant="body2" fontWeight={500}>{r.title || '—'}</Typography>
                                  <Typography variant="caption" color="text.secondary">{r.name || 'Анонимный'}{r.age ? `, ${r.age} лет` : ''}</Typography>
                                </TableCell>
                                <TableCell><Typography variant="body2">{r.city || '—'}</Typography></TableCell>
                                <TableCell>
                                  <Typography variant="body2">{r.salary ? `${Number(r.salary).toLocaleString('ru-RU')} ${r.currency || 'RUR'}` : '—'}</Typography>
                                </TableCell>
                                <TableCell>{r.ai_score ? <ScoreBadge score={r.ai_score} /> : <Chip label="—" size="small" variant="outlined" />}</TableCell>
                                <TableCell sx={{ minWidth: 140 }}>{r.match_percentage ? <MatchBar pct={r.match_percentage} /> : '—'}</TableCell>
                                <TableCell align="center">
                                  <Box display="flex" gap={0.5} justifyContent="center">
                                    {r.hh_url && (
                                      <Tooltip title="Открыть на HH.ru">
                                        <IconButton size="small" color="success" onClick={(e) => { e.stopPropagation(); window.open(r.hh_url, '_blank'); }}>
                                          <OpenInNewIcon fontSize="small" />
                                        </IconButton>
                                      </Tooltip>
                                    )}
                                    <Tooltip title="Подробнее">
                                      <IconButton size="small" color="primary" onClick={(e) => { e.stopPropagation(); setSelectedCandidate(r); }}>
                                        <VisibilityIcon fontSize="small" />
                                      </IconButton>
                                    </Tooltip>
                                  </Box>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </>
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

      <Dialog open={!!selectedCandidate} onClose={() => setSelectedCandidate(null)} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        {selectedCandidate && (
          <>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between" alignItems="start">
                <Box>
                  <Typography variant="h6" fontWeight={600}>{selectedCandidate.name || 'Анонимный кандидат'}</Typography>
                  <Typography variant="body2" color="text.secondary">{selectedCandidate.title} • {selectedCandidate.city}</Typography>
                </Box>
                {selectedCandidate.hh_url && (
                  <Button variant="outlined" color="success" size="small" startIcon={<OpenInNewIcon />}
                    onClick={() => window.open(selectedCandidate.hh_url, '_blank')}>
                    Открыть на HH
                  </Button>
                )}
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2} mb={2}>
                <Grid item xs={6}><Typography variant="caption" color="text.secondary">Возраст</Typography><Typography>{selectedCandidate.age ? `${selectedCandidate.age} лет` : '—'}</Typography></Grid>
                <Grid item xs={6}><Typography variant="caption" color="text.secondary">Зарплата</Typography><Typography>{selectedCandidate.salary ? `${Number(selectedCandidate.salary).toLocaleString('ru-RU')} ${selectedCandidate.currency || 'RUR'}` : '—'}</Typography></Grid>
                <Grid item xs={6}><Typography variant="caption" color="text.secondary">AI Score</Typography>{selectedCandidate.ai_score ? <ScoreBadge score={selectedCandidate.ai_score} /> : <Typography>—</Typography>}</Grid>
                <Grid item xs={6}><Typography variant="caption" color="text.secondary">Совпадение</Typography>{selectedCandidate.match_percentage ? <MatchBar pct={selectedCandidate.match_percentage} /> : <Typography>—</Typography>}</Grid>
              </Grid>
              {selectedCandidate.match_explanation && (<><Divider sx={{ my: 2 }} /><Typography variant="subtitle2" fontWeight={600} color="primary.main" gutterBottom>Анализ соответствия</Typography><Typography variant="body2">{selectedCandidate.match_explanation}</Typography></>)}
              {selectedCandidate.strengths?.length > 0 && (<><Divider sx={{ my: 2 }} /><Typography variant="subtitle2" fontWeight={600} color="success.main" gutterBottom>Сильные стороны</Typography>{selectedCandidate.strengths.map((s, i) => (<Box key={i} display="flex" gap={1} mb={0.5}><CheckCircleIcon color="success" fontSize="small" sx={{ mt: 0.3 }} /><Typography variant="body2">{s}</Typography></Box>))}</>)}
              {selectedCandidate.weaknesses?.length > 0 && (<><Divider sx={{ my: 2 }} /><Typography variant="subtitle2" fontWeight={600} color="warning.main" gutterBottom>Области для улучшения</Typography>{selectedCandidate.weaknesses.map((w, i) => (<Box key={i} display="flex" gap={1} mb={0.5}><WarningIcon color="warning" fontSize="small" sx={{ mt: 0.3 }} /><Typography variant="body2">{w}</Typography></Box>))}</>)}
              {selectedCandidate.recommendation && (<><Divider sx={{ my: 2 }} /><Typography variant="subtitle2" fontWeight={600} color="info.main" gutterBottom>Рекомендация</Typography><Typography variant="body2">{selectedCandidate.recommendation}</Typography></>)}
              {selectedCandidate.ai_questions?.length > 0 && (<><Divider sx={{ my: 2 }} /><Typography variant="subtitle2" fontWeight={600} color="secondary.main" gutterBottom>Вопросы для собеседования</Typography><Box component="ul" sx={{ pl: 3, m: 0 }}>{selectedCandidate.ai_questions.map((q, i) => (<li key={i}><Typography variant="body2">{q}</Typography></li>))}</Box></>)}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedCandidate(null)}>Закрыть</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}
