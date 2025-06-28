import { z } from 'zod';

export const brandSchema = z.object({
  name: z.string().min(1, 'Brand name is required'),
  website: z
    .string()
    .url('Please enter a valid URL')
    .refine((url) => {
      return url.startsWith('http://') || url.startsWith('https://');
    }, 'URL must use HTTP or HTTPS protocol')
    .default('https://'),
  origin: z.string(),
  logo: z
    .instanceof(File, { message: 'Please upload a file.' })
    .refine((f) => f.size < 5_000_000, 'Max 5 mB upload size.')
    .optional(),
  oldBrandName: z.string().optional(),
});
