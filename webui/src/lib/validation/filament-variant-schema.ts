import { z } from 'zod';

export const traitsSchema = z.object({
  translucent: z.boolean().optional(),
  glow: z.boolean().optional(),
  matte: z.boolean().optional(),
  recycled: z.boolean().optional(),
  recyclable: z.boolean().optional(),
  biodegradable: z.boolean().optional(),
});

export const filamentVariantSchema = z.object({
  color_name: z.string(),
  color_hex: z.string().regex(/^#?[a-fA-F0-9]{6}$/, 'Must be a valid hex code (#RRGGBB)'),
  discontinued: z.boolean().default(false),
  traits: traitsSchema.optional(),
  serializedTraits: z.string(),
});
