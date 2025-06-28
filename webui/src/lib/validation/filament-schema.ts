import { z } from 'zod';
import { genericSlicerSchema } from './filament-material-schema';

export const baseFilamentSchema = z.object({
  name: z.string(),
  diameter_tolerance: z.number().optional(),
  density: z.number(),
  data_sheet_url: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
      return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .default('https://')
    .optional(),
  safety_sheet_url: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
      return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .default('https://')
    .optional(),
});

export const filamentSchema = z
  .object({
    name: z.string(),
    diameter_tolerance: z.number().optional(),
    density: z.number(),
    data_sheet_url: z
      .string()
      .url('Please enter a valid URL')
      .refine((url) => {
        return url.startsWith('http://') || url.startsWith('https://');
      }, 'URL must use HTTP or HTTPS protocol')
      .default('https://')
      .optional(),
    safety_sheet_url: z
      .string()
      .url('Please enter a valid URL')
      .refine((url) => {
        return url.startsWith('http://') || url.startsWith('https://');
      }, 'URL must use HTTP or HTTPS protocol')
      .default('https://')
      .optional(),
  })
  .merge(genericSlicerSchema);

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

const traitsSchema = z.object({
  translucent: z.boolean().optional(),
  glow: z.boolean().optional(),
  matte: z.boolean().optional(),
  recycled: z.boolean().optional(),
  recyclable: z.boolean().optional(),
  biodegradable: z.boolean().optional(),
});

const pathData = z.object({
  brandName: z.string(),
  materialName: z.string(),
  filamentName: z.string(),
});

export const filamentVariantSchema = z
  .object({
    color_name: z.string(),
    // color_hex can be a string or string[]
    color_hex: z.string().regex(/^#?[a-fA-F0-9]{6}$/, 'Must be a valid hex code (#RRGGBB)'),
  })
  .merge(traitsSchema)
  .merge(traitsSchema)
  .merge(filamentSizeSchema)
  .merge(filamentSchema)
  .merge(pathData);
