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
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    fullName: '',
    companyName: '',
    position: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.fullName || undefined,
        company_name: formData.companyName || undefined,
        position: formData.position || undefined,
      });
      navigate('/login');
    } catch (err) {
      // Handle validation errors (422)
      if (err.response?.status === 422) {
        const errors = err.response?.data?.detail || [];
        if (Array.isArray(errors)) {
          const passwordError = errors.find(e => e.loc?.includes('password'));
          if (passwordError) {
            setError(passwordError.msg || 'Password must be at least 8 characters with uppercase, lowercase, and digit');
          } else {
            const firstError = errors[0];
            setError(firstError?.msg || 'Validation error: ' + (firstError?.loc?.join('.') || ''));
          }
        } else {
          setError(err.response?.data?.message || 'Validation error');
        }
      } else {
        setError(err.response?.data?.message || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Create Account
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              name="email"
              margin="normal"
              value={formData.email}
              onChange={handleChange}
              required
              autoFocus
            />
            <TextField
              fullWidth
              label="Username"
              name="username"
              margin="normal"
              value={formData.username}
              onChange={handleChange}
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              name="password"
              margin="normal"
              value={formData.password}
              onChange={handleChange}
              required
              helperText="Minimum 8 characters, must include uppercase, lowercase, and digit"
              error={formData.password.length > 0 && formData.password.length < 8}
            />
            <TextField
              fullWidth
              label="Full Name"
              name="fullName"
              margin="normal"
              value={formData.fullName}
              onChange={handleChange}
            />
            <TextField
              fullWidth
              label="Company Name"
              name="companyName"
              margin="normal"
              value={formData.companyName}
              onChange={handleChange}
            />
            <TextField
              fullWidth
              label="Position"
              name="position"
              margin="normal"
              value={formData.position}
              onChange={handleChange}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
            <Box textAlign="center">
              <Link to="/login" style={{ textDecoration: 'none' }}>
                <Typography variant="body2" color="primary">
                  Already have an account? Sign in
                </Typography>
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
