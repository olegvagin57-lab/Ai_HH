import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Switch,
  Typography,
  Divider,
  Alert,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { vacanciesAPI } from '../../../api/api';

export default function VacancyForm({ vacancy, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    city: '',
    remote: false,
    salary_min: '',
    salary_max: '',
    currency: 'RUB',
    search_query: '',
    search_city: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (vacancy) {
      setFormData({
        title: vacancy.title || '',
        description: vacancy.description || '',
        requirements: vacancy.requirements || '',
        city: vacancy.city || '',
        remote: vacancy.remote || false,
        salary_min: vacancy.salary_min || '',
        salary_max: vacancy.salary_max || '',
        currency: vacancy.currency || 'RUB',
        search_query: vacancy.search_query || '',
        search_city: vacancy.search_city || '',
      });
    }
  }, [vacancy]);

  const createMutation = useMutation({
    mutationFn: (data) => vacanciesAPI.create(data),
    onSuccess: () => {
      onSuccess?.();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data) => vacanciesAPI.update(vacancy.id, data),
    onSuccess: () => {
      onSuccess?.();
    },
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Название вакансии обязательно';
    }
    if (!formData.description.trim()) {
      newErrors.description = 'Описание обязательно';
    }
    if (!formData.city.trim() && !formData.remote) {
      newErrors.city = 'Укажите город или выберите удаленную работу';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const data = {
        title: formData.title,
        description: formData.description,
        requirements: formData.requirements,
        city: formData.city,
        remote: formData.remote,
        salary_min: formData.salary_min ? parseInt(formData.salary_min) : null,
        salary_max: formData.salary_max ? parseInt(formData.salary_max) : null,
        currency: formData.currency,
        search_query: formData.search_query,
        search_city: formData.search_city,
      };

      if (vacancy) {
        await updateMutation.mutateAsync(data);
      } else {
        await createMutation.mutateAsync(data);
      }
    } catch (error) {
      console.error('Error saving vacancy:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Название вакансии"
            name="title"
            value={formData.title}
            onChange={handleChange}
            error={!!errors.title}
            helperText={errors.title}
            required
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Описание"
            name="description"
            value={formData.description}
            onChange={handleChange}
            multiline
            rows={4}
            error={!!errors.description}
            helperText={errors.description}
            required
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Требования"
            name="requirements"
            value={formData.requirements}
            onChange={handleChange}
            multiline
            rows={4}
            placeholder="Опишите требования к кандидату..."
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Город"
            name="city"
            value={formData.city}
            onChange={handleChange}
            error={!!errors.city}
            helperText={errors.city}
            disabled={formData.remote}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControlLabel
            control={
              <Switch
                checked={formData.remote}
                onChange={handleChange}
                name="remote"
              />
            }
            label="Удаленная работа"
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="Зарплата от"
            name="salary_min"
            type="number"
            value={formData.salary_min}
            onChange={handleChange}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="Зарплата до"
            name="salary_max"
            type="number"
            value={formData.salary_max}
            onChange={handleChange}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel>Валюта</InputLabel>
            <Select
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              label="Валюта"
            >
              <MenuItem value="RUB">RUB</MenuItem>
              <MenuItem value="USD">USD</MenuItem>
              <MenuItem value="EUR">EUR</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>
            Параметры поиска кандидатов
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Запрос для поиска"
            name="search_query"
            value={formData.search_query}
            onChange={handleChange}
            placeholder="Например: Python разработчик"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Город для поиска"
            name="search_city"
            value={formData.search_city}
            onChange={handleChange}
            placeholder="Например: Москва"
          />
        </Grid>
      </Grid>

      {(createMutation.isError || updateMutation.isError) && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Ошибка при сохранении вакансии
        </Alert>
      )}

      <Box display="flex" justifyContent="flex-end" gap={2} mt={4}>
        <Button onClick={onCancel} disabled={loading}>
          Отмена
        </Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {loading ? 'Сохранение...' : vacancy ? 'Сохранить' : 'Создать'}
        </Button>
      </Box>
    </Box>
  );
}
