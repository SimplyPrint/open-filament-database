<script lang="ts">
  import { enhance } from '$app/forms';
  import { env } from '$env/dynamic/public';
  import { pseudoEdit } from '$lib/pseudoEditor';
  import { invalidateAll } from '$app/navigation';
  import { booleanProxy } from 'sveltekit-superforms';
  import { pseudoUndoDelete } from '$lib/pseudoDeleter';
  import { redirect } from '@sveltejs/kit';

  type formType = 'edit' | 'create';
  let { form, errors, message, formType, brandName, materialName, filamentName } =
    $props();

  // Proxies are needed for nested properties to work correctly with sveltekit-superforms
  const translucent = booleanProxy(form, 'traits.translucent');
  const glow = booleanProxy(form, 'traits.glow');
  const matte = booleanProxy(form, 'traits.matte');
  const recycled = booleanProxy(form, 'traits.recycled');
  const recyclable = booleanProxy(form, 'traits.recyclable');
  const biodegradable = booleanProxy(form, 'traits.biodegradable');

  // Function to add a new purchase link
  function addPurchaseLink(sizeIndex: number) {
    if (!$form.sizes[sizeIndex].purchase_links) {
      $form.sizes[sizeIndex].purchase_links = [];
    }
    $form.sizes[sizeIndex].purchase_links = [
      ...$form.sizes[sizeIndex].purchase_links,
      { store_id: '', url: '', affiliate: false, ships_from: '', ships_to: '' },
    ];
  }

  // Function to remove a purchase link
  function removePurchaseLink(sizeIndex: number, index: number) {
    $form.sizes[sizeIndex].purchase_links = $form.sizes[sizeIndex].purchase_links.filter((_, i) => i !== index);
  }

  // Function to add a new purchase link
  function addSize() {
    if (!$form.sizes) {
      $form.sizes = [];
    }
    $form.sizes = [
      ...$form.sizes,
      { filament_weight: undefined, diameter: undefined },
    ];
  }

  // Function to remove a purchase link
  function removeSize(index: number) {
    $form.sizes = $form.sizes.filter((_, i) => i !== index);
  }

  const enhancedSubmit = ({ formData }) => {
    formData.set("serializedSizes", JSON.stringify($form.sizes));

    if ($form.traits) {
      let traitData = $form.traits;
      // 🤷‍♀️ for some reason $form.traits all has the value of false, setting them to true as if they exist they should be
      Object.keys(traitData).forEach((key: any) => {
        traitData[key] = true;
      });
      formData.set("serializedTraits", JSON.stringify(traitData));
    }

    return async ({ result, update }) => {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (result.type === 'success' && !isLocal) {

        const filamentData = {
          color_name: $form.color_name,
          color_hex: $form.color_hex,
          discontinued: $form.discontinued || undefined,
          traits: $form.traits || {},
        };
        pseudoEdit('filament', brandName, filamentData, materialName, filamentName);
        pseudoUndoDelete('filament', $form.name);
        await invalidateAll();
      }

      if (result?.redirect) {
        redirect(303, result.redirect);
      }

      await update();
    };
  };
</script>

<div
  class="max-w-xl mx-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg p-4 text-gray-900 dark:text-gray-100">
  <form
    method="POST"
    use:enhance={enhancedSubmit}
    action="?/instance"
    enctype="multipart/form-data"
    class="space-y-5">
    <div>
      <h3 class="text-xl font-bold mb-4">{formType === 'edit' ? 'Edit' : 'Create'} Color Variant</h3>

      <label for="color_name" class="block font-medium mb-1">
        Color name<span class="text-red-500">*</span>
      </label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Enter the official color name as specified by the manufacturer
      </p>
      <input
        id="color_name"
        type="text"
        required
        placeholder="e.g. Galaxy Black"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.color_name} />
      {#if $errors.color_name}
        <span class="text-red-600 text-xs">{$errors.color_name}</span>
      {/if}
    </div>

    <div class="mb-4">
      <label for="color_hex" class="block font-medium mb-1"
        >Color hex<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Choose the color or enter the hex code that best represents this filament color
      </p>
      <div class="flex items-center gap-3">
        <input
          id="color_hex"
          type="color"
          aria-required="true"
          aria-describedby="color-hex-help"
          class="w-10 h-10 border-2 border-gray-300 dark:border-gray-600 rounded cursor-pointer"
          aria-invalid={$errors.color_hex ? 'true' : undefined}
          bind:value={$form.color_hex}
          style="padding:0;" />
        <input
          type="text"
          class="rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-2 py-1"
          bind:value={$form.color_hex}
          maxlength="7"
          placeholder="#RRGGBB" />
      </div>
      {#if $errors.color_hex}
        <span class="text-red-600 text-xs">{$errors.color_hex}</span>
      {/if}
    </div>

    <div>
      <div>
        <div class="flex flex-row items-center">
          <input
          id="discontinued"
          type="checkbox"
          name="discontinued"
          class="accent-blue-600 w-4 h-4 mr-2"
          bind:checked={$form.discontinued} />

          <label for="discontinued" class="inline-block font-medium">
            Discontinued
          </label>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Select if this colour variant is discontinued 
          </p>
      </div>
      {#if $errors.discontinued}
        <span class="text-red-600 text-xs">{$errors.discontinued}</span>
      {/if}
    </div>

    <fieldset>
      <legend class="block font-medium mb-2">Material Traits</legend>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Select all special properties that apply to this filament variant
      </p>
      <div class="grid grid-cols-2 gap-4">
        <div class="flex items-center gap-2">
          <input
            id="translucent"
            type="checkbox"
            name="traits.translucent"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$translucent} />
          <label for="translucent" class="font-medium text-sm">Translucent</label>
        </div>

        <div class="flex items-center gap-2">
          <input
            id="glow"
            type="checkbox"
            name="traits.glow"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$glow} />
          <label for="glow" class="font-medium text-sm">Glow in dark</label>
        </div>

        <div class="flex items-center gap-2">
          <input
            id="matte"
            type="checkbox"
            name="traits.matte"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$matte} />
          <label for="matte" class="font-medium text-sm">Matte finish</label>
        </div>

        <div class="flex items-center gap-2">
          <input
            id="recycled"
            type="checkbox"
            name="traits.recycled"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$recycled} />
          <label for="recycled" class="font-medium text-sm">Recycled</label>
        </div>

        <div class="flex items-center gap-2">
          <input
            id="recyclable"
            type="checkbox"
            name="traits.recyclable"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$recyclable} />
          <label for="recyclable" class="font-medium text-sm">Recyclable</label>
        </div>

        <div class="flex items-center gap-2">
          <input
            id="biodegradable"
            type="checkbox"
            name="traits.biodegradable"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$biodegradable} />
          <label for="biodegradable" class="font-medium text-sm">Biodegradable</label>
        </div>
      </div>
    </fieldset>

    {#if $form.sizes.length <= 0}
      <span class="text-red-600 text-xs">You need at least one size</span>
    {/if}
    <fieldset>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold mb-4">{formType === 'edit' ? 'Edit' : 'Add'} Sizes<span class="text-red-500">*</span></h3>
        <button
          type="button"
          onclick={addSize}
          class="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors">
          + Add Size
        </button>
      </div>

      {#if $form.sizes && $form.sizes.length > 0}
        <div class="space-y-5">
          {#each $form.sizes as size, sizesIndex}
            <div class="rounded-lg border border-gray-300 dark:border-gray-700 p-2">
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl text-gray-600 dark:text-gray-400">
                  <b>Size {sizesIndex + 1}</b>
                </h2>
                  <button
                    type="button"
                    onclick={() => removeSize(sizesIndex)}
                    class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200">
                    <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
              </div>

              <div>
                <label for="filament_weight_{sizesIndex}" class="block font-medium mb-1">
                  Weight (g)<span class="text-red-500">*</span>
                </label>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Net weight of the filament material (excluding spool)
                </p>
                <input
                  id="filament_weight_{sizesIndex}"
                  type="number"
                  name="sizes[{sizesIndex}].filament_weight"
                  step="0.1"
                  required
                  placeholder="1000"
                  class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  bind:value={$form.sizes[sizesIndex].filament_weight} />
                {#if $errors.filament_weight}
                  <span class="text-red-600 text-xs">{$errors.filament_weight}</span>
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
                  bind:value={$form.sizes[sizesIndex].diameter} />
                {#if $errors.diameter}
                  <span class="text-red-600 text-xs">{$errors.diameter}</span>
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
                  bind:value={$form.sizes[sizesIndex].empty_spool_weight} />
                {#if $errors.empty_spool_weight}
                  <span class="text-red-600 text-xs">{$errors.empty_spool_weight}</span>
                {/if}
              </div>

              <div>
                <label for="spool_core_diameter" class="block font-medium mb-1">
                  Spool core diameter (mm)
                </label>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  The diameter of the core of the spool
                </p>
                <input
                  id="spool_core_diameter"
                  type="number"
                  name="spool_core_diameter"
                  step="0.1"
                  placeholder="100"
                  class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  bind:value={$form.sizes[sizesIndex].spool_core_diameter} />
                {#if $errors.spool_core_diameter}
                  <span class="text-red-600 text-xs">{$errors.spool_core_diameter}</span>
                {/if}
              </div>

              <div>
                <label for="ean" class="block font-medium mb-1">EAN</label>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  European Article Number - barcode identifier
                </p>
                <input
                  id="ean"
                  type="text"
                  name="ean"
                  placeholder="1234567890123"
                  class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  bind:value={$form.sizes[sizesIndex].ean} />
                {#if $errors.ean}
                  <span class="text-red-600 text-xs">{$errors.ean}</span>
                {/if}
              </div>

              <div>
                <label for="article_number" class="block font-medium mb-1">
                  Article number
                </label>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Article number - manufacturer's internal product code
                </p>
                <input
                  id="article_number"
                  type="text"
                  name="article_number"
                  placeholder="PLA-1000-BLK"
                  class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  bind:value={$form.sizes[sizesIndex].article_number} />
                {#if $errors.article_number}
                  <span class="text-red-600 text-xs">{$errors.article_number}</span>
                {/if}
              </div>

              <div>
                <div>
                  <div class="flex flex-row items-center">
                    <input
                    id="discontinued"
                    type="checkbox"
                    name="discontinued"
                    class="accent-blue-600 w-4 h-4 mr-2"
                    bind:checked={$form.sizes[sizesIndex].discontinued} />

                    <label for="discontinued" class="inline-block font-medium">
                      Discontinued
                    </label>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Select if this size is discontinued 
                    </p>
                </div>
                {#if $errors.discontinued}
                  <span class="text-red-600 text-xs">{$errors.discontinued}</span>
                {/if}
              </div>

              <fieldset>
                <div class="flex items-center justify-between mb-4">
                  <legend class="block font-medium">Purchase Links (Optional)</legend>
                  <button
                    type="button"
                    onclick={() => addPurchaseLink(sizesIndex)}
                    class="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors">
                    + Add Link
                  </button>
                </div>

                {#if size.purchase_links && size.purchase_links.length > 0}
                  <div class="space-y-6">
                    {#each size.purchase_links as link, purchaseIndex}
                      <div
                        class="border border-gray-300 dark:border-gray-600 rounded-lg p-4 mb-2 bg-gray-50 dark:bg-gray-800">
                        <div class="flex justify-between items-center mb-4">
                          <h4 class="font-medium text-gray-700 dark:text-gray-300">
                            Purchase Link {purchaseIndex + 1}
                          </h4>
                            <button
                              type="button"
                              onclick={() => removePurchaseLink(sizesIndex, purchaseIndex)}
                              class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200">
                              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                  stroke-width="2"
                                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                        </div>

                        <div class="space-y-4">
                          <div>
                            <label for="sizes_{sizesIndex}_store_id_{purchaseIndex}" class="block font-medium mb-1 text-sm"
                              >Store ID</label>
                            <input
                              id="sizes_{sizesIndex}_store_id_{purchaseIndex}"
                              type="text"
                              name="sizes[{sizesIndex}].purchase_links[{purchaseIndex}].store_id"
                              placeholder="amazon-us"
                              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                              bind:value={link.store_id} />
                            {#if $errors?.purchase_links?.[purchaseIndex]?.store_id}
                              <span class="text-red-600 text-xs"
                                >{$errors?.purchase_links[purchaseIndex].store_id}</span>
                            {/if}
                          </div>

                          <div>
                            <label for="sizes_{sizesIndex}_url_{purchaseIndex}" class="block font-medium mb-1 text-sm"
                              >Purchase URL</label>
                            <input
                              id="sizes_{sizesIndex}_url_{purchaseIndex}"
                              type="url"
                              name="sizes[{sizesIndex}].purchase_links[{purchaseIndex}].url"
                              placeholder="https://www.store.com/product/12345"
                              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                              bind:value={link.url} />
                            {#if $errors?.purchase_links?.[purchaseIndex]?.url}
                              <span class="text-red-600 text-xs">{$errors?.purchase_links[purchaseIndex].url}</span>
                            {/if}
                          </div>

                          <div class="flex items-center gap-2">
                            <input
                              id="sizes_{sizesIndex}_affiliate_{purchaseIndex}"
                              type="checkbox"
                              name="sizes[{sizesIndex}].purchase_links[{purchaseIndex}].affiliate"
                              class="accent-blue-600 w-4 h-4"
                              bind:checked={link.affiliate} />
                            <label for="sizes_{sizesIndex}_affiliate_{purchaseIndex}" class="font-medium text-sm">Affiliate link</label>
                          </div>

                          <div class="flex items-center gap-2">
                            <input
                              id="sizes_{sizesIndex}_spool_refill_{purchaseIndex}"
                              type="checkbox"
                              name="sizes[{sizesIndex}].purchase_links[{purchaseIndex}].spool_refill"
                              class="accent-blue-600 w-4 h-4"
                              bind:checked={link.spool_refill} />
                            <label for="sizes_{sizesIndex}_spool_refill_{purchaseIndex}" class="font-medium text-sm">Is spool refill</label>
                          </div>

                          <div class="grid grid-cols-2 gap-3">
                            <div>
                              <label for="sizes_{sizesIndex}_ships_from_{purchaseIndex}" class="block font-medium mb-1 text-sm"
                                >Ships from</label>
                              <input
                                id="sizes_{sizesIndex}_ships_from_{purchaseIndex}"
                                type="text"
                                name="sizes[{sizesIndex}].purchase_links[{purchaseIndex}].ships_from"
                                placeholder="USA"
                                class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                bind:value={link.ships_from} />
                            </div>

                            <div>
                              <label for="sizes_{sizesIndex}_ships_to_{purchaseIndex}" class="block font-medium mb-1 text-sm"
                                >Ships to</label>
                              <input
                                id="sizes_{sizesIndex}_ships_to_{purchaseIndex}"
                                type="text"
                                name="sizes[{sizesIndex}].purchase_links[{purchaseIndex}].ships_to"
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
            </div>
          {/each}
        </div>
      {:else}
        <div class="text-center py-4 text-gray-500 dark:text-gray-400">
          <p class="text-sm">No sizes added yet.</p>
          <p class="text-xs mt-1">Click "Add Size" to add sizes.</p>
        </div>
      {/if}
    </fieldset>

    <button
      type="submit"
      class="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition-colors">
      {formType === 'edit' ? 'Save' : 'Create'}
    </button>
  </form>
</div>
