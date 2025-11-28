<script>
  export let title;
  export let icon;
</script>

<details class="group border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white dark:bg-gray-900" open>
  <summary class="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800 cursor-pointer select-none font-medium text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors list-none">
    <span class="text-lg">{icon}</span>
    <span>{title}</span>
    <span class="ml-auto transform transition-transform group-open:rotate-180">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
        <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>
      </svg>
    </span>
  </summary>
  <div class="p-4 grid grid-cols-1 sm:grid-cols-2 gap-3 border-t border-gray-200 dark:border-gray-700">
    <slot />
  </div>
</details>

<style>
  /* Remove default marker */
  summary::-webkit-details-marker {
    display: none;
  }
</style>
