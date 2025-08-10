export interface DeletedItem {
  type: 'brand' | 'material' | 'filament' | 'instance';
  name: string;
  brandName?: string;
  materialName?: string;
  filamentName?: string;
}

export const pseudoDelete = (
  type: 'brand' | 'material' | 'filament' | 'instance' | 'store',
  name: string,
  brandName?: string,
  materialName?: string,
  filamentName?: string,
) => {
  const storageKey = 'deletedItems';
  const existingItems = localStorage.getItem(storageKey);
  let deletedItems: DeletedItem[] = [];

  if (existingItems) {
    try {
      deletedItems = JSON.parse(existingItems);
    } catch (error) {
      console.error('Error parsing deleted items from localStorage:', error);
      deletedItems = [];
    }
  }

  // Create item keys that are brand-specific for materials, filaments, and instances
  const itemKey =
    type === 'brand'
      ? `${type}|${name}`
      : type === 'material'
      ? `${type}|${brandName}|${name}`
      : type === 'filament'
      ? `${type}|${brandName}|${materialName}|${name}`
      : `${type}|${brandName}|${materialName}|${filamentName}|${name}`;

  const itemExists = deletedItems.some((item) => {
    const existingKey =
      item.type === 'brand'
        ? `${item.type}|${item.name}`
        : item.type === 'material'
        ? `${item.type}|${item.brandName}|${item.name}`
        : item.type === 'filament'
        ? `${item.type}|${item.brandName}|${item.materialName}|${item.name}`
        : `${item.type}|${item.brandName}|${item.materialName}|${item.filamentName}|${item.name}`;
    return existingKey === itemKey;
  });

  if (!itemExists) {
    const newItem: DeletedItem = {
      type,
      name,
      brandName: type !== 'brand' ? brandName : undefined,
      materialName: type === 'filament' || type === 'instance' ? materialName : undefined,
      filamentName: type === 'instance' ? filamentName : undefined,
    };

    deletedItems.push(newItem);
    localStorage.setItem(storageKey, JSON.stringify(deletedItems));

    // Navigate to parent page
    const currentPath = window.location.pathname;
    const pathSegments = currentPath.split('/').filter((segment) => segment !== '');
    pathSegments.pop(); // Remove the current item
    const parentPath = pathSegments.length > 0 ? '/' + pathSegments.join('/') : '/';

    window.location.href = parentPath;
  }
};

export const pseudoUndoDelete = (
  type: 'brand' | 'material' | 'filament' | 'instance',
  name: string
) => {
  if (typeof localStorage === 'undefined') return true;

  const storageKey = 'deletedItems';
  const existingItems = localStorage.getItem(storageKey);

  if (!existingItems) return true;

  let deletedItems: DeletedItem[] = [];

  if (existingItems) {
    try {
      deletedItems = JSON.parse(existingItems);
    } catch (error) {
      console.error('Error parsing deleted items from localStorage:', error);
      // return true; // We assume the key cannot exist in this case
    }
  }

  deletedItems = deletedItems.filter((item) => {
    return !( // Return false on match
      item.type == type &&
      item.name == name
    )
  });

  localStorage.setItem(storageKey, JSON.stringify(deletedItems));

  return true;
}

export const isItemDeleted = (
  type: 'brand' | 'material' | 'filament' | 'instance',
  name: string,
  brandName?: string,
  materialName?: string,
  filamentName?: string,
): boolean => {
  if (typeof localStorage === 'undefined') return false;

  const storageKey = 'deletedItems';
  const existingItems = localStorage.getItem(storageKey);

  if (!existingItems) return false;

  try {
    const deletedItems: DeletedItem[] = JSON.parse(existingItems);

    return deletedItems.some((item) => {
      if (item.type !== type || item.name !== name) return false;

      switch (type) {
        case 'brand':
          return true;
        case 'material':
          return item.brandName === brandName;
        case 'filament':
          return item.brandName === brandName && item.materialName === materialName;
        case 'instance':
          return (
            item.brandName === brandName &&
            item.materialName === materialName &&
            item.filamentName === filamentName
          );
        default:
          return false;
      }
    });
  } catch (error) {
    console.error('Error parsing deleted items from localStorage:', error);
    return false;
  }
};
