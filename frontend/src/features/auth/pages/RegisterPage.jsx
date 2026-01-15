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
  Grid,
  Fade,
  LinearProgress,
} from '@mui/material';
import {
  Lock as LockIcon,
  Email as EmailIcon,
  Person as PersonIcon,
  Visibility,
  VisibilityOff,
  CheckCircle as CheckCircleIcon,
  BusinessCenter as BusinessIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const validateEmail = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Введите корректный email';
    return '';
  };

  const validateUsername = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    if (value.length < 3) return 'Имя пользователя должно содержать минимум 3 символа';
    if (value.length > 30) return 'Имя пользователя не должно превышать 30 символов';
    if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Имя пользователя может содержать только буквы, цифры и _';
    return '';
  };

  const validatePassword = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    if (value.length < 8) return 'Пароль должен содержать минимум 8 символов';
    if (!/(?=.*[a-z])/.test(value)) return 'Пароль должен содержать хотя бы одну строчную букву';
    if (!/(?=.*[A-Z])/.test(value)) return 'Пароль должен содержать хотя бы одну заглавную букву';
    if (!/(?=.*\d)/.test(value)) return 'Пароль должен содержать хотя бы одну цифру';
    return '';
  };

  const validateConfirmPassword = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    if (value !== formData.password) return 'Пароли не совпадают';
    return '';
  };

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: 'grey' };
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/(?=.*[a-z])/.test(password)) strength++;
    if (/(?=.*[A-Z])/.test(password)) strength++;
    if (/(?=.*\d)/.test(password)) strength++;
    if (/(?=.*[@$!%*?&])/.test(password)) strength++;

    if (strength <= 2) return { strength: 33, label: 'Слабый', color: 'error' };
    if (strength <= 4) return { strength: 66, label: 'Средний', color: 'warning' };
    return { strength: 100, label: 'Сильный', color: 'success' };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  const handleBlur = (field, value) => {
    let error = '';
    if (field === 'email') {
      error = validateEmail(value);
    } else if (field === 'username') {
      error = validateUsername(value);
    } else if (field === 'password') {
      error = validatePassword(value);
    } else if (field === 'confirmPassword') {
      error = validateConfirmPassword(value);
    }
    setFieldErrors({ ...fieldErrors, [field]: error });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors({ ...fieldErrors, [name]: '' });
    }
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate all fields
    const emailError = validateEmail(formData.email);
    const usernameError = validateUsername(formData.username);
    const passwordError = validatePassword(formData.password);
    const confirmPasswordError = validateConfirmPassword(formData.confirmPassword);

    if (emailError || usernameError || passwordError || confirmPasswordError) {
      setFieldErrors({
        email: emailError,
        username: usernameError,
        password: passwordError,
        confirmPassword: confirmPasswordError,
      });
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
      await login(formData.email, formData.password);
      
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
                  Присоединяйтесь к нам
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
                  Создайте аккаунт и начните работу
                </Typography>
                <Box sx={{ mt: 4 }}>
                  <Typography variant="body1" sx={{ opacity: 0.8, mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                    <CheckCircleIcon fontSize="small" /> Быстрая регистрация
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.8, mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                    <CheckCircleIcon fontSize="small" /> Безопасное хранение данных
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                    <CheckCircleIcon fontSize="small" /> Полный доступ к функциям
                  </Typography>
                </Box>
              </Box>
            </Fade>
          </Grid>

          {/* Right side - Register Form */}
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
                    Регистрация
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                    Создайте аккаунт для начала работы
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
                      label="Email"
                      name="email"
                      type="email"
                      margin="normal"
                      value={formData.email}
                      onChange={handleChange}
                      onBlur={(e) => handleBlur('email', e.target.value)}
                      error={!!fieldErrors.email}
                      helperText={fieldErrors.email}
                      required
                      autoComplete="email"
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
                      label="Имя пользователя"
                      name="username"
                      type="text"
                      margin="normal"
                      value={formData.username}
                      onChange={handleChange}
                      onBlur={(e) => handleBlur('username', e.target.value)}
                      error={!!fieldErrors.username}
                      helperText={fieldErrors.username || '3-30 символов, только буквы, цифры и _'}
                      required
                      autoComplete="username"
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <PersonIcon sx={{ color: 'primary.main' }} />
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
                      value={formData.password}
                      onChange={handleChange}
                      onBlur={(e) => handleBlur('password', e.target.value)}
                      error={!!fieldErrors.password}
                      helperText={fieldErrors.password || 'Минимум 8 символов, заглавные и строчные буквы, цифры'}
                      required
                      autoComplete="new-password"
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
                    {formData.password && (
                      <Box sx={{ mt: 1, mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Надёжность пароля:
                          </Typography>
                          <Typography variant="caption" color={`${passwordStrength.color}.main`} fontWeight={600}>
                            {passwordStrength.label}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={passwordStrength.strength}
                          color={passwordStrength.color}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    )}
                    <TextField
                      fullWidth
                      label="Подтвердите пароль"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      margin="normal"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      onBlur={(e) => handleBlur('confirmPassword', e.target.value)}
                      error={!!fieldErrors.confirmPassword}
                      helperText={fieldErrors.confirmPassword}
                      required
                      autoComplete="new-password"
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
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              edge="end"
                              aria-label="toggle confirm password visibility"
                            >
                              {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      size="large"
                      sx={{
                        mt: 4,
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
                      {loading ? <CircularProgress size={24} color="inherit" /> : 'Зарегистрироваться'}
                    </Button>
                    <Box textAlign="center">
                      <Typography variant="body2" color="text.secondary">
                        Уже есть аккаунт?{' '}
                        <Link to="/login" style={{ textDecoration: 'none', color: 'inherit' }}>
                          <Typography
                            component="span"
                            variant="body2"
                            color="primary"
                            sx={{ fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}
                          >
                            Войти
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
