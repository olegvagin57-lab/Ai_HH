import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  InputAdornment,
  IconButton,
  Checkbox,
  FormControlLabel,
  Grid,
  Fade,
} from '@mui/material';
import {
  AccountCircle as AccountCircleIcon,
  Lock as LockIcon,
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  BusinessCenter as BusinessIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const [emailOrUsername, setEmailOrUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const validateEmail = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value) && value.length < 3) {
      return 'Введите корректный email или имя пользователя';
    }
    return '';
  };

  const validatePassword = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    if (value.length < 6) return 'Пароль должен содержать минимум 6 символов';
    return '';
  };

  const handleBlur = (field, value) => {
    let error = '';
    if (field === 'emailOrUsername') {
      error = validateEmail(value);
    } else if (field === 'password') {
      error = validatePassword(value);
    }
    setFieldErrors({ ...fieldErrors, [field]: error });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate all fields
    const emailError = validateEmail(emailOrUsername);
    const passwordError = validatePassword(password);
    
    if (emailError || passwordError) {
      setFieldErrors({
        emailOrUsername: emailError,
        password: passwordError,
      });
      return;
    }

    setLoading(true);

    try {
      await login(emailOrUsername, password);
      if (rememberMe) {
        // Refresh token already saved in AuthContext
        // Could extend token expiration here if needed
      }
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Ошибка входа';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        background: 'linear-gradient(135deg, #003366 0%, #0066CC 50%, #0099FF 100%)',
        position: 'relative',
        overflow: 'hidden',
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
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Grid container sx={{ minHeight: 'calc(100vh - 64px)' }}>
          {/* Left side - Branding */}
          <Grid
            item
            xs={12}
            md={6}
            sx={{
              display: { xs: 'none', md: 'flex' },
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
              p: 4,
              position: 'relative',
            }}
          >
            <Fade in timeout={800}>
              <Box sx={{ textAlign: 'center', zIndex: 1 }}>
                <BusinessIcon sx={{ fontSize: 80, mb: 3, opacity: 0.9 }} />
                <Typography variant="h3" fontWeight={700} gutterBottom>
                  HH Resume Analyzer
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
                  Система подбора персонала с AI-анализом
                </Typography>
                <Box sx={{ mt: 4 }}>
                  <Typography variant="body1" sx={{ opacity: 0.8, mb: 2 }}>
                    ✓ Умный поиск кандидатов
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.8, mb: 2 }}>
                    ✓ AI-анализ резюме
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.8 }}>
                    ✓ Автоматический подбор
                  </Typography>
                </Box>
              </Box>
            </Fade>
          </Grid>

          {/* Right side - Login Form */}
          <Grid
            item
            xs={12}
            md={6}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              p: { xs: 2, sm: 4 },
            }}
          >
            <Fade in timeout={1000}>
              <Card
                elevation={0}
                sx={{
                  width: '100%',
                  maxWidth: 480,
                  borderRadius: 4,
                  overflow: 'hidden',
                  border: '1px solid',
                  borderColor: 'divider',
                  boxShadow: '0 12px 40px rgba(0,0,0,0.15)',
                }}
              >
                <Box
                  sx={{
                    background: 'linear-gradient(135deg, #003366 0%, #0066CC 100%)',
                    color: 'white',
                    p: 3,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="h5" component="h1" fontWeight={700}>
                    Добро пожаловать
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                    Войдите в свой аккаунт
                  </Typography>
                </Box>
                <CardContent sx={{ p: 4 }}>
                  {error && (
                    <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                      {error}
                    </Alert>
                  )}

                  <Box component="form" onSubmit={handleSubmit} noValidate>
                    <TextField
                      fullWidth
                      label="Email или имя пользователя"
                      name="emailOrUsername"
                      type="text"
                      margin="normal"
                      value={emailOrUsername}
                      onChange={(e) => {
                        setEmailOrUsername(e.target.value);
                        if (fieldErrors.emailOrUsername) {
                          setFieldErrors({ ...fieldErrors, emailOrUsername: '' });
                        }
                      }}
                      onBlur={(e) => handleBlur('emailOrUsername', e.target.value)}
                      error={!!fieldErrors.emailOrUsername}
                      helperText={fieldErrors.emailOrUsername}
                      required
                      autoFocus
                      autoComplete="username"
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailIcon sx={{ color: 'primary.main' }} />
                          </InputAdornment>
                        ),
                      }}
                    />
                    <TextField
                      fullWidth
                      label="Пароль"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      margin="normal"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        if (fieldErrors.password) {
                          setFieldErrors({ ...fieldErrors, password: '' });
                        }
                      }}
                      onBlur={(e) => handleBlur('password', e.target.value)}
                      error={!!fieldErrors.password}
                      helperText={fieldErrors.password}
                      required
                      autoComplete="current-password"
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockIcon sx={{ color: 'primary.main' }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                              aria-label="toggle password visibility"
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, mb: 3 }}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={rememberMe}
                            onChange={(e) => setRememberMe(e.target.checked)}
                            color="primary"
                          />
                        }
                        label="Запомнить меня"
                      />
                      <Link to="/forgot-password" style={{ textDecoration: 'none' }}>
                        <Typography variant="body2" color="primary" sx={{ '&:hover': { textDecoration: 'underline' } }}>
                          Забыли пароль?
                        </Typography>
                      </Link>
                    </Box>
                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      size="large"
                      sx={{
                        mt: 2,
                        mb: 3,
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
                      {loading ? <CircularProgress size={24} color="inherit" /> : 'Войти'}
                    </Button>
                    <Box textAlign="center">
                      <Typography variant="body2" color="text.secondary">
                        Нет аккаунта?{' '}
                        <Link to="/register" style={{ textDecoration: 'none', color: 'inherit' }}>
                          <Typography
                            component="span"
                            variant="body2"
                            color="primary"
                            sx={{ fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}
                          >
                            Зарегистрироваться
                          </Typography>
                        </Link>
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Fade>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
