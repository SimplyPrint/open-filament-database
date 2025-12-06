"""
CSV exporter that creates denormalized-friendly CSV files.
"""

import csv
import json
from pathlib import Path

from ..models import Database


def list_to_str(value):
    """Convert a list to a pipe-separated string or return empty string."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "|".join(str(v) for v in value)
    return str(value)


def dict_to_str(value):
    """Convert a dict to JSON string or return empty string."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def export_csv(db: Database, output_dir: str, version: str, generated_at: str):
    """Export database to CSV files."""
    print("Exporting CSV...")
    
    output_path = Path(output_dir) / "csv"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Export brands
    brands_file = output_path / "brands.csv"
    with open(brands_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'slug', 'website', 'logo', 'country', 'origin', 'aliases', 'created_at', 'updated_at'])
        for brand in db.brands:
            writer.writerow([
                brand.id,
                brand.name,
                brand.slug,
                brand.website or "",
                getattr(brand, 'logo', '') or "",
                brand.country or "",
                getattr(brand, 'origin', '') or "",
                list_to_str(brand.aliases),
                brand.created_at or "",
                brand.updated_at or ""
            ])
    print(f"  Written: {brands_file}")
    
    # Export material families
    materials_file = output_path / "material_families.csv"
    with open(materials_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'code', 'name'])
        for mf in db.material_families:
            writer.writerow([mf.id, mf.code, mf.name])
    print(f"  Written: {materials_file}")
    
    # Export filaments
    filaments_file = output_path / "filaments.csv"
    with open(filaments_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'brand_id', 'material_family_id', 'name', 'slug',
            'description', 'diameters', 'specs', 'images', 'source_path',
            'created_at', 'updated_at'
        ])
        for filament in db.filaments:
            writer.writerow([
                filament.id,
                filament.brand_id,
                filament.material_family_id,
                filament.name,
                filament.slug,
                filament.description or "",
                list_to_str(filament.diameters),
                dict_to_str(filament.specs),
                list_to_str(filament.images),
                filament.source_path or "",
                filament.created_at or "",
                filament.updated_at or ""
            ])
    print(f"  Written: {filaments_file}")

    # Export variants
    variants_file = output_path / "variants.csv"
    with open(variants_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'filament_id', 'color_name', 'finish',
            'color_value', 'colorants', 'images', 'source_path'
        ])
        for variant in db.variants:
            writer.writerow([
                variant.id,
                variant.filament_id,
                variant.color_name or "",
                variant.finish or "",
                variant.color_value or "",
                list_to_str(variant.colorants),
                list_to_str(variant.images),
                variant.source_path or ""
            ])
    print(f"  Written: {variants_file}")

    # Export sizes
    sizes_file = output_path / "sizes.csv"
    with open(sizes_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'variant_id', 'sku', 'gtin', 'weight_g',
            'length_m', 'diameter_mm', 'msrp_amount', 'msrp_currency'
        ])
        for size in db.sizes:
            writer.writerow([
                size.id,
                size.variant_id,
                size.sku or "",
                size.gtin or "",
                size.weight_g,
                size.length_m or "",
                size.diameter_mm,
                size.msrp_amount or "",
                size.msrp_currency or ""
            ])
    print(f"  Written: {sizes_file}")
    
    # Export stores
    stores_file = output_path / "stores.csv"
    with open(stores_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'slug', 'storefront_url', 'ships_from', 'ships_to', 'logo'])
        for store in db.stores:
            writer.writerow([
                store.id,
                store.name,
                store.slug,
                store.storefront_url or "",
                store.ships_from or "",
                store.ships_to or "",
                getattr(store, 'logo', '') or ""
            ])
    print(f"  Written: {stores_file}")

    # Export purchase links
    purchase_links_file = output_path / "purchase_links.csv"
    with open(purchase_links_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'size_id', 'store_id', 'url', 'spool_refill', 'ships_from', 'ships_to'])
        for pl in db.purchase_links:
            writer.writerow([
                pl.id,
                pl.size_id,
                pl.store_id,
                pl.url,
                1 if pl.spool_refill else 0,
                list_to_str(pl.ships_from),
                list_to_str(pl.ships_to)
            ])
    print(f"  Written: {purchase_links_file}")

    # Export documents
    documents_file = output_path / "documents.csv"
    with open(documents_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'filament_id', 'type', 'url', 'language'])
        for doc in db.documents:
            writer.writerow([
                doc.id,
                doc.filament_id,
                doc.type,
                doc.url,
                doc.language or ""
            ])
    print(f"  Written: {documents_file}")

    # Export a denormalized full sizes view (most useful for analysis)
    full_sizes_file = output_path / "full_sizes.csv"

    # Build lookup maps
    brands_map = {b.id: b for b in db.brands}
    materials_map = {m.id: m for m in db.material_families}
    filaments_map = {f.id: f for f in db.filaments}
    variants_map = {v.id: v for v in db.variants}

    with open(full_sizes_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'size_id', 'sku', 'gtin', 'weight_g', 'length_m', 'diameter_mm',
            'msrp_amount', 'msrp_currency',
            'variant_id', 'color_name', 'finish', 'color_value',
            'filament_id', 'filament_name', 'filament_slug',
            'material_family_id', 'material_code', 'material_name',
            'brand_id', 'brand_name', 'brand_slug'
        ])
        for size in db.sizes:
            variant = variants_map.get(size.variant_id)
            if not variant:
                continue
            filament = filaments_map.get(variant.filament_id)
            if not filament:
                continue
            material = materials_map.get(filament.material_family_id)
            brand = brands_map.get(filament.brand_id)

            writer.writerow([
                size.id,
                size.sku or "",
                size.gtin or "",
                size.weight_g,
                size.length_m or "",
                size.diameter_mm,
                size.msrp_amount or "",
                size.msrp_currency or "",
                variant.id,
                variant.color_name or "",
                variant.finish or "",
                variant.color_value or "",
                filament.id,
                filament.name,
                filament.slug,
                material.id if material else "",
                material.code if material else "",
                material.name if material else "",
                brand.id if brand else "",
                brand.name if brand else "",
                brand.slug if brand else ""
            ])
    print(f"  Written: {full_sizes_file}")
    
    # Write README for CSV files
    readme_file = output_path / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Open Filament Database - CSV Export

Version: {version}
Generated: {generated_at}

## Files

- `brands.csv` - Filament manufacturers/brands
- `material_families.csv` - Material types (PLA, PETG, ABS, etc.)
- `filaments.csv` - Filament lines (linked to brand and material)
- `variants.csv` - Color/finish variants (linked to filament)
- `sizes.csv` - Individual sizes/SKUs (linked to variant)
- `stores.csv` - Retail stores
- `purchase_links.csv` - Purchase links (linked to size and store)
- `documents.csv` - TDS/SDS documents (linked to filament)
- `full_sizes.csv` - Denormalized view joining size→variant→filament→material→brand

## Column Conventions

- IDs are UUIDs stored as strings
- Lists are pipe-separated (`|`)
- JSON objects are stored as JSON strings
- Empty strings represent NULL values
- Boolean values: `1` = true, `0` = false, empty = unknown

## Relationships

```
brand (1) ←── (N) filament (1) ←── (N) variant (1) ←── (N) size (1) ←── (N) purchase_link
                   │                                          │
                   │                                          └───────────→ store
                   ↓
            material_family
                   │
                   ↓
              document
```
""")
    print(f"  Written: {readme_file}")
    
    print("CSV export complete!")
    
    return output_path
