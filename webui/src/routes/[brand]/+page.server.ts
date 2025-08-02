import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { brandSchema } from '$lib/validation/filament-brand-schema';
import { createMaterial, updateBrand } from '$lib/server/helpers';
import { stripOfIllegalChars } from '$lib/globalHelpers';
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
    brand: brandData.brand,
    website: brandData.website || 'https://',
    origin: brandData.origin || '',
    oldBrandName: brandData.brand,
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
    redirect(303, `/${stripOfIllegalChars(form.data.brand)}/`);
  },
  material: async ({ request, params, cookies }) => {
    const form = await superValidate(request, zod(filamentMaterialSchema));
    const { brand } = params;
    if (!form.valid) {
      fail(400, { form });
    }

    try {
      let submitData = form.data;
      // Deserialize data after getting it from front end
      submitData.generic = JSON.parse(submitData.serializedGeneric);
      submitData.prusa = JSON.parse(submitData.serializedPrusa);
      submitData.bambus = JSON.parse(submitData.serializedBambus);
      submitData.orca = JSON.parse(submitData.serializedOrca);
      submitData.cura = JSON.parse(submitData.serializedCura);

      await createMaterial(brand, submitData);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to create material:', error);
      setFlash({ type: 'error', message: 'Failed to create material. Please try again.' }, cookies);
      return fail(500, { form });
    }
    setFlash({ type: 'success', message: 'Material created successfully!' }, cookies);
    redirect(303, `/${brand}/${form.data.material}`);
    return { form, redirect: `/${brand}/${form.data.material}`, success: true };
  },
};
