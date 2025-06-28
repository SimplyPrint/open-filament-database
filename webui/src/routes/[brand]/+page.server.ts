import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { brandSchema } from '$lib/validation/filament-brand-schema';
import { createMaterial, removeUndefined, updateBrand } from '$lib/server/helpers';
import { filamentMaterialSchema } from '$lib/validation/filament-material-schema';
import { refreshDatabase } from '$lib/dataCacher';
import { setFlash } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ params, parent, cookies }) => {
  const { brand } = params;
  const { filamentData } = await parent();

  const normalizedBrand = brand.trim().toLowerCase().replace(/\s+/g, '');

  const brandKey = Object.keys(filamentData.brands).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedBrand,
  );
  if (!brandKey) {
    throw error(404, 'Brand not found');
  }

  const brandData = filamentData.brands[brandKey];
  const materialKey = Object.keys(brandData.materials).find(
    (key) => key.toLowerCase().replace(/\s+/g, '') === normalizedBrand,
  );

  const formData = {
    name: brandData.name,
    website: brandData.website || 'https://',
    origin: brandData.origin || '',
    oldBrandName: brandData.name,
  };

  const brandForm = await superValidate(formData, zod(brandSchema));
  const materialForm = await superValidate(zod(filamentMaterialSchema));
  return {
    brandForm,
    materialForm,
    brandData,
  };
};

export const actions = {
  brand: async ({ request, cookies }) => {
    const form = await superValidate(request, zod(brandSchema));
    console.log('Form data:', form.data);

    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      await updateBrand(form.data);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to update brand:', error);
      setFlash({ type: 'error', message: 'Failed to update brand. Please try again.' }, cookies);
      return fail(500, { form });
    }
    setFlash({ type: 'success', message: 'Brand updated successfully!' }, cookies);
    redirect(303, `/${form.data.name}/`);
  },
  material: async ({ request, params, cookies }) => {
    const form = await superValidate(request, zod(filamentMaterialSchema));
    const { brand } = params;
    if (!form.valid) {
      fail(400, { form });
    }

    try {
      await createMaterial(brand, form.data);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to create material:', error);
      setFlash({ type: 'error', message: 'Failed to create material. Please try again.' }, cookies);
      return fail(500, { form });
    }
    setFlash({ type: 'success', message: 'Material created successfully!' }, cookies);
    return { form, redirect: `/${brand}/${form.data.name}`, success: true };
  },
};
