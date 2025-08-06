<script>
  import SectionsItem from "$lib/components/items/sectionsItem.svelte";


</script>

<svelte:head>
	<title>WebUI Landing</title>
	<meta name="description" content="This is a overview of the sections of the webui"/>
</svelte:head>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-screen flex-col">
  <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 text-center">Open Filament Database WebUI</h1>
  <p class="mb-8 text-center">Hello and welcome to our WebUI, below you can select whether you'd like to edit our brands or stores.</p>

  <div class="flex w-full space-x-4">
    <SectionsItem
      link="/Brand/"
      title="Brands"
    />

    <SectionsItem
      link="/Store/"
      title="Storefronts"
    />
  </div>

</section>
