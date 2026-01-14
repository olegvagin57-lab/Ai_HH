import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../features/auth/contexts/AuthContext';
import ProtectedRoute from '../features/auth/components/ProtectedRoute';
import LoginPage from '../features/auth/pages/LoginPage';
import RegisterPage from '../features/auth/pages/RegisterPage';
import SearchPage from '../features/search/pages/SearchPage';
import ResultsPage from '../features/results/pages/ResultsPage';
import AdminPage from '../features/admin/pages/AdminPage';
import Layout from '../shared/components/Layout';
import Dashboard from '../shared/components/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="results/:searchId" element={<ResultsPage />} />
          <Route path="candidates" element={<div>Кандидаты (в разработке)</div>} />
          <Route path="vacancies" element={<div>Вакансии (в разработке)</div>} />
          <Route path="analytics" element={<div>Аналитика (в разработке)</div>} />
          <Route path="notifications" element={<div>Уведомления (в разработке)</div>} />
          <Route path="admin" element={<AdminPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
