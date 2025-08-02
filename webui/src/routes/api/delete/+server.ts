import { json } from '@sveltejs/kit';
import fs from 'node:fs';
import path from 'node:path';
import { refreshDatabase } from '$lib/dataCacher';

const DATA_DIR = path.resolve('../data');

function deleteFolderRecursive(folderPath) {
  if (fs.existsSync(folderPath)) {
    fs.rmSync(folderPath, { recursive: true, force: true });
    return true;
  }
  return false;
}

export async function DELETE({ request }) {
  try {
    const { type, name, brandName, materialName, filamentName } = await request.json();

    let targetPath;

    switch (type) {
      case 'brand':
        targetPath = path.join(DATA_DIR, name);
        break;

      case 'material':
        if (!brandName) {
          return json({ error: 'Brand name is required for material deletion' }, { status: 400 });
        }
        targetPath = path.join(DATA_DIR, brandName, name);
        break;

      case 'filament':
        if (!brandName || !materialName) {
          return json(
            { error: 'Brand name and material name are required for filament deletion' },
            { status: 400 },
          );
        }
        targetPath = path.join(DATA_DIR, brandName, materialName, name);
        break;

      case 'instance':
        if (!brandName || !materialName || !filamentName) {
          return json(
            {
              error:
                'Brand name, material name, and filament name are required for instance deletion',
            },
            { status: 400 },
          );
        }
        targetPath = path.join(DATA_DIR, brandName, materialName, filamentName, name);
        break;

      default:
        return json(
          { error: 'Invalid type. Must be brand, material, filament, or instance' },
          { status: 400 },
        );
    }

    // Check if the path exists and is within the data directory (security check)
    if (!targetPath.startsWith(DATA_DIR)) {
      return json({ error: 'Invalid path' }, { status: 400 });
    }

    const deleted = deleteFolderRecursive(targetPath);

    if (deleted) {
      await refreshDatabase();
      return json({ success: true, message: `${type} "${name}" deleted successfully` });
    } else {
      return json({ error: `${type} "${name}" not found` }, { status: 404 });
    }
  } catch (error) {
    console.error('Delete error:', error);
    return json({ error: 'Internal server error' }, { status: 500 });
  }
}
