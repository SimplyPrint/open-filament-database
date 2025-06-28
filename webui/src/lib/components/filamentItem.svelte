<script lang="ts">
  import DownloadBtn from './downloadBtn.svelte';

  let { color, brandName, materialName, filamentName } = $props();
</script>

<div
  class="border rounded p-4 bg-white border-gray-200 text-gray-900 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 transition-colors relative">
  <div class="flex items-center justify-between mb-2">
    <div class="flex items-center gap-3">
      {#if color.variant?.color_hex}
        <span
          class="inline-block w-6 h-6 rounded-full border border-gray-300 dark:border-gray-600"
          style="background-color: {color.variant.color_hex};"
          title={color.variant.color_hex}></span>
      {/if}
      <span class="font-medium">{color.name}</span>
      {#if color.variant?.color_hex}
        <span class="text-xs text-gray-500 dark:text-gray-400">{color.variant.color_hex}</span>
      {/if}
    </div>
  </div>
  {#if color.variant?.traits}
    <div class="mb-1 text-xs text-gray-700 dark:text-gray-300">
      <strong>Traits:</strong>
      {#each Object.entries(color.variant.traits) as [trait, value], i}
        <span>
          <svg
            class="w-4 h-4 text-green-600 inline"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          {trait}{i < Object.entries(color.variant.traits).length - 1 ? ', ' : ''}
        </span>
      {/each}
    </div>
  {/if}
  <div>
    <table class="min-w-full text-sm">
      <thead>
        <tr>
          <th class="text-left pr-4">Weight (g)</th>
          <th class="text-left pr-4">Diameter (mm)</th>
          <th class="text-left pr-4">EAN</th>
        </tr>
      </thead>
      <tbody>
        {#each color.sizes as size}
          <tr>
            <td class="pr-4">{size.filament_weight}</td>
            <td class="pr-4">{size.diameter}</td>
            <td class="pr-4">{size.ean}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
