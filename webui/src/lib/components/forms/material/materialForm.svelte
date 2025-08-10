<script lang="ts">
  import { env } from '$env/dynamic/public';
  import { pseudoDelete, } from '$lib/pseudoDeleter';
  import { realDelete } from '$lib/realDeleter';
  import { intProxy } from 'sveltekit-superforms';
  import Form from '../components/form.svelte';
  import TextField from '../components/textField.svelte';
  import NumberField from '../components/numberField.svelte';
  import SubmitButton from '../components/submitButton.svelte';
  import DeleteButton from '../components/deleteButton.svelte';
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { filamentMaterialSchema } from '$lib/validation/filament-material-schema';

  type formType = 'edit' | 'create';
  let { defaultForm, formType, brandName } = $props();
  
  const {
    form,
    errors,
    message,
    enhance,
  } = superForm(defaultForm, {
    dataType: 'json',
    resetForm: false,
    invalidateAll: false,
    clearOnSubmit: "none",
    validationMethod: 'onblur',
    validators: zodClient(filamentMaterialSchema),
    onResult: ({ result}) => {
      console.log(result);
    }
  });
  
  async function handleDelete() {
    if (
      confirm(
        `Are you sure you want to delete the material "${$form.material}"? This action cannot be undone.`,
      )
    ) {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (isLocal) {
        await realDelete('material', $form.material, brandName);
      } else {
        pseudoDelete('material', $form.material, brandName);
      }
    }
  }

  const slicerOptions = [
    { key: 'generic', label: 'Generic' },
    { key: 'prusaslicer', label: 'PrusaSlicer' },
    { key: 'bambustudio', label: 'Bambu Studio' },
    { key: 'orcaslicer', label: 'OrcaSlicer' },
    { key: 'cura', label: 'Cura' },
  ];

  let selectedSlicer: string[] = $state([]);

  // Proxies are needed for nested properties to work correctly with sveltekit-superforms
  const generic_flbt = intProxy(form, 'generic.first_layer_bed_temp');
  const generic_flnt = intProxy(form, 'generic.first_layer_nozzle_temp');
  const generic_bt = intProxy(form, 'generic.bed_temp');
  const generic_nt = intProxy(form, 'generic.nozzle_temp');

  const prusa_flbt = intProxy(form, 'prusa.first_layer_bed_temp');
  const prusa_flnt = intProxy(form, 'prusa.first_layer_nozzle_temp');
  const prusa_bt = intProxy(form, 'prusa.bed_temp');
  const prusa_nt = intProxy(form, 'prusa.nozzle_temp');

  const bambus_flbt = intProxy(form, 'bambus.first_layer_bed_temp');
  const bambus_flnt = intProxy(form, 'bambus.first_layer_nozzle_temp');
  const bambus_bt = intProxy(form, 'bambus.bed_temp');
  const bambus_nt = intProxy(form, 'bambus.nozzle_temp');

  const orca_flbt = intProxy(form, 'orca.first_layer_bed_temp');
  const orca_flnt = intProxy(form, 'orca.first_layer_nozzle_temp');
  const orca_bt = intProxy(form, 'orca.bed_temp');
  const orca_nt = intProxy(form, 'orca.nozzle_temp');

  const cura_flbt = intProxy(form, 'cura.first_layer_bed_temp');
  const cura_flnt = intProxy(form, 'cura.first_layer_nozzle_temp');
  const cura_bt = intProxy(form, 'cura.bed_temp');
  const cura_nt = intProxy(form, 'cura.nozzle_temp');

  $effect(() => {
    console.log()
  });
</script>

<Form
  endpoint="material"
  enhance={enhance}
>
  <TextField
    id="material"
    title="Material name"
    description='Enter the material type or category (e.g., "PLA", "PETG", "ABS", "TPU")'
    placeholder="e.g. PLA"
    bind:formVar={$form.material}
    errorVar={$errors.material}
    required={true}
  />

  <NumberField
    id="default_max_dry_temperature"
    title="Default Max Dry Temperature"
    description='Default Maximum drying temperature (typically somewhere around 55-65°C)'
    placeholder="e.g. ±55-65°C"
    bind:formVar={$form.default_max_dry_temperature}
    errorVar={$errors.default_max_dry_temperature}
  />

  <div class="slicerSettings space-y-4">
    <p class="block font-medium mb-1">Slicer Type</p>
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
      Select which slicers you want to provide print settings for.
    </p>

    <div class="flex flex-wrap gap-4 mb-4">
      {#each slicerOptions as option}
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            value={option.key}
            bind:group={selectedSlicer}
            class="rounded border-gray-300 dark:border-gray-600" />
          {option.label}
        </label>
      {/each}
    </div>

    <!-- Generic Settings -->
    {#if selectedSlicer.includes('generic')}
      <fieldset class="border border-gray-200 dark:border-gray-700 rounded p-4 mb-4">
        <legend class="font-semibold text-base mb-2">
          Generic
        </legend>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <NumberField
              id="generic_first_layer_bed_temp"
              title="First Layer Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$generic_flbt}
            />

            <NumberField
              id="generic_first_layer_nozzle_temp"
              title="First Layer Nozzle Temp (°C)"
              description=""
              placeholder="215"
              bind:formVar={$generic_flnt}
            />

            <NumberField
              id="generic_bed_temp"
              title="Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$generic_bt}
            />

            <NumberField
              id="generic_nozzle_temp"
              title="Nozzle Temp (°C)"
              description=""
              placeholder="210"
              bind:formVar={$generic_nt}
            />
          </div>
        </div>
      </fieldset>
    {/if}

    <!-- PrusaSlicer Settings -->
    {#if selectedSlicer.includes('prusaslicer')}
      <fieldset class="border border-gray-200 dark:border-gray-700 rounded p-4 mb-4">
        <legend class="font-semibold text-base mb-2">
          Generic
        </legend>
        <div class="space-y-4">
          <TextField
            id="prusa_profile_name"
            title="Profile Name"
            description={null}
            placeholder="profiles/filament/PLA_Basic.ini"
            bind:formVar={$form.prusa.profile_name}
            errorVar={null}
          />

          <p class="text-lg font-bold mb-2">Temperature Overrides</p>
          <div class="grid grid-cols-2 gap-4">
            <NumberField
              id="prusa_first_layer_bed_temp"
              title="First Layer Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$prusa_flbt}
            />

            <NumberField
              id="prusa_first_layer_nozzle_temp"
              title="First Layer Nozzle Temp (°C)"
              description=""
              placeholder="215"
              bind:formVar={$prusa_flnt}
            />

            <NumberField
              id="prusa_bed_temp"
              title="Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$prusa_bt}
            />

            <NumberField
              id="prusa_nozzle_temp"
              title="Nozzle Temp (°C)"
              description=""
              placeholder="210"
              bind:formVar={$prusa_nt}
            />
          </div>
        </div>
      </fieldset>
    {/if}

    <!-- Bambu Studio Settings -->
    {#if selectedSlicer.includes('bambustudio')}
      <fieldset class="border border-gray-200 dark:border-gray-700 rounded p-4 mb-4">
        <legend class="font-semibold text-base mb-2">
          Generic
        </legend>
        <div class="space-y-4">
          <TextField
            id="bambus_profile_name"
            title="Profile Name"
            description={null}
            placeholder="profiles/filament/PLA_Basic.ini"
            bind:formVar={$form.bambus.profile_name}
            errorVar={null}
          />

          <p class="text-lg font-bold mb-2">Temperature Overrides</p>
          <div class="grid grid-cols-2 gap-4">
            <NumberField
              id="bambus_first_layer_bed_temp"
              title="First Layer Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$bambus_flbt}
            />

            <NumberField
              id="bambus_first_layer_nozzle_temp"
              title="First Layer Nozzle Temp (°C)"
              description=""
              placeholder="215"
              bind:formVar={$bambus_flnt}
            />

            <NumberField
              id="bambus_bed_temp"
              title="Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$bambus_bt}
            />

            <NumberField
              id="bambus_nozzle_temp"
              title="Nozzle Temp (°C)"
              description=""
              placeholder="210"
              bind:formVar={$bambus_nt}
            />
          </div>
        </div>
      </fieldset>
    {/if}

    <!-- OrcaSlicer Settings -->
    {#if selectedSlicer.includes('orcaslicer')}
      <fieldset class="border border-gray-200 dark:border-gray-700 rounded p-4 mb-4">
        <legend class="font-semibold text-base mb-2">
          Generic
        </legend>
        <div class="space-y-4">
          <TextField
            id="orca_profile_name"
            title="Profile Name"
            description={null}
            placeholder="profiles/filament/PLA_Basic.ini"
            bind:formVar={$form.orca.profile_name}
            errorVar={null}
          />

          <p class="text-lg font-bold mb-2">Temperature Overrides</p>
          <div class="grid grid-cols-2 gap-4">
            <NumberField
              id="orca_first_layer_bed_temp"
              title="First Layer Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$orca_flbt}
            />

            <NumberField
              id="orca_first_layer_nozzle_temp"
              title="First Layer Nozzle Temp (°C)"
              description=""
              placeholder="215"
              bind:formVar={$orca_flnt}
            />

            <NumberField
              id="orca_bed_temp"
              title="Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$orca_bt}
            />

            <NumberField
              id="orca_nozzle_temp"
              title="Nozzle Temp (°C)"
              description=""
              placeholder="210"
              bind:formVar={$orca_nt}
            />
          </div>
        </div>
      </fieldset>
    {/if}

    <!-- Cura Settings -->
    {#if selectedSlicer.includes('cura')}
      <fieldset class="border border-gray-200 dark:border-gray-700 rounded p-4 mb-4">
        <legend class="font-semibold text-base mb-2">
          Generic
        </legend>
        <div class="space-y-4">
          <TextField
            id="cura_profile_name"
            title="Profile Name"
            description={null}
            placeholder="profiles/filament/PLA_Basic.ini"
            bind:formVar={$form.cura.profile_name}
            errorVar={null}
          />

          <p class="text-lg font-bold mb-2">Temperature Overrides</p>
          <div class="grid grid-cols-2 gap-4">
            <NumberField
              id="cura_first_layer_bed_temp"
              title="First Layer Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$cura_flbt}
            />

            <NumberField
              id="cura_first_layer_nozzle_temp"
              title="First Layer Nozzle Temp (°C)"
              description=""
              placeholder="215"
              bind:formVar={$cura_flnt}
            />

            <NumberField
              id="cura_bed_temp"
              title="Bed Temp (°C)"
              description=""
              placeholder="60"
              bind:formVar={$cura_bt}
            />

            <NumberField
              id="cura_nozzle_temp"
              title="Nozzle Temp (°C)"
              description=""
              placeholder="210"
              bind:formVar={$cura_nt}
            />
          </div>
        </div>
      </fieldset>
    {/if}
  </div>

  <SubmitButton>
    {formType === 'edit' ? 'Save' : 'Create'}
  </SubmitButton>

  {#if formType === 'edit'}
    <DeleteButton
      handleDelete={handleDelete}
    />
  {/if}
</Form>