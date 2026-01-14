import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import {
  AccountCircle as AccountCircleIcon,
  Lock as LockIcon,
  Email as EmailIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (formData.password.length < 8) {
      setError('Пароль должен содержать минимум 8 символов');
      return;
    }

    setLoading(true);

    try {
      // Register user
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
      });
      
      // Automatically login after registration
      console.log('Registration successful, auto-login...');
      await login(formData.email, formData.password);
      console.log('Auto-login successful');
      
      navigate('/dashboard');
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail) && errorDetail.length > 0) {
        setError(errorDetail[0].msg || 'Ошибка регистрации');
      } else {
        setError(err.response?.data?.detail || err.response?.data?.message || 'Ошибка регистрации');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #003366 0%, #0066CC 100%)',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          opacity: 0.1,
        },
      }}
    >
      <Container maxWidth="sm">
        <Card
          elevation={0}
          sx={{
            borderRadius: 4,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: 'divider',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
          }}
        >
          <Box
            sx={{
              background: 'linear-gradient(135deg, #003366 0%, #0066CC 100%)',
              color: 'white',
              p: 4,
              textAlign: 'center',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -50,
                right: -50,
                width: 200,
                height: 200,
                borderRadius: '50%',
                bgcolor: 'rgba(255,255,255,0.1)',
              },
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: -30,
                left: -30,
                width: 150,
                height: 150,
                borderRadius: '50%',
                bgcolor: 'rgba(255,255,255,0.08)',
              },
            }}
          >
            <Typography 
              variant="h4" 
              component="h1" 
              fontWeight={700} 
              gutterBottom
              sx={{ position: 'relative', zIndex: 1 }}
            >
              Регистрация
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                opacity: 0.95,
                position: 'relative',
                zIndex: 1,
              }}
            >
              Создайте аккаунт для начала работы
            </Typography>
          </Box>
          <CardContent sx={{ p: 4 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                margin="normal"
                value={formData.email}
                onChange={handleChange}
                required
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'background.paper',
                  },
                }}
                InputProps={{
                  startAdornment: <EmailIcon sx={{ mr: 1.5, color: 'primary.main' }} />,
                }}
              />
              <TextField
                fullWidth
                label="Имя пользователя"
                name="username"
                margin="normal"
                value={formData.username}
                onChange={handleChange}
                required
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'background.paper',
                  },
                }}
                InputProps={{
                  startAdornment: <PersonIcon sx={{ mr: 1.5, color: 'primary.main' }} />,
                }}
              />
              <TextField
                fullWidth
                label="Пароль"
                name="password"
                type="password"
                margin="normal"
                value={formData.password}
                onChange={handleChange}
                required
                helperText="Минимум 8 символов"
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'background.paper',
                  },
                }}
                InputProps={{
                  startAdornment: <LockIcon sx={{ mr: 1.5, color: 'primary.main' }} />,
                }}
              />
              <TextField
                fullWidth
                label="Подтвердите пароль"
                name="confirmPassword"
                type="password"
                margin="normal"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'background.paper',
                  },
                }}
                InputProps={{
                  startAdornment: <LockIcon sx={{ mr: 1.5, color: 'primary.main' }} />,
                }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ 
                  mt: 4, 
                  mb: 2, 
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(0, 51, 102, 0.3)',
                  '&:hover': {
                    boxShadow: '0 6px 16px rgba(0, 51, 102, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Зарегистрироваться'}
              </Button>
              <Box textAlign="center">
                <Link to="/login" style={{ textDecoration: 'none' }}>
                  <Typography variant="body2" color="primary" sx={{ '&:hover': { textDecoration: 'underline' } }}>
                    Уже есть аккаунт? Войти
                  </Typography>
                </Link>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}
