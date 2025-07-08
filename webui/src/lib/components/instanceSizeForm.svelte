<script lang="ts">
  import { env } from '$env/dynamic/public';
  import { pseudoEdit } from '$lib/pseudoEditor';
  import { invalidateAll } from '$app/navigation';

  let {
    form,
    errors,
    message,
    enhance,
    formType,
    brandName,
    materialName,
    filamentName,
    colorName,
  } = $props();

  // Function to add a new purchase link
  function addPurchaseLink() {
    if (!$form.purchase_links) {
      $form.purchase_links = [];
    }
    $form.purchase_links = [
      ...$form.purchase_links,
      { store_id: '', url: '', affiliate: false, ships_from: '', ships_to: '' },
    ];
  }

  // Function to remove a purchase link
  function removePurchaseLink(index: number) {
    $form.purchase_links = $form.purchase_links.filter((_, i) => i !== index);
  }

  // Enhanced form submission
  const enhancedSubmit = () => {
    return async ({ result, update }) => {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (result.type === 'success' && !isLocal) {
        // For web version, apply pseudo edit after server returns
        const sizeData = {
          filament_weight: Number($form.filament_weight),
          empty_spool_weight: $form.empty_spool_weight
            ? Number($form.empty_spool_weight)
            : undefined,
          diameter: Number($form.diameter),
          spool_refill: Boolean($form.spool_refill),
          sku: $form.sku || undefined,
          ean: $form.ean || undefined,
          purchase_links: $form.purchase_links || [],
        };

        try {
          pseudoEdit('color_size', brandName, sizeData, materialName, filamentName, colorName);
          await invalidateAll();
        } catch (error) {
          console.error('Pseudo edit failed:', error);
        }
      }

      await update();
    };
  };

  // Reactive statement to ensure purchase_links exists
  $effect(() => {
    if (!$form.purchase_links) {
      $form.purchase_links = [];
    }
  });
</script>

<div
  class="max-w-md mx-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg p-8 text-gray-900 dark:text-gray-100">
  <form method="POST" use:enhance={enhancedSubmit} action="?/updateSize" class="space-y-5">
    <h3 class="text-xl font-bold mb-4">{formType === 'edit' ? 'Edit' : 'Add'} Size</h3>

    <div>
      <label for="filament_weight" class="block font-medium mb-1">
        Weight (g)<span class="text-red-500">*</span>
      </label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Net weight of the filament material (excluding spool)
      </p>
      <input
        id="filament_weight"
        type="number"
        name="filament_weight"
        step="0.1"
        required
        placeholder="1000"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.filament_weight} />
      {#if $errors.filament_weight}
        <span class="text-red-600 text-xs">{$errors.filament_weight}</span>
      {/if}
    </div>

    <div>
      <label for="empty_spool_weight" class="block font-medium mb-1">
        Empty spool weight (g)
      </label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Weight of the empty spool without any filament
      </p>
      <input
        id="empty_spool_weight"
        type="number"
        name="empty_spool_weight"
        step="0.1"
        placeholder="250"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.empty_spool_weight} />
      {#if $errors.empty_spool_weight}
        <span class="text-red-600 text-xs">{$errors.empty_spool_weight}</span>
      {/if}
    </div>

    <div>
      <label for="diameter" class="block font-medium mb-1">
        Diameter (mm)<span class="text-red-500">*</span>
      </label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Filament diameter (typically 1.75mm or 3.0mm)
      </p>
      <input
        id="diameter"
        type="number"
        name="diameter"
        step="0.01"
        required
        placeholder="1.75"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.diameter} />
      {#if $errors.diameter}
        <span class="text-red-600 text-xs">{$errors.diameter}</span>
      {/if}
    </div>

    <div class="flex items-center gap-2">
      <input
        id="spool_refill"
        type="checkbox"
        name="spool_refill"
        class="accent-blue-600 w-4 h-4"
        bind:checked={$form.spool_refill} />
      <label for="spool_refill" class="font-medium"> Spool refill </label>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Check if this is a refill (filament only) without a spool
      </p>
    </div>
    {#if $errors.spool_refill}
      <span class="text-red-600 text-xs">{$errors.spool_refill}</span>
    {/if}

    <div>
      <label for="sku" class="block font-medium mb-1">SKU</label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Stock Keeping Unit - manufacturer's internal product code (optional)
      </p>
      <input
        id="sku"
        type="text"
        name="sku"
        placeholder="PLA-1000-BLK"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.sku} />
      {#if $errors.sku}
        <span class="text-red-600 text-xs">{$errors.sku}</span>
      {/if}
    </div>

    <div>
      <label for="ean" class="block font-medium mb-1">EAN</label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        European Article Number - barcode identifier (optional)
      </p>
      <input
        id="ean"
        type="text"
        name="ean"
        placeholder="1234567890123"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.ean} />
      {#if $errors.ean}
        <span class="text-red-600 text-xs">{$errors.ean}</span>
      {/if}
    </div>

    <fieldset>
      <div class="flex items-center justify-between mb-4">
        <legend class="block font-medium">Purchase Links (Optional)</legend>
        <button
          type="button"
          onclick={addPurchaseLink}
          class="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors">
          + Add Link
        </button>
      </div>

      {#if $form.purchase_links && $form.purchase_links.length > 0}
        <div class="space-y-6">
          {#each $form.purchase_links as link, index}
            <div
              class="border border-gray-300 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
              <div class="flex justify-between items-center mb-4">
                <h4 class="font-medium text-gray-700 dark:text-gray-300">
                  Purchase Link {index + 1}
                </h4>
                {#if $form.purchase_links.length > 1}
                  <button
                    type="button"
                    onclick={() => removePurchaseLink(index)}
                    class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                {/if}
              </div>

              <div class="space-y-4">
                <div>
                  <label for="store_id_{index}" class="block font-medium mb-1 text-sm"
                    >Store ID</label>
                  <input
                    id="store_id_{index}"
                    type="text"
                    name="purchase_links[{index}].store_id"
                    placeholder="amazon-us"
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    bind:value={link.store_id} />
                  {#if $errors.purchase_links?.[index]?.store_id}
                    <span class="text-red-600 text-xs"
                      >{$errors.purchase_links[index].store_id}</span>
                  {/if}
                </div>

                <div>
                  <label for="url_{index}" class="block font-medium mb-1 text-sm"
                    >Purchase URL</label>
                  <input
                    id="url_{index}"
                    type="url"
                    name="purchase_links[{index}].url"
                    placeholder="https://www.store.com/product/12345"
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    bind:value={link.url} />
                  {#if $errors.purchase_links?.[index]?.url}
                    <span class="text-red-600 text-xs">{$errors.purchase_links[index].url}</span>
                  {/if}
                </div>

                <div class="flex items-center gap-2">
                  <input
                    id="affiliate_{index}"
                    type="checkbox"
                    name="purchase_links[{index}].affiliate"
                    class="accent-blue-600 w-4 h-4"
                    bind:checked={link.affiliate} />
                  <label for="affiliate_{index}" class="font-medium text-sm">Affiliate link</label>
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label for="ships_from_{index}" class="block font-medium mb-1 text-sm"
                      >Ships from</label>
                    <input
                      id="ships_from_{index}"
                      type="text"
                      name="purchase_links[{index}].ships_from"
                      placeholder="USA"
                      class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      bind:value={link.ships_from} />
                  </div>

                  <div>
                    <label for="ships_to_{index}" class="block font-medium mb-1 text-sm"
                      >Ships to</label>
                    <input
                      id="ships_to_{index}"
                      type="text"
                      name="purchase_links[{index}].ships_to"
                      placeholder="Worldwide"
                      class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      bind:value={link.ships_to} />
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="text-center py-4 text-gray-500 dark:text-gray-400">
          <p class="text-sm">No purchase links added yet.</p>
          <p class="text-xs mt-1">Click "Add Link" to add purchase information.</p>
        </div>
      {/if}
    </fieldset>

    <button
      type="submit"
      class="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition-colors">
      {formType === 'edit' ? 'Save Changes' : 'Add Size'}
    </button>
  </form>
</div>
