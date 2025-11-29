import { z } from 'zod';

const functioningNumber = z.union([z.number(), z.nan()]).optional();

export const genericSlicerSchema = z.object({
  first_layer_bed_temp: functioningNumber,
  first_layer_nozzle_temp: functioningNumber,
  bed_temp: functioningNumber,
  nozzle_temp: functioningNumber,
});

export const specificSlicerSchema = z.object({
  profile_name: z.string().optional()
}).merge(genericSlicerSchema);

export const slicerSettingsSchema = z.object({
  generic: genericSlicerSchema.optional(),
  prusaslicer: specificSlicerSchema.optional(),
  orcaslicer: specificSlicerSchema.optional(),
  bambustudio: specificSlicerSchema.optional(),
  cura: specificSlicerSchema.optional(),
});

export const filamentMaterialSchema = z
  .object({
    material: z.string(),
    material_class: z.enum(['FFF', 'SLA']).default('FFF').optional(),
    default_max_dry_temperature: functioningNumber,
    default_slicer_settings: slicerSettingsSchema.optional()
  });
