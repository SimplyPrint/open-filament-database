import { z } from 'zod';

const traitsSchema = z.object({
  translucent: z.boolean().optional(),
  glow: z.boolean().optional(),
  matte: z.boolean().optional(),
  recycled: z.boolean().optional(),
  recyclable: z.boolean().optional(),
  biodegradable: z.boolean().optional(),
});

export const filamentVariantSchema = z.object({
  color_name: z.string(),
  // color_hex can be a string or string[]
  color_hex: z.union([
    z.string().regex(/^#?[a-fA-F0-9]{6}$/, 'Must be a valid hex code (#RRGGBB)'),
    z.array(z.string().regex(/^#?[a-fA-F0-9]{6}$/, 'Must be a valid hex code (#RRGGBB)')),
  ]),
  traits: traitsSchema.optional(),
});
