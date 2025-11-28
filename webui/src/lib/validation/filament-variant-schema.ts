import { z } from 'zod';

export const purchaseLinkSchema = z.object({
  store_id: z.string(),
  url: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
      return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .default('https://'),
  affiliate: z.boolean().default(false),
  spool_refill: z.boolean().optional(),
  ships_from: z.union([z.string(), z.array(z.string())]).optional(),
  ships_to: z.union([z.string(), z.array(z.string())]).optional(),
});

export const filamentSizeSchema = z.object({
  filament_weight: z.number(),
  diameter: z.number(),
  empty_spool_weight: z.number().nullable().optional(),
  spool_core_diameter: z.number().nullable().optional(),
  container_width: z.number().int().optional(),
  container_outer_diameter: z.number().int().optional(),
  container_hole_diameter: z.number().int().optional(),
  ean: z.string().optional(),
  article_number: z.string().optional(),
  discontinued: z.boolean().default(false),
  purchase_links: z.array(purchaseLinkSchema).optional(),
});

export const traitsSchema = z.object({
  translucent: z.boolean().optional(),
  glow: z.boolean().optional(),
  matte: z.boolean().optional(),
  recycled: z.boolean().optional(),
  recyclable: z.boolean().optional(),
  biodegradable: z.boolean().optional(),
  filtration_recommended: z.boolean().optional(),
  biocompatible: z.boolean().optional(),
  home_compostable: z.boolean().optional(),
  industrially_compostable: z.boolean().optional(),
  bio_based: z.boolean().optional(),
  antibacterial: z.boolean().optional(),
  air_filtering: z.boolean().optional(),
  abrasive: z.boolean().optional(),
  foaming: z.boolean().optional(),
  castable: z.boolean().optional(),
  self_extinguishing: z.boolean().optional(),
  paramagnetic: z.boolean().optional(),
  radiation_shielding: z.boolean().optional(),
  high_temperature: z.boolean().optional(),
  esd_safe: z.boolean().optional(),
  conductive: z.boolean().optional(),
  emi_shielding: z.boolean().optional(),
  blend: z.boolean().optional(),
  water_soluble: z.boolean().optional(),
  ipa_soluble: z.boolean().optional(),
  limonene_soluble: z.boolean().optional(),
  low_outgassing: z.boolean().optional(),
  silk: z.boolean().optional(),
  transparent: z.boolean().optional(),
  without_pigments: z.boolean().optional(),
  iridescent: z.boolean().optional(),
  pearlescent: z.boolean().optional(),
  glitter: z.boolean().optional(),
  neon: z.boolean().optional(),
  illuminescent_color_change: z.boolean().optional(),
  temperature_color_change: z.boolean().optional(),
  gradual_color_change: z.boolean().optional(),
  coextruded: z.boolean().optional(),
  contains_carbon: z.boolean().optional(),
  contains_carbon_fiber: z.boolean().optional(),
  contains_carbon_nano_tubes: z.boolean().optional(),
  contains_glass: z.boolean().optional(),
  contains_glass_fiber: z.boolean().optional(),
  contains_kevlar: z.boolean().optional(),
  contains_ptfe: z.boolean().optional(),
  contains_stone: z.boolean().optional(),
  contains_magnetite: z.boolean().optional(),
  contains_ceramic: z.boolean().optional(),
  contains_boron_carbide: z.boolean().optional(),
  contains_organic_material: z.boolean().optional(),
  contains_cork: z.boolean().optional(),
  contains_wax: z.boolean().optional(),
  contains_wood: z.boolean().optional(),
  contains_algae: z.boolean().optional(),
  contains_bamboo: z.boolean().optional(),
  contains_pine: z.boolean().optional(),
  contains_metal: z.boolean().optional(),
  contains_bronze: z.boolean().optional(),
  contains_iron: z.boolean().optional(),
  contains_steel: z.boolean().optional(),
  contains_silver: z.boolean().optional(),
  contains_copper: z.boolean().optional(),
  contains_aluminium: z.boolean().optional(),
  contains_brass: z.boolean().optional(),
  contains_tungsten: z.boolean().optional(),
  imitates_wood: z.boolean().optional(),
  imitates_metal: z.boolean().optional(),
  imitates_marble: z.boolean().optional(),
  imitates_stone: z.boolean().optional(),
  lithophane: z.boolean().optional(),
  limited_edition: z.boolean().optional(),
});

export const filamentSizesSchema = z.array(filamentSizeSchema).min(1);
export const purchaseLinksSchema = z.array(purchaseLinkSchema);

export const filamentVariantHex = z.string().regex(/^#?[a-fA-F0-9]{6}$/, 'Must be a valid hex code (#RRGGBB)');

export const filamentVariantSchema = z.object({
  color_name: z.string(),
  color_hex: z.union([filamentVariantHex, z.array(filamentVariantHex).min(1)]).default(""),
  discontinued: z.boolean().default(false),
  traits: traitsSchema.optional(),
  sizes: filamentSizesSchema,
});
