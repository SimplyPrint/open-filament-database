# Open Filament Database - WebUI

A modern CRUD (Create, Read, Update, Delete) interface built with SvelteKit for managing the Open Filament Database. This web application provides an intuitive way to browse, add, edit, and manage filament data from various manufacturers.

## 🛠️ Local Development Setup

[See webui.md](/docs/webui.md)

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run check` - Run TypeScript and Svelte checks

## TODO: 
[ ] Rebuild with less repetition in code
[ ] Rebuild closer to schemas so if they change it'd be almost automatic and not require rewriting parts of UI, Validation and backend
[ ] Use instanceVariantForm.svelte and instanceSizeForm.svekte in filamentVariantForm.svelte instead of replicating them almost exactly, might also be worht renaming filamentVariantForm.svelte to something like instanceForm.svelte
[ ] Add emojis and alt codes to illegal characters, should be reflected in /data_validator.py
[ ] add slicer settings for filaments
[ ] add hex_variants, color_standards for instances