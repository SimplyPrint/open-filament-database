import { loadFilamentDatabase } from './jsonParser';
import { getEditedItem, isItemEdited } from './pseudoEditor';
import { browser } from '$app/environment';
import path from 'node:path';
import type { FilamentDatabase } from './jsonParser';

let cachedDatabase: FilamentDatabase | null = null;
let loadingPromise: Promise<FilamentDatabase> | null = null;

export async function getFilamentDatabase(): Promise<FilamentDatabase> {
  if (cachedDatabase) {
    return browser ? applyPseudoEdits(cachedDatabase) : cachedDatabase;
  }

  if (loadingPromise) {
    const database = await loadingPromise;
    return browser ? applyPseudoEdits(database) : database;
  }

  loadingPromise = loadDatabase();
  const database = await loadingPromise;
  cachedDatabase = database;
  loadingPromise = null;

  return browser ? applyPseudoEdits(database) : database;
}

async function loadDatabase(): Promise<FilamentDatabase> {
  const dataPath = path.resolve('../data');
  console.log(`Loading database from: ${dataPath}`);
  return await loadFilamentDatabase(dataPath);
}

function applyPseudoEdits(database: FilamentDatabase): FilamentDatabase {
  console.log('Applying pseudo edits to database (browser-side)');

  // Only apply edits in browser environment
  if (!browser || typeof localStorage === 'undefined') {
    console.log('Not in browser or localStorage not available, returning original database');
    return database;
  }

  // Deep clone the database to avoid mutations
  const editedDatabase = JSON.parse(JSON.stringify(database));
  console.log('Database cloned for pseudo edits');

  // Apply brand edits
  for (const [brandKey, brand] of Object.entries(editedDatabase.brands)) {
    if (isItemEdited('brand', brandKey)) {
      const editedData = getEditedItem('brand', brandKey);
      if (editedData) {
        console.log(`Applying brand edit for ${brandKey}:`, editedData);
        Object.assign(brand, editedData);
      }
    }

    // Apply material edits
    for (const [materialKey, material] of Object.entries(brand.materials)) {
      if (isItemEdited('material', brandKey, materialKey)) {
        const editedData = getEditedItem('material', brandKey, materialKey);
        if (editedData) {
          console.log(`Applying material edit for ${brandKey}/${materialKey}:`, editedData);
          Object.assign(material, editedData);
        }
      }

      // Apply filament edits
      for (const [filamentKey, filament] of Object.entries(material.filaments)) {
        if (isItemEdited('filament', brandKey, materialKey, filamentKey)) {
          const editedData = getEditedItem('filament', brandKey, materialKey, filamentKey);
          if (editedData) {
            console.log(
              `Applying filament edit for ${brandKey}/${materialKey}/${filamentKey}:`,
              editedData,
            );
            Object.assign(filament, editedData);
          }
        }

        // Apply color edits
        for (const [colorKey, color] of Object.entries(filament.colors)) {
          // Apply variant edits
          if (isItemEdited('color_variant', brandKey, materialKey, filamentKey, colorKey)) {
            const editedVariantData = getEditedItem(
              'color_variant',
              brandKey,
              materialKey,
              filamentKey,
              colorKey,
            );
            if (editedVariantData && color.variant) {
              console.log(
                `Applying variant edit for ${brandKey}/${materialKey}/${filamentKey}/${colorKey}:`,
                editedVariantData,
              );
              Object.assign(color.variant, editedVariantData);
            }
          }

          // Apply size edits
          if (isItemEdited('color_size', brandKey, materialKey, filamentKey, colorKey)) {
            const editedSizeData = getEditedItem(
              'color_size',
              brandKey,
              materialKey,
              filamentKey,
              colorKey,
            );
            if (editedSizeData && color.sizes && color.sizes.length > 0) {
              console.log(
                `Applying size edit for ${brandKey}/${materialKey}/${filamentKey}/${colorKey}:`,
                editedSizeData,
              );
              // Replace the first size object with the edited version
              color.sizes[0] = { ...color.sizes[0], ...editedSizeData };
            }
          }
        }
      }
    }
  }

  console.log('Pseudo edits applied successfully, returning edited database');
  return editedDatabase;
}

// Optional: Function to refresh cache if needed during development
export function clearCache() {
  cachedDatabase = null;
  loadingPromise = null;
}

export async function refreshDatabase(): Promise<FilamentDatabase> {
  clearCache();
  return await getFilamentDatabase();
}
