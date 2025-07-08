import { z } from 'zod';

const purchaseLinkSchema = z.object({
  store_id: z.string().optional(),
  url: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
      return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .default('https://'),
  affiliate: z.boolean(),
  ships_from: z.union([z.string(), z.array(z.string())]).optional(),
  ships_to: z.union([z.string(), z.array(z.string())]).optional(),
});

export const filamentSizeSchema = z.object({
  filament_weight: z.number(),
  empty_spool_weight: z.number().optional(),
  diameter: z.number(),
  spool_refill: z.boolean().default(false),
  sku: z.string().optional(),
  ean: z.string().optional(),
  purchase_links: z.array(purchaseLinkSchema).optional(),
});
