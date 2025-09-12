/**
 * Основные маршруты приложения
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout.tsx';
import { Dashboard } from '../pages/Dashboard.tsx';
import { Projects } from '../pages/Projects.tsx';
import { Defects } from '../pages/Defects.tsx';
import { DefectDetail } from '../pages/DefectDetail.tsx';
import { Reports } from '../pages/Reports.tsx';
import { Login } from '../pages/auth/Login.tsx';
import { useAuth } from '../contexts/AuthContext.tsx';

export const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="projects" element={<Projects />} />
        <Route path="defects" element={<Defects />} />
        <Route path="defects/:id" element={<DefectDetail />} />
        <Route path="reports" element={<Reports />} />
      </Route>
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};