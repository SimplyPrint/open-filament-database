import { createBrand } from '$lib/server/helpers';
import { stripOfIllegalChars } from '$lib/globalHelpers';
import { brandSchema } from '$lib/validation/filament-brand-schema';
import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { redirect, setFlash } from 'sveltekit-flash-message/server';
import { refreshDatabase } from '$lib/dataCacher';

export const load = async () => {
  const form = await superValidate(zod(brandSchema));
  return { form };
};

export const actions = {
  brand: async ({ request, cookies }) => {
    const form = await superValidate(request, zod(brandSchema));

    if (!form.valid) {
      setFlash({ type: 'error', message: 'Please check your form data.' }, cookies);

      const sanitizedForm = {
        ...form,
        data: {
          ...form.data,
          logo: undefined,
        },
      };

      return fail(400, { form: sanitizedForm });
    }

    try {
      await createBrand(form.data);

      await refreshDatabase();
    } catch (error) {
      console.error('Failed to create brand:', error);
      setFlash({ type: 'error', message: 'Failed to create brand. Please try again.' }, cookies);
      const sanitizedForm = {
        ...form,
        data: {
          ...form.data,
          logo: undefined,
        },
      };

      return fail(500, { form: sanitizedForm });
    }

    redirect(stripOfIllegalChars(form.data.brand), { type: 'success', message: 'Brand created successfully!' }, cookies);
  },
};
