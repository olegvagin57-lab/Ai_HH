import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  LinearProgress,
  Divider,
  IconButton,
  Tooltip,
  Paper,
  Slider,
  Collapse,
  Snackbar,
} from '@mui/material';
import {
  GetApp as GetAppIcon,
  PictureAsPdf as PdfIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  OpenInNew as OpenInNewIcon,
  PersonAdd as PersonAddIcon,
  FilterList as FilterListIcon,
} from '@mui/icons-material';
import { searchAPI, vacanciesAPI } from '../../../api/api';
import { queryKeys } from '@/lib/query';

const ScoreBadge = ({ score, maxScore = 10 }) => {
  const color = score >= 8 ? 'success' : score >= 6 ? 'warning' : 'error';
  return <Chip label={`${score}/${maxScore}`} color={color} size="small" sx={{ fontWeight: 600 }} />;
};

const MatchBar = ({ percentage }) => {
  const color = percentage >= 80 ? 'success' : percentage >= 60 ? 'warning' : 'error';
  return (
    <Box display="flex" alignItems="center" gap={1}>
      <Typography variant="body2" fontWeight={600} minWidth={45}>{percentage.toFixed(1)}%</Typography>
      <LinearProgress variant="determinate" value={percentage} color={color} sx={{ flex: 1, height: 8, borderRadius: 4 }} />
    </Box>
  );
};

export default function ResultsPage() {
  const { searchId } = useParams();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [sortBy, setSortBy] = useState('ai_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedResume, setSelectedResume] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [minScore, setMinScore] = useState(0);
  const [addToVacancyOpen, setAddToVacancyOpen] = useState(false);
  const [selectedVacancyId, setSelectedVacancyId] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleSortChange = (field) => {
    setSortBy(field);
    setPage(0);
  };

  const handleSortOrderChange = (order) => {
    setSortOrder(order);
    setPage(0);
  };

  const handleMinScoreChange = (val) => {
    setMinScore(val);
    setPage(0);
  };

  const { data: search, isLoading: searchLoading } = useQuery({
    queryKey: queryKeys.search.detail(searchId),
    queryFn: () => searchAPI.get(searchId),
    enabled: !!searchId,
    refetchInterval: (data) => {
      if (data?.status === 'processing' || data?.status === 'pending') return 2000;
      return false;
    },
  });

  const { data: resumesData, isLoading: resumesLoading } = useQuery({
    queryKey: [...queryKeys.search.resumes(searchId), page, pageSize, sortBy, sortOrder, minScore],
    queryFn: () => searchAPI.getResumes(searchId, page + 1, pageSize, sortBy, sortOrder, minScore || undefined),
    enabled: !!searchId && (search?.status === 'completed' || search?.status === 'processing'),
    placeholderData: keepPreviousData,
  });

  const { data: vacanciesData } = useQuery({
    queryKey: ['vacancies', 'active'],
    queryFn: () => vacanciesAPI.list('active', 1, 50),
    enabled: addToVacancyOpen,
  });

  const addCandidateMutation = useMutation({
    mutationFn: ({ vacancyId, resumeId }) => vacanciesAPI.addCandidate(vacancyId, resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries(['vacancy', selectedVacancyId, 'candidates']);
      setAddToVacancyOpen(false);
      setSelectedVacancyId('');
      setSnackbar({ open: true, message: 'Кандидат добавлен к вакансии', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Ошибка при добавлении кандидата', severity: 'error' });
    },
  });

  const handleAddToVacancy = () => {
    if (!selectedVacancyId || !selectedResume) return;
    addCandidateMutation.mutate({ vacancyId: selectedVacancyId, resumeId: selectedResume.id });
  };

  const handleExportExcel = async () => {
    try {
      const blob = await searchAPI.exportExcel(searchId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `search_${searchId}_results.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  if (searchLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!search) {
    return <Alert severity="error">Поиск не найден</Alert>;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Результаты поиска
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {search.query} • {search.city}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Экспорт в Excel">
            <IconButton color="success" onClick={handleExportExcel}>
              <GetAppIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>Статус</Typography>
              <Chip
                label={search.status === 'completed' ? 'Завершен' : search.status === 'processing' ? 'Обработка' : search.status}
                color={search.status === 'completed' ? 'success' : search.status === 'processing' ? 'info' : 'default'}
                size="small" sx={{ mt: 1, fontWeight: 600 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid', borderColor: 'divider', borderLeft: '4px solid', borderLeftColor: 'primary.main' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>Найдено резюме</Typography>
              <Typography variant="h4" fontWeight={700} color="primary.main" sx={{ mt: 0.5 }}>{search.total_found || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid', borderColor: 'divider', borderLeft: '4px solid', borderLeftColor: 'success.main' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>Проанализировано</Typography>
              <Typography variant="h4" fontWeight={700} color="success.main" sx={{ mt: 0.5 }}>{search.analyzed_count || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid', borderColor: 'divider', borderLeft: '4px solid', borderLeftColor: 'secondary.main' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>Средний AI Score</Typography>
              <Typography variant="h4" fontWeight={700} color="secondary.main" sx={{ mt: 0.5 }}>
                {resumesData?.resumes?.length > 0
                  ? (resumesData.resumes.reduce((sum, r) => sum + (r.ai_score || 0), 0) / resumesData.resumes.length).toFixed(1)
                  : '0.0'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {(search.status === 'processing' || search.status === 'pending') && search.total_to_process > 0 && (
        <Card sx={{ mb: 3, border: '1px solid', borderColor: 'divider' }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body1" fontWeight={600}>Обработка поиска</Typography>
              <Typography variant="body2" color="text.secondary">{search.processed_count || 0} / {search.total_to_process}</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={search.total_to_process > 0 ? ((search.processed_count || 0) / search.total_to_process) * 100 : 0}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </CardContent>
        </Card>
      )}

      {search.status === 'completed' && (
        <>
          <Box display="flex" gap={2} mb={2} flexWrap="wrap" alignItems="center">
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel>Сортировать по</InputLabel>
              <Select value={sortBy} label="Сортировать по" onChange={(e) => handleSortChange(e.target.value)}>
                <MenuItem value="ai_score">AI Score</MenuItem>
                <MenuItem value="match_percentage">Процент совпадения</MenuItem>
                <MenuItem value="created_at">Дата создания</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Порядок</InputLabel>
              <Select value={sortOrder} label="Порядок" onChange={(e) => handleSortOrderChange(e.target.value)}>
                <MenuItem value="desc">По убыванию</MenuItem>
                <MenuItem value="asc">По возрастанию</MenuItem>
              </Select>
            </FormControl>
            <Button
              size="small"
              variant={showFilters ? 'contained' : 'outlined'}
              startIcon={<FilterListIcon />}
              onClick={() => setShowFilters(!showFilters)}
            >
              Фильтры {minScore > 0 ? `(score ≥ ${minScore})` : ''}
            </Button>
            {minScore > 0 && (
              <Button size="small" color="error" onClick={() => handleMinScoreChange(0)}>Сбросить</Button>
            )}
          </Box>

          <Collapse in={showFilters}>
            <Paper variant="outlined" sx={{ p: 2.5, mb: 2, borderRadius: 2 }}>
              <Typography variant="body2" fontWeight={600} gutterBottom>Минимальный AI Score: {minScore || 'не задан'}</Typography>
              <Slider
                value={minScore}
                min={0} max={10} step={1}
                marks={[{value:0,label:'0'},{value:5,label:'5'},{value:8,label:'8'},{value:10,label:'10'}]}
                onChange={(_, val) => handleMinScoreChange(val)}
                sx={{ maxWidth: 400, mt: 1 }}
              />
            </Paper>
          </Collapse>

          {resumesLoading ? (
            <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
          ) : resumesData?.resumes ? (
            <>
              <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, overflow: 'hidden' }}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'primary.main', '& .MuiTableCell-head': { color: 'white', fontWeight: 700, fontSize: '0.875rem', py: 2 } }}>
                      <TableCell>Кандидат</TableCell>
                      <TableCell>Должность</TableCell>
                      <TableCell>Город</TableCell>
                      <TableCell>Зарплата</TableCell>
                      <TableCell>AI Score</TableCell>
                      <TableCell>Совпадение</TableCell>
                      <TableCell align="center">Действия</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {resumesData.resumes.map((resume) => (
                      <TableRow
                        key={resume.id}
                        hover
                        sx={{
                          cursor: 'pointer',
                          '&:nth-of-type(even)': { bgcolor: 'action.hover' },
                        }}
                        onClick={() => { setSelectedResume(resume); setOpenDialog(true); }}
                      >
                        <TableCell>
                          <Typography variant="body2" fontWeight={500}>{resume.name || 'Анонимный кандидат'}</Typography>
                          {resume.age && <Typography variant="caption" color="text.secondary">{resume.age} лет</Typography>}
                        </TableCell>
                        <TableCell>{resume.title || '—'}</TableCell>
                        <TableCell>{resume.city || '—'}</TableCell>
                        <TableCell>
                          {resume.salary ? `${Number(resume.salary).toLocaleString('ru-RU')} ${resume.currency || 'RUR'}` : '—'}
                        </TableCell>
                        <TableCell>
                          {resume.ai_score ? <ScoreBadge score={resume.ai_score} /> : <Chip label="—" size="small" variant="outlined" />}
                        </TableCell>
                        <TableCell sx={{ minWidth: 140 }}>
                          {resume.match_percentage ? <MatchBar percentage={resume.match_percentage} /> : '—'}
                        </TableCell>
                        <TableCell align="center">
                          <Box display="flex" gap={0.5} justifyContent="center">
                            {resume.hh_url && (
                              <Tooltip title="Открыть на HeadHunter">
                                <IconButton size="small" color="success" onClick={(e) => { e.stopPropagation(); window.open(resume.hh_url, '_blank'); }}>
                                  <OpenInNewIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            <Tooltip title="Подробнее / добавить к вакансии">
                              <IconButton size="small" color="primary" onClick={(e) => { e.stopPropagation(); setSelectedResume(resume); setOpenDialog(true); }}>
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

              <TablePagination
                component="div"
                count={resumesData.total || 0}
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                rowsPerPage={pageSize}
                onRowsPerPageChange={(e) => { setPageSize(parseInt(e.target.value, 10)); setPage(0); }}
                rowsPerPageOptions={[10, 20, 50, 100]}
                labelRowsPerPage="Строк на странице:"
                labelDisplayedRows={({ from, to, count }) => `${from}–${to} из ${count}`}
              />
            </>
          ) : (
            <Alert severity="info">Резюме не найдены</Alert>
          )}
        </>
      )}

      {/* Resume detail dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="start">
            <Box>
              <Typography variant="h5" fontWeight={600}>{selectedResume?.name || 'Анонимный кандидат'}</Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedResume?.title || '—'} • {selectedResume?.city || '—'}
              </Typography>
            </Box>
            <Box display="flex" gap={1}>
              {selectedResume?.hh_url && (
                <Button variant="outlined" color="success" size="small" startIcon={<OpenInNewIcon />}
                  onClick={() => window.open(selectedResume.hh_url, '_blank')}>
                  HH.ru
                </Button>
              )}
              <Button variant="contained" size="small" startIcon={<PersonAddIcon />}
                onClick={() => { setAddToVacancyOpen(true); }}>
                В вакансию
              </Button>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedResume && (
            <Box>
              <Grid container spacing={2} mb={3}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Возраст</Typography>
                  <Typography variant="body1" fontWeight={500}>{selectedResume.age ? `${selectedResume.age} лет` : '—'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Зарплата</Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {selectedResume.salary ? `${Number(selectedResume.salary).toLocaleString('ru-RU')} ${selectedResume.currency || 'RUR'}` : '—'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">AI Score</Typography>
                  {selectedResume.ai_score ? <ScoreBadge score={selectedResume.ai_score} /> : <Typography>—</Typography>}
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Совпадение</Typography>
                  {selectedResume.match_percentage ? <MatchBar percentage={selectedResume.match_percentage} /> : <Typography>—</Typography>}
                </Grid>
              </Grid>

              {selectedResume.match_explanation && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600} color="primary.main">Объяснение совпадения</Typography>
                <Typography variant="body1" paragraph>{selectedResume.match_explanation}</Typography></>
              )}

              {selectedResume.strengths?.length > 0 && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600} color="success.main">Сильные стороны</Typography>
                {selectedResume.strengths.map((s, i) => (
                  <Box key={i} display="flex" alignItems="start" gap={1} mb={0.5}>
                    <CheckCircleIcon color="success" fontSize="small" sx={{ mt: 0.3 }} />
                    <Typography variant="body2">{s}</Typography>
                  </Box>
                ))}</>
              )}

              {selectedResume.weaknesses?.length > 0 && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600} color="warning.main">Области для улучшения</Typography>
                {selectedResume.weaknesses.map((w, i) => (
                  <Box key={i} display="flex" alignItems="start" gap={1} mb={0.5}>
                    <WarningIcon color="warning" fontSize="small" sx={{ mt: 0.3 }} />
                    <Typography variant="body2">{w}</Typography>
                  </Box>
                ))}</>
              )}

              {selectedResume.recommendation && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600} color="info.main">Рекомендация</Typography>
                <Typography variant="body1" paragraph>{selectedResume.recommendation}</Typography></>
              )}

              {selectedResume.red_flags?.length > 0 && (
                <><Divider sx={{ my: 2 }} />
                <Alert severity="warning">
                  <Typography variant="subtitle2" gutterBottom>Предупреждения:</Typography>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {selectedResume.red_flags.map((flag, i) => (
                      <li key={i}><Typography variant="body2">{flag}</Typography></li>
                    ))}
                  </ul>
                </Alert></>
              )}

              {selectedResume.ai_questions?.length > 0 && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600} color="secondary.main">Вопросы для собеседования</Typography>
                <Box component="ul" sx={{ pl: 3, m: 0 }}>
                  {selectedResume.ai_questions.map((q, i) => (
                    <li key={i}><Typography variant="body2" paragraph>{q}</Typography></li>
                  ))}
                </Box></>
              )}

              {selectedResume.evaluation_details && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600}>Детальная оценка</Typography>
                <Grid container spacing={2}>
                  {['technical_skills', 'experience', 'education', 'soft_skills'].map((key) => {
                    const detail = selectedResume.evaluation_details[key];
                    if (!detail) return null;
                    const labels = { technical_skills: 'Технические навыки', experience: 'Опыт работы', education: 'Образование', soft_skills: 'Гибкие навыки' };
                    return (
                      <Grid item xs={12} md={6} key={key}>
                        <Card variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="subtitle2" fontWeight={600} gutterBottom>{labels[key]}</Typography>
                          <Typography variant="h6" color="primary.main" gutterBottom>{detail.score}/10</Typography>
                          <Typography variant="body2" color="text.secondary">{detail.details || detail.explanation}</Typography>
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid></>
              )}

              {selectedResume.ai_summary && (
                <><Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom fontWeight={600}>AI Резюме</Typography>
                <Typography variant="body2" color="text.secondary">{selectedResume.ai_summary}</Typography></>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>

      {/* Add to vacancy dialog */}
      <Dialog open={addToVacancyOpen} onClose={() => setAddToVacancyOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Добавить к вакансии</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Кандидат: <b>{selectedResume?.title || 'Анонимный кандидат'}</b>
          </Typography>
          <FormControl fullWidth size="small">
            <InputLabel>Выберите вакансию</InputLabel>
            <Select value={selectedVacancyId} label="Выберите вакансию" onChange={(e) => setSelectedVacancyId(e.target.value)}>
              {(vacanciesData?.vacancies || []).map((v) => (
                <MenuItem key={v.id} value={v.id}>{v.title}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddToVacancyOpen(false)}>Отмена</Button>
          <Button
            variant="contained"
            onClick={handleAddToVacancy}
            disabled={!selectedVacancyId || addCandidateMutation.isPending}
          >
            Добавить
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />
    </Box>
  );
}
