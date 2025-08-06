import { stripOfIllegalChars } from '$lib/globalHelpers';
import { storeSchema } from '$lib/validation/store-schema.js';
import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { redirect, setFlash } from 'sveltekit-flash-message/server';
import { refreshDatabase } from '$lib/dataCacher';

export const load = async () => {
  const form = await superValidate(zod(storeSchema));
 
  console.log(form);

  return { form };
};

export const actions = {
  store: async ({ request, cookies }) => {
    const form = await superValidate(request, zod(storeSchema));

    console.log(form);

    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      // IMPLEMENT FRIDAAAAAAAAAAAAA
      //await createBrand(form.data);
      await refreshDatabase();
    } catch (error) {
      console.error('Failed to create brand:', error);
      setFlash({ type: 'error', message: 'Failed to create brand. Please try again.' }, cookies);
      return fail(500, { form });
    }

    redirect(stripOfIllegalChars(form.data.brand), { type: 'success', message: 'Brand created successfully!' }, cookies);
  },
};
