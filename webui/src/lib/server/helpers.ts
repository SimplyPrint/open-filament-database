import type { brandSchema } from '$lib/validation/filament-brand-schema';
import type { z } from 'zod';

import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { filamentMaterialSchema } from '$lib/validation/filament-material-schema';
import type { baseFilamentSchema } from '$lib/validation/filament-schema';

export const removeUndefined = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map(removeUndefined);
  } else if (obj && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj)
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, removeUndefined(v)]),
    );
  }
  return obj;
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.join(__dirname, '../../../../data');

export const createBrand = async (brandData: z.infer<typeof brandSchema>) => {
  const brandDir = path.join(DATA_DIR, brandData.name);
  if (!fs.existsSync(brandDir)) {
    fs.mkdirSync(brandDir, { recursive: true });
  }

  let logoPath = '';
  let logoUrl = '';
  if (
    brandData.logo &&
    typeof brandData.logo === 'object' &&
    typeof brandData.logo.arrayBuffer === 'function'
  ) {
    const arrayBuffer = await brandData.logo.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    logoPath = path.join(brandDir, brandData.logo.name);
    fs.writeFileSync(logoPath, buffer);
    logoUrl = `/data/${brandData.name}/${brandData.logo.name}`;
  }

  const brandJson = {
    brand: brandData.name,
    website: brandData.website,
    logo: logoUrl,
    origin: brandData.origin,
  };

  const brandJsonPath = path.join(brandDir, 'brand.json');
  fs.writeFileSync(brandJsonPath, JSON.stringify(brandJson, null, 2), 'utf-8');

  return brandDir;
};

export async function updateBrand(brandData: z.infer<typeof brandSchema>) {
  const oldDir = path.join(DATA_DIR, brandData.oldBrandName || brandData.name);
  const newDir = path.join(DATA_DIR, brandData.name);

  if (
    brandData.oldBrandName &&
    brandData.oldBrandName !== brandData.name &&
    fs.existsSync(oldDir)
  ) {
    if (fs.existsSync(newDir)) {
      throw new Error(`Brand folder "${brandData.name}" already exists.`);
    }
    fs.renameSync(oldDir, newDir);
  } else if (!fs.existsSync(newDir)) {
    fs.mkdirSync(newDir, { recursive: true });
  }

  // Handle logo upload if it's a new file
  let logoUrl = '';
  if (
    brandData.logo &&
    typeof brandData.logo === 'object' &&
    typeof brandData.logo.arrayBuffer === 'function'
  ) {
    // New logo uploaded
    const arrayBuffer = await brandData.logo.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const logoPath = path.join(newDir, brandData.logo.name);
    fs.writeFileSync(logoPath, buffer);
    logoUrl = `/data/${brandData.name}/${brandData.logo.name}`;
  } else if (typeof brandData.logo === 'string') {
    // Existing logo URL
    logoUrl = brandData.logo;
  } else {
    // Try to find existing logo in the directory
    try {
      const files = fs.readdirSync(newDir);
      const logoFile = files.find(
        (file) => file.toLowerCase().match(/\.(jpg|jpeg|png|gif|webp)$/i) && !file.startsWith('.'),
      );
      if (logoFile) {
        logoUrl = `/data/${brandData.name}/${logoFile}`;
      }
    } catch (error) {
      console.warn('Could not find existing logo:', error);
    }
  }

  const brandJson = {
    name: brandData.name, // Changed from 'brand' to 'name' to match your schema
    website: brandData.website,
    logo: logoUrl,
    origin: brandData.origin,
  };

  const brandJsonPath = path.join(newDir, 'brand.json');
  fs.writeFileSync(brandJsonPath, JSON.stringify(brandJson, null, 2), 'utf-8');

  console.log(`Brand updated: ${brandData.oldBrandName || brandData.name} -> ${brandData.name}`);
  return newDir;
}

export const createMaterial = async (
  brandName: string,
  materialData: z.infer<typeof filamentMaterialSchema>,
) => {
  const brandDir = path.join(DATA_DIR, brandName);

  if (!fs.existsSync(brandDir)) {
    throw new Error(`Brand directory "${brandName}" does not exist.`);
  }

  const materialDir = path.join(brandDir, materialData.name);
  if (fs.existsSync(materialDir)) {
    throw new Error(`Material "${materialData.name}" already exists in brand "${brandName}".`);
  }

  try {
    fs.mkdirSync(materialDir, { recursive: true });

    const materialJsonPath = path.join(materialDir, 'material.json');
    const transformedData = transformMaterialData(materialData);

    fs.writeFileSync(materialJsonPath, JSON.stringify(transformedData, null, 2), 'utf-8');
  } catch (error) {
    console.error('Error creating material:', error);
    throw error;
  }
};
function transformMaterialData(materialData: any) {
  const transformedData: any = {
    name: materialData.name,
  };

  // Handle generic settings - already in correct structure
  if (materialData.generic) {
    const genericSettings: any = {};
    if (
      materialData.generic.first_layer_bed_temp !== undefined &&
      materialData.generic.first_layer_bed_temp !== null
    ) {
      genericSettings.first_layer_bed_temp = materialData.generic.first_layer_bed_temp;
    }
    if (
      materialData.generic.first_layer_nozzle_temp !== undefined &&
      materialData.generic.first_layer_nozzle_temp !== null
    ) {
      genericSettings.first_layer_nozzle_temp = materialData.generic.first_layer_nozzle_temp;
    }
    if (materialData.generic.bed_temp !== undefined && materialData.generic.bed_temp !== null) {
      genericSettings.bed_temp = materialData.generic.bed_temp;
    }
    if (
      materialData.generic.nozzle_temp !== undefined &&
      materialData.generic.nozzle_temp !== null
    ) {
      genericSettings.nozzle_temp = materialData.generic.nozzle_temp;
    }
    // Only add generic object if it has properties
    if (Object.keys(genericSettings).length > 0) {
      transformedData.generic = genericSettings;
    }
  }

  // Handle PrusaSlicer settings
  if (materialData.prusa) {
    const prusaSettings: any = {};
    if (materialData.prusa.prusa_profile_path) {
      prusaSettings.profile_path = materialData.prusa.prusa_profile_path;
    }

    // Handle prusa overrides
    if (materialData.prusa.prusa_overrides) {
      const overrides = materialData.prusa.prusa_overrides;
      if (overrides.first_layer_bed_temp !== undefined) {
        prusaSettings.first_layer_bed_temp = overrides.first_layer_bed_temp;
      }
      if (overrides.first_layer_nozzle_temp !== undefined) {
        prusaSettings.first_layer_nozzle_temp = overrides.first_layer_nozzle_temp;
      }
      if (overrides.bed_temp !== undefined) {
        prusaSettings.bed_temp = overrides.bed_temp;
      }
      if (overrides.nozzle_temp !== undefined) {
        prusaSettings.nozzle_temp = overrides.nozzle_temp;
      }
    }

    // Only add prusa object if it has properties
    if (Object.keys(prusaSettings).length > 0) {
      transformedData.prusa = prusaSettings;
    }
  }

  // Handle Bambu Studio settings
  if (materialData.bambus) {
    const bambusSettings: any = {};
    if (materialData.bambus.bambus_profile_path) {
      bambusSettings.profile_path = materialData.bambus.bambus_profile_path;
    }

    // Handle bambus overrides
    if (materialData.bambus.bambus_overrides) {
      const overrides = materialData.bambus.bambus_overrides;
      if (overrides.first_layer_bed_temp !== undefined) {
        bambusSettings.first_layer_bed_temp = overrides.first_layer_bed_temp;
      }
      if (overrides.first_layer_nozzle_temp !== undefined) {
        bambusSettings.first_layer_nozzle_temp = overrides.first_layer_nozzle_temp;
      }
      if (overrides.bed_temp !== undefined) {
        bambusSettings.bed_temp = overrides.bed_temp;
      }
      if (overrides.nozzle_temp !== undefined) {
        bambusSettings.nozzle_temp = overrides.nozzle_temp;
      }
    }

    // Only add bambus object if it has properties
    if (Object.keys(bambusSettings).length > 0) {
      transformedData.bambus = bambusSettings;
    }
  }

  // Handle OrcaSlicer settings
  if (materialData.orca) {
    const orcaSettings: any = {};
    if (materialData.orca.orca_profile_path) {
      orcaSettings.profile_path = materialData.orca.orca_profile_path;
    }

    // Handle orca overrides
    if (materialData.orca.orca_overrides) {
      const overrides = materialData.orca.orca_overrides;
      if (overrides.first_layer_bed_temp !== undefined) {
        orcaSettings.first_layer_bed_temp = overrides.first_layer_bed_temp;
      }
      if (overrides.first_layer_nozzle_temp !== undefined) {
        orcaSettings.first_layer_nozzle_temp = overrides.first_layer_nozzle_temp;
      }
      if (overrides.bed_temp !== undefined) {
        orcaSettings.bed_temp = overrides.bed_temp;
      }
      if (overrides.nozzle_temp !== undefined) {
        orcaSettings.nozzle_temp = overrides.nozzle_temp;
      }
    }

    // Only add orca object if it has properties
    if (Object.keys(orcaSettings).length > 0) {
      transformedData.orca = orcaSettings;
    }
  }

  // Handle Cura settings
  if (materialData.cura) {
    const curaSettings: any = {};
    if (materialData.cura.cura_profile_path) {
      curaSettings.profile_path = materialData.cura.cura_profile_path;
    }

    // Handle cura overrides
    if (materialData.cura.cura_overrides) {
      const overrides = materialData.cura.cura_overrides;
      if (overrides.first_layer_bed_temp !== undefined) {
        curaSettings.first_layer_bed_temp = overrides.first_layer_bed_temp;
      }
      if (overrides.first_layer_nozzle_temp !== undefined) {
        curaSettings.first_layer_nozzle_temp = overrides.first_layer_nozzle_temp;
      }
      if (overrides.bed_temp !== undefined) {
        curaSettings.bed_temp = overrides.bed_temp;
      }
      if (overrides.nozzle_temp !== undefined) {
        curaSettings.nozzle_temp = overrides.nozzle_temp;
      }
    }

    // Only add cura object if it has properties
    if (Object.keys(curaSettings).length > 0) {
      transformedData.cura = curaSettings;
    }
  }

  return transformedData;
}

export const createFilament = async (
  brandName: string,
  materialName: string,
  filamentData: z.infer<typeof baseFilamentSchema>,
) => {
  const brandDir = path.join(DATA_DIR, brandName);
  if (!fs.existsSync(brandDir)) {
    throw new Error(`Brand directory "${brandName}" does not exist.`);
  }

  const materialDir = path.join(brandDir, materialName);
  if (!fs.existsSync(materialDir)) {
    throw new Error(`Material directory "${materialName}" does not exist in brand "${brandName}".`);
  }

  const filamentDir = path.join(materialDir, filamentData.name);
  if (!fs.existsSync(filamentDir)) {
    fs.mkdirSync(filamentDir, { recursive: true });
  }

  const filamentJsonPath = path.join(filamentDir, 'filament.json');
  fs.writeFileSync(filamentJsonPath, JSON.stringify(filamentData, null, 2), 'utf-8');

  return filamentDir;
};

export async function createColorFiles(formData: any) {
  const DATA_DIR_FILAMENT = path.resolve('../data');
  const colorFolder = path.join(
    DATA_DIR_FILAMENT,
    formData.brandName,
    formData.materialName,
    formData.filamentName,
    formData.color_name,
  );

  if (!fs.existsSync(colorFolder)) fs.mkdirSync(colorFolder, { recursive: true });
  const sizeFields = [
    'filament_weight',
    'empty_spool_weight',
    'diameter',
    'spool_refill',
    'sku',
    'ean',
    'purchase_links',
  ];
  const sizeObj: any = {};
  for (const key of sizeFields) {
    if (formData[key] !== undefined) sizeObj[key] = formData[key];
  }
  if (formData.diameter_tolerance !== undefined)
    sizeObj.diameter_tolerance = formData.diameter_tolerance;
  if (formData.density !== undefined) sizeObj.density = formData.density;

  // Read existing sizes.json if it exists, otherwise start with empty array
  let sizesArr: any[] = [];
  const sizesPath = path.join(colorFolder, 'sizes.json');
  if (fs.existsSync(sizesPath)) {
    try {
      sizesArr = JSON.parse(fs.readFileSync(sizesPath, 'utf-8'));
      if (!Array.isArray(sizesArr)) sizesArr = [];
    } catch {
      sizesArr = [];
    }
  }
  // Add the new size object if it has at least filament_weight or diameter
  if (Object.keys(sizeObj).length > 0) {
    sizesArr.push(removeUndefined(sizeObj));
  }
  fs.writeFileSync(sizesPath, JSON.stringify(sizesArr, null, 2), 'utf-8');

  // --- 2. Prepare variant.json (single object) ---
  // Traits are grouped under a "traits" object
  const traitKeys = ['translucent', 'glow', 'matte', 'recycled', 'recyclable', 'biodegradable'];
  const traits: Record<string, boolean> = {};
  for (const key of traitKeys) {
    if (formData[key] !== undefined) traits[key] = formData[key];
  }

  // Only include traits if at least one is present
  const variantObj: any = {
    color_name: formData.color_name,
    color_hex: formData.color_hex,
  };
  if (Object.keys(traits).length > 0) {
    variantObj.traits = traits;
  }
  // Add any additional fields you want in variant.json
  if (formData.data_sheet_url) variantObj.data_sheet_url = formData.data_sheet_url;
  if (formData.safety_sheet_url) variantObj.safety_sheet_url = formData.safety_sheet_url;

  fs.writeFileSync(
    path.join(colorFolder, 'variant.json'),
    JSON.stringify(removeUndefined(variantObj), null, 2),
    'utf-8',
  );
}

function copyFileSync(src: string, dest: string) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

export function prepareFilamentDownload(colorFolder: string, tempDownloadDir: string) {
  for (const file of ['sizes.json', 'variant.json']) {
    const srcFile = path.join(colorFolder, file);
    if (fs.existsSync(srcFile)) {
      copyFileSync(
        srcFile,
        path.join(tempDownloadDir, path.relative('src/data', path.join(colorFolder, file))),
      );
    }
  }

  const filamentFolder = path.dirname(colorFolder);
  const filamentJson = path.join(filamentFolder, 'filament.json');
  if (fs.existsSync(filamentJson)) {
    copyFileSync(filamentJson, path.join(tempDownloadDir, path.relative('src/data', filamentJson)));
  }

  const materialFolder = path.dirname(filamentFolder);
  const materialJson = path.join(materialFolder, 'material.json');
  if (fs.existsSync(materialJson)) {
    copyFileSync(materialJson, path.join(tempDownloadDir, path.relative('src/data', materialJson)));
  }

  const brandFolder = path.dirname(materialFolder);
  const brandJson = path.join(brandFolder, 'brand.json');
  if (fs.existsSync(brandJson)) {
    copyFileSync(brandJson, path.join(tempDownloadDir, path.relative('src/data', brandJson)));
  }
}

export function downloadColor(brand: string, material: string, filament: string, color: string) {
  const url = `/api/download/${encodeURIComponent(brand)}/${encodeURIComponent(
    material,
  )}/${encodeURIComponent(filament)}/${encodeURIComponent(color)}`;

  const a = document.createElement('a');
  a.href = url;
  a.download = '';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
export function updateMaterial(brandName: string, currentMaterialName: string, materialData: any) {
  const brandDir = path.join(DATA_DIR, brandName);

  if (!fs.existsSync(brandDir)) {
    throw new Error(`Brand directory "${brandName}" does not exist.`);
  }

  const currentMaterialDir = path.join(brandDir, currentMaterialName);

  if (!fs.existsSync(currentMaterialDir)) {
    throw new Error(
      `Material directory "${currentMaterialName}" not found in brand "${brandName}"`,
    );
  }

  try {
    if (materialData.name !== currentMaterialName) {
      const newMaterialDir = path.join(brandDir, materialData.name);

      if (fs.existsSync(newMaterialDir)) {
        throw new Error(`Material "${materialData.name}" already exists in brand "${brandName}"`);
      }

      fs.renameSync(currentMaterialDir, newMaterialDir);

      const materialJsonPath = path.join(newMaterialDir, 'material.json');
      const transformedData = transformMaterialData(materialData);

      fs.writeFileSync(materialJsonPath, JSON.stringify(transformedData, null, 2), 'utf-8');
    } else {
      const materialJsonPath = path.join(currentMaterialDir, 'material.json');

      const transformedData = transformMaterialData(materialData);

      fs.writeFileSync(materialJsonPath, JSON.stringify(transformedData, null, 2), 'utf-8');
    }
  } catch (error) {
    console.error('Error updating material:', error);
    throw error;
  }
}

export function updateFilament(
  brandName: string,
  materialName: string,
  currentFilamentName: string,
  filamentData: any,
) {
  const brandDir = path.join(DATA_DIR, brandName);

  if (!fs.existsSync(brandDir)) {
    throw new Error(`Brand directory "${brandName}" does not exist.`);
  }

  const materialDir = path.join(brandDir, materialName);
  if (!fs.existsSync(materialDir)) {
    throw new Error(`Material directory "${materialName}" does not exist in brand "${brandName}".`);
  }

  const currentFilamentDir = path.join(materialDir, currentFilamentName);
  if (!fs.existsSync(currentFilamentDir)) {
    throw new Error(
      `Filament directory "${currentFilamentName}" not found in material "${materialName}"`,
    );
  }

  try {
    if (filamentData.name !== currentFilamentName) {
      const newFilamentDir = path.join(materialDir, filamentData.name);

      if (fs.existsSync(newFilamentDir)) {
        throw new Error(
          `Filament "${filamentData.name}" already exists in material "${materialName}"`,
        );
      }

      fs.renameSync(currentFilamentDir, newFilamentDir);

      const filamentJsonPath = path.join(newFilamentDir, 'filament.json');
      const transformedData = transformFilamentData(filamentData);

      fs.writeFileSync(filamentJsonPath, JSON.stringify(transformedData, null, 2), 'utf-8');

      console.log(
        `Filament updated and renamed: ${brandName}/${materialName}/${currentFilamentName} -> ${filamentData.name}`,
      );
    } else {
      const filamentJsonPath = path.join(currentFilamentDir, 'filament.json');

      const transformedData = transformFilamentData(filamentData);

      fs.writeFileSync(filamentJsonPath, JSON.stringify(transformedData, null, 2), 'utf-8');

      console.log(`Filament updated: ${brandName}/${materialName}/${currentFilamentName}`);
    }
  } catch (error) {
    console.error('Error updating filament:', error);
    throw error;
  }
}

function transformFilamentData(filamentData: any) {
  const transformedData: any = {
    name: filamentData.name,
  };

  // Add filament-specific properties
  if (filamentData.diameter_tolerance !== undefined) {
    transformedData.diameter_tolerance = filamentData.diameter_tolerance;
  }
  if (filamentData.density !== undefined) {
    transformedData.density = filamentData.density;
  }
  if (filamentData.data_sheet_url !== undefined) {
    transformedData.data_sheet_url = filamentData.data_sheet_url;
  }
  if (filamentData.safety_sheet_url !== undefined) {
    transformedData.safety_sheet_url = filamentData.safety_sheet_url;
  }

  // Add slicer profile paths if they exist
  if (filamentData.prusa_profile_path !== undefined) {
    transformedData.prusa_profile_path = filamentData.prusa_profile_path;
  }
  if (filamentData.bambus_profile_path !== undefined) {
    transformedData.bambus_profile_path = filamentData.bambus_profile_path;
  }
  if (filamentData.orca_profile_path !== undefined) {
    transformedData.orca_profile_path = filamentData.orca_profile_path;
  }
  if (filamentData.cura_profile_path !== undefined) {
    transformedData.cura_profile_path = filamentData.cura_profile_path;
  }

  return removeUndefined(transformedData);
}

export function flattenMaterialData(materialData: any) {
  const flattened: any = {
    name: materialData.name,
  };

  // Build nested structure that matches your form schema
  flattened.generic = {
    first_layer_bed_temp: materialData.generic?.first_layer_bed_temp,
    first_layer_nozzle_temp: materialData.generic?.first_layer_nozzle_temp,
    bed_temp: materialData.generic?.bed_temp,
    nozzle_temp: materialData.generic?.nozzle_temp,
  };

  flattened.prusa = {
    prusa_profile_path: materialData.prusa?.profile_path, // This should match your JSON structure
    prusa_overrides: {
      // Map the direct properties from prusa object to overrides
      first_layer_bed_temp: materialData.prusa?.first_layer_bed_temp,
      first_layer_nozzle_temp: materialData.prusa?.first_layer_nozzle_temp,
      bed_temp: materialData.prusa?.bed_temp,
      nozzle_temp: materialData.prusa?.nozzle_temp,
    },
  };

  flattened.bambus = {
    bambus_profile_path: materialData.bambus?.profile_path,
    bambus_overrides: {
      first_layer_bed_temp: materialData.bambus?.first_layer_bed_temp,
      first_layer_nozzle_temp: materialData.bambus?.first_layer_nozzle_temp,
      bed_temp: materialData.bambus?.bed_temp,
      nozzle_temp: materialData.bambus?.nozzle_temp,
    },
  };

  flattened.orca = {
    orca_profile_path: materialData.orca?.profile_path,
    orca_overrides: {
      first_layer_bed_temp: materialData.orca?.first_layer_bed_temp,
      first_layer_nozzle_temp: materialData.orca?.first_layer_nozzle_temp,
      bed_temp: materialData.orca?.bed_temp,
      nozzle_temp: materialData.orca?.nozzle_temp,
    },
  };

  flattened.cura = {
    cura_profile_path: materialData.cura?.profile_path,
    cura_overrides: {
      first_layer_bed_temp: materialData.cura?.first_layer_bed_temp,
      first_layer_nozzle_temp: materialData.cura?.first_layer_nozzle_temp,
      bed_temp: materialData.cura?.bed_temp,
      nozzle_temp: materialData.cura?.nozzle_temp,
    },
  };

  return flattened;
}
