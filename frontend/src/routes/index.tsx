/**
 * Основные маршруты приложения
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { Dashboard } from '../pages/Dashboard';
import { Projects } from '../pages/Projects';
import { Defects } from '../pages/Defects';
import { DefectDetail } from '../pages/DefectDetail';
import { Reports } from '../pages/Reports';
import { Users } from '../pages/Users';
import { Profile } from '../pages/Profile';
import { Settings } from '../pages/Settings';
import { Notifications } from '../pages/Notifications';
import { Analytics } from '../pages/Analytics';
import { Login } from '../pages/auth/Login';
import { useAuth } from '../contexts/AuthContext';

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
        <Route path="users" element={<Users />} />
        <Route path="profile" element={<Profile />} />
        <Route path="settings" element={<Settings />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="analytics" element={<Analytics />} />
      </Route>
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};