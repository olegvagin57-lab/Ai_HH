import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Work as WorkIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../../../api/api';
import LoadingState from '../../../shared/components/LoadingState';

const StatCard = ({ title, value, icon, color, trend, trendValue }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="flex-start" justifyContent="space-between">
        <Box sx={{ flex: 1 }}>
          <Typography color="text.secondary" gutterBottom variant="body2" fontWeight={500}>
            {title}
          </Typography>
          <Typography variant="h3" fontWeight={700} color={color || 'primary.main'} sx={{ mb: 1 }}>
            {value}
          </Typography>
          {trend && trendValue && (
            <Box display="flex" alignItems="center" gap={0.5}>
              <TrendingUpIcon
                fontSize="small"
                sx={{
                  color: trend === 'up' ? 'success.main' : 'error.main',
                  transform: trend === 'down' ? 'rotate(180deg)' : 'none',
                }}
              />
              <Typography
                variant="caption"
                color={trend === 'up' ? 'success.main' : 'error.main'}
                fontWeight={600}
              >
                {trendValue}%
              </Typography>
            </Box>
          )}
        </Box>
        <Box
          sx={{
            bgcolor: `${color || 'primary.main'}15`,
            color: color || 'primary.main',
            borderRadius: 2,
            p: 1.5,
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['analytics', 'dashboard', days],
    queryFn: () => analyticsAPI.getDashboard(days),
  });

  const { data: funnel } = useQuery({
    queryKey: ['analytics', 'funnel', days],
    queryFn: () => analyticsAPI.getHiringFunnel(days),
  });

  if (isLoading) {
    return <LoadingState message="Загрузка аналитики..." />;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight={600}>
          Аналитика
        </Typography>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Период</InputLabel>
          <Select value={days} onChange={(e) => setDays(e.target.value)} label="Период">
            <MenuItem value={7}>7 дней</MenuItem>
            <MenuItem value={30}>30 дней</MenuItem>
            <MenuItem value={90}>90 дней</MenuItem>
            <MenuItem value={365}>Год</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Всего поисков"
            value={dashboard?.searches?.total || 0}
            icon={<AssessmentIcon />}
            color="primary.main"
            trend="up"
            trendValue="12"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Активные вакансии"
            value={dashboard?.vacancies?.active || 0}
            icon={<WorkIcon />}
            color="secondary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Кандидаты"
            value={dashboard?.candidates?.total || 0}
            icon={<PeopleIcon />}
            color="success.main"
            trend="up"
            trendValue="8"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Нанято"
            value={dashboard?.candidates?.hired || 0}
            icon={<TrendingUpIcon />}
            color="info.main"
            trend="up"
            trendValue="15"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Воронка найма
              </Typography>
              <Box mt={3}>
                {dashboard?.candidates?.by_status && (
                  <>
                    {Object.entries(dashboard.candidates.by_status).map(([status, count]) => (
                      <Box key={status} mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2">
                            {status === 'new' && 'Новые'}
                            {status === 'reviewed' && 'На рассмотрении'}
                            {status === 'interviewed' && 'Собеседование'}
                            {status === 'hired' && 'Наняты'}
                            {!['new', 'reviewed', 'interviewed', 'hired'].includes(status) && status}
                          </Typography>
                          <Typography variant="body2" fontWeight={600}>
                            {count}
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            height: 8,
                            bgcolor: 'action.hover',
                            borderRadius: 4,
                            overflow: 'hidden',
                          }}
                        >
                          <Box
                            sx={{
                              height: '100%',
                              width: `${(count / (dashboard.candidates.total || 1)) * 100}%`,
                              bgcolor: 'primary.main',
                              transition: 'width 0.3s ease',
                            }}
                          />
                        </Box>
                      </Box>
                    ))}
                  </>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Статистика по статусам
              </Typography>
              <Box mt={2}>
                {dashboard?.candidates?.by_status &&
                  Object.entries(dashboard.candidates.by_status).map(([status, count]) => (
                    <Box key={status} display="flex" justifyContent="space-between" mb={1.5}>
                      <Typography variant="body2">
                        {status === 'new' && 'Новые'}
                        {status === 'reviewed' && 'На рассмотрении'}
                        {status === 'interviewed' && 'Собеседование'}
                        {status === 'hired' && 'Наняты'}
                        {status === 'rejected' && 'Отклонены'}
                        {!['new', 'reviewed', 'interviewed', 'hired', 'rejected'].includes(status) && status}
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {count}
                      </Typography>
                    </Box>
                  ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
