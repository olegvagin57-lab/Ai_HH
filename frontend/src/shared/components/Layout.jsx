import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import { useAuth } from '../../features/auth/contexts/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            HH Resume Analyzer
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.username || user?.email}
          </Typography>
          <Button color="inherit" onClick={() => navigate('/search')}>
            Search
          </Button>
          {user?.role_names?.includes('admin') && (
            <Button color="inherit" onClick={() => navigate('/admin')}>
              Admin
            </Button>
          )}
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
