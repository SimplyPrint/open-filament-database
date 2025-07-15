<script lang="ts">
  import { page } from '$app/state';

  let dialogElement: HTMLDialogElement | null = null;
  let { children, spanText = 'Edit' } = $props();

  const closeDialog = $derived(page.data.flash?.type === 'success');

  $effect(() => {
    if (closeDialog && dialogElement) {
      dialogElement.close();
    }
  });
</script>

<button
  type="button"
  onclick={() => dialogElement?.showModal()}
  class="flex items-center gap-2 p-2 mb-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-green-100 hover:text-green-700 dark:hover:bg-green-900 dark:hover:text-green-300 shadow transition-colors"
  aria-label="Edit">
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
  <span class="text-sm font-medium">{spanText}</span>
</button>

<dialog
  bind:this={dialogElement}
  class="w-full h-full bg-transparent p-4 backdrop:bg-black/40 backdrop:backdrop-blur-sm">
  <div
    class="max-w-2xl w-full mx-auto relative bg-white dark:bg-gray-900 p-6 rounded-xl shadow-2xl text-gray-900 dark:text-gray-100">
    <button
      type="button"
      class="absolute top-0 right-0 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
      aria-label="Close"
      onclick={() => dialogElement?.close()}>
      <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
    {@render children()}
  </div>
</dialog>
