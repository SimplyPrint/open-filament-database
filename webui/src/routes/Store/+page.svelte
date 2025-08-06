<script>
  import { browser } from '$app/environment';
  import StoreItem from '$lib/components/items/storeItem.svelte';
  const { data } = $props();

  const filamentData = $derived(data.filamentData);

  const filteredStores = $derived(
    !browser || !filamentData?.stores
      ? {}
      : Object.fromEntries(
          Object.entries(filamentData.stores).filter(([store]) => true),
        ),
  );
</script>

<svelte:head>
	<title>Storefronts</title>
	<meta name="description" content="This is a overview of the storefronts"/>
</svelte:head>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8 text-center">Storefronts</h1>

  <div class="flex flex-col space-y-4">
    {#each Object.entries(filteredStores) as [storeName, storeData]}
      <StoreItem {storeName} {storeData} />
    {/each}
  </div>
</section>
