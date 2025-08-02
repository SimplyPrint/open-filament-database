import { z } from 'zod';

export const genericSlicerSchema = z.object({
  first_layer_bed_temp: z.number().optional(),
  first_layer_nozzle_temp: z.number().optional(),
  bed_temp: z.number().optional(),
  nozzle_temp: z.number().optional(),
});

export const specificSlicerSchema = z.object({
  profile_name: z.string().optional()
}).merge(genericSlicerSchema);

export const slicerSettingsSchema = z.object({
  generic: genericSlicerSchema,
  prusa: specificSlicerSchema,
  bambus: specificSlicerSchema,
  orca: specificSlicerSchema,
  cura: specificSlicerSchema,
});

export const filamentMaterialSchema = z
  .object({
    material: z.string(),
    default_max_dry_temperature: z.number().optional(),
    // The list indicators account for 2, 2 for ", everything above is it means there's data inside
    serializedGeneric: z.string(),
    serializedPrusa: z.string(),
    serializedBambus: z.string(),
    serializedOrca: z.string(),
    serializedCura: z.string(),
  })
  .merge(slicerSettingsSchema);
