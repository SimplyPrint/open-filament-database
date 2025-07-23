<script lang="ts">
  import { browser } from '$app/environment';
  import { page } from '$app/state';
  import CreateNew from '$lib/components/createNew.svelte';
  import EditModal from '$lib/components/editModal.svelte';
  import FilamentForm from '$lib/components/filamentForm.svelte';
  import MaterialForm from '$lib/components/materialForm.svelte';
  import MaterialItem from '$lib/components/MaterialItem.svelte';
  import { isItemDeleted } from '$lib/pseudoDeleter.js';
  import { filamentMaterialSchema } from '$lib/validation/filament-material-schema.js';
  import { baseFilamentSchema } from '$lib/validation/filament-schema.js';
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';

  const { data } = $props();
  const filamentKeys = Object.keys(data.materialData.filaments ?? {});

  const filteredFilamentKeys = $derived(
    !browser
      ? filamentKeys
      : filamentKeys.filter((filamentKey) => !isItemDeleted('filament', filamentKey)),
  );

  const { form, errors, message, enhance } = superForm(data.materialForm, {
    dataType: 'json',
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(filamentMaterialSchema),
  });

  const {
    form: filamentForm,
    errors: filamentErrors,
    message: filamentMessage,
    enhance: filamentEnhance,
  } = superForm(data.filamentForm, {
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(baseFilamentSchema),
  });
</script>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">
    Filaments for {data.materialData.material}
  </h1>
  <div class="btn-wrapper flex gap-2">
    <EditModal>
      <MaterialForm
        {form}
        {errors}
        {message}
        brandName={data.brandData.brand}
        {enhance}
        formType={'edit'} />
    </EditModal>
    <CreateNew
      ><FilamentForm
        form={filamentForm}
        errors={filamentErrors}
        message={filamentMessage}
        enhance={filamentEnhance}
        brandName={data.brandData.brand}
        materialName={data.materialData.material}
        formType={'create'} />
    </CreateNew>
  </div>

  <div class="space-y-8">
    {#each filteredFilamentKeys as filamentKey}
      {#if data.materialData.filaments[filamentKey]}
        <MaterialItem
          filament={data.materialData.filaments[filamentKey]}
          {filamentKey}
          brandName={data.brandData.brand}
          materialName={data.materialData.material} />
      {/if}
    {/each}
  </div>
</section>
