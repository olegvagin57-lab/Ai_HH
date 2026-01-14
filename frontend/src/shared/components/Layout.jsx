import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Search as SearchIcon,
  People as PeopleIcon,
  Work as WorkIcon,
  Assessment as AssessmentIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
import { useAuth } from '../../features/auth/contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { notificationsAPI } from '../../api/api';

const drawerWidth = 280;

const menuItems = [
  { text: 'Панель управления', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Поиск резюме', icon: <SearchIcon />, path: '/search' },
  { text: 'Кандидаты', icon: <PeopleIcon />, path: '/candidates' },
  { text: 'Вакансии', icon: <WorkIcon />, path: '/vacancies' },
  { text: 'Аналитика', icon: <AssessmentIcon />, path: '/analytics' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsAPI.getNotifications(true, 1, 1),
    refetchInterval: 30000, // Обновлять каждые 30 секунд
  });

  const unreadCount = notifications?.unread_count || 0;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box 
        sx={{ 
          p: 3, 
          bgcolor: 'primary.main', 
          color: 'white',
          background: 'linear-gradient(135deg, #003366 0%, #0066CC 100%)',
        }}
      >
        <Typography variant="h6" fontWeight={700} gutterBottom>
          HH Resume Analyzer
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.75rem' }}>
          Система подбора персонала
        </Typography>
      </Box>
      <Box sx={{ flex: 1, overflow: 'auto', pt: 1 }}>
        <List>
          {menuItems.map((item) => (
            <ListItem
              key={item.path}
              button
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                setMobileOpen(false);
              }}
              sx={{
                mx: 1,
                mb: 0.5,
                borderRadius: 2,
                transition: 'all 0.2s ease',
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: 'white',
                  boxShadow: '0 2px 8px rgba(0, 51, 102, 0.3)',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                    transform: 'translateX(4px)',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  bgcolor: 'action.hover',
                  transform: 'translateX(4px)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path ? 'white' : 'text.secondary',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{
                  fontWeight: location.pathname === item.path ? 600 : 500,
                  fontSize: '0.95rem',
                }}
              />
            </ListItem>
          ))}
        </List>
        <Divider sx={{ my: 1, mx: 2 }} />
        {user?.role_names?.includes('admin') && (
          <List>
            <ListItem
              button
              selected={location.pathname === '/admin'}
              onClick={() => {
                navigate('/admin');
                setMobileOpen(false);
              }}
              sx={{
                mx: 1,
                mb: 0.5,
                borderRadius: 2,
                transition: 'all 0.2s ease',
                '&.Mui-selected': {
                  bgcolor: 'error.main',
                  color: 'white',
                  boxShadow: '0 2px 8px rgba(229, 57, 53, 0.3)',
                  '&:hover': {
                    bgcolor: 'error.dark',
                    transform: 'translateX(4px)',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  bgcolor: 'action.hover',
                  transform: 'translateX(4px)',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <AdminIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Администрирование"
                primaryTypographyProps={{
                  fontWeight: location.pathname === '/admin' ? 600 : 500,
                  fontSize: '0.95rem',
                }}
              />
            </ListItem>
          </List>
        )}
      </Box>
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Box display="flex" alignItems="center" gap={1.5} mb={1}>
          <Avatar
            sx={{ 
              width: 40, 
              height: 40, 
              bgcolor: 'primary.main',
              fontWeight: 600,
            }}
          >
            {(user?.username || user?.email || 'U').charAt(0).toUpperCase()}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight={600} noWrap>
              {user?.username || user?.email || 'Пользователь'}
            </Typography>
            {user?.role_names && user.role_names.length > 0 && (
              <Box display="flex" gap={0.5} mt={0.5}>
                {user.role_names.slice(0, 2).map((role) => (
                  <Chip 
                    key={role} 
                    label={role} 
                    size="small" 
                    sx={{ 
                      height: 18,
                      fontSize: '0.65rem',
                      '& .MuiChip-label': { px: 0.75 },
                    }}
                  />
                ))}
              </Box>
            )}
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        elevation={1}
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          zIndex: (theme) => theme.zIndex.drawer + 1,
          bgcolor: 'background.paper',
          color: 'text.primary',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ px: { xs: 2, sm: 3 } }}>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              flexGrow: 1,
              fontWeight: 600,
              color: 'text.primary',
            }}
          >
            {menuItems.find((item) => item.path === location.pathname)?.text || 'HH Resume Analyzer'}
          </Typography>
          <IconButton
            color="inherit"
            onClick={() => navigate('/notifications')}
            sx={{ 
              mr: 1,
              color: 'text.secondary',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <Box display="flex" alignItems="center" gap={1}>
            <IconButton
              onClick={handleMenuOpen}
              sx={{ 
                p: 0.5,
                '&:hover': { bgcolor: 'action.hover' },
              }}
            >
              <Avatar
                sx={{ 
                  width: 36, 
                  height: 36, 
                  bgcolor: 'primary.main',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {(user?.username || user?.email || 'U').charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              PaperProps={{
                sx: {
                  mt: 1.5,
                  minWidth: 200,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                  borderRadius: 2,
                },
              }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                <Typography variant="body2" fontWeight={600} noWrap>
                  {user?.username || user?.email}
                </Typography>
                {user?.role_names && user.role_names.length > 0 && (
                  <Box display="flex" gap={0.5} mt={0.5} flexWrap="wrap">
                    {user.role_names.map((role) => (
                      <Chip 
                        key={role} 
                        label={role} 
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                )}
              </Box>
              <MenuItem 
                onClick={() => { navigate('/settings'); handleMenuClose(); }}
                sx={{ py: 1.5 }}
              >
                <ListItemIcon>
                  <SettingsIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Настройки" />
              </MenuItem>
              <MenuItem onClick={handleLogout} sx={{ py: 1.5 }}>
                <ListItemIcon>
                  <LogoutIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Выход" />
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, sm: 3, md: 4 },
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: { xs: 7, sm: 8 },
          bgcolor: 'background.default',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 0, sm: 2 } }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}

