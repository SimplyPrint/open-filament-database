import { z } from 'zod';

export const filamentSchema = z.object({
  name: z.string(),
  diameter_tolerance: z.coerce.number().positive(),
  density: z.coerce.number().positive(),
  max_dry_temperature: z.number().int().optional(),
  discontinued: z.boolean().default(false),
  shore_hardness_a: z.coerce.number().int().optional(),
  shore_hardness_d: z.coerce.number().int().optional(),
  certifications: z.array(z.string()).optional(),
  min_print_temperature: z.coerce.number().int().optional(),
  max_print_temperature: z.coerce.number().int().optional(),
  preheat_temperature: z.coerce.number().int().optional(),
  min_bed_temperature: z.coerce.number().int().optional(),
  max_bed_temperature: z.coerce.number().int().optional(),
  min_chamber_temperature: z.coerce.number().int().optional(),
  max_chamber_temperature: z.coerce.number().int().optional(),
  chamber_temperature: z.coerce.number().int().optional(),
  min_nozzle_diameter: z.coerce.number().optional(),
  data_sheet_url: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
        return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .optional(),
  safety_sheet_url: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
        return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .optional(),
});
