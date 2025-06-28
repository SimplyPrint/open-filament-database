import { loadFilamentDatabase } from './jsonParser';
import path from 'node:path';
import type { FilamentDatabase } from './jsonParser';

let cachedDatabase: FilamentDatabase | null = null;
let loadingPromise: Promise<FilamentDatabase> | null = null;

export async function getFilamentDatabase(): Promise<FilamentDatabase> {
  // If we already have cached data, return it immediately
  if (cachedDatabase) {
    return cachedDatabase;
  }

  // If we're currently loading, wait for that promise to avoid duplicate loads
  if (loadingPromise) {
    return loadingPromise;
  }

  // Start loading and cache the promise
  console.log('Loading filament database (one time only)...');
  loadingPromise = loadDatabase();

  try {
    cachedDatabase = await loadingPromise;
    return cachedDatabase;
  } finally {
    loadingPromise = null;
  }
}

async function loadDatabase(): Promise<FilamentDatabase> {
  const dataPath = path.resolve('../data');
  return await loadFilamentDatabase(dataPath);
}

// Optional: Function to refresh cache if needed during development
export function clearCache() {
  cachedDatabase = null;
  loadingPromise = null;
}

export async function refreshDatabase(): Promise<FilamentDatabase> {
  console.log('Refreshing filament database...');
  clearCache();
  return await getFilamentDatabase();
}
