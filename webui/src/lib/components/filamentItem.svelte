<script lang="ts">
  let { color, brandName, materialName, filamentName } = $props();

  $inspect('Color Item', color);
</script>

<div
  class="border rounded p-4 bg-white border-gray-200 text-gray-900 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 transition-colors relative">
  <div class="absolute top-2 right-2">
    <a
      href={`/${brandName}/${materialName}/${filamentName}/${color.name}`}
      class="flex items-center gap-2 p-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-green-100 hover:text-green-700 dark:hover:bg-green-900 dark:hover:text-green-300 shadow transition-colors"
      title="Edit {color.name}">
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
          d="M16.862 4.487a2.25 2.25 0 1 1 3.182 3.182l-11.25 11.25a2 2 0 0 1-.878.513l-4 1a.5.5 0 0 1-.606-.606l1-4a2 2 0 0 1 .513-.878l11.25-11.25z" />
      </svg>
      <span class="text-sm font-medium">Edit</span>
    </a>
  </div>

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
