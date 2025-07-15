import { z } from 'zod';

// For "generic" field
const genericSlicerSchema = z.object({
  first_layer_bed_temp: z.number().optional(),
  first_layer_nozzle_temp: z.number().optional(),
  bed_temp: z.number().optional(),
  nozzle_temp: z.number().optional(),
});

// For "specific slicer settings"
const specificSlicerSettingsSchema = z.object({
  profile_path: z.string(),
  overrides: z.object({}).optional(),
});

export const slicerSettingsSchema = z.object({
  generic: genericSlicerSchema.optional(),
  prusaslicer: specificSlicerSettingsSchema.optional(),
  bambustudio: specificSlicerSettingsSchema.optional(),
  orcaslicer: specificSlicerSettingsSchema.optional(),
  cura: specificSlicerSettingsSchema.optional(),
});
