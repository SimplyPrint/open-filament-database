<script lang="ts">
  import { env } from '$env/dynamic/public';
  import { pseudoDelete } from '$lib/pseudoDeleter';
  import { realDelete } from '$lib/realDeleter';

  let { brandName, materialName, filamentName, instanceName } = $props();

  async function handleDelete() {
    if (
      confirm(
        `Are you sure you want to delete the instance "${instanceName}"? This action cannot be undone.`,
      )
    ) {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (isLocal) {
        await realDelete('instance', instanceName, brandName, materialName, filamentName);
      } else {
        pseudoDelete('instance', instanceName, brandName, materialName, filamentName);
      }
    }
  }
</script>

<button
  type="button"
  class="flex items-center gap-2 p-2 mb-2 rounded-lg bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-300 hover:bg-red-200 hover:text-red-700 dark:hover:bg-red-800 dark:hover:text-red-200 shadow transition-colors"
  aria-label="Delete instance"
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
      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
  <span class="text-sm font-medium">Delete</span>
</button>
