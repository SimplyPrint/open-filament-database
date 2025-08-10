<script>
  import SectionsItem from "$lib/components/items/sectionsItem.svelte";
  const { data } = $props();

  let filamentData = data.filamentData;

  let brandImages = [], storeImages = [];

  function getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

  function getRandomImage(dict, arr) {
    let index = getRandomInt(Object.keys(filamentData.brands).length - 1);
    let brandKey = Object.keys(filamentData.brands)[index];
    let brand = filamentData.brands[brandKey];
    
    if (!arr.includes(brand.logo)) {
      return brand.logo;
    } else {
      brandKey = Object.keys(filamentData.brands)[index + 1];
      return filamentData.brands[brandKey].logo;
    }
  }

  for(let i = 0; i < 3; i++){
    brandImages[i] = getRandomImage(filamentData.brands, brandImages);
    storeImages[i] = getRandomImage(filamentData.stores, storeImages);
  }

  /*let firstBrands = Object.keys(filamentData.brands).slice(0, 3);
  firstBrands.forEach((value, index) => {
    let brand = filamentData.brands[value];
    brandImages[index] = brand.logo
  });
  let firstStores = Object.keys(filamentData.stores).slice(0, 3);
  firstStores.forEach((value, index) => {
    let store = filamentData.stores[value];
    storeImages[index] = store.logo
  });*/
</script>

<svelte:head>
	<title>WebUI Landing</title>
	<meta name="description" content="This is a overview of the sections of the webui"/>
</svelte:head>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-screen flex-col">
  <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 text-center">Open Filament Database WebUI</h1>
  <p class="mb-8 text-center">Hello and welcome to our WebUI, below you can select whether you'd like to edit our brands or stores.</p>

  <div class="flex w-full aspect-3/1 space-x-4">
    <SectionsItem
      link="/Brand/"
      title="Filament Brands"
      images={brandImages}
    />

    <SectionsItem
      link="/Store/"
      title="Filament Storefronts"
      images={storeImages}
    />
  </div>

</section>
