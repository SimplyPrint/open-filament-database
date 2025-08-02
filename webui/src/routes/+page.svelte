<script>
  import { superForm } from 'sveltekit-superforms';
  import BrandForm from '$lib/components/brandForm.svelte';
  import BrandItem from '$lib/components/brandItem.svelte';
  import CreateNew from '$lib/components/createNew.svelte';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { brandSchema } from '$lib/validation/filament-brand-schema.js';
  import { browser } from '$app/environment';
  import { stripOfIllegalChars } from '$lib/globalHelpers';
  import { isItemDeleted } from '$lib/pseudoDeleter.js';
  const { data } = $props();
  const { form, errors, constraints, delayed, message } = superForm(data.form, {
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(brandSchema),
  });

  const filamentData = $derived(data.filamentData);

  const filteredBrands = $derived(
    !browser || !filamentData?.brands
      ? {}
      : Object.fromEntries(
          Object.entries(filamentData.brands).filter(([brand]) => !isItemDeleted('brand', stripOfIllegalChars(brand))),
        ),
  );
</script>

<svelte:head>
	<title>Brands</title>
	<meta name="description" content="This is a overview of the brands"/>
</svelte:head>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8 text-center">Brands</h1>

  <CreateNew>
    <BrandForm {form} {errors} {constraints} {delayed} {message} formType={'create'} />
  </CreateNew>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
    {#each Object.entries(filteredBrands) as [brandName, brandData]}
      <BrandItem {brandName} {brandData} />
    {/each}
  </div>
</section>
