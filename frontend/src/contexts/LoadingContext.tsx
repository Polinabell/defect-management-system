/**
 * Контекст для управления состоянием загрузки
 */

import React, { createContext, useContext, useState } from 'react';

interface LoadingContextType {
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  loadingText: string;
  setLoadingText: (text: string) => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const useLoading = (): LoadingContextType => {
  const context = useContext(LoadingContext);
  if (!context) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
};

export const LoadingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Загрузка...');

  const setLoading = (loading: boolean) => {
    setIsLoading(loading);
    if (!loading) {
      setLoadingText('Загрузка...');
    }
  };

  return (
    <LoadingContext.Provider value={{
      isLoading,
      setLoading,
      loadingText,
      setLoadingText
    }}>
      {children}
    </LoadingContext.Provider>
  );
};