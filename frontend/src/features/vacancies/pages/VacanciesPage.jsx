import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  TextField,
  InputAdornment,
  Menu,
  MenuItem,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  Work as WorkIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vacanciesAPI } from '../../../api/api';
import VacancyForm from '../components/VacancyForm';
import EmptyState from '../../../shared/components/EmptyState';
import LoadingState from '../../../shared/components/LoadingState';

export default function VacanciesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState(null);
  const [filterAnchor, setFilterAnchor] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedVacancy, setSelectedVacancy] = useState(null);
  const [menuAnchor, setMenuAnchor] = useState(null);

  const { data: vacancies, isLoading } = useQuery({
    queryKey: ['vacancies', statusFilter],
    queryFn: () => vacanciesAPI.list(statusFilter),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => vacanciesAPI.updateStatus(id, 'closed'),
    onSuccess: () => {
      queryClient.invalidateQueries(['vacancies']);
      setMenuAnchor(null);
    },
  });

  const handleCreate = () => {
    setSelectedVacancy(null);
    setCreateDialogOpen(true);
  };

  const handleEdit = (vacancy) => {
    setSelectedVacancy(vacancy);
    setEditDialogOpen(true);
  };

  const handleDelete = (vacancy) => {
    if (window.confirm(`Вы уверены, что хотите закрыть вакансию "${vacancy.title}"?`)) {
      deleteMutation.mutate(vacancy.id);
    }
    setMenuAnchor(null);
  };

  const handleMenuOpen = (event, vacancy) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
    setSelectedVacancy(vacancy);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedVacancy(null);
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

  const filteredVacancies = vacancies?.vacancies?.filter((vacancy) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        vacancy.title?.toLowerCase().includes(query) ||
        vacancy.description?.toLowerCase().includes(query) ||
        vacancy.city?.toLowerCase().includes(query)
      );
    }
    return true;
  }) || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight={600}>
          Вакансии
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Создать вакансию
        </Button>
      </Box>

      <Box display="flex" gap={2} mb={3} flexWrap="wrap">
        <TextField
          placeholder="Поиск вакансий..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{ flexGrow: 1, minWidth: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <Button
          variant="outlined"
          startIcon={<FilterListIcon />}
          onClick={(e) => setFilterAnchor(e.currentTarget)}
          size="small"
        >
          Фильтры
        </Button>
      </Box>

      {isLoading ? (
        <LoadingState message="Загрузка вакансий..." />
      ) : filteredVacancies.length > 0 ? (
        <Grid container spacing={3}>
          {filteredVacancies.map((vacancy) => (
            <Grid item xs={12} md={6} lg={4} key={vacancy.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  },
                }}
                onClick={() => navigate(`/vacancies/${vacancy.id}`)}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box flex={1}>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        {vacancy.title}
                      </Typography>
                      <Chip
                        label={getStatusLabel(vacancy.status)}
                        color={getStatusColor(vacancy.status)}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, vacancy)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </Box>

                  {vacancy.city && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      📍 {vacancy.city}
                      {vacancy.remote && ' • Удаленно'}
                    </Typography>
                  )}

                  {vacancy.salary_min && vacancy.salary_max && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      💰 {vacancy.salary_min} - {vacancy.salary_max} {vacancy.currency || 'RUB'}
                    </Typography>
                  )}

                  {vacancy.description && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mt: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {vacancy.description}
                    </Typography>
                  )}

                  {vacancy.candidate_ids && vacancy.candidate_ids.length > 0 && (
                    <Box mt={2}>
                      <Typography variant="caption" color="text.secondary">
                        Кандидатов: {vacancy.candidate_ids.length}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <EmptyState
          icon={<WorkIcon sx={{ fontSize: 64, color: 'text.secondary' }} />}
          title="Вакансии не найдены"
          description={
            searchQuery || statusFilter
              ? 'Попробуйте изменить параметры поиска'
              : 'Создайте первую вакансию, чтобы начать работу'
          }
          action={
            <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
              Создать вакансию
            </Button>
          }
        />
      )}

      <Menu anchorEl={filterAnchor} open={Boolean(filterAnchor)} onClose={() => setFilterAnchor(null)}>
        <MenuItem onClick={() => { setStatusFilter(null); setFilterAnchor(null); }}>
          Все статусы
        </MenuItem>
        <MenuItem onClick={() => { setStatusFilter('active'); setFilterAnchor(null); }}>
          Активные
        </MenuItem>
        <MenuItem onClick={() => { setStatusFilter('paused'); setFilterAnchor(null); }}>
          Приостановленные
        </MenuItem>
        <MenuItem onClick={() => { setStatusFilter('closed'); setFilterAnchor(null); }}>
          Закрытые
        </MenuItem>
        <MenuItem onClick={() => { setStatusFilter('filled'); setFilterAnchor(null); }}>
          Закрытые (найдена)
        </MenuItem>
      </Menu>

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={handleMenuClose}>
        <MenuItem onClick={() => { handleEdit(selectedVacancy); handleMenuClose(); }}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Редактировать
        </MenuItem>
        <MenuItem onClick={() => handleDelete(selectedVacancy)}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Закрыть
        </MenuItem>
      </Menu>

      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Создать вакансию</DialogTitle>
        <DialogContent>
          <VacancyForm
            onSuccess={() => {
              setCreateDialogOpen(false);
              queryClient.invalidateQueries(['vacancies']);
            }}
            onCancel={() => setCreateDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Редактировать вакансию</DialogTitle>
        <DialogContent>
          <VacancyForm
            vacancy={selectedVacancy}
            onSuccess={() => {
              setEditDialogOpen(false);
              queryClient.invalidateQueries(['vacancies']);
            }}
            onCancel={() => setEditDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
}
