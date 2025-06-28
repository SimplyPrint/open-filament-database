export const pseudoDelete = (type: 'brand' | 'material' | 'filament', name: string) => {
  const storageKey = 'deletedItems';
  const existingItems = localStorage.getItem(storageKey);
  let deletedItems: Array<{ type: string; name: string }> = [];

  if (existingItems) {
    try {
      deletedItems = JSON.parse(existingItems);
    } catch (error) {
      console.error('Error parsing deleted items from localStorage:', error);
      deletedItems = [];
    }
  }
  const itemExists = deletedItems.some((item) => item.type === type && item.name === name);

  if (!itemExists) {
    deletedItems.push({ type, name });

    localStorage.setItem(storageKey, JSON.stringify(deletedItems));

    const currentPath = window.location.pathname;
    const pathSegments = currentPath.split('/').filter((segment) => segment !== '');
    pathSegments.pop(); // Remove the last segment
    const parentPath = pathSegments.length > 0 ? '/' + pathSegments.join('/') : '/';

    window.location.href = parentPath;
  }
};

export const isItemDeleted = (type: 'brand' | 'material' | 'filament', name: string): boolean => {
  if (typeof localStorage === 'undefined') return false;

  const storageKey = 'deletedItems';
  const existingItems = localStorage.getItem(storageKey);

  if (!existingItems) return false;

  try {
    const deletedItems = JSON.parse(existingItems);
    return deletedItems.some(
      (item: { type: string; name: string }) => item.type === type && item.name === name,
    );
  } catch (error) {
    console.error('Error parsing deleted items from localStorage:', error);
    return false;
  }
};
