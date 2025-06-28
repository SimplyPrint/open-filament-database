import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { filamentSchema, filamentVariantSchema } from '$lib/validation/filament-schema';
import fs from 'node:fs';
import path from 'node:path';
import { createColorFiles, removeUndefined, updateFilament } from '$lib/server/helpers';
import { setFlash } from 'sveltekit-flash-message/server';
import { refreshDatabase } from '$lib/dataCacher';

export const load: PageServerLoad = async ({ params, parent }) => {
  const { brand, material, filament } = params;
  const { filamentData } = await parent();

  const normalizedBrand = brand.trim().toLowerCase().replace(/\s+/g, '');
  const normalizedMaterial = material.trim().toLowerCase().replace(/\s+/g, '');
  const normalizedFilament = filament.trim().toLowerCase().replace(/\s+/g, '');

  const brandKey = Object.keys(filamentData.brands).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedBrand,
  );
  if (!brandKey) throw error(404, 'Brand not found');
  const brandData = filamentData.brands[brandKey];

  const materialKey = Object.keys(brandData.materials).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedMaterial,
  );
  if (!materialKey) throw error(404, 'Material not found');
  const materialData = brandData.materials[materialKey];

  const filamentKey = Object.keys(materialData.filaments).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedFilament,
  );
  if (!filamentKey) throw error(404, 'Filament not found');
  const filamentDataObj = materialData.filaments[filamentKey];

  const filamentForm = await superValidate(filamentDataObj, zod(filamentSchema));
  const filamentVariantForm = await superValidate(zod(filamentVariantSchema));

  return {
    brandData,
    materialData,
    filamentForm,
    filamentVariantForm,
    filamentData: filamentDataObj,
  };
};

export const actions = {
  createFilament: async ({ url, request, cookies }) => {
    const form = await superValidate(request, zod(filamentVariantSchema));
    if (!form.valid) {
      fail(400, { form });
    }
    try {
      const DATA_DIR = path.resolve('../data');
      const colorFolder = path.join(
        DATA_DIR,
        form.data.brandName,
        form.data.materialName,
        form.data.filamentName,
        form.data.color_name,
      );

      if (!fs.existsSync(colorFolder)) {
        fs.mkdirSync(colorFolder, { recursive: true });
      }

      await createColorFiles(form.data);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to create color:', error);
      setFlash({ type: 'error', message: 'Failed to create color. Please try again.' }, cookies);
      return fail(500, { form });
    }

    // Redirect to current page with success message
    setFlash({ type: 'success', message: 'Color created successfully!' }, cookies);
    redirect(303, url.pathname);
  },
  filament: async ({ request, params, cookies }) => {
    const form = await superValidate(request, zod(filamentSchema));
    const { brand, material, filament } = params;

    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      const filteredFilament = removeUndefined(form.data);
      await updateFilament(brand, material, filament, filteredFilament);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to update filament:', error);
      setFlash({ type: 'error', message: 'Failed to update filament. Please try again.' }, cookies);
      return fail(500, { form });
    }

    setFlash({ type: 'success', message: 'Filament updated successfully!' }, cookies);
    return { form, success: true };
  },
};
