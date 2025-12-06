"""
JSON exporters for various formats: all.json, per-brand JSON, NDJSON.
"""

import gzip
import json
import os
from pathlib import Path
from typing import Any

from ..models import Database, Brand


def entity_to_dict(entity: Any) -> dict:
    """Convert a dataclass entity to a dictionary, removing None values."""
    if hasattr(entity, '__dataclass_fields__'):
        result = {}
        for field in entity.__dataclass_fields__:
            value = getattr(entity, field)
            if value is not None:
                result[field] = value
        return result
    return entity


def database_to_dict(db: Database, version: str, generated_at: str) -> dict:
    """Convert the entire database to a dictionary."""
    return {
        "version": version,
        "generated_at": generated_at,
        "brands": [entity_to_dict(b) for b in db.brands],
        "material_families": [entity_to_dict(m) for m in db.material_families],
        "filaments": [entity_to_dict(f) for f in db.filaments],
        "variants": [entity_to_dict(v) for v in db.variants],
        "sizes": [entity_to_dict(s) for s in db.sizes],
        "stores": [entity_to_dict(s) for s in db.stores],
        "purchase_links": [entity_to_dict(pl) for pl in db.purchase_links],
        "documents": [entity_to_dict(d) for d in db.documents],
        "tags": [entity_to_dict(t) for t in db.tags],
    }


def export_all_json(db: Database, output_dir: str, version: str, generated_at: str):
    """Export all data to a single all.json file."""
    output_path = Path(output_dir) / "json"
    output_path.mkdir(parents=True, exist_ok=True)
    
    data = database_to_dict(db, version, generated_at)
    
    # Write uncompressed JSON
    json_file = output_path / "all.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Written: {json_file}")
    
    # Write compressed JSON
    gz_file = output_path / "all.json.gz"
    with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"  Written: {gz_file}")
    
    return json_file, gz_file


def export_ndjson(db: Database, output_dir: str, version: str, generated_at: str):
    """Export all data as newline-delimited JSON (NDJSON)."""
    output_path = Path(output_dir) / "json"
    output_path.mkdir(parents=True, exist_ok=True)
    
    ndjson_file = output_path / "all.ndjson"
    
    with open(ndjson_file, 'w', encoding='utf-8') as f:
        # Write metadata line first
        meta = {
            "_type": "meta",
            "version": version,
            "generated_at": generated_at
        }
        f.write(json.dumps(meta, ensure_ascii=False) + '\n')
        
        # Write each entity type
        for brand in db.brands:
            record = {"_type": "brand", **entity_to_dict(brand)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        for material in db.material_families:
            record = {"_type": "material_family", **entity_to_dict(material)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        for filament in db.filaments:
            record = {"_type": "filament", **entity_to_dict(filament)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        for variant in db.variants:
            record = {"_type": "variant", **entity_to_dict(variant)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        for size in db.sizes:
            record = {"_type": "size", **entity_to_dict(size)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        for store in db.stores:
            record = {"_type": "store", **entity_to_dict(store)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        for purchase_link in db.purchase_links:
            record = {"_type": "purchase_link", **entity_to_dict(purchase_link)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        for document in db.documents:
            record = {"_type": "document", **entity_to_dict(document)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        for tag in db.tags:
            record = {"_type": "tag", **entity_to_dict(tag)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"  Written: {ndjson_file}")
    return ndjson_file


def export_per_brand_json(db: Database, output_dir: str, version: str, generated_at: str):
    """Export separate JSON files for each brand."""
    output_path = Path(output_dir) / "json" / "brands"
    output_path.mkdir(parents=True, exist_ok=True)

    # Build lookup maps for efficient filtering
    filaments_by_brand = {}
    for filament in db.filaments:
        filaments_by_brand.setdefault(filament.brand_id, []).append(filament)

    variants_by_filament = {}
    for variant in db.variants:
        variants_by_filament.setdefault(variant.filament_id, []).append(variant)

    sizes_by_variant = {}
    for size in db.sizes:
        sizes_by_variant.setdefault(size.variant_id, []).append(size)

    purchase_links_by_size = {}
    for pl in db.purchase_links:
        purchase_links_by_size.setdefault(pl.size_id, []).append(pl)

    documents_by_filament = {}
    for doc in db.documents:
        documents_by_filament.setdefault(doc.filament_id, []).append(doc)

    # Create index for brand listing
    brand_index = []

    for brand in db.brands:
        brand_filaments = filaments_by_brand.get(brand.id, [])

        # Collect all variants for this brand
        brand_variants = []
        for filament in brand_filaments:
            brand_variants.extend(variants_by_filament.get(filament.id, []))

        # Collect all sizes for this brand
        brand_sizes = []
        for variant in brand_variants:
            brand_sizes.extend(sizes_by_variant.get(variant.id, []))

        # Collect all purchase links for this brand
        brand_purchase_links = []
        for size in brand_sizes:
            brand_purchase_links.extend(purchase_links_by_size.get(size.id, []))

        # Collect all documents for this brand
        brand_documents = []
        for filament in brand_filaments:
            brand_documents.extend(documents_by_filament.get(filament.id, []))

        # Get relevant material families
        material_ids = set(f.material_family_id for f in brand_filaments)
        brand_materials = [m for m in db.material_families if m.id in material_ids]

        # Build brand data
        brand_data = {
            "version": version,
            "generated_at": generated_at,
            "brand": entity_to_dict(brand),
            "material_families": [entity_to_dict(m) for m in brand_materials],
            "filaments": [entity_to_dict(f) for f in brand_filaments],
            "variants": [entity_to_dict(v) for v in brand_variants],
            "sizes": [entity_to_dict(s) for s in brand_sizes],
            "purchase_links": [entity_to_dict(pl) for pl in brand_purchase_links],
            "documents": [entity_to_dict(d) for d in brand_documents],
        }

        # Write brand JSON
        brand_file = output_path / f"{brand.slug}.json"
        with open(brand_file, 'w', encoding='utf-8') as f:
            json.dump(brand_data, f, indent=2, ensure_ascii=False)

        # Also write compressed version
        gz_file = output_path / f"{brand.slug}.json.gz"
        with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
            json.dump(brand_data, f, ensure_ascii=False)

        # Add to index
        brand_index.append({
            "id": brand.id,
            "slug": brand.slug,
            "name": brand.name,
            "filament_count": len(brand_filaments),
            "variant_count": len(brand_variants),
            "size_count": len(brand_sizes),
            "file": f"{brand.slug}.json",
            "file_gz": f"{brand.slug}.json.gz"
        })
    
    # Write brand index
    index_file = output_path / "index.json"
    index_data = {
        "version": version,
        "generated_at": generated_at,
        "brands": brand_index
    }
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Written: {len(db.brands)} brand files to {output_path}")
    print(f"  Written: {index_file}")
    
    return output_path


def export_json(db: Database, output_dir: str, version: str, generated_at: str):
    """Export all JSON formats."""
    print("Exporting JSON...")
    
    export_all_json(db, output_dir, version, generated_at)
    export_ndjson(db, output_dir, version, generated_at)
    export_per_brand_json(db, output_dir, version, generated_at)
    
    print("JSON export complete!")
