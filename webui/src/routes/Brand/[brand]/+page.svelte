<script lang="ts">
  import BrandForm from '$lib/components/forms/brand/brandForm.svelte';
  import EditModal from '$lib/components/editModal.svelte';
  import type { PageProps } from './$types';
  import MaterialForm from '$lib/components/forms/material/materialForm.svelte';
  import { isItemDeleted } from '$lib/pseudoDeleter';
  import { browser } from '$app/environment';
  import { stripOfIllegalChars } from '$lib/globalHelpers.js';
  let { data }: PageProps = $props();

  let materialKeys = Object.keys(data.brandData.materials ?? {});

  const websiteUrl = $derived(
    data.brandData.website?.startsWith('http')
      ? data.brandData.website
      : `https://${data.brandData.website || ''}`,
  );

  const filteredMaterialKeys = $derived(
    !browser
      ? materialKeys
      : materialKeys.filter(
          (materialKey) => !isItemDeleted('material', materialKey, data.brandData.brand),
        ),
  );

  $effect(() => {
    materialKeys = Object.keys(data.brandData.materials ?? {});
  });
</script>

<svelte:head>
	<title>{data?.brandData?.brand ? data.brandData.brand : "Brand"}</title>
	<meta name="description" content="This is an overview {data?.brandData?.brand ? data.brandData.brand : "a Brand"}"/>
</svelte:head>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <div class="relative flex flex-col md:flex-row items-center md:items-start gap-6 mb-12">
    <img
      src={`/data/${stripOfIllegalChars(data.brandData.brand)}/${data.brandData.logo}`}
      alt={data.brandData.brand ?? 'Brand logo'}
      class="w-32 h-32 rounded-xl object-contain bg-white shadow-md dark:bg-gray-900" />
    
    <div class="text-center md:text-left">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        {data.brandData.brand ?? ''}
      </h1>
      <a
        href={websiteUrl}
        target="_blank"
        rel="noopener noreferrer"
        class="text-blue-600 dark:text-blue-400 hover:underline">
        Visit Website
      </a>
    </div>

    <EditModal
      externalStyling="bg-yellow-600 hover:bg-yellow-700 border border-gray-300 dark:border-gray-700 mb-4 rounded-lg shadow transition-colors"
    >
      <BrandForm
        defaultForm={data.brandForm}
        formType={'edit'}
      />
    </EditModal>
  </div>

  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">Materials</h2>

    <EditModal
      externalStyling="bg-blue-500 hover:bg-blue-700 border border-gray-300 dark:border-gray-700 mb-4 rounded-lg shadow transition-colors"
      btnType={'create'}
      spanText="Add material"
    >
      <MaterialForm
        defaultForm={data.materialForm}
        brandName={data.brandData.brand}
        formType={'create'}
      />
    </EditModal>

    <ul class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#key [filteredMaterialKeys, data.brandData.materials]}
        {#each filteredMaterialKeys as materialKey}
          {#if data.brandData.materials[materialKey]}
            <a href={`/Brand/${stripOfIllegalChars(data.brandData.brand)}/${materialKey}`}>
              <li
                class="border rounded p-4 bg-white border-gray-200 text-gray-900 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 shadow-md transition-colors flex flex-col justify-between">
                <div>
                  <div class="font-medium text-lg mb-1">
                    {data.brandData.materials[materialKey].material ?? materialKey}
                  </div>
                </div>
              </li>
            </a>
          {/if}
        {/each}
      {/key}
    </ul>
  </div>
</section>
