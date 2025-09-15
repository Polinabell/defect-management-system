/**
 * Настройка тестовой среды для Jest
 */

import '@testing-library/jest-dom';

// Мокируем ResizeObserver
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserver;

// Мокируем IntersectionObserver
class IntersectionObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.IntersectionObserver = IntersectionObserver;

// Мокируем matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Мокируем scrollTo
window.scrollTo = jest.fn();

// Настройки для тестирования Material-UI
global.window = Object.assign(global.window, {
  HTMLElement: window.HTMLElement,
  HTMLAnchorElement: window.HTMLAnchorElement,
  HTMLButtonElement: window.HTMLButtonElement,
  HTMLInputElement: window.HTMLInputElement,
});

// Мокируем console.warn для тестов (убираем warning'и от Material-UI)
const originalWarn = console.warn;
beforeAll(() => {
  console.warn = (...args) => {
    const warningMessage = args[0];
    if (
      typeof warningMessage === 'string' &&
      (warningMessage.includes('Material-UI') ||
       warningMessage.includes('useLayoutEffect') ||
       warningMessage.includes('act'))
    ) {
      return;
    }
    originalWarn(...args);
  };
});

afterAll(() => {
  console.warn = originalWarn;
});

// Настройка часового пояса для консистентных тестов дат
process.env.TZ = 'UTC';