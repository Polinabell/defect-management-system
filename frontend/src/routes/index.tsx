/**
 * Основные маршруты приложения
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { Dashboard } from '../pages/Dashboard';
import { Projects } from '../pages/Projects';
import { Defects } from '../pages/Defects';

export const AppRoutes: React.FC = () => {
  // Для демонстрации этапа 1 - только базовые страницы
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="projects" element={<Projects />} />
        <Route path="defects" element={<Defects />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};