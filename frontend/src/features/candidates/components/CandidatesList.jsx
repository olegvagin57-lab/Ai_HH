import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Star as StarIcon,
  Person as PersonIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesAPI } from '../../../api/api';

export default function CandidatesList({ candidates }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const updateStatusMutation = useMutation({
    mutationFn: ({ resumeId, status }) => candidatesAPI.updateStatus(resumeId, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['candidates']);
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

  if (candidates.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Typography color="text.secondary">Кандидаты не найдены</Typography>
      </Box>
    );
  }

  return (
    <>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Кандидат</TableCell>
              <TableCell>Должность</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Оценка</TableCell>
              <TableCell>Теги</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {candidates.map((candidate) => (
              <TableRow
                key={candidate.resume_id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/candidates/${candidate.resume_id}`)}
              >
                <TableCell>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <PersonIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight={500}>
                        {candidate.name || 'Без имени'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {candidate.email || 'Нет email'}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {candidate.title || 'Без должности'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getStatusLabel(candidate.status)}
                    color={getStatusColor(candidate.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {candidate.average_rating ? (
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <StarIcon fontSize="small" sx={{ color: 'warning.main' }} />
                      <Typography variant="body2">{candidate.average_rating.toFixed(1)}</Typography>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Нет оценки
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {candidate.tags?.slice(0, 3).map((tag, idx) => (
                      <Chip key={idx} label={tag} size="small" variant="outlined" />
                    ))}
                    {candidate.tags?.length > 3 && (
                      <Chip label={`+${candidate.tags.length - 3}`} size="small" />
                    )}
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, candidate)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={() => navigate(`/candidates/${selectedCandidate?.resume_id}`)}>
          <VisibilityIcon fontSize="small" sx={{ mr: 1 }} />
          Просмотр
        </MenuItem>
        <MenuItem onClick={() => handleStatusChange('reviewed')}>
          Изменить статус
        </MenuItem>
      </Menu>
    </>
  );
}
