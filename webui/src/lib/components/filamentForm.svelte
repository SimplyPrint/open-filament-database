<script lang="ts">
  import { pseudoDelete } from '$lib/pseudoDeleter';
  import { realDelete } from '$lib/realDeleter';
  import { env } from '$env/dynamic/public';
  import { pseudoEdit, pseudoEdit } from '$lib/pseudoEditor';
  import { invalidateAll } from '$app/navigation';

  type formType = 'edit' | 'create';
  let { form, errors, message, enhance, formType: formType, brandName, materialName } = $props();

  async function handleDelete() {
    if (
      confirm(
        `Are you sure you want to delete the filament "${$form.name}"? This action cannot be undone.`,
      )
    ) {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (isLocal) {
        await realDelete('filament', $form.name, brandName, materialName);
      } else {
        pseudoDelete('filament', $form.name);
      }
    }
  }
  const slicerOptions = [
    { key: 'generic', label: 'Generic' },
    { key: 'prusaslicer', label: 'PrusaSlicer' },
    { key: 'bambustudio', label: 'Bambu Studio' },
    { key: 'orcaslicer', label: 'OrcaSlicer' },
    { key: 'cura', label: 'Cura' },
  ];

  let selectedSlicer = $state('generic');

  const enhancedSubmit = () => {
    return async ({ result, update }) => {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (result.type === 'success' && !isLocal) {
        const filamentData = {
          name: $form.name,
          // Add other filament fields as needed
        };

        pseudoEdit('filament', brandName, filamentData, materialName);
        await invalidateAll();
      }

      await update();
    };
  };
</script>

<div
  class="max-w-md mx-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg p-8 text-gray-900 dark:text-gray-100">
  <form
    method="POST"
    use:enhance={enhancedSubmit}
    action="?/filament"
    enctype="multipart/form-data"
    class="space-y-5">
    <div>
      <label for="name" class="block font-medium mb-1"
        >Filament name<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Enter the specific name or type of this filament material (e.g., "PLA+", "PETG", "ABS Pro")
      </p>
      <input
        id="name"
        type="text"
        name="name"
        aria-required="true"
        aria-describedby="name-help"
        placeholder="e.g. PLA+"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.name ? 'true' : undefined}
        bind:value={$form.name} />

      {#if $errors.name}
        <span class="text-red-600 text-xs">{$errors.name}</span>
      {/if}
    </div>

    <div>
      <label for="diameter_tolerance" class="block font-medium mb-1"
        >Diameter tolerance<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Acceptable variation in filament diameter (typically ±0.02mm or ±0.03mm)
      </p>
      <input
        id="diameter_tolerance"
        type="number"
        step="0.01"
        name="diameter_tolerance"
        aria-required="true"
        aria-describedby="diameter-tolerance-help"
        placeholder="e.g. ±0.02mm"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.diameter_tolerance ? 'true' : undefined}
        bind:value={$form.diameter_tolerance} />

      {#if $errors.diameter_tolerance}
        <span class="text-red-600 text-xs">{$errors.diameter_tolerance}</span>
      {/if}
    </div>

    <div>
      <label for="density" class="block font-medium mb-1"
        >Density<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Material density in grams per cubic centimeter (g/cm³)
      </p>
      <input
        id="density"
        type="number"
        name="density"
        step="0.01"
        aria-required="true"
        aria-describedby="density-help"
        placeholder="e.g. 1.24"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.density ? 'true' : undefined}
        bind:value={$form.density} />

      {#if $errors.density}
        <span class="text-red-600 text-xs">{$errors.density}</span>
      {/if}
    </div>

    <div>
      <label for="data_sheet_url" class="block font-medium mb-1">Data sheet URL</label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Link to technical data sheet with material specifications (optional)
      </p>
      <input
        id="data_sheet_url"
        type="text"
        name="data_sheet_url"
        aria-describedby="data-sheet-help"
        placeholder="https://www.example.com/datasheet.pdf"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.data_sheet_url ? 'true' : undefined}
        bind:value={$form.data_sheet_url} />

      {#if $errors.data_sheet_url}
        <span class="text-red-600 text-xs">{$errors.data_sheet_url}</span>
      {/if}
    </div>

    <div>
      <label for="safety_sheet_url" class="block font-medium mb-1">Safety sheet URL</label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Link to Material Safety Data Sheet (MSDS) for handling and safety information
      </p>
      <input
        id="safety_sheet_url"
        type="text"
        name="safety_sheet_url"
        aria-describedby="safety-sheet-help"
        placeholder="https://www.example.com/msds.pdf"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-invalid={$errors.safety_sheet_url ? 'true' : undefined}
        bind:value={$form.safety_sheet_url} />

      {#if $errors.safety_sheet_url}
        <span class="text-red-600 text-xs">{$errors.safety_sheet_url}</span>
      {/if}
    </div>

    <button
      type="submit"
      class="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition-colors">
      {formType === 'edit' ? 'Save' : 'Create'}
    </button>
    {#if formType === 'edit'}
      <button
        type="button"
        class="w-full flex items-center justify-center gap-2 mt-2 py-2 px-4 rounded-lg bg-red-600 text-white font-semibold shadow hover:bg-red-700 transition-colors"
        aria-label="Delete filament"
        onclick={handleDelete}>
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
