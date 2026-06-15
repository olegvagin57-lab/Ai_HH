import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Button, Card, CardContent, Chip, Avatar, Grid, Divider,
  TextField, IconButton, Menu, MenuItem, Rating, Tabs, Tab, List, ListItem,
  ListItemText, LinearProgress, Paper, Alert,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon, Edit as EditIcon, Label as LabelIcon,
  Person as PersonIcon, OpenInNew as OpenInNewIcon,
  Psychology as PsychologyIcon, Star as StarIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesAPI } from '../../../api/api';
import LoadingState from '../../../shared/components/LoadingState';
import EmptyState from '../../../shared/components/EmptyState';

const STATUS_CONFIG = {
  new: { label: 'Новый', color: '#1976d2' },
  reviewed: { label: 'На рассмотрении', color: '#0288d1' },
  shortlisted: { label: 'В шорт-листе', color: '#f57c00' },
  interview_scheduled: { label: 'Собеседование назначено', color: '#7b1fa2' },
  interviewed: { label: 'Прошли собеседование', color: '#512da8' },
  offer_sent: { label: 'Оффер отправлен', color: '#2e7d32' },
  hired: { label: 'Нанят', color: '#1b5e20' },
  rejected: { label: 'Отклонён', color: '#c62828' },
  on_hold: { label: 'На паузе', color: '#616161' },
};

const STATUSES = Object.keys(STATUS_CONFIG);

function ScoreCircle({ score, size = 64 }) {
  const color = score >= 8 ? '#2e7d32' : score >= 6 ? '#f57c00' : score >= 4 ? '#1565c0' : '#c62828';
  return (
    <Box sx={{
      width: size, height: size, borderRadius: '50%', bgcolor: color,
      display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
    }}>
      <Typography sx={{ color: '#fff', fontWeight: 700, fontSize: size * 0.28, lineHeight: 1 }}>
        {score}
      </Typography>
      <Typography sx={{ color: 'rgba(255,255,255,0.8)', fontSize: size * 0.16, lineHeight: 1 }}>
        /10
      </Typography>
    </Box>
  );
}

function MatchBar({ value, label }) {
  const color = value >= 80 ? '#2e7d32' : value >= 60 ? '#f57c00' : value >= 40 ? '#1565c0' : '#c62828';
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" mb={0.5}>
        <Typography variant="caption" color="text.secondary">{label}</Typography>
        <Typography variant="caption" fontWeight={600} sx={{ color }}>{Math.round(value)}%</Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={Math.min(100, value)}
        sx={{ height: 8, borderRadius: 4, bgcolor: 'action.hover', '& .MuiLinearProgress-bar': { bgcolor: color, borderRadius: 4 } }}
      />
    </Box>
  );
}

const ACTION_LABELS = {
  status_changed: 'Изменён статус',
  tag_added: 'Добавлен тег',
  tag_removed: 'Удалён тег',
  rating_added: 'Добавлена оценка',
  notes_updated: 'Обновлены заметки',
  assigned: 'Назначен ответственный',
  folder_changed: 'Изменена папка',
};

export default function CandidateDetailPage() {
  const { resumeId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentTab, setCurrentTab] = useState(0);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState(null);
  const [tagInput, setTagInput] = useState('');
  const [showTagInput, setShowTagInput] = useState(false);
  const [notes, setNotes] = useState('');
  const [isEditingNotes, setIsEditingNotes] = useState(false);

  const { data: candidate, isLoading } = useQuery({
    queryKey: ['candidate', resumeId],
    queryFn: () => candidatesAPI.get(resumeId),
    enabled: !!resumeId,
  });

  const { data: interactions } = useQuery({
    queryKey: ['candidate', resumeId, 'interactions'],
    queryFn: () => candidatesAPI.getInteractions(resumeId),
    enabled: !!resumeId,
  });

  React.useEffect(() => {
    if (candidate) setNotes(candidate.notes || '');
  }, [candidate]);

  const invalidate = () => {
    queryClient.invalidateQueries(['candidate', resumeId]);
    queryClient.invalidateQueries(['candidates']);
  };

  const updateStatusMutation = useMutation({
    mutationFn: (status) => candidatesAPI.updateStatus(resumeId, status),
    onSuccess: () => { invalidate(); setStatusMenuAnchor(null); },
  });

  const addTagMutation = useMutation({
    mutationFn: (tag) => candidatesAPI.addTag(resumeId, tag),
    onSuccess: () => { invalidate(); setTagInput(''); setShowTagInput(false); },
  });

  const removeTagMutation = useMutation({
    mutationFn: (tag) => candidatesAPI.removeTag(resumeId, tag),
    onSuccess: invalidate,
  });

  const updateNotesMutation = useMutation({
    mutationFn: (n) => candidatesAPI.updateNotes(resumeId, n),
    onSuccess: () => { invalidate(); setIsEditingNotes(false); },
  });

  const addRatingMutation = useMutation({
    mutationFn: (r) => candidatesAPI.addRating(resumeId, r),
    onSuccess: invalidate,
  });

  if (isLoading) return <LoadingState message="Загрузка данных кандидата..." />;
  if (!candidate) return (
    <EmptyState
      icon={<PersonIcon sx={{ fontSize: 64, color: 'text.secondary' }} />}
      title="Кандидат не найден"
      description="Кандидат с указанным ID не существует"
      action={<Button variant="contained" onClick={() => navigate('/candidates')}>Вернуться к списку</Button>}
    />
  );

  const statusCfg = STATUS_CONFIG[candidate.status] || STATUS_CONFIG.new;
  const hhUrl = candidate.hh_id ? `https://hh.ru/resume/${candidate.hh_id}` : null;

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={4}>
        <IconButton onClick={() => navigate('/candidates')}><ArrowBackIcon /></IconButton>
        <Box flex={1}>
          <Typography variant="h5" fontWeight={700}>
            {candidate.title || 'Кандидат'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {[candidate.age ? `${candidate.age} лет` : null, candidate.city].filter(Boolean).join(' · ')}
          </Typography>
        </Box>
        {hhUrl && (
          <Button
            variant="outlined"
            startIcon={<OpenInNewIcon />}
            href={hhUrl}
            target="_blank"
            rel="noopener noreferrer"
            size="small"
          >
            Резюме на HH
          </Button>
        )}
      </Box>

      <Grid container spacing={3}>
        {/* Left sidebar */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Box display="flex" flexDirection="column" alignItems="center" mb={2}>
                <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main', mb: 1.5 }}>
                  <PersonIcon sx={{ fontSize: 40 }} />
                </Avatar>
                <Typography variant="h6" fontWeight={600} textAlign="center">
                  {candidate.title || 'Специалист'}
                </Typography>
                {candidate.age && (
                  <Typography variant="body2" color="text.secondary">{candidate.age} лет</Typography>
                )}
              </Box>

              {/* AI Score */}
              {(candidate.ai_score != null || candidate.match_percentage != null) && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    {candidate.ai_score != null && <ScoreCircle score={candidate.ai_score} />}
                    <Box flex={1}>
                      <Typography variant="caption" color="text.secondary" display="block">AI-оценка</Typography>
                      <Typography variant="h6" fontWeight={700}>{candidate.ai_score}/10</Typography>
                    </Box>
                  </Box>
                  {candidate.match_percentage != null && (
                    <MatchBar value={candidate.match_percentage} label="Совпадение с вакансией" />
                  )}
                </>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Status */}
              <Box mb={2}>
                <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Статус</Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip
                    label={statusCfg.label}
                    size="small"
                    sx={{ bgcolor: statusCfg.color, color: '#fff', fontWeight: 600 }}
                  />
                  <IconButton size="small" onClick={(e) => setStatusMenuAnchor(e.currentTarget)}>
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>

              {/* Rating */}
              <Box mb={2}>
                <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>HR-оценка</Typography>
                <Rating
                  value={candidate.average_rating || 0}
                  onChange={(_, v) => v && addRatingMutation.mutate(v)}
                  size="medium"
                />
                {candidate.average_rating && (
                  <Typography variant="caption" color="text.secondary"> {candidate.average_rating.toFixed(1)}/5</Typography>
                )}
              </Box>

              {/* Salary */}
              {candidate.salary && (
                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Желаемая зарплата</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {candidate.salary.toLocaleString('ru-RU')} {candidate.currency || '₽'}
                  </Typography>
                </Box>
              )}

              {/* Tags */}
              <Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                  <Typography variant="caption" color="text.secondary">Теги</Typography>
                  <IconButton size="small" onClick={() => setShowTagInput(!showTagInput)}>
                    <LabelIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Box display="flex" gap={0.5} flexWrap="wrap" mb={1}>
                  {candidate.tags?.map((tag) => (
                    <Chip key={tag} label={tag} size="small" onDelete={() => removeTagMutation.mutate(tag)} variant="outlined" />
                  ))}
                  {(!candidate.tags || candidate.tags.length === 0) && (
                    <Typography variant="caption" color="text.disabled">Нет тегов</Typography>
                  )}
                </Box>
                {showTagInput && (
                  <Box display="flex" gap={1}>
                    <TextField
                      size="small" placeholder="Новый тег" value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && tagInput.trim() && addTagMutation.mutate(tagInput.trim())}
                      sx={{ flex: 1 }}
                    />
                    <Button size="small" onClick={() => tagInput.trim() && addTagMutation.mutate(tagInput.trim())}>
                      OK
                    </Button>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Main content */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}>
                <Tab label="AI Анализ" icon={<PsychologyIcon />} iconPosition="start" />
                <Tab label="Заметки" icon={<EditIcon />} iconPosition="start" />
                <Tab label="История" icon={<StarIcon />} iconPosition="start" />
              </Tabs>

              {/* Tab 0 — AI Analysis */}
              {currentTab === 0 && (
                <Box>
                  {!candidate.ai_score && !candidate.match_percentage ? (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      AI-анализ ещё не выполнен для этого резюме. Запустите поиск, чтобы активировать анализ.
                    </Alert>
                  ) : (
                    <>
                      {candidate.recommendation && (
                        <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'success.50', borderColor: 'success.main' }}>
                          <Typography variant="subtitle2" color="success.dark" gutterBottom>
                            Рекомендация
                          </Typography>
                          <Typography variant="body2">{candidate.recommendation}</Typography>
                        </Paper>
                      )}

                      {candidate.match_explanation && (
                        <Box mb={3}>
                          <Typography variant="subtitle2" gutterBottom>Объяснение совпадения</Typography>
                          <Typography variant="body2" color="text.secondary">{candidate.match_explanation}</Typography>
                        </Box>
                      )}

                      {candidate.strengths?.length > 0 && (
                        <Box mb={3}>
                          <Typography variant="subtitle2" gutterBottom sx={{ color: 'success.main' }}>Сильные стороны</Typography>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {candidate.strengths.map((s, i) => (
                              <Chip key={i} label={s} size="small" color="success" variant="outlined" />
                            ))}
                          </Box>
                        </Box>
                      )}

                      {candidate.weaknesses?.length > 0 && (
                        <Box mb={3}>
                          <Typography variant="subtitle2" gutterBottom sx={{ color: 'warning.main' }}>Слабые стороны</Typography>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {candidate.weaknesses.map((w, i) => (
                              <Chip key={i} label={w} size="small" color="warning" variant="outlined" />
                            ))}
                          </Box>
                        </Box>
                      )}

                      {candidate.red_flags?.length > 0 && (
                        <Box mb={3}>
                          <Typography variant="subtitle2" gutterBottom sx={{ color: 'error.main' }}>Красные флаги</Typography>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {candidate.red_flags.map((f, i) => (
                              <Chip key={i} label={f} size="small" color="error" variant="outlined" />
                            ))}
                          </Box>
                        </Box>
                      )}

                      {candidate.interview_focus && (
                        <Box mb={3}>
                          <Typography variant="subtitle2" gutterBottom>Фокус на собеседовании</Typography>
                          <Typography variant="body2" color="text.secondary">{candidate.interview_focus}</Typography>
                        </Box>
                      )}

                      {candidate.career_trajectory && (
                        <Box mb={2}>
                          <Typography variant="subtitle2" gutterBottom>Карьерная траектория</Typography>
                          <Typography variant="body2" color="text.secondary">{candidate.career_trajectory}</Typography>
                        </Box>
                      )}
                    </>
                  )}
                </Box>
              )}

              {/* Tab 1 — Notes */}
              {currentTab === 1 && (
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="subtitle2">Персональные заметки</Typography>
                    {!isEditingNotes && (
                      <IconButton size="small" onClick={() => setIsEditingNotes(true)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    )}
                  </Box>
                  {isEditingNotes ? (
                    <Box>
                      <TextField
                        fullWidth multiline rows={6} value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Добавьте заметки о кандидате..."
                      />
                      <Box display="flex" gap={1} mt={2}>
                        <Button variant="contained" onClick={() => updateNotesMutation.mutate(notes)}>
                          Сохранить
                        </Button>
                        <Button onClick={() => { setIsEditingNotes(false); setNotes(candidate.notes || ''); }}>
                          Отмена
                        </Button>
                      </Box>
                    </Box>
                  ) : (
                    <Typography variant="body2" color={notes ? 'text.primary' : 'text.secondary'} sx={{ whiteSpace: 'pre-wrap' }}>
                      {notes || 'Заметок пока нет. Нажмите на иконку редактирования, чтобы добавить.'}
                    </Typography>
                  )}
                </Box>
              )}

              {/* Tab 2 — History */}
              {currentTab === 2 && (
                <Box>
                  {interactions?.interactions?.length > 0 ? (
                    <List dense>
                      {interactions.interactions.map((item) => (
                        <ListItem key={item.id} sx={{ px: 0 }}>
                          <ListItemText
                            primary={ACTION_LABELS[item.action_type] || item.action_type}
                            secondary={
                              <Box component="span">
                                <Typography component="span" variant="caption" color="text.secondary">
                                  {new Date(item.created_at).toLocaleString('ru-RU')}
                                </Typography>
                                {item.action_data?.new_status && (
                                  <Typography component="span" variant="caption" color="text.secondary">
                                    {' → '}{STATUS_CONFIG[item.action_data.new_status]?.label}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">История взаимодействий пуста</Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Menu anchorEl={statusMenuAnchor} open={Boolean(statusMenuAnchor)} onClose={() => setStatusMenuAnchor(null)}>
        {STATUSES.map((s) => (
          <MenuItem
            key={s}
            onClick={() => updateStatusMutation.mutate(s)}
            disabled={candidate.status === s}
            sx={{ gap: 1 }}
          >
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: STATUS_CONFIG[s].color }} />
            {STATUS_CONFIG[s].label}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
}
