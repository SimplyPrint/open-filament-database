<script lang="ts">
  import { env } from '$env/dynamic/public';
  import { pseudoDelete } from '$lib/pseudoDeleter';
  import { realDelete } from '$lib/realDeleter';
  import DeleteButton from '../components/deleteButton.svelte';
  import BigCheck from '../components/bigCheck.svelte';
  import Form from '../components/form.svelte';
  import NumberField from '../components/numberField.svelte';
  import SubmitButton from '../components/submitButton.svelte';
  import TextField from '../components/textField.svelte';
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { filamentSchema } from '$lib/validation/filament-schema';

  type formType = 'edit' | 'create';
  let { defaultForm, formType: formType, brandName, materialName } = $props();

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
    validators: zodClient(filamentSchema)
  });

  if (!$form.certifications) {
    $form.certifications = [];
  }

  async function handleDelete() {
    if (
      confirm(
        `Are you sure you want to delete the filament "${$form.name}"? This action cannot be undone.`,
      )
    ) {
      const isLocal = env.PUBLIC_IS_LOCAL === 'true';

      if (isLocal) {
        await realDelete('filament', $form.name, brandName, materialName);
      } else {
        pseudoDelete('filament', $form.name, brandName, materialName);
      }
    }
  }

</script>

<Form
  endpoint="filament"
  enhance={enhance}
>
  <TextField
    id="name"
    title="Filament name"
    description='Enter the specific name or type of this filament material (e.g., "PLA+", "PETG", "ABS Pro")'
    placeholder="e.g. PLA+"
    bind:formVar={$form.name}
    errorVar={$errors.name}
    required={true}
  />

  <NumberField
    id="diameter_tolerance"
    title="Diameter tolerance"
    description='Acceptable variation in filament diameter (typically ±0.02mm or ±0.03mm)'
    placeholder="e.g. 0.02"
    bind:formVar={$form.diameter_tolerance}
    errorVar={$errors.diameter_tolerance}
    required={true}
  />

  <NumberField
    id="density"
    title="Density"
    description='Material density in grams per cubic centimeter (g/cm³)'
    placeholder="e.g. 1.24"
    bind:formVar={$form.density}
    errorVar={$errors.density}
    required={true}
  />

  <NumberField
    id="max_dry_temperature"
    title="Max Dry Temperature"
    description='Maximum drying temperature (typically somewhere around 55-65°C)'
    placeholder="e.g. 55"
    bind:formVar={$form.max_dry_temperature}
    errorVar={$errors.max_dry_temperature}
  />

  <div class="flex space-x-2">
    <NumberField
      id="shore_hardness_a"
      title="Shore Hardness A"
      description="Scale A (Softer)"
      placeholder="e.g. 95"
      bind:formVar={$form.shore_hardness_a}
      errorVar={$errors.shore_hardness_a}
    />
    <NumberField
      id="shore_hardness_d"
      title="Shore Hardness D"
      description="Scale D (Harder)"
      placeholder="e.g. 30"
      bind:formVar={$form.shore_hardness_d}
      errorVar={$errors.shore_hardness_d}
    />
  </div>

  <div class="flex space-x-2">
    <NumberField
      id="min_print_temperature"
      title="Min Print Temp (°C)"
      description="Min nozzle temp"
      placeholder="200"
      bind:formVar={$form.min_print_temperature}
      errorVar={$errors.min_print_temperature}
    />
    <NumberField
      id="max_print_temperature"
      title="Max Print Temp (°C)"
      description="Max nozzle temp"
      placeholder="220"
      bind:formVar={$form.max_print_temperature}
      errorVar={$errors.max_print_temperature}
    />
    <NumberField
      id="preheat_temperature"
      title="Preheat Temp (°C)"
      description="For load/unload"
      placeholder="170"
      bind:formVar={$form.preheat_temperature}
      errorVar={$errors.preheat_temperature}
    />
  </div>

  <div class="flex space-x-2">
    <NumberField
      id="min_bed_temperature"
      title="Min Bed Temp (°C)"
      description="Min bed temp"
      placeholder="60"
      bind:formVar={$form.min_bed_temperature}
      errorVar={$errors.min_bed_temperature}
    />
    <NumberField
      id="max_bed_temperature"
      title="Max Bed Temp (°C)"
      description="Max bed temp"
      placeholder="80"
      bind:formVar={$form.max_bed_temperature}
      errorVar={$errors.max_bed_temperature}
    />
  </div>

  <div class="flex space-x-2">
    <NumberField
      id="min_chamber_temperature"
      title="Min Chamber (°C)"
      description="Min chamber temp"
      placeholder="20"
      bind:formVar={$form.min_chamber_temperature}
      errorVar={$errors.min_chamber_temperature}
    />
    <NumberField
      id="max_chamber_temperature"
      title="Max Chamber (°C)"
      description="Max chamber temp"
      placeholder="50"
      bind:formVar={$form.max_chamber_temperature}
      errorVar={$errors.max_chamber_temperature}
    />
    <NumberField
      id="chamber_temperature"
      title="Ideal Chamber (°C)"
      description="Ideal chamber temp"
      placeholder="40"
      bind:formVar={$form.chamber_temperature}
      errorVar={$errors.chamber_temperature}
    />
  </div>

  <NumberField
    id="min_nozzle_diameter"
    title="Min Nozzle Dia (mm)"
    description="Recommended min nozzle size"
    placeholder="0.4"
    bind:formVar={$form.min_nozzle_diameter}
    errorVar={$errors.min_nozzle_diameter}
  />

  <div class="mb-4">
    <label class="block font-medium mb-1">Certifications</label>
    <div class="flex gap-4">
      <label class="flex items-center gap-2">
        <input type="checkbox" value="ul_2818" bind:group={$form.certifications} class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
        <span class="text-sm">UL 2818 (Greenguard)</span>
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" value="ul_94_v0" bind:group={$form.certifications} class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
        <span class="text-sm">UL 94 V0 (Flammability)</span>
      </label>
    </div>
  </div>

  <BigCheck
    bind:formVar={$form.discontinued}
    errorVar={$errors.discontinued}
    description="Select if this filament is discontinued"
  />

  <TextField
    id="data_sheet_url"
    title="Data sheet URL"
    description='Link to technical data sheet with material specifications'
    placeholder="https://www.example.com/datasheet.pdf"
    bind:formVar={$form.data_sheet_url}
    errorVar={$errors.data_sheet_url}
  />

  <TextField
    id="safety_sheet_url"
    title="Safety sheet URL"
    description='Link to Material Safety Data Sheet (MSDS) for handling and safety information'
    placeholder="https://www.example.com/msds.pdf"
    bind:formVar={$form.safety_sheet_url}
    errorVar={$errors.safety_sheet_url}
  />

  <SubmitButton>
    {formType === 'edit' ? 'Save' : 'Create'}
  </SubmitButton>  

  {#if formType === 'edit'}
    <DeleteButton
      handleDelete={handleDelete}
    />
  {/if}
</Form>
