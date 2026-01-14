import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
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
} from '@mui/material';
import {
  GetApp as GetAppIcon,
  PictureAsPdf as PdfIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { searchAPI } from '../../../api/api';
import { queryKeys } from '../../../lib/query';

const ScoreBadge = ({ score, maxScore = 10 }) => {
  const getColor = () => {
    if (score >= 8) return 'success';
    if (score >= 6) return 'warning';
    return 'error';
  };

  return (
    <Chip
      label={`${score}/${maxScore}`}
      color={getColor()}
      size="small"
      sx={{ fontWeight: 600 }}
    />
  );
};

const MatchPercentage = ({ percentage }) => {
  const getColor = () => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1} mb={0.5}>
        <Typography variant="body2" fontWeight={600}>
          {percentage.toFixed(1)}%
        </Typography>
        <LinearProgress
          variant="determinate"
          value={percentage}
          color={getColor()}
          sx={{ flex: 1, height: 8, borderRadius: 4 }}
        />
      </Box>
    </Box>
  );
};

export default function ResultsPage() {
  const { searchId } = useParams();
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [sortBy, setSortBy] = useState('ai_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedResume, setSelectedResume] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);

  const { data: search, isLoading: searchLoading } = useQuery({
    queryKey: queryKeys.search.detail(searchId),
    queryFn: () => searchAPI.get(searchId),
    refetchInterval: (data) => {
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 2000;
      }
      return false;
    },
  });

  const { data: resumesData, isLoading: resumesLoading } = useQuery({
    queryKey: queryKeys.search.resumes(searchId),
    queryFn: () => searchAPI.getResumes(searchId, page + 1, pageSize, sortBy, sortOrder),
    enabled: !!searchId && (search?.status === 'completed' || search?.status === 'processing'),
  });

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

  const handleExportPdf = async () => {
    try {
      const response = await fetch(`/api/v1/search/${searchId}/export/pdf`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `search_${searchId}_report.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF export error:', error);
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
          <Tooltip title="Экспорт в PDF">
            <IconButton color="error" onClick={handleExportPdf}>
              <PdfIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>
                Статус
              </Typography>
              <Chip
                label={search.status === 'completed' ? 'Завершен' : search.status === 'processing' ? 'Обработка' : search.status}
                color={search.status === 'completed' ? 'success' : search.status === 'processing' ? 'info' : 'default'}
                size="small"
                sx={{ mt: 1, fontWeight: 600 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              border: '1px solid', 
              borderColor: 'divider',
              borderLeft: '4px solid',
              borderLeftColor: 'primary.main',
            }}
          >
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>
                Найдено резюме
              </Typography>
              <Typography variant="h4" fontWeight={700} color="primary.main" sx={{ mt: 0.5 }}>
                {search.total_found || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              border: '1px solid', 
              borderColor: 'divider',
              borderLeft: '4px solid',
              borderLeftColor: 'success.main',
            }}
          >
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>
                Проанализировано
              </Typography>
              <Typography variant="h4" fontWeight={700} color="success.main" sx={{ mt: 0.5 }}>
                {search.analyzed_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              border: '1px solid', 
              borderColor: 'divider',
              borderLeft: '4px solid',
              borderLeftColor: 'secondary.main',
            }}
          >
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>
                Средний AI Score
              </Typography>
              <Typography variant="h4" fontWeight={700} color="secondary.main" sx={{ mt: 0.5 }}>
                {resumesData?.resumes?.length > 0
                  ? (resumesData.resumes.reduce((sum, r) => sum + (r.ai_score || 0), 0) / resumesData.resumes.length).toFixed(1)
                  : '0.0'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {search.status === 'processing' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Поиск обрабатывается. Результаты появятся здесь, когда будут готовы.
        </Alert>
      )}

      {search.status === 'completed' && (
        <>
          <Box display="flex" gap={2} mb={3} flexWrap="wrap">
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel>Сортировать по</InputLabel>
              <Select
                value={sortBy}
                label="Сортировать по"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="ai_score">AI Score</MenuItem>
                <MenuItem value="match_percentage">Процент совпадения</MenuItem>
                <MenuItem value="preliminary_score">Предварительный Score</MenuItem>
                <MenuItem value="created_at">Дата создания</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Порядок</InputLabel>
              <Select
                value={sortOrder}
                label="Порядок"
                onChange={(e) => setSortOrder(e.target.value)}
              >
                <MenuItem value="desc">По убыванию</MenuItem>
                <MenuItem value="asc">По возрастанию</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {resumesLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : resumesData && resumesData.resumes ? (
            <>
              <TableContainer 
                component={Paper} 
                elevation={0}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  overflow: 'hidden',
                }}
              >
                <Table>
                  <TableHead>
                    <TableRow 
                      sx={{ 
                        bgcolor: 'primary.main',
                        '& .MuiTableCell-head': {
                          color: 'white',
                          fontWeight: 700,
                          fontSize: '0.875rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          py: 2,
                        },
                      }}
                    >
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
                          transition: 'all 0.2s ease',
                          '&:hover': { 
                            bgcolor: 'primary.main',
                            cursor: 'pointer',
                            '& .MuiTableCell-root': {
                              color: 'white',
                            },
                            '& .MuiChip-root': {
                              bgcolor: 'rgba(255,255,255,0.2)',
                              color: 'white',
                            },
                          },
                          '&:nth-of-type(even)': {
                            bgcolor: 'action.hover',
                          },
                        }}
                        onClick={() => {
                          setSelectedResume(resume);
                          setOpenDialog(true);
                        }}
                      >
                        <TableCell>
                          <Typography variant="body2" fontWeight={500}>
                            {resume.name || 'N/A'}
                          </Typography>
                          {resume.age && (
                            <Typography variant="caption" color="text.secondary">
                              {resume.age} лет
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>{resume.title || 'N/A'}</TableCell>
                        <TableCell>{resume.city || 'N/A'}</TableCell>
                        <TableCell>
                          {resume.salary
                            ? `${resume.salary.toLocaleString('ru-RU')} ${resume.currency || 'RUR'}`
                            : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {resume.ai_score ? (
                            <ScoreBadge score={resume.ai_score} />
                          ) : (
                            <Chip label="N/A" size="small" variant="outlined" />
                          )}
                        </TableCell>
                        <TableCell>
                          {resume.match_percentage ? (
                            <MatchPercentage percentage={resume.match_percentage} />
                          ) : (
                            'N/A'
                          )}
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Подробнее">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedResume(resume);
                                setOpenDialog(true);
                              }}
                            >
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
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
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={pageSize}
                onRowsPerPageChange={(e) => {
                  setPageSize(parseInt(e.target.value, 10));
                  setPage(0);
                }}
                rowsPerPageOptions={[10, 20, 50, 100]}
                labelRowsPerPage="Строк на странице:"
                labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
              />
            </>
          ) : (
            <Alert severity="info">Резюме не найдены</Alert>
          )}
        </>
      )}

      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle>
          <Typography variant="h5" fontWeight={600}>
            {selectedResume?.name || 'Кандидат'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {selectedResume?.title || 'N/A'} • {selectedResume?.city || 'N/A'}
          </Typography>
        </DialogTitle>
        <DialogContent dividers>
          {selectedResume && (
            <Box>
              <Grid container spacing={2} mb={3}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Возраст
                  </Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {selectedResume.age || 'N/A'} лет
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Зарплата
                  </Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {selectedResume.salary
                      ? `${selectedResume.salary.toLocaleString('ru-RU')} ${selectedResume.currency || 'RUR'}`
                      : 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    AI Score
                  </Typography>
                  {selectedResume.ai_score ? (
                    <ScoreBadge score={selectedResume.ai_score} />
                  ) : (
                    'N/A'
                  )}
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Совпадение
                  </Typography>
                  {selectedResume.match_percentage ? (
                    <MatchPercentage percentage={selectedResume.match_percentage} />
                  ) : (
                    'N/A'
                  )}
                </Grid>
              </Grid>

              {selectedResume.match_explanation && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom fontWeight={600} color="primary.main">
                    Объяснение совпадения
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {selectedResume.match_explanation}
                  </Typography>
                </>
              )}

              {selectedResume.strengths && selectedResume.strengths.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom fontWeight={600} color="success.main">
                    Сильные стороны
                  </Typography>
                  <Box display="flex" flexDirection="column" gap={1}>
                    {selectedResume.strengths.map((strength, idx) => (
                      <Box key={idx} display="flex" alignItems="start" gap={1}>
                        <CheckCircleIcon color="success" fontSize="small" sx={{ mt: 0.5 }} />
                        <Typography variant="body2">{strength}</Typography>
                      </Box>
                    ))}
                  </Box>
                </>
              )}

              {selectedResume.weaknesses && selectedResume.weaknesses.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom fontWeight={600} color="warning.main">
                    Области для улучшения
                  </Typography>
                  <Box display="flex" flexDirection="column" gap={1}>
                    {selectedResume.weaknesses.map((weakness, idx) => (
                      <Box key={idx} display="flex" alignItems="start" gap={1}>
                        <WarningIcon color="warning" fontSize="small" sx={{ mt: 0.5 }} />
                        <Typography variant="body2">{weakness}</Typography>
                      </Box>
                    ))}
                  </Box>
                </>
              )}

              {selectedResume.recommendation && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom fontWeight={600} color="info.main">
                    Рекомендация
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {selectedResume.recommendation}
                  </Typography>
                </>
              )}

              {selectedResume.red_flags && selectedResume.red_flags.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Alert severity="warning" icon={<WarningIcon />}>
                    <Typography variant="subtitle2" gutterBottom>
                      Предупреждения:
                    </Typography>
                    <ul style={{ margin: 0, paddingLeft: 20 }}>
                      {selectedResume.red_flags.map((flag, idx) => (
                        <li key={idx}>
                          <Typography variant="body2">{flag}</Typography>
                        </li>
                      ))}
                    </ul>
                  </Alert>
                </>
              )}

              {selectedResume.ai_summary && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    AI Резюме
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedResume.ai_summary}
                  </Typography>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
