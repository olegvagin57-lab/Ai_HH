import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  Grid,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesAPI } from '../../../api/api';
import { useNavigate } from 'react-router-dom';

const statusConfig = {
  new: { label: 'Новые', color: 'primary' },
  reviewed: { label: 'На рассмотрении', color: 'info' },
  shortlisted: { label: 'В шорт-листе', color: 'warning' },
  interview_scheduled: { label: 'Собеседование', color: 'secondary' },
  interviewed: { label: 'Прошли собеседование', color: 'secondary' },
  offer_sent: { label: 'Оффер отправлен', color: 'success' },
  hired: { label: 'Наняты', color: 'success' },
  rejected: { label: 'Отклонены', color: 'error' },
  on_hold: { label: 'На паузе', color: 'default' },
};

export default function KanbanBoard({ data, onUpdate }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const updateStatusMutation = useMutation({
    mutationFn: ({ resumeId, status }) => candidatesAPI.updateStatus(resumeId, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidates', 'kanban']);
      onUpdate?.();
      setAnchorEl(null);
    },
  });

  const handleMenuOpen = (event, candidate) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedCandidate(candidate);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCandidate(null);
  };

  const handleStatusChange = (newStatus) => {
    if (selectedCandidate) {
      updateStatusMutation.mutate({
        resumeId: selectedCandidate.resume_id,
        status: newStatus,
      });
    }
  };

  const handleCardClick = (candidate) => {
    navigate(`/candidates/${candidate.resume_id}`);
  };

  if (!data) {
    return (
      <Box textAlign="center" py={8}>
        <Typography color="text.secondary">Нет данных для отображения</Typography>
      </Box>
    );
  }

  const statuses = Object.keys(statusConfig);

  return (
    <Box sx={{ overflowX: 'auto', pb: 2 }}>
      <Grid container spacing={2} sx={{ minWidth: statuses.length * 320 }}>
        {statuses.map((status) => {
          const config = statusConfig[status];
          const candidates = data[status] || [];
          
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} key={status} sx={{ minWidth: 300 }}>
              <Paper
                sx={{
                  height: 'calc(100vh - 250px)',
                  display: 'flex',
                  flexDirection: 'column',
                  bgcolor: 'background.default',
                }}
              >
                <Box
                  sx={{
                    p: 2,
                    bgcolor: `${config.color}.main`,
                    color: 'white',
                    borderRadius: '4px 4px 0 0',
                  }}
                >
                  <Typography variant="h6" fontWeight={600}>
                    {config.label}
                  </Typography>
                  <Chip
                    label={candidates.length}
                    size="small"
                    sx={{
                      mt: 1,
                      bgcolor: 'rgba(255,255,255,0.2)',
                      color: 'white',
                    }}
                  />
                </Box>
                <Box
                  sx={{
                    flex: 1,
                    overflowY: 'auto',
                    p: 2,
                    '&::-webkit-scrollbar': {
                      width: '8px',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      bgcolor: 'divider',
                      borderRadius: '4px',
                    },
                  }}
                >
                  {candidates.length === 0 ? (
                    <Box
                      sx={{
                        textAlign: 'center',
                        py: 4,
                        color: 'text.secondary',
                      }}
                    >
                      <Typography variant="body2">Нет кандидатов</Typography>
                    </Box>
                  ) : (
                    candidates.map((candidate) => (
                      <Card
                        key={candidate.resume_id}
                        sx={{
                          mb: 2,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: 3,
                          },
                        }}
                        onClick={() => handleCardClick(candidate)}
                      >
                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                            <Box flex={1}>
                              <Typography variant="subtitle2" fontWeight={600} noWrap>
                                {candidate.name || 'Без имени'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary" noWrap>
                                {candidate.title || 'Без должности'}
                              </Typography>
                            </Box>
                            <IconButton
                              size="small"
                              onClick={(e) => handleMenuOpen(e, candidate)}
                              sx={{ ml: 1 }}
                            >
                              <MoreVertIcon fontSize="small" />
                            </IconButton>
                          </Box>
                          {candidate.match_percentage && (
                            <Chip
                              label={`${Math.round(candidate.match_percentage)}%`}
                              size="small"
                              color={candidate.match_percentage >= 80 ? 'success' : candidate.match_percentage >= 60 ? 'warning' : 'default'}
                              sx={{ mb: 1, height: 20, fontSize: '0.7rem' }}
                            />
                          )}
                          {candidate.tags && candidate.tags.length > 0 && (
                            <Box display="flex" gap={0.5} flexWrap="wrap" mt={1}>
                              {candidate.tags.slice(0, 2).map((tag, idx) => (
                                <Chip
                                  key={idx}
                                  label={tag}
                                  size="small"
                                  variant="outlined"
                                  sx={{ height: 20, fontSize: '0.65rem' }}
                                />
                              ))}
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  )}
                </Box>
              </Paper>
            </Grid>
          );
        })}
      </Grid>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        {statuses.map((status) => (
          <MenuItem
            key={status}
            onClick={() => handleStatusChange(status)}
            disabled={selectedCandidate?.status === status}
          >
            {statusConfig[status].label}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
}
