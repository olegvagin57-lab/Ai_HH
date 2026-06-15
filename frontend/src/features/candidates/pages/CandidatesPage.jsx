import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  Avatar,
  Divider,
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
  Badge,
  Paper,
  Skeleton,
  Menu,
} from '@mui/material';
import {
  Search as SearchIcon,
  ViewList as ViewListIcon,
  ViewModule as ViewModuleIcon,
  WorkOutline as WorkIcon,
  LocationOn as LocationIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  MoreVert as MoreVertIcon,
  OpenInNew as OpenInNewIcon,
  Person as PersonIcon,
  FilterList as FilterListIcon,
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesAPI } from '../../../api/api';

const STATUS_CONFIG = {
  new:                  { label: 'Новый',              color: '#2563eb', bg: '#eff6ff' },
  reviewed:             { label: 'На рассмотрении',    color: '#7c3aed', bg: '#f5f3ff' },
  shortlisted:          { label: 'Шорт-лист',          color: '#d97706', bg: '#fffbeb' },
  interview_scheduled:  { label: 'Назначено собесед.', color: '#0891b2', bg: '#ecfeff' },
  interviewed:          { label: 'Собеседование',      color: '#059669', bg: '#ecfdf5' },
  offer_sent:           { label: 'Оффер отправлен',    color: '#16a34a', bg: '#f0fdf4' },
  hired:                { label: 'Нанят',              color: '#15803d', bg: '#dcfce7' },
  rejected:             { label: 'Отклонён',           color: '#dc2626', bg: '#fef2f2' },
  on_hold:              { label: 'На паузе',           color: '#6b7280', bg: '#f9fafb' },
};

const SORT_OPTIONS = [
  { value: 'ai_score_desc',      label: 'AI-оценка ↓' },
  { value: 'ai_score_asc',       label: 'AI-оценка ↑' },
  { value: 'match_desc',         label: 'Совпадение ↓' },
  { value: 'created_desc',       label: 'Дата добавления ↓' },
];

function ScoreBadge({ score }) {
  const color = score >= 8 ? '#16a34a' : score >= 6 ? '#d97706' : score >= 4 ? '#2563eb' : '#dc2626';
  const bg   = score >= 8 ? '#dcfce7' : score >= 6 ? '#fef3c7' : score >= 4 ? '#dbeafe' : '#fee2e2';
  return (
    <Box
      sx={{
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        width: 44, height: 44, borderRadius: '50%',
        bgcolor: bg, border: `2px solid ${color}`, flexShrink: 0,
      }}
    >
      <Typography variant="subtitle2" fontWeight={700} sx={{ color, fontSize: '0.85rem', lineHeight: 1 }}>
        {score}
      </Typography>
    </Box>
  );
}

function MatchBar({ value }) {
  const color = value >= 80 ? '#16a34a' : value >= 60 ? '#d97706' : '#94a3b8';
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Box sx={{ flex: 1, height: 4, borderRadius: 2, bgcolor: '#e2e8f0', overflow: 'hidden' }}>
        <Box sx={{ height: '100%', width: `${Math.min(value, 100)}%`, bgcolor: color, borderRadius: 2, transition: 'width 0.4s ease' }} />
      </Box>
      <Typography variant="caption" sx={{ color, fontWeight: 600, minWidth: 32 }}>
        {Math.round(value)}%
      </Typography>
    </Box>
  );
}

function StatusChip({ status }) {
  const cfg = STATUS_CONFIG[status] || { label: status, color: '#6b7280', bg: '#f9fafb' };
  return (
    <Box
      component="span"
      sx={{
        display: 'inline-block',
        px: 1.5, py: 0.25,
        borderRadius: '999px',
        bgcolor: cfg.bg,
        color: cfg.color,
        fontSize: '0.7rem',
        fontWeight: 600,
        border: `1px solid ${cfg.color}22`,
        letterSpacing: '0.02em',
        whiteSpace: 'nowrap',
      }}
    >
      {cfg.label}
    </Box>
  );
}

function CandidateCard({ candidate, onStatusChange }) {
  const navigate = useNavigate();
  const [menuAnchor, setMenuAnchor] = useState(null);

  const title = candidate.title || 'Специалист';
  const location = [candidate.city, candidate.age ? `${candidate.age} лет` : null].filter(Boolean).join(' · ');
  const hasScore = candidate.ai_score != null;
  const hasMatch = candidate.match_percentage != null;

  return (
    <Card
      elevation={0}
      sx={{
        border: '1px solid #e2e8f0',
        borderRadius: 2,
        transition: 'all 0.18s ease',
        '&:hover': { borderColor: '#94a3b8', boxShadow: '0 4px 16px rgba(0,0,0,0.08)', transform: 'translateY(-1px)' },
      }}
    >
      <CardActionArea
        onClick={() => navigate(`/candidates/${candidate.resume_id}`)}
        sx={{ p: 0, borderRadius: 2 }}
      >
        <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
          <Box display="flex" alignItems="flex-start" gap={2}>
            {/* Score circle */}
            {hasScore ? (
              <ScoreBadge score={candidate.ai_score} />
            ) : (
              <Avatar sx={{ width: 44, height: 44, bgcolor: '#f1f5f9', color: '#94a3b8', flexShrink: 0 }}>
                <PersonIcon sx={{ fontSize: 22 }} />
              </Avatar>
            )}

            {/* Main content */}
            <Box flex={1} minWidth={0}>
              <Box display="flex" alignItems="flex-start" justifyContent="space-between" gap={1} mb={0.5}>
                <Typography
                  variant="subtitle1"
                  fontWeight={600}
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    lineHeight: 1.3,
                    fontSize: '0.925rem',
                    color: '#0f172a',
                  }}
                >
                  {title}
                </Typography>
                <StatusChip status={candidate.status} />
              </Box>

              {location && (
                <Box display="flex" alignItems="center" gap={0.5} mb={1}>
                  <LocationIcon sx={{ fontSize: 13, color: '#94a3b8' }} />
                  <Typography variant="caption" color="text.secondary">
                    {location}
                  </Typography>
                </Box>
              )}

              {hasMatch && (
                <Box mb={1}>
                  <MatchBar value={candidate.match_percentage} />
                </Box>
              )}

              {candidate.tags?.length > 0 && (
                <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                  {candidate.tags.slice(0, 4).map((tag, i) => (
                    <Box
                      key={i}
                      component="span"
                      sx={{
                        px: 1, py: 0.2,
                        borderRadius: '4px',
                        bgcolor: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        fontSize: '0.68rem',
                        color: '#475569',
                      }}
                    >
                      {tag}
                    </Box>
                  ))}
                  {candidate.tags.length > 4 && (
                    <Typography variant="caption" color="text.secondary">+{candidate.tags.length - 4}</Typography>
                  )}
                </Box>
              )}
            </Box>

            {/* Actions */}
            <IconButton
              size="small"
              sx={{ mt: -0.5, flexShrink: 0 }}
              onClick={(e) => { e.stopPropagation(); setMenuAnchor(e.currentTarget); }}
            >
              <MoreVertIcon fontSize="small" sx={{ color: '#94a3b8' }} />
            </IconButton>
          </Box>
        </CardContent>
      </CardActionArea>

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={() => setMenuAnchor(null)}>
        {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
          <MenuItem
            key={key}
            disabled={candidate.status === key}
            onClick={() => { onStatusChange(candidate.resume_id, key); setMenuAnchor(null); }}
            sx={{ fontSize: '0.85rem' }}
          >
            <Box component="span" sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: cfg.color, mr: 1.5, display: 'inline-block' }} />
            {cfg.label}
          </MenuItem>
        ))}
      </Menu>
    </Card>
  );
}

function StatPill({ label, count, color, onClick, active }) {
  return (
    <Box
      onClick={onClick}
      sx={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        px: 2.5, py: 1.5, borderRadius: 2, cursor: 'pointer', minWidth: 80,
        bgcolor: active ? `${color}15` : 'transparent',
        border: active ? `1.5px solid ${color}` : '1.5px solid #e2e8f0',
        transition: 'all 0.15s',
        '&:hover': { bgcolor: `${color}10`, borderColor: color },
      }}
    >
      <Typography sx={{ fontSize: '1.4rem', fontWeight: 700, color: active ? color : '#1e293b', lineHeight: 1.1 }}>
        {count}
      </Typography>
      <Typography variant="caption" sx={{ color: '#64748b', mt: 0.3, textAlign: 'center', lineHeight: 1.2, fontSize: '0.68rem' }}>
        {label}
      </Typography>
    </Box>
  );
}

export default function CandidatesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('ai_score_desc');

  const { data, isLoading } = useQuery({
    queryKey: ['candidates', 'all'],
    queryFn: () => candidatesAPI.getAll(1, 200),
    staleTime: 30_000,
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ resumeId, status }) => candidatesAPI.updateStatus(resumeId, status),
    onSuccess: () => queryClient.invalidateQueries(['candidates']),
  });

  const allCandidates = data?.candidates || [];

  // Count by status
  const counts = useMemo(() => {
    const c = { all: allCandidates.length };
    allCandidates.forEach((x) => { c[x.status] = (c[x.status] || 0) + 1; });
    return c;
  }, [allCandidates]);

  // Filter + sort
  const visible = useMemo(() => {
    let list = allCandidates;
    if (statusFilter !== 'all') list = list.filter((c) => c.status === statusFilter);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((c) =>
        (c.title || '').toLowerCase().includes(q) ||
        (c.city || '').toLowerCase().includes(q) ||
        (c.tags || []).some((t) => t.toLowerCase().includes(q))
      );
    }
    const [field, dir] = sortBy.split('_');
    const asc = dir === 'asc';
    list = [...list].sort((a, b) => {
      let av = field === 'ai' ? (a.ai_score ?? 0) : field === 'match' ? (a.match_percentage ?? 0) : 0;
      let bv = field === 'ai' ? (b.ai_score ?? 0) : field === 'match' ? (b.match_percentage ?? 0) : 0;
      return asc ? av - bv : bv - av;
    });
    return list;
  }, [allCandidates, statusFilter, search, sortBy]);

  const statuses = ['new', 'reviewed', 'shortlisted', 'interview_scheduled', 'interviewed', 'offer_sent', 'hired', 'rejected', 'on_hold'];
  const mainStatuses = ['new', 'reviewed', 'shortlisted', 'hired', 'rejected'];

  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto' }}>
      {/* Header */}
      <Box display="flex" alignItems="baseline" gap={2} mb={3}>
        <Typography variant="h4" fontWeight={700} color="#0f172a">
          Кандидаты
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isLoading ? '...' : `${allCandidates.length} в базе`}
        </Typography>
      </Box>

      {/* Status summary pills */}
      {isLoading ? (
        <Box display="flex" gap={1.5} mb={3} flexWrap="wrap">
          {[...Array(6)].map((_, i) => <Skeleton key={i} variant="rounded" width={80} height={60} />)}
        </Box>
      ) : (
        <Paper elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2, p: 2, mb: 3 }}>
          <Box display="flex" gap={1.5} flexWrap="wrap">
            <StatPill
              label="Все"
              count={counts.all || 0}
              color="#2563eb"
              active={statusFilter === 'all'}
              onClick={() => setStatusFilter('all')}
            />
            {mainStatuses.map((s) => (
              <StatPill
                key={s}
                label={STATUS_CONFIG[s].label}
                count={counts[s] || 0}
                color={STATUS_CONFIG[s].color}
                active={statusFilter === s}
                onClick={() => setStatusFilter(s)}
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Filters row */}
      <Box display="flex" gap={2} mb={3} flexWrap="wrap" alignItems="center">
        <TextField
          placeholder="Поиск по должности, городу, тегам..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          sx={{ flex: '1 1 280px', minWidth: 220, '& .MuiOutlinedInput-root': { borderRadius: '10px' } }}
          InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: '#94a3b8', fontSize: 20 }} /></InputAdornment> }}
        />

        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Статус</InputLabel>
          <Select
            value={statusFilter}
            label="Статус"
            onChange={(e) => setStatusFilter(e.target.value)}
            sx={{ borderRadius: '10px' }}
          >
            <MenuItem value="all">Все статусы</MenuItem>
            {statuses.map((s) => (
              <MenuItem key={s} value={s}>{STATUS_CONFIG[s].label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 170 }}>
          <InputLabel>Сортировка</InputLabel>
          <Select
            value={sortBy}
            label="Сортировка"
            onChange={(e) => setSortBy(e.target.value)}
            sx={{ borderRadius: '10px' }}
          >
            {SORT_OPTIONS.map((o) => (
              <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto', whiteSpace: 'nowrap' }}>
          {visible.length} из {allCandidates.length}
        </Typography>
      </Box>

      {/* Candidates grid */}
      {isLoading ? (
        <Grid container spacing={2}>
          {[...Array(6)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Skeleton variant="rounded" height={140} />
            </Grid>
          ))}
        </Grid>
      ) : visible.length === 0 ? (
        <Box
          sx={{
            textAlign: 'center', py: 10,
            border: '2px dashed #e2e8f0', borderRadius: 3,
          }}
        >
          <PersonIcon sx={{ fontSize: 56, color: '#cbd5e1', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {allCandidates.length === 0 ? 'Ещё нет кандидатов' : 'Ничего не найдено'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {allCandidates.length === 0
              ? 'Откройте страницу результатов и добавьте кандидата в вакансию'
              : 'Попробуйте изменить фильтры или поисковый запрос'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {visible.map((candidate) => (
            <Grid item xs={12} sm={6} md={4} key={candidate.resume_id}>
              <CandidateCard
                candidate={candidate}
                onStatusChange={(resumeId, status) =>
                  updateStatusMutation.mutate({ resumeId, status })
                }
              />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
