import { readdir, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
export interface FilamentDatabase {
  brands: Record<string, Brand>;
}

interface Brand {
  brand: string;
  logo: string;
  website?: string;
  origin?: string;
  materials: Record<string, Material>;
}

interface Material {
  material: string;
  filaments: Record<string, Filament>;
}

interface Filament {
  name: string;
  colors: Record<string, Color>;
}

interface Color {
  name: string;
  sizes: Size[];
  variant: Variant;
}

interface Size {
  filament_weight: number;
  diameter: number;
  ean: string;
  purchase_links: PurchaseLink[];
}

interface PurchaseLink {
  store_id: string;
  url: string;
  affiliate: boolean;
}

interface Variant {
  [key: string]: any;
}

export async function loadFilamentDatabase(dataPath: string): Promise<FilamentDatabase> {
  console.log('Running optimized parser!');
  const startMem = process.memoryUsage().heapUsed;
  const brands: Record<string, Brand> = {};

  try {
    const brandFolders = await readdir(dataPath, { withFileTypes: true });
    const brandDirents = brandFolders.filter((dirent) => dirent.isDirectory());

    // Process all brands in parallel
    const brandPromises = brandDirents.map(async (brandFolder) => {
      const brandPath = join(dataPath, brandFolder.name);
      const brandJsonPath = join(brandPath, 'brand.json');

      if (!existsSync(brandJsonPath)) return null;

      // Read brand data and find logo in parallel
      const [brandDataBuffer, files] = await Promise.all([
        readFile(brandJsonPath),
        readdir(brandPath),
      ]);

      const brandData = JSON.parse(brandDataBuffer.toString());
      const logoFile = files.find((file) => /\.(png|jpg|jpeg|svg)$/i.test(file));
      const logo = logoFile ? `/data/${brandFolder.name}/${logoFile}` : '';

      // Get material folders
      const materialFolders = await readdir(brandPath, { withFileTypes: true });
      const materialDirents = materialFolders.filter((dirent) => dirent.isDirectory());

      // Process all materials in parallel
      const materialPromises = materialDirents.map(async (materialFolder) => {
        const materialPath = join(brandPath, materialFolder.name);
        const materialJsonPath = join(materialPath, 'material.json');

        if (!existsSync(materialJsonPath)) return null;

        const materialData = JSON.parse(await readFile(materialJsonPath, 'utf-8'));

        // Get filament folders
        const filamentFolders = await readdir(materialPath, { withFileTypes: true });
        const filamentDirents = filamentFolders.filter((dirent) => dirent.isDirectory());

        // Process all filaments in parallel
        const filamentPromises = filamentDirents.map(async (filamentFolder) => {
          const filamentPath = join(materialPath, filamentFolder.name);
          const filamentJsonPath = join(filamentPath, 'filament.json');

          if (!existsSync(filamentJsonPath)) return null;

          const filamentData = JSON.parse(await readFile(filamentJsonPath, 'utf-8'));

          // Get color folders
          const colorFolders = await readdir(filamentPath, { withFileTypes: true });
          const colorDirents = colorFolders.filter((dirent) => dirent.isDirectory());

          // Process all colors in parallel
          const colorPromises = colorDirents.map(async (colorFolder) => {
            const colorPath = join(filamentPath, colorFolder.name);
            const sizesJsonPath = join(colorPath, 'sizes.json');
            const variantJsonPath = join(colorPath, 'variant.json');

            if (!existsSync(sizesJsonPath) || !existsSync(variantJsonPath)) return null;

            // Read both files in parallel
            const [sizesBuffer, variantBuffer] = await Promise.all([
              readFile(sizesJsonPath),
              readFile(variantJsonPath),
            ]);

            const sizesData: Size[] = JSON.parse(sizesBuffer.toString());
            const variantData: Variant = JSON.parse(variantBuffer.toString());

            return {
              key: colorFolder.name,
              value: {
                name: colorFolder.name,
                sizes: sizesData,
                variant: variantData,
              },
            };
          });

          const colorResults = await Promise.all(colorPromises);
          const colors: Record<string, Color> = {};

          colorResults.forEach((result) => {
            if (result) colors[result.key] = result.value;
          });

          return {
            key: filamentFolder.name,
            value: {
              ...filamentData,
              name: filamentFolder.name,
              colors,
            },
          };
        });

        const filamentResults = await Promise.all(filamentPromises);
        const filaments: Record<string, Filament> = {};

        filamentResults.forEach((result) => {
          if (result) filaments[result.key] = result.value;
        });

        return {
          key: materialFolder.name,
          value: {
            ...materialData,
            name: materialFolder.name,
            filaments,
          },
        };
      });

      const materialResults = await Promise.all(materialPromises);
      const materials: Record<string, Material> = {};

      materialResults.forEach((result) => {
        if (result) materials[result.key] = result.value;
      });

      return {
        key: brandFolder.name,
        value: {
          brand: brandData.brand ?? brandFolder.name,
          logo,
          website: brandData.website ?? '',
          origin: brandData.origin ?? '',
          materials,
        },
      };
    });

    const brandResults = await Promise.all(brandPromises);

    brandResults.forEach((result) => {
      if (result) brands[result.key] = result.value;
    });
  } catch (error) {
    console.error('Error loading filament database:', error);
    throw error;
  }
  const endMem = process.memoryUsage().heapUsed;
  console.log(
    `Filament DB: ${(endMem / 1024 / 1024).toFixed(2)} MB used (${(
      (endMem - startMem) /
      1024 /
      1024
    ).toFixed(2)} MB delta)`,
  );
  return { brands };
}
