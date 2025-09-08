/**
 * Точка входа в React приложение
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

// Настройка для React 18
const container = document.getElementById('root');
if (!container) {
  throw new Error('Не найден элемент с id="root"');
}

const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
