<script lang="ts">
  import { goto } from '$app/navigation';

  function goBack() {
    history.length > 1 ? history.back() : goto('/');
  }
</script>

<menu>
  <button
    class="flex items-center justify-center  h-10 w-10 p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 shadow hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors cursor-pointer"
    onclick={goBack}
    aria-label="Go back"
  >
    <svg
      class="h-8 w-8 text-gray-400"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
  </button>
</menu>