export interface EditedItem {
  type: 'brand' | 'material' | 'filament' | 'color_variant' | 'color_size';
  brandName: string;
  materialName?: string;
  filamentName?: string;
  colorName?: string;
  data: any;
  timestamp: number;
}

export const pseudoEdit = (
  type: 'brand' | 'material' | 'filament' | 'color_variant' | 'color_size',
  brandName: string,
  data: any,
  materialName?: string,
  filamentName?: string,
  colorName?: string,
) => {
  const storageKey = 'editedItems';
  const existingItems = localStorage.getItem(storageKey);
  let editedItems: EditedItem[] = [];

  if (existingItems) {
    try {
      editedItems = JSON.parse(existingItems);
    } catch (error) {
      console.error('Error parsing edited items from localStorage:', error);
      editedItems = [];
    }
  }

  // Create unique identifier for the item
  const itemKey = createItemKey(type, brandName, materialName, filamentName, colorName);

  // Remove existing edit for this item if it exists
  editedItems = editedItems.filter(
    (item) =>
      createItemKey(
        item.type,
        item.brandName,
        item.materialName,
        item.filamentName,
        item.colorName,
      ) !== itemKey,
  );

  // Add new edit
  editedItems.push({
    type,
    brandName,
    materialName,
    filamentName,
    colorName,
    data,
    timestamp: Date.now(),
  });

  localStorage.setItem(storageKey, JSON.stringify(editedItems));
};

export const getEditedItem = (
  type: 'brand' | 'material' | 'filament' | 'color_variant' | 'color_size',
  brandName: string,
  materialName?: string,
  filamentName?: string,
  colorName?: string,
): any | null => {
  if (typeof localStorage === 'undefined') return null;

  const storageKey = 'editedItems';
  const existingItems = localStorage.getItem(storageKey);

  if (!existingItems) return null;

  try {
    const editedItems: EditedItem[] = JSON.parse(existingItems);
    const itemKey = createItemKey(type, brandName, materialName, filamentName, colorName);

    const editedItem = editedItems.find(
      (item) =>
        createItemKey(
          item.type,
          item.brandName,
          item.materialName,
          item.filamentName,
          item.colorName,
        ) === itemKey,
    );

    return editedItem ? editedItem.data : null;
  } catch (error) {
    console.error('Error parsing edited items from localStorage:', error);
    return null;
  }
};

export const isItemEdited = (
  type: 'brand' | 'material' | 'filament' | 'color_variant' | 'color_size',
  brandName: string,
  materialName?: string,
  filamentName?: string,
  colorName?: string,
): boolean => {
  return getEditedItem(type, brandName, materialName, filamentName, colorName) !== null;
};

export const clearEditedItems = () => {
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem('editedItems');
  }
};

export const getAllEditedItems = (): EditedItem[] => {
  if (typeof localStorage === 'undefined') return [];

  const storageKey = 'editedItems';
  const existingItems = localStorage.getItem(storageKey);

  if (!existingItems) return [];

  try {
    return JSON.parse(existingItems);
  } catch (error) {
    console.error('Error parsing edited items from localStorage:', error);
    return [];
  }
};

function createItemKey(
  type: string,
  brandName: string,
  materialName?: string,
  filamentName?: string,
  colorName?: string,
): string {
  const parts = [type, brandName];
  if (materialName) parts.push(materialName);
  if (filamentName) parts.push(filamentName);
  if (colorName) parts.push(colorName);
  return parts.join('|');
}
