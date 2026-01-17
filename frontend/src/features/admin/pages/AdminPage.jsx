import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { usersAPI } from '../../../api/api';
import { queryKeys } from '@/lib/query';

export default function AdminPage() {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [selectedUser, setSelectedUser] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editData, setEditData] = useState({});
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: () => usersAPI.list(page + 1, pageSize),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => usersAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
      setOpenDialog(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => usersAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
  });

  const handleEdit = (user) => {
    setSelectedUser(user);
    setEditData({
      full_name: user.full_name || '',
      company_name: user.company_name || '',
      position: user.position || '',
      is_active: user.is_active,
      role_names: user.role_names || [],
    });
    setOpenDialog(true);
  };

  const handleSave = () => {
    updateMutation.mutate({ id: selectedUser.id, data: editData });
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Management
      </Typography>

      {data && data.users ? (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>Username</TableCell>
                  <TableCell>Full Name</TableCell>
                  <TableCell>Roles</TableCell>
                  <TableCell>Active</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.full_name || 'N/A'}</TableCell>
                    <TableCell>
                      {(user.role_names || []).map((role) => (
                        <Chip key={role} label={role} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? 'Active' : 'Inactive'}
                        color={user.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Button size="small" onClick={() => handleEdit(user)} sx={{ mr: 1 }}>
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        onClick={() => handleDelete(user.id)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            component="div"
            count={data.total || 0}
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
        <Alert severity="info">No users found</Alert>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Full Name"
              margin="normal"
              value={editData.full_name || ''}
              onChange={(e) => setEditData({ ...editData, full_name: e.target.value })}
            />
            <TextField
              fullWidth
              label="Company Name"
              margin="normal"
              value={editData.company_name || ''}
              onChange={(e) => setEditData({ ...editData, company_name: e.target.value })}
            />
            <TextField
              fullWidth
              label="Position"
              margin="normal"
              value={editData.position || ''}
              onChange={(e) => setEditData({ ...editData, position: e.target.value })}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Active</InputLabel>
              <Select
                value={editData.is_active !== undefined ? editData.is_active : true}
                label="Active"
                onChange={(e) => setEditData({ ...editData, is_active: e.target.value })}
              >
                <MenuItem value={true}>Active</MenuItem>
                <MenuItem value={false}>Inactive</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Roles (comma-separated)"
              margin="normal"
              value={Array.isArray(editData.role_names) ? editData.role_names.join(', ') : ''}
              onChange={(e) =>
                setEditData({
                  ...editData,
                  role_names: e.target.value.split(',').map((r) => r.trim()).filter(Boolean),
                })
              }
              helperText="e.g., admin, hr_manager, hr_specialist, viewer"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" disabled={updateMutation.isPending}>
            {updateMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
