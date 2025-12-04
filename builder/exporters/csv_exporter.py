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
    
    # Export products
    products_file = output_path / "products.csv"
    with open(products_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'brand_id', 'material_family_id', 'name', 'slug', 
            'description', 'diameters', 'specs', 'images', 'source_path',
            'created_at', 'updated_at'
        ])
        for product in db.products:
            writer.writerow([
                product.id,
                product.brand_id,
                product.material_family_id,
                product.name,
                product.slug,
                product.description or "",
                list_to_str(product.diameters),
                dict_to_str(product.specs),
                list_to_str(product.images),
                product.source_path or "",
                product.created_at or "",
                product.updated_at or ""
            ])
    print(f"  Written: {products_file}")
    
    # Export variants
    variants_file = output_path / "variants.csv"
    with open(variants_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'product_id', 'color_name', 'finish', 
            'color_value', 'colorants', 'images', 'source_path'
        ])
        for variant in db.variants:
            writer.writerow([
                variant.id,
                variant.product_id,
                variant.color_name or "",
                variant.finish or "",
                variant.color_value or "",
                list_to_str(variant.colorants),
                list_to_str(variant.images),
                variant.source_path or ""
            ])
    print(f"  Written: {variants_file}")
    
    # Export spools
    spools_file = output_path / "spools.csv"
    with open(spools_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'variant_id', 'sku', 'gtin', 'weight_g', 
            'length_m', 'diameter_mm', 'msrp_amount', 'msrp_currency'
        ])
        for spool in db.spools:
            writer.writerow([
                spool.id,
                spool.variant_id,
                spool.sku or "",
                spool.gtin or "",
                spool.weight_g,
                spool.length_m or "",
                spool.diameter_mm,
                spool.msrp_amount or "",
                spool.msrp_currency or ""
            ])
    print(f"  Written: {spools_file}")
    
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
    
    # Export documents
    documents_file = output_path / "documents.csv"
    with open(documents_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'product_id', 'type', 'url', 'language'])
        for doc in db.documents:
            writer.writerow([
                doc.id,
                doc.product_id,
                doc.type,
                doc.url,
                doc.language or ""
            ])
    print(f"  Written: {documents_file}")
    
    # Export a denormalized full spools view (most useful for analysis)
    full_spools_file = output_path / "full_spools.csv"
    
    # Build lookup maps
    brands_map = {b.id: b for b in db.brands}
    materials_map = {m.id: m for m in db.material_families}
    products_map = {p.id: p for p in db.products}
    variants_map = {v.id: v for v in db.variants}
    
    with open(full_spools_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'spool_id', 'sku', 'gtin', 'weight_g', 'length_m', 'diameter_mm',
            'msrp_amount', 'msrp_currency',
            'variant_id', 'color_name', 'finish', 'color_value',
            'product_id', 'product_name', 'product_slug',
            'material_family_id', 'material_code', 'material_name',
            'brand_id', 'brand_name', 'brand_slug'
        ])
        for spool in db.spools:
            variant = variants_map.get(spool.variant_id)
            if not variant:
                continue
            product = products_map.get(variant.product_id)
            if not product:
                continue
            material = materials_map.get(product.material_family_id)
            brand = brands_map.get(product.brand_id)
            
            writer.writerow([
                spool.id,
                spool.sku or "",
                spool.gtin or "",
                spool.weight_g,
                spool.length_m or "",
                spool.diameter_mm,
                spool.msrp_amount or "",
                spool.msrp_currency or "",
                variant.id,
                variant.color_name or "",
                variant.finish or "",
                variant.color_value or "",
                product.id,
                product.name,
                product.slug,
                material.id if material else "",
                material.code if material else "",
                material.name if material else "",
                brand.id if brand else "",
                brand.name if brand else "",
                brand.slug if brand else ""
            ])
    print(f"  Written: {full_spools_file}")
    
    # Write README for CSV files
    readme_file = output_path / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Open Filament Database - CSV Export

Version: {version}
Generated: {generated_at}

## Files

- `brands.csv` - Filament manufacturers/brands
- `material_families.csv` - Material types (PLA, PETG, ABS, etc.)
- `products.csv` - Product lines (linked to brand and material)
- `variants.csv` - Color/finish variants (linked to product)
- `spools.csv` - Individual spool sizes/SKUs (linked to variant)
- `stores.csv` - Retail stores
- `offers.csv` - Store offers/prices (linked to store and spool)
- `documents.csv` - TDS/SDS documents (linked to product)
- `full_spools.csv` - Denormalized view joining spool→variant→product→material→brand

## Column Conventions

- IDs are UUIDs stored as strings
- Lists are pipe-separated (`|`)
- JSON objects are stored as JSON strings
- Empty strings represent NULL values
- Boolean values: `1` = true, `0` = false, empty = unknown

## Relationships

```
brand (1) ←── (N) product (1) ←── (N) variant (1) ←── (N) spool
                   │                                        │
                   │                                        │
                   ↓                                        ↓
            material_family                          offer ───→ store
                   │
                   ↓
              document
```
""")
    print(f"  Written: {readme_file}")
    
    print("CSV export complete!")
    
    return output_path
