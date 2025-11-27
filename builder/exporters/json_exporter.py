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
        "products": [entity_to_dict(p) for p in db.products],
        "variants": [entity_to_dict(v) for v in db.variants],
        "spools": [entity_to_dict(s) for s in db.spools],
        "stores": [entity_to_dict(s) for s in db.stores],
        "offers": [entity_to_dict(o) for o in db.offers],
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
        
        for product in db.products:
            record = {"_type": "product", **entity_to_dict(product)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        for variant in db.variants:
            record = {"_type": "variant", **entity_to_dict(variant)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        for spool in db.spools:
            record = {"_type": "spool", **entity_to_dict(spool)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        for store in db.stores:
            record = {"_type": "store", **entity_to_dict(store)}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        for offer in db.offers:
            record = {"_type": "offer", **entity_to_dict(offer)}
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
    products_by_brand = {}
    for product in db.products:
        products_by_brand.setdefault(product.brand_id, []).append(product)
    
    variants_by_product = {}
    for variant in db.variants:
        variants_by_product.setdefault(variant.product_id, []).append(variant)
    
    spools_by_variant = {}
    for spool in db.spools:
        spools_by_variant.setdefault(spool.variant_id, []).append(spool)
    
    documents_by_product = {}
    for doc in db.documents:
        documents_by_product.setdefault(doc.product_id, []).append(doc)
    
    offers_by_spool = {}
    for offer in db.offers:
        if offer.spool_id:
            offers_by_spool.setdefault(offer.spool_id, []).append(offer)
    
    # Create index for brand listing
    brand_index = []
    
    for brand in db.brands:
        brand_products = products_by_brand.get(brand.id, [])
        
        # Collect all variants for this brand
        brand_variants = []
        for product in brand_products:
            brand_variants.extend(variants_by_product.get(product.id, []))
        
        # Collect all spools for this brand
        brand_spools = []
        for variant in brand_variants:
            brand_spools.extend(spools_by_variant.get(variant.id, []))
        
        # Collect all documents for this brand
        brand_documents = []
        for product in brand_products:
            brand_documents.extend(documents_by_product.get(product.id, []))
        
        # Collect relevant offers
        brand_offers = []
        relevant_store_ids = set()
        for spool in brand_spools:
            for offer in offers_by_spool.get(spool.id, []):
                brand_offers.append(offer)
                relevant_store_ids.add(offer.store_id)
        
        # Get relevant stores
        brand_stores = [s for s in db.stores if s.id in relevant_store_ids]
        
        # Get relevant material families
        material_ids = set(p.material_family_id for p in brand_products)
        brand_materials = [m for m in db.material_families if m.id in material_ids]
        
        # Build brand data
        brand_data = {
            "version": version,
            "generated_at": generated_at,
            "brand": entity_to_dict(brand),
            "material_families": [entity_to_dict(m) for m in brand_materials],
            "products": [entity_to_dict(p) for p in brand_products],
            "variants": [entity_to_dict(v) for v in brand_variants],
            "spools": [entity_to_dict(s) for s in brand_spools],
            "documents": [entity_to_dict(d) for d in brand_documents],
            "stores": [entity_to_dict(s) for s in brand_stores],
            "offers": [entity_to_dict(o) for o in brand_offers],
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
            "product_count": len(brand_products),
            "variant_count": len(brand_variants),
            "spool_count": len(brand_spools),
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
