<script lang="ts">
  import { enhance } from '$app/forms';
  import { pseudoDelete } from '$lib/pseudoDeleter';
  import SuperDebug, { fileProxy, superForm } from 'sveltekit-superforms';
  type formType = 'edit' | 'create';
  let { form, errors, constraints, delayed, message, formType, oldName = '' } = $props();
  const file = fileProxy(form, 'logo');
</script>

<div
  class="max-w-md mx-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg p-8 text-gray-900 dark:text-gray-100">
  <form method="POST" use:enhance action="?/brand" enctype="multipart/form-data" class="space-y-5">
    <div>
      <label for="name" class="block font-medium mb-1"
        >Brand name<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Enter the official name of the filament manufacturer (e.g., "Prusa", "Hatchbox")
      </p>
      <input
        id="name"
        type="text"
        name="name"
        aria-required="true"
        aria-describedby="name-help"
        placeholder="e.g. Prusa"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.name ? 'true' : undefined}
        bind:value={$form.name} />
      {#if $errors.name}
        <span class="text-red-600 text-xs">{$errors.name}</span>
      {/if}
    </div>

    <div>
      <label for="website" class="block font-medium mb-1"
        >Website<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Official website URL of the brand</p>
      <input
        id="website"
        type="text"
        name="website"
        aria-required="true"
        aria-describedby="website-help"
        placeholder="https://www.example.com"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.website ? 'true' : undefined}
        bind:value={$form.website} />
      {#if $errors.website}
        <span class="text-red-600 text-xs">{$errors.website}</span>
      {/if}
    </div>

    <div>
      <label for="origin" class="block font-medium mb-1"
        >Origin<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Country or region where the brand is based
      </p>
      <input
        id="origin"
        type="text"
        name="origin"
        aria-required="true"
        aria-describedby="origin-help"
        placeholder="e.g. DK"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.origin ? 'true' : undefined}
        bind:value={$form.origin} />
      {#if $errors.origin}
        <span class="text-red-600 text-xs">{$errors.origin}</span>
      {/if}
    </div>
    {#if formType === 'create'}
      <div>
        <label for="logo" class="block font-medium mb-1"
          >Logo<span class="text-red-500">*</span></label>
        <input
          id="logo"
          type="file"
          name="logo"
          accept="image/png, image/jpeg"
          bind:files={$file}
          class="block w-full text-sm text-gray-700 dark:text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-gray-800 dark:file:text-blue-400" />
        {#if $errors.logo}
          <span class="text-red-600 text-xs">{$errors.logo}</span>
        {/if}
      </div>
    {/if}
    <button
      type="submit"
      class="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition-colors">
      {formType === 'edit' ? 'Save' : 'Create'}
    </button>
    {#if formType === 'edit'}
      <input type="hidden" name="oldBrandName" value={oldName} />
      <button
        type="button"
        class="w-full flex items-center justify-center gap-2 mt-2 py-2 px-4 rounded-lg bg-red-600 text-white font-semibold shadow hover:bg-red-700 transition-colors"
        aria-label="Delete brand"
        onclick={() => pseudoDelete('brand', $form.name)}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M19 7l-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M8 7V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v2" />
        </svg>
        Delete
      </button>
    {/if}
  </form>
</div>
