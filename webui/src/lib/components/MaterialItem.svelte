<script lang="ts">
  import { stripOfIllegalChars } from '$lib/globalHelpers.js';
  
  let { filament, filamentKey, brandName, materialName } = $props();
</script>
<a href={`/${stripOfIllegalChars(brandName)}/${materialName}/${filamentKey}`}>
<div class="border rounded p-4 bg-white border-gray-200 text-gray-900 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 transition-colors shadow-md">
  <div class="flex items-center justify-between mb-2">
    <h2 class="text-xl font-semibold">{filament.name ?? filamentKey}</h2>
  </div>
  <div class="text-sm text-gray-600 dark:text-gray-300 space-y-1">
    {#if filament.density}
      <div>Density: <span class="font-mono">{filament.density}</span></div>
    {/if}
    {#if filament.diameter_tolerance}
      <div>Diameter Tolerance: <span class="font-mono">{filament.diameter_tolerance}</span></div>
    {/if}
  </div>
</div>
</a>