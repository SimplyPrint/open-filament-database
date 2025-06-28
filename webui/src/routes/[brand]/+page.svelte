<script lang="ts">
  import BrandForm from '$lib/components/brandForm.svelte';
  import EditModal from '$lib/components/editModal.svelte';
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';

  import type { PageProps } from './$types';
  import CreateNew from '$lib/components/createNew.svelte';
  import MaterialForm from '$lib/components/materialForm.svelte';
  import { isItemDeleted } from '$lib/pseudoDeleter';
  import { browser } from '$app/environment';
  import { brandSchema } from '$lib/validation/filament-brand-schema';
  import { filamentMaterialSchema } from '$lib/validation/filament-material-schema';
  import { getFlash } from 'sveltekit-flash-message';
  let { data }: PageProps = $props();

  const { form, errors, constraints, delayed, message, enhance } = superForm(data.brandForm, {
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(brandSchema),
  });

  const {
    form: materialForm,
    errors: materialErrors,
    message: materialMessage,
    enhance: materialEnhance,
  } = superForm(data.materialForm, {
    dataType: 'json',
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(filamentMaterialSchema),
  });

  const materialKeys = Object.keys(data.brandData.materials ?? {});

  const websiteUrl = $derived(
    data.brandData.website?.startsWith('http')
      ? data.brandData.website
      : `https://${data.brandData.website || ''}`,
  );

  const filteredMaterialKeys = $derived(
    !browser
      ? materialKeys
      : materialKeys.filter((materialKey) => !isItemDeleted('material', materialKey)),
  );
</script>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <div class="relative flex flex-col md:flex-row items-center md:items-start gap-6 mb-12">
    <img
      src={data.brandData.logo}
      alt={data.brandData.name ?? 'Brand logo'}
      class="w-32 h-32 rounded-xl object-contain bg-white shadow-md dark:bg-gray-900" />
    <div class="text-center md:text-left">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        {data.brandData.name ?? ''}
      </h1>
      <a
        href={websiteUrl}
        target="_blank"
        rel="noopener noreferrer"
        class="text-blue-600 dark:text-blue-400 hover:underline">
        Visit Website
      </a>
    </div>
    <EditModal>
      <BrandForm
        {form}
        {errors}
        {constraints}
        {delayed}
        {message}
        formType={'edit'}
        oldName={data.brandData.name} />
    </EditModal>
  </div>

  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">Materials</h2>
    <CreateNew>
      <MaterialForm
        form={materialForm}
        errors={materialErrors}
        message={materialMessage}
        brandName={data.brandData.name}
        enhance={materialEnhance}
        formType={'create'} />
    </CreateNew>
    <ul class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each filteredMaterialKeys as materialKey}
        {#if data.brandData.materials[materialKey]}
          <a href={`/${data.brandData.name}/${materialKey}`}>
            <li
              class="border rounded p-4 bg-white border-gray-200 text-gray-900 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 shadow-md transition-colors flex flex-col justify-between">
              <div>
                <div class="font-medium text-lg mb-1">
                  {data.brandData.materials[materialKey].name ?? materialKey}
                </div>
              </div>
            </li>
          </a>
        {/if}
      {/each}
    </ul>
  </div>
</section>
