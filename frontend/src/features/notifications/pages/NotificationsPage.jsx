import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Button,
  Tabs,
  Tab,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Circle as CircleIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsAPI } from '../../../api/api';
import EmptyState from '../../../shared/components/EmptyState';
import LoadingState from '../../../shared/components/LoadingState';

export default function NotificationsPage() {
  const [currentTab, setCurrentTab] = useState(0);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const queryClient = useQueryClient();

  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications', currentTab === 0],
    queryFn: () => notificationsAPI.getNotifications(currentTab === 0, 1, 100),
  });

  const markAsReadMutation = useMutation({
    mutationFn: (id) => notificationsAPI.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      setMenuAnchor(null);
    },
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationsAPI.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => notificationsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      setMenuAnchor(null);
    },
  });

  const handleMenuOpen = (event, notification) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
    setSelectedNotification(notification);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedNotification(null);
  };

  const handleMarkAsRead = () => {
    if (selectedNotification) {
      markAsReadMutation.mutate(selectedNotification.id);
    }
  };

  const handleDelete = () => {
    if (selectedNotification) {
      deleteMutation.mutate(selectedNotification.id);
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      candidate_found: <CircleIcon />,
      auto_match: <CircleIcon />,
      comment: <CircleIcon />,
      status_change: <CircleIcon />,
    };
    return icons[type] || <NotificationsIcon />;
  };

  const getNotificationColor = (type) => {
    const colors = {
      candidate_found: 'primary',
      auto_match: 'info',
      comment: 'warning',
      status_change: 'success',
    };
    return colors[type] || 'default';
  };

  const filteredNotifications = notifications?.notifications || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight={600}>
          Уведомления
        </Typography>
        {currentTab === 0 && filteredNotifications.length > 0 && (
          <Button
            variant="outlined"
            onClick={() => markAllAsReadMutation.mutate()}
            disabled={markAllAsReadMutation.isLoading}
          >
            Пометить все как прочитанные
          </Button>
        )}
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)}>
          <Tab label={`Непрочитанные (${notifications?.unread_count || 0})`} />
          <Tab label="Все" />
        </Tabs>
      </Paper>

      {isLoading ? (
        <LoadingState message="Загрузка уведомлений..." />
      ) : filteredNotifications.length > 0 ? (
        <Card>
          <List>
            {filteredNotifications.map((notification) => (
              <ListItem
                key={notification.id}
                sx={{
                  bgcolor: notification.is_read ? 'background.paper' : 'action.hover',
                  borderLeft: notification.is_read ? 'none' : '4px solid',
                  borderColor: 'primary.main',
                }}
                secondaryAction={
                  <IconButton
                    edge="end"
                    onClick={(e) => handleMenuOpen(e, notification)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  {notification.is_read ? (
                    <CheckCircleIcon color="action" />
                  ) : (
                    getNotificationIcon(notification.type)
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle2" fontWeight={notification.is_read ? 400 : 600}>
                        {notification.title}
                      </Typography>
                      <Chip
                        label={notification.type}
                        size="small"
                        color={getNotificationColor(notification.type)}
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="text.secondary">
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(notification.created_at).toLocaleString('ru-RU')}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Card>
      ) : (
        <EmptyState
          icon={<NotificationsIcon sx={{ fontSize: 64, color: 'text.secondary' }} />}
          title={
            currentTab === 0 ? 'Нет непрочитанных уведомлений' : 'Нет уведомлений'
          }
          description={
            currentTab === 0
              ? 'Все уведомления прочитаны'
              : 'Уведомления появятся здесь, когда будут новые события'
          }
        />
      )}

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={handleMenuClose}>
        {!selectedNotification?.is_read && (
          <MenuItem onClick={handleMarkAsRead}>
            <CheckCircleIcon fontSize="small" sx={{ mr: 1 }} />
            Пометить как прочитанное
          </MenuItem>
        )}
        <MenuItem onClick={handleDelete}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Удалить
        </MenuItem>
      </Menu>
    </Box>
  );
}
