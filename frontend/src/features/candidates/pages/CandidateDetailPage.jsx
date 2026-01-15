import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Avatar,
  Grid,
  Divider,
  TextField,
  IconButton,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Rating,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Star as StarIcon,
  Label as LabelIcon,
  Folder as FolderIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesAPI, searchAPI } from '../../../api/api';
import LoadingState from '../../../shared/components/LoadingState';
import EmptyState from '../../../shared/components/EmptyState';

export default function CandidateDetailPage() {
  const { resumeId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentTab, setCurrentTab] = useState(0);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState(null);
  const [tagInput, setTagInput] = useState('');
  const [showTagInput, setShowTagInput] = useState(false);
  const [notes, setNotes] = useState('');
  const [rating, setRating] = useState(0);
  const [isEditingNotes, setIsEditingNotes] = useState(false);

  const { data: candidate, isLoading: candidateLoading } = useQuery({
    queryKey: ['candidate', resumeId],
    queryFn: () => candidatesAPI.get(resumeId),
  });

  // Note: Resume data should be fetched from search results
  // For now, we'll use candidate data and try to find resume in search results
  const { data: searches } = useQuery({
    queryKey: ['searches'],
    queryFn: () => searchAPI.list(1, 100),
  });

  const resume = React.useMemo(() => {
    if (!searches?.searches) return null;
    // Find resume in all search results
    for (const search of searches.searches) {
      // This is a simplified approach - in production, you'd want a direct endpoint
      // to get resume by ID
    }
    return null;
  }, [searches]);

  const { data: interactions } = useQuery({
    queryKey: ['candidate', resumeId, 'interactions'],
    queryFn: () => candidatesAPI.getInteractions(resumeId),
    enabled: !!resumeId,
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status) => candidatesAPI.updateStatus(resumeId, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidate', resumeId]);
      queryClient.invalidateQueries(['candidates']);
      setStatusMenuAnchor(null);
    },
  });

  const addTagMutation = useMutation({
    mutationFn: (tag) => candidatesAPI.addTag(resumeId, tag),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidate', resumeId]);
      setTagInput('');
      setShowTagInput(false);
    },
  });

  const removeTagMutation = useMutation({
    mutationFn: (tag) => candidatesAPI.removeTag(resumeId, tag),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidate', resumeId]);
    },
  });

  const updateNotesMutation = useMutation({
    mutationFn: (notes) => candidatesAPI.updateNotes(resumeId, notes),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidate', resumeId]);
      setIsEditingNotes(false);
    },
  });

  const addRatingMutation = useMutation({
    mutationFn: (rating) => candidatesAPI.addRating(resumeId, rating),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidate', resumeId]);
    },
  });

  React.useEffect(() => {
    if (candidate) {
      setNotes(candidate.notes || '');
      setRating(candidate.average_rating || 0);
    }
  }, [candidate]);

  const handleStatusChange = (newStatus) => {
    updateStatusMutation.mutate(newStatus);
  };

  const handleAddTag = () => {
    if (tagInput.trim()) {
      addTagMutation.mutate(tagInput.trim());
    }
  };

  const handleRemoveTag = (tag) => {
    removeTagMutation.mutate(tag);
  };

  const handleSaveNotes = () => {
    updateNotesMutation.mutate(notes);
  };

  const handleRatingChange = (newRating) => {
    setRating(newRating);
    addRatingMutation.mutate(newRating);
  };

  const getStatusColor = (status) => {
    const colors = {
      new: 'primary',
      reviewed: 'info',
      shortlisted: 'warning',
      interview_scheduled: 'secondary',
      interviewed: 'secondary',
      offer_sent: 'success',
      hired: 'success',
      rejected: 'error',
      on_hold: 'default',
    };
    return colors[status] || 'default';
  };

  const getStatusLabel = (status) => {
    const labels = {
      new: 'Новый',
      reviewed: 'На рассмотрении',
      shortlisted: 'В шорт-листе',
      interview_scheduled: 'Собеседование назначено',
      interviewed: 'Прошли собеседование',
      offer_sent: 'Оффер отправлен',
      hired: 'Нанят',
      rejected: 'Отклонен',
      on_hold: 'На паузе',
    };
    return labels[status] || status;
  };

  if (candidateLoading) {
    return <LoadingState message="Загрузка данных кандидата..." />;
  }

  if (!candidate) {
    return (
      <EmptyState
        icon={<PersonIcon sx={{ fontSize: 64, color: 'text.secondary' }} />}
        title="Кандидат не найден"
        description="Кандидат с указанным ID не существует"
        action={
          <Button variant="contained" onClick={() => navigate('/candidates')}>
            Вернуться к списку
          </Button>
        }
      />
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={4}>
        <IconButton onClick={() => navigate('/candidates')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" fontWeight={600}>
          Профиль кандидата
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
                <Avatar sx={{ width: 120, height: 120, bgcolor: 'primary.main', mb: 2 }}>
                  <PersonIcon sx={{ fontSize: 60 }} />
                </Avatar>
                <Typography variant="h5" fontWeight={600}>
                  Кандидат #{resumeId.slice(0, 8)}
                </Typography>
                <Typography variant="body2" color="text.secondary" mt={1}>
                  Resume ID: {resumeId}
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Статус
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip
                    label={getStatusLabel(candidate.status)}
                    color={getStatusColor(candidate.status)}
                    size="small"
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => setStatusMenuAnchor(e.currentTarget)}
                  >
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Оценка
                </Typography>
                <Rating
                  value={rating}
                  onChange={(event, newValue) => handleRatingChange(newValue)}
                  size="large"
                />
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Теги
                  </Typography>
                  <IconButton size="small" onClick={() => setShowTagInput(!showTagInput)}>
                    <LabelIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Box display="flex" gap={0.5} flexWrap="wrap" mb={1}>
                  {candidate.tags?.map((tag, idx) => (
                    <Chip
                      key={idx}
                      label={tag}
                      size="small"
                      onDelete={() => handleRemoveTag(tag)}
                      variant="outlined"
                    />
                  ))}
                </Box>
                {showTagInput && (
                  <Box display="flex" gap={1}>
                    <TextField
                      size="small"
                      placeholder="Добавить тег"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleAddTag();
                        }
                      }}
                    />
                    <Button size="small" onClick={handleAddTag}>
                      Добавить
                    </Button>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} sx={{ mb: 3 }}>
                <Tab label="Информация" />
                <Tab label="AI Анализ" />
                <Tab label="Заметки" />
                <Tab label="История" />
              </Tabs>

              {currentTab === 0 && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Детальная информация о резюме будет доступна после интеграции с поиском резюме.
                  </Typography>
                  <Box mt={2}>
                    <Typography variant="subtitle2" gutterBottom>
                      Resume ID
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {resumeId}
                    </Typography>
                  </Box>
                </Box>
              )}

              {currentTab === 1 && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    AI-анализ резюме будет доступен после интеграции с поиском резюме.
                  </Typography>
                </Box>
              )}

              {currentTab === 2 && (
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
                        fullWidth
                        multiline
                        rows={6}
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Добавьте заметки о кандидате..."
                      />
                      <Box display="flex" gap={1} mt={2}>
                        <Button variant="contained" onClick={handleSaveNotes}>
                          Сохранить
                        </Button>
                        <Button onClick={() => setIsEditingNotes(false)}>
                          Отмена
                        </Button>
                      </Box>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {notes || 'Заметок пока нет. Нажмите на иконку редактирования, чтобы добавить.'}
                    </Typography>
                  )}
                </Box>
              )}

              {currentTab === 3 && (
                <Box>
                  {interactions?.interactions?.length > 0 ? (
                    <List>
                      {interactions.interactions.map((interaction) => (
                        <ListItem key={interaction.id}>
                          <ListItemText
                            primary={interaction.action_type}
                            secondary={new Date(interaction.created_at).toLocaleString('ru-RU')}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      История взаимодействий пуста
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Menu
        anchorEl={statusMenuAnchor}
        open={Boolean(statusMenuAnchor)}
        onClose={() => setStatusMenuAnchor(null)}
      >
        {['new', 'reviewed', 'shortlisted', 'interview_scheduled', 'interviewed', 'offer_sent', 'hired', 'rejected', 'on_hold'].map((status) => (
          <MenuItem
            key={status}
            onClick={() => handleStatusChange(status)}
            disabled={candidate.status === status}
          >
            {getStatusLabel(status)}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
}
