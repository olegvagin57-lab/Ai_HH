import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { searchAPI } from '../../../api/api';
import { queryKeys } from '../../../lib/query';

export default function ResultsPage() {
  const { searchId } = useParams();
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [sortBy, setSortBy] = useState('ai_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedResume, setSelectedResume] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);

  const { data: search, isLoading: searchLoading } = useQuery({
    queryKey: queryKeys.search.detail(searchId),
    queryFn: () => searchAPI.get(searchId),
    refetchInterval: (data) => {
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 2000; // Poll every 2 seconds
      }
      return false;
    },
  });

  const { data: resumesData, isLoading: resumesLoading } = useQuery({
    queryKey: queryKeys.search.resumes(searchId),
    queryFn: () => searchAPI.getResumes(searchId, page + 1, pageSize, sortBy, sortOrder),
    enabled: !!searchId && (search?.status === 'completed' || search?.status === 'processing'),
  });

  const handleExportExcel = async () => {
    try {
      const blob = await searchAPI.exportExcel(searchId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `search_${searchId}_results.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleExportCsv = async () => {
    try {
      const blob = await searchAPI.exportCsv(searchId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `search_${searchId}_results.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  if (searchLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!search) {
    return <Alert severity="error">Search not found</Alert>;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">
          Search Results: {search.query}
        </Typography>
        <Box>
          <Button variant="outlined" onClick={handleExportExcel} sx={{ mr: 1 }}>
            Export Excel
          </Button>
          <Button variant="outlined" onClick={handleExportCsv}>
            Export CSV
          </Button>
        </Box>
      </Box>

      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Typography variant="body1">
          <strong>City:</strong> {search.city}
        </Typography>
        <Typography variant="body1">
          <strong>Status:</strong> {search.status}
        </Typography>
        <Typography variant="body1">
          <strong>Total Found:</strong> {search.total_found}
        </Typography>
        <Typography variant="body1">
          <strong>Analyzed:</strong> {search.analyzed_count}
        </Typography>
      </Paper>

      {search.status === 'processing' && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Search is being processed. Results will appear here when ready.
        </Alert>
      )}

      {search.status === 'completed' && (
        <>
          <Box display="flex" gap={2} mb={2}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="ai_score">AI Score</MenuItem>
                <MenuItem value="preliminary_score">Preliminary Score</MenuItem>
                <MenuItem value="created_at">Created At</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Order</InputLabel>
              <Select
                value={sortOrder}
                label="Order"
                onChange={(e) => setSortOrder(e.target.value)}
              >
                <MenuItem value="desc">Descending</MenuItem>
                <MenuItem value="asc">Ascending</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {resumesLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : resumesData && resumesData.resumes ? (
            <>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Age</TableCell>
                      <TableCell>City</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Salary</TableCell>
                      <TableCell>AI Score</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {resumesData.resumes.map((resume) => (
                      <TableRow key={resume.id}>
                        <TableCell>{resume.name || 'N/A'}</TableCell>
                        <TableCell>{resume.age || 'N/A'}</TableCell>
                        <TableCell>{resume.city || 'N/A'}</TableCell>
                        <TableCell>{resume.title || 'N/A'}</TableCell>
                        <TableCell>
                          {resume.salary
                            ? `${resume.salary} ${resume.currency || ''}`
                            : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {resume.ai_score ? (
                            <Chip
                              label={resume.ai_score}
                              color={resume.ai_score >= 8 ? 'success' : resume.ai_score >= 6 ? 'warning' : 'default'}
                            />
                          ) : (
                            'N/A'
                          )}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            onClick={() => {
                              setSelectedResume(resume);
                              setOpenDialog(true);
                            }}
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <TablePagination
                component="div"
                count={resumesData.total || 0}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={pageSize}
                onRowsPerPageChange={(e) => {
                  setPageSize(parseInt(e.target.value, 10));
                  setPage(0);
                }}
                rowsPerPageOptions={[10, 20, 50, 100]}
              />
            </>
          ) : (
            <Alert severity="info">No resumes found</Alert>
          )}
        </>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Resume Details</DialogTitle>
        <DialogContent>
          {selectedResume && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedResume.name || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {selectedResume.title || 'N/A'} • {selectedResume.city || 'N/A'} • Age: {selectedResume.age || 'N/A'}
              </Typography>
              {selectedResume.salary && (
                <Typography variant="body2" gutterBottom>
                  Salary: {selectedResume.salary} {selectedResume.currency || ''}
                </Typography>
              )}
              {selectedResume.ai_score && (
                <Typography variant="body2" gutterBottom>
                  AI Score: {selectedResume.ai_score}/10
                </Typography>
              )}
              {selectedResume.ai_summary && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    AI Summary:
                  </Typography>
                  <Typography variant="body2">{selectedResume.ai_summary}</Typography>
                </Box>
              )}
              {selectedResume.ai_questions && selectedResume.ai_questions.length > 0 && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Interview Questions:
                  </Typography>
                  <ul>
                    {selectedResume.ai_questions.map((q, i) => (
                      <li key={i}>
                        <Typography variant="body2">{q}</Typography>
                      </li>
                    ))}
                  </ul>
                </Box>
              )}
              {selectedResume.ai_generated_detected && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  This resume may have been generated by AI
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
