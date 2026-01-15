import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../features/auth/contexts/AuthContext';
import ProtectedRoute from '../features/auth/components/ProtectedRoute';
import LoginPage from '../features/auth/pages/LoginPage';
import RegisterPage from '../features/auth/pages/RegisterPage';
import ForgotPasswordPage from '../features/auth/pages/ForgotPasswordPage';
import SearchPage from '../features/search/pages/SearchPage';
import ResultsPage from '../features/results/pages/ResultsPage';
import AdminPage from '../features/admin/pages/AdminPage';
import CandidatesPage from '../features/candidates/pages/CandidatesPage';
import CandidateDetailPage from '../features/candidates/pages/CandidateDetailPage';
import VacanciesPage from '../features/vacancies/pages/VacanciesPage';
import VacancyDetailPage from '../features/vacancies/pages/VacancyDetailPage';
import AnalyticsPage from '../features/analytics/pages/AnalyticsPage';
import NotificationsPage from '../features/notifications/pages/NotificationsPage';
import Layout from '../shared/components/Layout';
import Dashboard from '../shared/components/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
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
          <Route path="candidates" element={<CandidatesPage />} />
          <Route path="candidates/:resumeId" element={<CandidateDetailPage />} />
          <Route path="vacancies" element={<VacanciesPage />} />
          <Route path="vacancies/:id" element={<VacancyDetailPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="admin" element={<AdminPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
