<script lang="ts">
  import SuperDebug from 'sveltekit-superforms';

  let { form, errors, message, enhance, formType, brandName, materialName, filamentName } =
    $props();
</script>

<div
  class="max-w-md mx-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg p-8 text-gray-900 dark:text-gray-100">
  <form
    method="POST"
    use:enhance
    action="?/createFilament"
    enctype="multipart/form-data"
    class="space-y-5">
    <div>
      <label for="color_name" class="block font-medium mb-1">
        Color name<span class="text-red-500">*</span>
      </label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Enter the official color name as specified by the manufacturer
      </p>
      <input
        id="color_name"
        type="text"
        name="color_name"
        required
        placeholder="e.g. Galaxy Black"
        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        bind:value={$form.color_name} />
      {#if $errors.color_name}
        <span class="text-red-600 text-xs">{$errors.color_name}</span>
      {/if}
    </div>

    <div class="mb-4">
      <label for="color_hex" class="block font-medium mb-1"
        >Color hex<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Choose the color or enter the hex code that best represents this filament color
      </p>
      <div class="flex items-center gap-3">
        <input
          id="color_hex"
          type="color"
          name="color_hex"
          aria-required="true"
          aria-describedby="color-hex-help"
          class="w-10 h-10 border-2 border-gray-300 dark:border-gray-600 rounded cursor-pointer"
          aria-invalid={$errors.color_hex ? 'true' : undefined}
          bind:value={$form.color_hex}
          style="padding:0;" />
        <input
          type="text"
          class="w-28 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-2 py-1"
          bind:value={$form.color_hex}
          maxlength="7"
          placeholder="#RRGGBB" />
      </div>
      {#if $errors.color_hex}
        <span class="text-red-600 text-xs">{$errors.color_hex}</span>
      {/if}
    </div>

    <div class="mb-4">
      <label for="data_sheet_url" class="block font-medium mb-1"
        >Data sheet URL<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Link to technical data sheet with material specifications for this specific color variant
      </p>
      <div class="flex items-center gap-3">
        <input
          id="data_sheet_url"
          type="url"
          name="data_sheet_url"
          aria-required="true"
          aria-describedby="data-sheet-help"
          placeholder="https://www.example.com/color-datasheet.pdf"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-invalid={$errors.data_sheet_url ? 'true' : undefined}
          bind:value={$form.data_sheet_url} />
      </div>
      {#if $errors.data_sheet_url}
        <span class="text-red-600 text-xs">{$errors.data_sheet_url}</span>
      {/if}
    </div>

    <div class="mb-4">
      <label for="safety_sheet_url" class="block font-medium mb-1"
        >Safety Sheet URL<span class="text-red-500">*</span></label>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Link to Material Safety Data Sheet (MSDS) for handling and safety information
      </p>
      <div class="flex items-center gap-3">
        <input
          id="safety_sheet_url"
          type="url"
          name="safety_sheet_url"
          aria-required="true"
          aria-describedby="safety-sheet-help"
          placeholder="https://www.example.com/msds.pdf"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-invalid={$errors.safety_sheet_url ? 'true' : undefined}
          bind:value={$form.safety_sheet_url} />
      </div>
      {#if $errors.safety_sheet_url}
        <span class="text-red-600 text-xs">{$errors.safety_sheet_url}</span>
      {/if}
    </div>

    <fieldset>
      <legend class="block font-medium mb-1">Traits</legend>
      <div class="traits flex flex-wrap gap-4 mb-2">
        <label class="flex items-center gap-2 cursor-pointer">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Select all special properties that apply to this filament variant
          </p>
          <input
            type="checkbox"
            id="translucent"
            name="translucent"
            bind:checked={$form.translucent}
            class="accent-blue-600 w-4 h-4" />
          <span>Translucent</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            id="glow"
            name="glow"
            bind:checked={$form.glow}
            class="accent-blue-600 w-4 h-4" />
          <span>Glow</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            id="matte"
            name="matte"
            bind:checked={$form.matte}
            class="accent-blue-600 w-4 h-4" />
          <span>Matte</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            id="recycled"
            name="recycled"
            bind:checked={$form.recycled}
            class="accent-blue-600 w-4 h-4" />
          <span>Recycled</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            id="recyclable"
            name="recyclable"
            bind:checked={$form.recyclable}
            class="accent-blue-600 w-4 h-4" />
          <span>Recyclable</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            id="biodegradable"
            name="biodegradable"
            bind:checked={$form.biodegradable}
            class="accent-blue-600 w-4 h-4" />
          <span>Biodegradable</span>
        </label>
      </div>
    </fieldset>

    <fieldset>
      <legend class="block font-medium mb-1">Sizes</legend>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
        Specify the physical dimensions and weights for this filament variant
      </p>
      <div class="sizes">
        <div class="size-item mb-4">
          <label for="filament_weight" class="block font-medium mb-1"
            >Filament weight (g)<span class="text-red-500">*</span></label>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Net weight of the filament material (excluding spool)
          </p>
          <input
            id="filament_weight"
            type="number"
            name="filament_weight"
            aria-required="true"
            aria-describedby="filament-weight-help"
            placeholder="e.g. 1000"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-invalid={$errors.filament_weight ? 'true' : undefined}
            bind:value={$form.filament_weight} />
          {#if $errors.filament_weight}
            <span class="text-red-600 text-xs">{$errors.filament_weight}</span>
          {/if}
        </div>
      </div>

      <div class="size-item mb-4">
        <label for="empty_spool_weight" class="block font-medium mb-1"
          >Empty spool weight (g)<span class="text-red-500">*</span></label>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Weight of the empty spool without any filament
        </p>
        <input
          id="empty_spool_weight"
          type="number"
          name="empty_spool_weight"
          aria-required="true"
          aria-describedby="empty-spool-weight-help"
          placeholder="e.g. 250"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-invalid={$errors.empty_spool_weight ? 'true' : undefined}
          bind:value={$form.empty_spool_weight} />
        {#if $errors.empty_spool_weight}
          <span class="text-red-600 text-xs">{$errors.empty_spool_weight}</span>
        {/if}
      </div>

      <div class="size-item mb-4">
        <label for="diameter" class="block font-medium mb-1">
          Diameter (mm)<span class="text-red-500">*</span>
        </label>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Filament diameter (typically 1.75mm or 3.0mm)
        </p>
        <input
          id="diameter"
          type="number"
          name="diameter"
          required
          placeholder="e.g. 1.75"
          step="0.01"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          bind:value={$form.diameter} />
        {#if $errors.diameter}
          <span class="text-red-600 text-xs">{$errors.diameter}</span>
        {/if}
      </div>

      <div class="size-item mb-4">
        <label for="spool_refill" class="inline-block font-medium mb-1">
          Spool refill<span class="text-red-500">*</span>
        </label>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Check if this is a refill (filament only) without a spool
        </p>
        <input
          id="spool_refill"
          type="checkbox"
          name="spool_refill"
          class="accent-blue-600 w-4 h-4"
          bind:checked={$form.spool_refill} />
        {#if $errors.spool_refill}
          <span class="text-red-600 text-xs">{$errors.spool_refill}</span>
        {/if}
      </div>

      <div class="size-item mb-4">
        <label for="sku" class="block font-medium mb-1">SKU</label>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Stock Keeping Unit - manufacturer's internal product code (optional)
        </p>
        <input
          id="sku"
          type="text"
          name="sku"
          aria-describedby="sku-help"
          placeholder="e.g. PLA-1000-BLK"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-invalid={$errors.sku ? 'true' : undefined}
          bind:value={$form.sku} />
        {#if $errors.sku}
          <span class="text-red-600 text-xs">{$errors.sku}</span>
        {/if}
      </div>
      <div class="size-item mb-4">
        <label for="ean" class="block font-medium mb-1">EAN</label>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
          European Article Number - barcode identifier (optional)
        </p>
        <input
          id="ean"
          type="text"
          name="ean"
          aria-describedby="ean-help"
          placeholder="e.g. 1234567890123"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-invalid={$errors.ean ? 'true' : undefined}
          bind:value={$form.ean} />
        {#if $errors.ean}
          <span class="text-red-600 text-xs">{$errors.ean}</span>
        {/if}
      </div>
    </fieldset>

    <fieldset>
      <legend class="block font-medium mb-1">Purchase Links</legend>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
        Add information about where this filament variant can be purchased (optional)
      </p>
      <div class="purchase-links">
        <div class="mb-4">
          <label for="store_id" class="block font-medium mb-1">Store ID</label>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Identifier for the store or retailer
          </p>
          <input
            id="store_id"
            type="text"
            name="store_id"
            aria-describedby="store-id-help"
            placeholder="e.g. amazon-us"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-invalid={$errors.store_id ? 'true' : undefined}
            bind:value={$form.store_id} />
          {#if $errors.store_id}
            <span class="text-red-600 text-xs">{$errors.store_id}</span>
          {/if}
        </div>
        <div class="mb-4">
          <label for="url" class="block font-medium mb-1">URL</label>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Direct link to purchase this specific filament variant
          </p>
          <input
            id="url"
            type="text"
            name="url"
            aria-describedby="url-help"
            placeholder="https://www.store.com/product/12345"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-invalid={$errors.url ? 'true' : undefined}
            bind:value={$form.url} />
          {#if $errors.url}
            <span class="text-red-600 text-xs">{$errors.url}</span>
          {/if}
        </div>
        <div class="mb-4">
          <label for="affiliate" class="inline-block font-medium mb-1">Affiliate</label>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Check if this is an affiliate link that earns commission
          </p>
          <input
            id="affiliate"
            type="checkbox"
            name="affiliate"
            aria-describedby="affiliate-help"
            class="accent-blue-600 w-4 h-4"
            bind:checked={$form.affiliate} />
        </div>
        <div class="mb-4">
          <label for="ships_from" class="block font-medium mb-1">Ships from</label>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Country or region where orders are shipped from
          </p>
          <input
            id="ships_from"
            type="text"
            name="ships_from"
            aria-describedby="ships-from-help"
            placeholder="e.g. USA"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-invalid={$errors.ships_from ? 'true' : undefined}
            bind:value={$form.ships_from} />
          {#if $errors.ships_from}
            <span class="text-red-600 text-xs">{$errors.ships_from}</span>
          {/if}
        </div>
        <div class="mb-4">
          <label for="ships_to" class="block font-medium mb-1">Ships to</label>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Countries or regions where this store ships to
          </p>
          <input
            id="ships_to"
            type="text"
            name="ships_to"
            aria-describedby="ships-to-help"
            placeholder="e.g. Worldwide"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-invalid={$errors.ships_to ? 'true' : undefined}
            bind:value={$form.ships_to} />
          {#if $errors.ships_to}
            <span class="text-red-600 text-xs">{$errors.ships_to}</span>
          {/if}
        </div>
      </div>
    </fieldset>
    <input type="hidden" name="brandName" value={brandName} />
    <input type="hidden" name="materialName" value={materialName} />
    <input type="hidden" name="filamentName" value={filamentName} />
    <button
      type="submit"
      class="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition-colors">
      {formType === 'edit' ? 'Save' : 'Create'}
    </button>
  </form>
</div>
