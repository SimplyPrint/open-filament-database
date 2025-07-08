import { error, fail, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { removeUndefined, updateColorSize, updateColorVariant } from '$lib/server/helpers';
import { setFlash } from 'sveltekit-flash-message/server';
import { filamentSizeSchema } from '$lib/validation/filament-size-schema';
import { filamentVariantSchema } from '$lib/validation/filament-variant-schema';
import { env } from '$env/dynamic/public';
import { refreshDatabase } from '$lib/dataCacher';

export const load: PageServerLoad = async ({ params, parent }) => {
  const { brand, material, filament, instance } = params;
  const { filamentData } = await parent();

  // Normalize the params for lookup
  const normalizedBrand = brand.trim().toLowerCase().replace(/\s+/g, '');
  const normalizedMaterial = material.trim().toLowerCase().replace(/\s+/g, '');
  const normalizedFilament = filament.trim().toLowerCase().replace(/\s+/g, '');
  const normalizedInstance = instance.trim().toLowerCase().replace(/\s+/g, '');

  // Find the brand
  const brandKey = Object.keys(filamentData.brands).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedBrand,
  );
  if (!brandKey) {
    error(404, 'Brand not found');
  }
  const brandData = filamentData.brands[brandKey];

  // Find the material
  const materialKey = Object.keys(brandData.materials).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedMaterial,
  );
  if (!materialKey) {
    error(404, 'Material not found');
  }
  const materialData = brandData.materials[materialKey];

  // Find the filament
  const filamentKey = Object.keys(materialData.filaments).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedFilament,
  );
  if (!filamentKey) {
    error(404, 'Filament not found');
  }
  const filamentDataObj = materialData.filaments[filamentKey];

  // Find the color/instance
  const colorKey = Object.keys(filamentDataObj.colors).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedInstance,
  );
  if (!colorKey) {
    error(404, 'Color not found');
  }
  const colorData = filamentDataObj.colors[colorKey];

  // Create forms with existing data
  const sizeData = colorData.sizes && colorData.sizes.length > 0 ? colorData.sizes[0] : {};

  const defaultVariantData = {
    color_name: '',
    color_hex: '#000000',
    data_sheet_url: '',
    safety_sheet_url: '',
    url: '',
    affiliate: false,
    sku: '',
    traits: {
      translucent: false,
      glow: false,
      matte: false,
      recycled: false,
      recyclable: false,
      biodegradable: false,
    },
  };

  const variantData = {
    ...defaultVariantData,
    ...colorData.variant,
    traits: {
      ...defaultVariantData.traits,
      ...(colorData.variant?.traits || {}),
    },
  };

  const sizeForm = await superValidate(sizeData, zod(filamentSizeSchema));
  const variantForm = await superValidate(variantData, zod(filamentVariantSchema));

  return {
    brandData,
    materialData,
    filamentData: filamentDataObj,
    colorData,
    sizeForm,
    variantForm,
  };
};

export const actions = {
  updateSize: async ({ request, params, cookies }) => {
    const form = await superValidate(request, zod(filamentSizeSchema));
    const { brand, material, filament, instance } = params;

    if (!form.valid) {
      return fail(400, { form });
    }

    // Check if this is a local environment
    const isLocal = env.PUBLIC_IS_LOCAL === 'true';

    if (!isLocal) {
      // For web version, just return success without updating files
      // The client-side pseudo edit will handle the local storage
      setFlash(
        { type: 'success', message: 'Size updated successfully (changes saved locally)!' },
        cookies,
      );
      return { form, success: true };
    }

    try {
      const filteredData = removeUndefined(form.data);
      await updateColorSize(brand, material, filament, instance, filteredData);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to update color size:', error);
      setFlash({ type: 'error', message: 'Failed to update size. Please try again.' }, cookies);
      return fail(500, { form });
    }

    setFlash({ type: 'success', message: 'Size updated successfully!' }, cookies);
    return { form, success: true };
  },

  updateVariant: async ({ request, params, cookies }) => {
    const form = await superValidate(request, zod(filamentVariantSchema));
    const { brand, material, filament, instance } = params;

    if (!form.valid) {
      return fail(400, { form });
    }

    // Check if this is a local environment
    const isLocal = env.PUBLIC_IS_LOCAL === 'true';

    if (!isLocal) {
      // For web version, just return success without updating files
      // The client-side pseudo edit will handle the local storage
      setFlash(
        { type: 'success', message: 'Variant updated successfully (changes saved locally)!' },
        cookies,
      );
      return { form, success: true };
    }

    try {
      const filteredData = removeUndefined(form.data);
      await updateColorVariant(brand, material, filament, instance, filteredData);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to update color variant:', error);
      setFlash({ type: 'error', message: 'Failed to update variant. Please try again.' }, cookies);
      return fail(500, { form });
    }

    setFlash({ type: 'success', message: 'Variant updated successfully!' }, cookies);
    return { form, success: true };
  },
};
