<script lang="ts">
  import CreateNew from '$lib/components/createNew.svelte';
  import DownloadBtn from '$lib/components/downloadBtn.svelte';
  import EditModal from '$lib/components/editModal.svelte';
  import FilamentForm from '$lib/components/filamentForm.svelte';
  import FilamentItem from '$lib/components/filamentItem.svelte';
  import FilamentVariantForm from '$lib/components/filamentVariantForm.svelte';
  import { baseFilamentSchema, filamentVariantSchema } from '$lib/validation/filament-schema.js';
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';

  const { data } = $props();
  const colorKeys = Object.keys(data.filamentData.colors ?? {});

  const { form, errors, message, enhance } = superForm(data.filamentForm, {
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(baseFilamentSchema),
  });

  const {
    form: filamentVariantForm,
    errors: filamentVariantErrors,
    message: filamentVariantMessage,
    enhance: filamentVariantEnhance,
  } = superForm(data.filamentVariantForm, {
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(filamentVariantSchema),
  });
</script>

<section
  class="max-w-4xl mt-5 mx-auto px-4 py-12 bg-white dark:bg-gray-900 rounded-xl shadow text-gray-900 dark:text-gray-100">
  <h1 class="text-3xl font-bold mb-4">
    Filament: {data.filamentData.name}
  </h1>

  <EditModal>
    <FilamentForm
      {form}
      {errors}
      {message}
      brandName={data.brandData.brand}
      materialName={data.materialData.name}
      {enhance}
      formType={'edit'} />
  </EditModal>

  <h2 class="text-2xl font-semibold mb-4">Colors & Sizes</h2>
  <div class="space-y-6">
    <div class="flex justify-between">
      <CreateNew>
        <FilamentVariantForm
          {form}
          {errors}
          {message}
          brandName={data.brandData.brand}
          materialName={data.materialData.name}
          filamentName={data.filamentData.name}
          {enhance}
          formType={'create'} />
      </CreateNew>
      <DownloadBtn
        brandName={data.brandData.brand}
        materialName={data.materialData.name}
        filamentName={data.filamentData.name} />
    </div>

    {#each colorKeys as colorKey}
      {#if data.filamentData.colors[colorKey]}
        <FilamentItem
          color={data.filamentData.colors[colorKey]}
          brandName={data.brandData.brand}
          materialName={data.materialData.name}
          filamentName={data.filamentData.name} />
      {/if}
    {/each}
  </div>
</section>
