import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Chip,
  Card,
  CardContent,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Paper,
} from '@mui/material';
import {
  Search as SearchIcon,
  ViewModule as ViewModuleIcon,
  ViewList as ViewListIcon,
  FilterList as FilterListIcon,
  Add as AddIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { candidatesAPI } from '../../../api/api';
import KanbanBoard from '../components/KanbanBoard';
import CandidatesList from '../components/CandidatesList';
import EmptyState from '../../../shared/components/EmptyState';
import LoadingState from '../../../shared/components/LoadingState';

const statusTabs = [
  { value: 'all', label: 'Все' },
  { value: 'new', label: 'Новые' },
  { value: 'reviewed', label: 'На рассмотрении' },
  { value: 'shortlisted', label: 'В шорт-листе' },
  { value: 'interview_scheduled', label: 'Собеседование назначено' },
  { value: 'interviewed', label: 'Прошли собеседование' },
  { value: 'offer_sent', label: 'Оффер отправлен' },
  { value: 'hired', label: 'Наняты' },
  { value: 'rejected', label: 'Отклонены' },
  { value: 'on_hold', label: 'На паузе' },
];

export default function CandidatesPage() {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState('kanban'); // 'kanban' or 'list'
  const [currentTab, setCurrentTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchor, setFilterAnchor] = useState(null);
  const [selectedTags, setSelectedTags] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState('');

  const { data: kanbanData, isLoading: kanbanLoading, refetch: refetchKanban } = useQuery({
    queryKey: ['candidates', 'kanban'],
    queryFn: () => candidatesAPI.getKanban(),
    enabled: viewMode === 'kanban',
  });

  const { data: candidatesByStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['candidates', 'status', currentTab],
    queryFn: () => candidatesAPI.getByStatus(currentTab, 1, 100),
    enabled: viewMode === 'list' && currentTab !== 'all',
  });

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };

  const filteredCandidates = candidatesByStatus?.candidates?.filter((candidate) => {
    if (searchQuery) {
      // TODO: Implement search by name, title, etc.
      return true;
    }
    return true;
  }) || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight={600}>
          Кандидаты
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant={viewMode === 'kanban' ? 'contained' : 'outlined'}
            startIcon={<ViewModuleIcon />}
            onClick={() => handleViewModeChange('kanban')}
            size="small"
          >
            Kanban
          </Button>
          <Button
            variant={viewMode === 'list' ? 'contained' : 'outlined'}
            startIcon={<ViewListIcon />}
            onClick={() => handleViewModeChange('list')}
            size="small"
          >
            Список
          </Button>
        </Box>
      </Box>

      {viewMode === 'list' && (
        <>
          <Box display="flex" gap={2} mb={3} flexWrap="wrap">
            <TextField
              placeholder="Поиск кандидатов..."
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

          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={currentTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              {statusTabs.map((tab) => (
                <Tab key={tab.value} label={tab.label} value={tab.value} />
              ))}
            </Tabs>
          </Paper>
        </>
      )}

      {viewMode === 'kanban' ? (
        kanbanLoading ? (
          <LoadingState message="Загрузка кандидатов..." />
        ) : (
          <KanbanBoard data={kanbanData} onUpdate={refetchKanban} />
        )
      ) : (
        statusLoading ? (
          <LoadingState message="Загрузка кандидатов..." />
        ) : filteredCandidates.length > 0 ? (
          <CandidatesList candidates={filteredCandidates} />
        ) : (
          <EmptyState
            icon={<PersonIcon sx={{ fontSize: 64, color: 'text.secondary' }} />}
            title="Кандидаты не найдены"
            description={
              currentTab === 'all'
                ? 'Начните поиск резюме, чтобы увидеть кандидатов здесь'
                : `Нет кандидатов со статусом "${statusTabs.find((t) => t.value === currentTab)?.label}"`
            }
            action={
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/search')}>
                Начать поиск
              </Button>
            }
          />
        )
      )}

      <Menu
        anchorEl={filterAnchor}
        open={Boolean(filterAnchor)}
        onClose={() => setFilterAnchor(null)}
      >
        <MenuItem>
          <FormControl fullWidth size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Папка</InputLabel>
            <Select
              value={selectedFolder}
              onChange={(e) => setSelectedFolder(e.target.value)}
              label="Папка"
            >
              <MenuItem value="">Все папки</MenuItem>
              <MenuItem value="favorites">Избранное</MenuItem>
              <MenuItem value="archive">Архив</MenuItem>
            </Select>
          </FormControl>
        </MenuItem>
      </Menu>
    </Box>
  );
}
