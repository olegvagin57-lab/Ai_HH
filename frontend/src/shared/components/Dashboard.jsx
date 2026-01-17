import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  LinearProgress,
  Chip,
} from '@mui/material';
import {
  Search as SearchIcon,
  People as PeopleIcon,
  Work as WorkIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { searchAPI, analyticsAPI, notificationsAPI } from '../../api/api';
import { queryKeys } from '@/lib/query';

const StatCard = ({ title, value, icon, color, onClick, trend, trendValue }) => (
  <Card
    sx={{
      height: '100%',
      cursor: onClick ? 'pointer' : 'default',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: 4,
        bgcolor: color || 'primary.main',
      },
      '&:hover': onClick ? {
        transform: 'translateY(-8px)',
        boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
      } : {},
    }}
    onClick={onClick}
  >
    <CardContent sx={{ p: 3 }}>
      <Box display="flex" alignItems="flex-start" justifyContent="space-between">
        <Box sx={{ flex: 1 }}>
          <Typography 
            color="text.secondary" 
            gutterBottom 
            variant="body2" 
            fontWeight={500}
            sx={{ mb: 1.5 }}
          >
            {title}
          </Typography>
          <Typography 
            variant="h3" 
            fontWeight={700} 
            color={color || 'primary.main'}
            sx={{ mb: 1 }}
          >
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
        <Avatar
          sx={{
            bgcolor: `${color || 'primary.main'}15`,
            color: color || 'primary.main',
            width: 64,
            height: 64,
            boxShadow: `0 4px 12px ${color || 'primary.main'}30`,
          }}
        >
          {icon}
        </Avatar>
      </Box>
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const navigate = useNavigate();

  const { data: analytics } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: () => analyticsAPI.getDashboard(30),
  });

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsAPI.getNotifications(true, 1, 5),
  });

  const { data: recentSearches } = useQuery({
    queryKey: queryKeys.search.all,
    queryFn: () => searchAPI.list(1, 5),
  });

  const unreadCount = notifications?.unread_count || 0;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight={600}>
          Панель управления
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<NotificationsIcon />}
            onClick={() => navigate('/notifications')}
            sx={{ position: 'relative' }}
          >
            Уведомления
            {unreadCount > 0 && (
              <Chip
                label={unreadCount}
                size="small"
                color="error"
                sx={{
                  position: 'absolute',
                  top: -8,
                  right: -8,
                  height: 20,
                  minWidth: 20,
                  fontSize: '0.75rem',
                }}
              />
            )}
          </Button>
          <Button
            variant="contained"
            startIcon={<SearchIcon />}
            onClick={() => navigate('/search')}
          >
            Новый поиск
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Всего поисков"
            value={analytics?.searches?.total || 0}
            icon={<SearchIcon />}
            color="primary.main"
            onClick={() => navigate('/search')}
            trend="up"
            trendValue="12"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Активные вакансии"
            value={analytics?.vacancies?.active || 0}
            icon={<WorkIcon />}
            color="secondary.main"
            onClick={() => navigate('/vacancies')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Кандидаты"
            value={analytics?.candidates?.total || 0}
            icon={<PeopleIcon />}
            color="success.main"
            onClick={() => navigate('/candidates')}
            trend="up"
            trendValue="8"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Нанято"
            value={analytics?.candidates?.hired || 0}
            icon={<TrendingUpIcon />}
            color="info.main"
            trend="up"
            trendValue="15"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <Typography variant="h6" fontWeight={600}>
                  Воронка найма
                </Typography>
                <Chip 
                  label="30 дней" 
                  size="small" 
                  variant="outlined"
                  color="primary"
                />
              </Box>
              {analytics?.metrics && (
                <Box mt={2}>
                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Новые</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {analytics.candidates.by_status?.new || 0}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(analytics.candidates.by_status?.new || 0) / (analytics.candidates.total || 1) * 100}
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        bgcolor: 'action.hover',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 5,
                        },
                      }}
                      color="primary"
                    />
                  </Box>
                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">На рассмотрении</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {analytics.candidates.by_status?.reviewed || 0}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(analytics.candidates.by_status?.reviewed || 0) / (analytics.candidates.total || 1) * 100}
                      color="info"
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        bgcolor: 'action.hover',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 5,
                        },
                      }}
                    />
                  </Box>
                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Собеседование</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {analytics.candidates.by_status?.interviewed || 0}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(analytics.candidates.by_status?.interviewed || 0) / (analytics.candidates.total || 1) * 100}
                      color="warning"
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        bgcolor: 'action.hover',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 5,
                        },
                      }}
                    />
                  </Box>
                  <Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Нанято</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {analytics.candidates.by_status?.hired || 0}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(analytics.candidates.by_status?.hired || 0) / (analytics.candidates.total || 1) * 100}
                      color="success"
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        bgcolor: 'action.hover',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 5,
                        },
                      }}
                    />
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <Typography variant="h6" fontWeight={600}>
                  Последние поиски
                </Typography>
                <Button
                  size="small"
                  variant="text"
                  onClick={() => navigate('/search')}
                  sx={{ textTransform: 'none' }}
                >
                  Все
                </Button>
              </Box>
              {recentSearches?.searches?.length > 0 ? (
                <Box mt={2}>
                  {recentSearches.searches.slice(0, 5).map((search) => (
                    <Box
                      key={search.id}
                      onClick={() => navigate(`/results/${search.id}`)}
                      sx={{
                        p: 2,
                        mb: 1,
                        borderRadius: 2,
                        bgcolor: 'background.default',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          bgcolor: 'primary.main',
                          color: 'white',
                          transform: 'translateX(4px)',
                          '& .MuiTypography-root': {
                            color: 'white',
                          },
                        },
                      }}
                    >
                      <Typography variant="body2" fontWeight={500} noWrap>
                        {search.query}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {search.city} • {search.total_found} найдено
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary" mt={2}>
                  Нет недавних поисков
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
