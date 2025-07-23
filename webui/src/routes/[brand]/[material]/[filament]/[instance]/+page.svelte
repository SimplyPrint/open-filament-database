<script lang="ts">
  import EditModal from '$lib/components/editModal.svelte';
  import InstanceSizeForm from '$lib/components/instanceSizeForm.svelte';
  import InstanceVariantForm from '$lib/components/instanceVariantForm.svelte';
  import { filamentVariantSchema } from '$lib/validation/filament-variant-schema';
  import { filamentSizeSchema } from '$lib/validation/filament-size-schema';
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import InstanceDeleteButton from '$lib/components/instanceDeleteButton.svelte';
  const { data } = $props();

  const {
    form: variantForm,
    errors: variantErrors,
    message: variantMessage,
    enhance: variantEnhance,
  } = superForm(data.variantForm, {
    dataType: 'json',
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(filamentVariantSchema),
  });

  const {
    form: sizeForm,
    errors: sizeErrors,
    message: sizeMessage,
    enhance: sizeEnhance,
  } = superForm(data.sizeForm, {
    dataType: 'json',
    resetForm: false,
    validationMethod: 'onblur',
    validators: zodClient(filamentSizeSchema),
  });
</script>

<div class="max-w-6xl mx-auto p-6">
  <!-- Main Color Card -->
  <div
    class="border rounded-lg p-8 bg-white border-gray-200 text-gray-900 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 transition-colors">
    <!-- Header Section -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-4">
        {#if data.colorData.variant?.color_hex}
          <span
            class="inline-block w-12 h-12 rounded-full border-2 border-gray-300 dark:border-gray-600 shadow-lg"
            style="background-color: {data.colorData.variant.color_hex};"
            title={data.colorData.variant.color_hex}></span>
        {/if}
        <div>
          <h1 class="text-4xl font-bold mb-1">{data.colorData.name}</h1>
          {#if data.colorData.variant?.color_hex}
            <span class="text-lg text-gray-500 dark:text-gray-400 font-mono">
              {data.colorData.variant.color_hex}
            </span>
          {/if}
        </div>
      </div>
      <div class="btn-wraper flex gap-2">
        <EditModal spanText={'Edit Size'}>
          <InstanceSizeForm
            form={sizeForm}
            errors={sizeErrors}
            message={sizeMessage}
            brandName={data.brandData.brand}
            materialName={data.materialData.material}
            filamentName={data.filamentData.name}
            colorName={data.colorData.name}
            enhance={sizeEnhance}
            formType={'edit'} />
        </EditModal>
        <EditModal spanText={'Edit Variant'}>
          <InstanceVariantForm
            form={variantForm}
            errors={variantErrors}
            message={variantMessage}
            brandName={data.brandData.brand}
            materialName={data.materialData.material}
            filamentName={data.filamentData.name}
            colorName={data.colorData.name}
            enhance={variantEnhance}
            formType={'edit'} />
        </EditModal>
        <InstanceDeleteButton
          brandName={data.brandData.brand}
          materialName={data.materialData.material}
          filamentName={data.filamentData.name}
          instanceName={data.colorData.name} />
      </div>
    </div>
  </div>

  <!-- Traits Section - Only show if traits exist and have values -->
  {#if data.colorData.variant?.traits && Object.entries(data.colorData.variant.traits).some(([trait, value]) => value)}
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Traits</h2>
      <div class="flex flex-wrap gap-3">
        {#each Object.entries(data.colorData.variant.traits) as [trait, value]}
          {#if value}
            <div
              class="flex items-center gap-2 px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm">
              <svg
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="3">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span class="capitalize">{trait}</span>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  {/if}

  <!-- Size Information Section -->
  <div class="mb-8">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Size Information</h2>
    </div>

    {#if data.colorData.sizes && data.colorData.sizes.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each data.colorData.sizes as size, index}
          <div
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700 dark:text-gray-300">Weight:</span>
                <span class="font-semibold">{size.filament_weight}g</span>
              </div>

              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700 dark:text-gray-300">Diameter:</span>
                <span class="font-semibold">{size.diameter}mm</span>
              </div>

              {#if size.empty_spool_weight}
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-700 dark:text-gray-300">Empty Spool:</span>
                  <span class="font-semibold">{size.empty_spool_weight}g</span>
                </div>
              {/if}

              {#if size.ean}
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-700 dark:text-gray-300">EAN:</span>
                  <span class="font-mono text-sm">{size.ean}</span>
                </div>
              {/if}

              {#if size.sku}
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-700 dark:text-gray-300">SKU:</span>
                  <span class="font-mono text-sm">{size.sku}</span>
                </div>
              {/if}

              {#if size.spool_refill}
                <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span class="text-sm font-medium">Refill</span>
                </div>
              {/if}
            </div>

            {#if size.purchase_links && size.purchase_links.length > 0}
              <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Purchase Links:
                </h4>
                <div class="space-y-2">
                  {#each size.purchase_links as link}
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      class="flex items-center justify-between text-sm text-blue-600 dark:text-blue-400 hover:underline">
                      <span>{link.store_id}</span>
                      {#if link.affiliate}
                        <span
                          class="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded">
                          Affiliate
                        </span>
                      {/if}
                    </a>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {:else}
      <div class="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>No size information available yet.</p>
        <p class="text-sm mt-2">Click the edit button above to add size details.</p>
      </div>
    {/if}
  </div>
</div>
