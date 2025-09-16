/**
 * Утилиты для оптимизации производительности
 */

import { useEffect, useMemo, useState } from 'react';

/**
 * Хук для дебаунса значения
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Хук для троттлинга функций
 */
export function useThrottle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): T {
  const [lastRun, setLastRun] = useState(Date.now());

  const throttledFunc = useMemo(
    () =>
      ((...args: Parameters<T>) => {
        if (Date.now() - lastRun >= delay) {
          func(...args);
          setLastRun(Date.now());
        }
      }) as T,
    [func, delay, lastRun]
  );

  return throttledFunc;
}

/**
 * Хук для ленивой загрузки компонентов
 */
export function useLazyLoading(threshold = 0.1) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [element, setElement] = useState<Element | null>(null);

  useEffect(() => {
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      { threshold }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [element, threshold]);

  return { isIntersecting, setElement };
}

/**
 * Хук для мемоизации вычислений
 */
export function useMemoizedComputation<T>(
  computation: () => T,
  dependencies: React.DependencyList
): T {
  return useMemo(computation, dependencies);
}

/**
 * Утилита для батчинга операций
 */
export class BatchProcessor<T> {
  private batch: T[] = [];
  private timeout: NodeJS.Timeout | null = null;
  private readonly batchSize: number;
  private readonly delay: number;
  private readonly processor: (batch: T[]) => Promise<void>;

  constructor(
    processor: (batch: T[]) => Promise<void>,
    batchSize = 10,
    delay = 1000
  ) {
    this.processor = processor;
    this.batchSize = batchSize;
    this.delay = delay;
  }

  public add(item: T): void {
    this.batch.push(item);

    if (this.batch.length >= this.batchSize) {
      this.processBatch();
    } else {
      this.scheduleProcessing();
    }
  }

  private scheduleProcessing(): void {
    if (this.timeout) {
      clearTimeout(this.timeout);
    }

    this.timeout = setTimeout(() => {
      this.processBatch();
    }, this.delay);
  }

  private async processBatch(): Promise<void> {
    if (this.batch.length === 0) return;

    const currentBatch = [...this.batch];
    this.batch = [];

    if (this.timeout) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }

    try {
      await this.processor(currentBatch);
    } catch (error) {
      console.error('Batch processing error:', error);
    }
  }

  public flush(): Promise<void> {
    return this.processBatch();
  }
}

/**
 * Утилита для кэширования данных
 */
export class MemoryCache<K, V> {
  private cache = new Map<K, { value: V; timestamp: number }>();
  private readonly maxSize: number;
  private readonly ttl: number;

  constructor(maxSize = 100, ttl = 5 * 60 * 1000) {
    this.maxSize = maxSize;
    this.ttl = ttl;
  }

  public get(key: K): V | undefined {
    const item = this.cache.get(key);

    if (!item) return undefined;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return undefined;
    }

    return item.value;
  }

  public set(key: K, value: V): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now(),
    });
  }

  public has(key: K): boolean {
    return this.get(key) !== undefined;
  }

  public delete(key: K): boolean {
    return this.cache.delete(key);
  }

  public clear(): void {
    this.cache.clear();
  }

  public size(): number {
    return this.cache.size;
  }
}

/**
 * Утилита для оптимизации изображений
 */
export function compressImage(
  file: File,
  maxWidth = 1920,
  maxHeight = 1080,
  quality = 0.8
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      let { width, height } = img;

      // Масштабирование
      if (width > maxWidth) {
        height = (height * maxWidth) / width;
        width = maxWidth;
      }

      if (height > maxHeight) {
        width = (width * maxHeight) / height;
        height = maxHeight;
      }

      canvas.width = width;
      canvas.height = height;

      if (ctx) {
        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to compress image'));
            }
          },
          'image/jpeg',
          quality
        );
      } else {
        reject(new Error('Failed to get canvas context'));
      }
    };

    img.onerror = () => reject(new Error('Failed to load image'));
    img.src = URL.createObjectURL(file);
  });
}

/**
 * Утилита для ленивой загрузки модулей
 */
export function lazy<T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
): React.LazyExoticComponent<T> {
  return React.lazy(() =>
    importFunc().catch((error) => {
      console.error('Lazy loading error:', error);
      return {
        default: (() => (
          <div>Ошибка загрузки компонента</div>
        )) as T,
      };
    })
  );
}

/**
 * Проверка производительности
 */
export class PerformanceMonitor {
  private static measures: Map<string, number> = new Map();

  public static start(name: string): void {
    this.measures.set(name, performance.now());
  }

  public static end(name: string): number {
    const startTime = this.measures.get(name);
    if (!startTime) {
      console.warn(`Performance measure "${name}" was not started`);
      return 0;
    }

    const endTime = performance.now();
    const duration = endTime - startTime;

    this.measures.delete(name);

    if (process.env.NODE_ENV === 'development') {
      console.log(`Performance measure "${name}": ${duration.toFixed(2)}ms`);
    }

    return duration;
  }

  public static measure<T>(name: string, fn: () => T): T {
    this.start(name);
    const result = fn();
    this.end(name);
    return result;
  }

  public static async measureAsync<T>(
    name: string,
    fn: () => Promise<T>
  ): Promise<T> {
    this.start(name);
    const result = await fn();
    this.end(name);
    return result;
  }
}