import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { baseFilamentSchema, filamentSchema } from '$lib/validation/filament-schema';
import { createColorFiles, removeUndefined, updateFilament } from '$lib/server/helpers';
import { setFlash } from 'sveltekit-flash-message/server';
import { refreshDatabase } from '$lib/dataCacher';
import { isValidJSON } from '$lib/globalHelpers';

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

  const filamentForm = await superValidate(filamentDataObj, zod(baseFilamentSchema));
  const filamentVariantForm = await superValidate(zod(filamentSchema));

  return {
    brandData,
    materialData,
    filamentForm,
    filamentVariantForm,
    filamentData: filamentDataObj,
  };
};

export const actions = {
  filament: async ({ request, params, cookies }) => {
    const form = await superValidate(request, zod(baseFilamentSchema));
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
  instance: async ({ request, params, cookies }) => {
    let data = await request.formData();
    const form = await superValidate(data, zod(filamentSchema));
    const { brand, material, filament } = params;

    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      let filteredData = removeUndefined(form.data);

      if (isValidJSON(form.data.serializedSizes)) {
        let tempSizesArr = JSON.parse(filteredData.serializedSizes);

        Array.from(tempSizesArr).forEach((size, si) => {
          Object.keys(size).forEach((key) => {
            if (!size[key]) {
              delete size[key];
            }

            if (size[key] === "") {
              delete size[key];
            }
          });
          
          tempSizesArr[si] = size;
        });

        filteredData['sizes'] = tempSizesArr;
      } else {
        filteredData['sizes'] = [];
      }

      if (isValidJSON(form.data.serializedTraits)) {
        filteredData['traits'] = JSON.parse(filteredData.serializedTraits);
      } else {
        filteredData['traits'] = {};
      }
      filteredData['brandName'] = brand;
      filteredData['materialName'] = material;
      filteredData['filamentName'] = filament;
      filteredData['color_name'] = filteredData.color_name;

      await createColorFiles(filteredData);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to update color:', error);
      setFlash({ type: 'error', message: 'Failed to update color. Please try again.' }, cookies);
      return fail(500, { form });
    }

    setFlash({ type: 'success', message: 'Color updated successfully!' }, cookies);
    return { form, type: 'success' };
  },
};
