<script>
  export let link, title;
</script>

<a
  href={link}
  class="flex flex-col items-center justify-center p-6 min-h-100 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 space-y-4 w-full border border-gray-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 text-gray-900">
  <h2 class="text-lg font-bold text-gray-800 dark:text-gray-100 text-center">
    {title}
  </h2>
</a>