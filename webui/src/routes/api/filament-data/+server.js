// src/routes/api/filament-data/+server.js

import fs from 'fs';
import path from 'path';
import Filament from "$schemas/filament.js";
import FilamentSize from "$schemas/filament-size.js";
import FilamentVariant from "$schemas/filament-variant.js";
import FilamentMaterial from "$schemas/filament-material.js";
import FilamentBrand from "$schemas/filament-brand.js";

/**
 * Safely reads and parses a JSON file if it exists. Otherwise returns null.
 */
function readJsonIfExists(filePath) {
    if (!fs.existsSync(filePath)) return null;
    const data = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(data);
}

/**
 * Load all variant folders in a single filament folder.
 * - Looks for `variant.json` and `sizes.json`.
 */
function loadVariants(filamentDir) {
    // Each variant is in its own folder: .../VariantName/variant.json, sizes.json
    const variantDirs = fs
        .readdirSync(filamentDir)
        .filter((entry) => {
            const fullPath = path.join(filamentDir, entry);
            return (
                !entry.startsWith('.') && // skip hidden
                fs.statSync(fullPath).isDirectory()
            );
        });

    return variantDirs.map((variantFolder) => {
        const variantPath = path.join(filamentDir, variantFolder);
        const variantData = readJsonIfExists(path.join(variantPath, 'variant.json'));
        const sizesData = readJsonIfExists(path.join(variantPath, 'sizes.json'));

        return {
            variant: variantData ? new FilamentVariant(variantData) : null,
            sizes: Array.isArray(sizesData)
                ? sizesData.map((sd) => new FilamentSize(sd))
                : []
        };
    });
}

/**
 * Load all filaments in a material folder.
 * - Looks for `filament.json`
 * - Then loads subdirectories for variants
 */
function loadFilaments(materialDir) {
    // Each filament is in its own folder: .../FilamentName/filament.json
    const filamentDirs = fs
        .readdirSync(materialDir)
        .filter((entry) => {
            const fullPath = path.join(materialDir, entry);
            return (
                !entry.startsWith('.') &&
                fs.statSync(fullPath).isDirectory()
            );
        });

    return filamentDirs.map((filamentFolder) => {
        const filamentPath = path.join(materialDir, filamentFolder);
        const filamentData = readJsonIfExists(path.join(filamentPath, 'filament.json'));
        return {
            filament: filamentData ? new Filament(filamentData) : null,
            variants: loadVariants(filamentPath)
        };
    });
}

/**
 * Load all materials in a brand folder.
 * - Looks for `material.json`
 * - Then loads subdirectories for filaments
 */
function loadMaterials(brandDir) {
    // Each material is in its own folder: .../MaterialName/material.json
    const materialDirs = fs
        .readdirSync(brandDir)
        .filter((entry) => {
            const fullPath = path.join(brandDir, entry);
            return (
                !entry.startsWith('.') &&
                fs.statSync(fullPath).isDirectory()
            );
        });

    return materialDirs.map((materialFolder) => {
        const materialPath = path.join(brandDir, materialFolder);
        const materialData = readJsonIfExists(path.join(materialPath, 'material.json'));
        return {
            material: materialData ? new FilamentMaterial(materialData) : null,
            filaments: loadFilaments(materialPath)
        };
    });
}

/**
 * Loads all brand folders in the `data` directory.
 * - Looks for `brand.json`
 * - Then loads subdirectories for materials
 */
function loadBrands(dataDir) {
    const brandDirs = fs
        .readdirSync(dataDir)
        .filter((entry) => {
            const fullPath = path.join(dataDir, entry);
            return (
                !entry.startsWith('.') &&
                fs.statSync(fullPath).isDirectory()
            );
        });

    return brandDirs.map((brandFolder) => {
        const brandPath = path.join(dataDir, brandFolder);
        const brandData = readJsonIfExists(path.join(brandPath, 'brand.json'));

        return {
            brand: brandData ? new FilamentBrand(brandData) : null,
            materials: loadMaterials(brandPath)
        };
    });
}

/**
 * Main entry to load everything from `data` folder into a structured array.
 */
function loadFilamentDatabase(rootDir) {
    return loadBrands(rootDir);
}

// Example usage in SvelteKit (server load or API route)
export async function GET() {
    const dataDir = path.join(process.cwd(), './../data');
    const structure = loadFilamentDatabase(dataDir);
    return new Response(JSON.stringify(structure), {status: 200});
}
