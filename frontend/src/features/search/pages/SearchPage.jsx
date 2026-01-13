import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import { searchAPI } from '../../../api/api';
import { queryKeys } from '../../../lib/query';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [city, setCity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const { data: searches, refetch } = useQuery({
    queryKey: queryKeys.search.all,
    queryFn: () => searchAPI.list(1, 20),
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const search = await searchAPI.create(query, city);
      refetch();
      navigate(`/results/${search.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create search');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        New Search
      </Typography>

      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Search Query"
            placeholder="e.g., Python developer with FastAPI experience"
            margin="normal"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />
          <TextField
            fullWidth
            label="City"
            placeholder="e.g., Москва"
            margin="normal"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            required
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            sx={{ mt: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Start Search'}
          </Button>
        </Box>
      </Paper>

      {searches && searches.searches && searches.searches.length > 0 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Recent Searches
          </Typography>
          <List>
            {searches.searches.map((search) => (
              <ListItem
                key={search.id}
                button
                onClick={() => navigate(`/results/${search.id}`)}
                sx={{ border: 1, borderColor: 'divider', mb: 1, borderRadius: 1 }}
              >
                <ListItemText
                  primary={search.query}
                  secondary={`City: ${search.city} • Found: ${search.total_found} • Analyzed: ${search.analyzed_count}`}
                />
                <Chip
                  label={search.status}
                  color={getStatusColor(search.status)}
                  size="small"
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Box>
  );
}
