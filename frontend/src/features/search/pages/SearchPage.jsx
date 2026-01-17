import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  Chip,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  History as HistoryIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  GetApp as GetAppIcon,
} from '@mui/icons-material';
import { searchAPI } from '../../../api/api';
import { queryKeys } from '@/lib/query';

const StatusChip = ({ status }) => {
  const getColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'Завершен';
      case 'processing':
        return 'Обработка';
      case 'failed':
        return 'Ошибка';
      default:
        return status;
    }
  };

  return <Chip label={getLabel(status)} color={getColor(status)} size="small" />;
};

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [city, setCity] = useState('Москва');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const { data: searches, refetch } = useQuery({
    queryKey: queryKeys.search.all,
    queryFn: () => searchAPI.list(1, 20),
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('Creating search:', { query, city });
      const search = await searchAPI.create(query, city);
      console.log('Search created:', search);
      refetch();
      navigate(`/results/${search.id}`);
    } catch (err) {
      console.error('Search creation error:', err);
      console.error('Error response:', err.response);
      const errorMessage = err.response?.data?.detail || 
                          (Array.isArray(err.response?.data?.detail) 
                            ? err.response.data.detail.map(d => d.msg || d).join(', ')
                            : err.response?.data?.message) || 
                          err.message || 
                          'Ошибка при создании поиска';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Поиск резюме
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={4}>
        Введите запрос для поиска подходящих кандидатов на HeadHunter
      </Typography>

      <Card 
        elevation={0}
        sx={{ 
          mb: 4,
          border: '1px solid',
          borderColor: 'divider',
          background: 'linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%)',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mb: 3,
                borderRadius: 2,
              }}
              onClose={() => setError('')}
            >
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Поисковый запрос"
                  placeholder="Например: Python разработчик с опытом работы FastAPI и MongoDB"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  required
                  helperText="Опишите требования к кандидату максимально подробно"
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'background.paper',
                      '&:hover': {
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    },
                  }}
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1.5, color: 'primary.main' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Город"
                  placeholder="Москва"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  required
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'background.paper',
                    },
                  }}
                />
              </Grid>
            </Grid>
            <Box mt={4} display="flex" gap={2} flexWrap="wrap">
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading || !query || !city}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
                sx={{ 
                  minWidth: 200,
                  px: 4,
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(0, 51, 102, 0.3)',
                  '&:hover': {
                    boxShadow: '0 6px 16px rgba(0, 51, 102, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                {loading ? 'Поиск...' : 'Начать поиск'}
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => {
                  setQuery('');
                  setCity('Москва');
                }}
                disabled={loading}
                sx={{
                  px: 3,
                  py: 1.5,
                }}
              >
                Очистить
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {searches && searches.searches && searches.searches.length > 0 && (
        <Box>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h5" fontWeight={600}>
              История поисков
            </Typography>
            <Chip
              icon={<HistoryIcon />}
              label={`${searches.total || 0} поисков`}
              variant="outlined"
            />
          </Box>

          <Grid container spacing={2}>
            {searches.searches.map((search) => (
              <Grid item xs={12} md={6} key={search.id}>
                <Card
                  sx={{
                    height: '100%',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    border: '1px solid',
                    borderColor: 'divider',
                    cursor: 'pointer',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 3,
                      bgcolor: search.status === 'completed' ? 'success.main' : 
                              search.status === 'processing' ? 'info.main' : 'warning.main',
                    },
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                      borderColor: 'primary.main',
                    },
                  }}
                  onClick={() => navigate(`/results/${search.id}`)}
                >
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                      <Typography variant="h6" fontWeight={500} sx={{ flex: 1, mr: 2 }}>
                        {search.query}
                      </Typography>
                      <StatusChip status={search.status} />
                    </Box>
                    <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                      <Chip
                        label={`📍 ${search.city}`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={`Найдено: ${search.total_found || 0}`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                      <Chip
                        label={`Проанализировано: ${search.analyzed_count || 0}`}
                        size="small"
                        variant="outlined"
                        color="success"
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Создан: {new Date(search.created_at).toLocaleString('ru-RU')}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                    <Tooltip title="Просмотреть результаты">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/results/${search.id}`);
                        }}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Экспорт Excel">
                      <IconButton
                        size="small"
                        color="success"
                        onClick={async (e) => {
                          e.stopPropagation();
                          try {
                            const blob = await searchAPI.exportExcel(search.id);
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `search_${search.id}_results.xlsx`;
                            a.click();
                            window.URL.revokeObjectURL(url);
                          } catch (error) {
                            console.error('Export error:', error);
                          }
                        }}
                      >
                        <GetAppIcon />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
}
