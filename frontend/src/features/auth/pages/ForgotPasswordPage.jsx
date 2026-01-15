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
  Grid,
  Fade,
} from '@mui/material';
import {
  Email as EmailIcon,
  ArrowBack as ArrowBackIcon,
  BusinessCenter as BusinessIcon,
} from '@mui/icons-material';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateEmail = (value) => {
    if (!value) return 'Поле обязательно для заполнения';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Введите корректный email';
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const emailError = validateEmail(email);
    if (emailError) {
      setError(emailError);
      return;
    }

    setLoading(true);

    try {
      // TODO: Implement forgot password API call
      // await authAPI.forgotPassword(email);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.message || 'Ошибка отправки запроса');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          background: 'linear-gradient(135deg, #003366 0%, #0066CC 50%, #0099FF 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="sm" sx={{ py: 4, display: 'flex', alignItems: 'center' }}>
          <Fade in timeout={1000}>
            <Card
              elevation={0}
              sx={{
                width: '100%',
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
                  Проверьте почту
                </Typography>
              </Box>
              <CardContent sx={{ p: 4, textAlign: 'center' }}>
                <Alert severity="success" sx={{ mb: 3 }}>
                  Инструкции по восстановлению пароля отправлены на {email}
                </Alert>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Если письмо не пришло, проверьте папку "Спам" или попробуйте еще раз через несколько минут.
                </Typography>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => navigate('/login')}
                  sx={{ mb: 2 }}
                >
                  Вернуться к входу
                </Button>
              </CardContent>
            </Card>
          </Fade>
        </Container>
      </Box>
    );
  }

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
                  Забыли пароль?
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
                  Не беспокойтесь, мы поможем восстановить доступ
                </Typography>
              </Box>
            </Fade>
          </Grid>

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
                    Восстановление пароля
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
                    Введите email для получения инструкций
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
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        setError('');
                      }}
                      error={!!error && !success}
                      required
                      autoFocus
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
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2, mb: 3 }}>
                      Мы отправим вам инструкции по восстановлению пароля на указанный email адрес.
                    </Typography>
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
                      {loading ? <CircularProgress size={24} color="inherit" /> : 'Отправить'}
                    </Button>
                    <Box textAlign="center">
                      <Button
                        startIcon={<ArrowBackIcon />}
                        onClick={() => navigate('/login')}
                        sx={{ textTransform: 'none' }}
                      >
                        Вернуться к входу
                      </Button>
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
