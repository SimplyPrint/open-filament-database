"""
Static API exporter that creates a split, GitHub Pages-friendly API structure.
"""

import json
from pathlib import Path
import shutil
from typing import Any

from ..models import Database, Brand, Product, Variant, Spool


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


def write_json(path: Path, data: dict):
    """Write JSON file with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_api(
    db: Database,
    output_dir: str,
    version: str,
    generated_at: str,
    base_url: str = "",
    data_dir: str | None = None,
    stores_dir: str | None = None,
    asset_url_mode: str = "auto",  # one of: auto | absolute | relative
):
    """Export database as a split static API."""
    print("Exporting Static API...")
    
    api_path = Path(output_dir) / "api" / "v1"
    api_path.mkdir(parents=True, exist_ok=True)
    assets_path = api_path / "assets"
    brands_assets = assets_path / "brands"
    stores_assets = assets_path / "stores"
    brands_assets.mkdir(parents=True, exist_ok=True)
    stores_assets.mkdir(parents=True, exist_ok=True)
    
    # Build lookup maps
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
    
    materials_map = {m.id: m for m in db.material_families}
    brands_map = {b.id: b for b in db.brands}
    products_map = {p.id: p for p in db.products}
    variants_map = {v.id: v for v in db.variants}
    spools_map = {s.id: s for s in db.spools}
    stores_map = {s.id: s for s in db.stores}
    
    # Helper: URL mode decision
    def is_localhost_url(url: str | None) -> bool:
        if not url:
            return True
        try:
            from urllib.parse import urlparse
            u = urlparse(url)
            host = (u.hostname or "").lower()
            return host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local")
        except Exception:
            return False

    def make_url(rel_path: str) -> str:
        mode = (asset_url_mode or "auto").lower()
        if mode not in {"auto", "absolute", "relative"}:
            mode = "auto"
        if mode == "relative":
            return rel_path
        if mode == "absolute":
            return f"{base_url.rstrip('/')}/{rel_path}" if base_url else rel_path
        # auto
        if base_url and not is_localhost_url(base_url):
            return f"{base_url.rstrip('/')}/{rel_path}"
        return rel_path

    # Helper: compute/copy logo assets and return URL (relative according to mode)
    def ensure_brand_logo_and_get_url(brand) -> str | None:
        logo = getattr(brand, 'logo', None)
        if not logo:
            return None
        src = None
        if data_dir and getattr(brand, 'source_path', None):
            cand = Path(data_dir) / brand.source_path / logo
            if cand.exists():
                src = cand
        if not src and data_dir:
            # Fallback: try brand name folder
            cand = Path(data_dir) / brand.name / logo
            if cand.exists():
                src = cand
        # Copy into assets/brands/{slug}/{filename}
        dest_dir = brands_assets / brand.slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / logo
        if src and src.exists():
            try:
                shutil.copy2(src, dest)
            except Exception:
                pass
        rel = f"assets/brands/{brand.slug}/{logo}"
        return make_url(rel)

    def ensure_store_logo_and_get_url(store) -> str | None:
        logo = getattr(store, 'logo', None)
        if not logo:
            return None
        src = None
        if stores_dir and getattr(store, 'source_path', None):
            cand = Path(stores_dir) / store.source_path / logo
            if cand.exists():
                src = cand
        if not src and stores_dir:
            cand = Path(stores_dir) / store.slug / logo
            if cand.exists():
                src = cand
        dest_dir = stores_assets / store.slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / logo
        if src and src.exists():
            try:
                shutil.copy2(src, dest)
            except Exception:
                pass
        rel = f"assets/stores/{store.slug}/{logo}"
        return make_url(rel)

    # === Root index.json ===
    root_index = {
        "version": version,
        "generated_at": generated_at,
        "base_url": base_url,
        "endpoints": {
            "brands": "brands/index.json",
            "materials": "materials/index.json",
            "products": "products/index.json",
            "stores": "stores/index.json",
            "search": "search/autocomplete.json",
            "catalog": "catalog/index.json",
            "spools": "spools/index.json"
        },
        "stats": {
            "brands": len(db.brands),
            "material_families": len(db.material_families),
            "products": len(db.products),
            "variants": len(db.variants),
            "spools": len(db.spools),
            "stores": len(db.stores),
            "offers": len(db.offers)
        }
    }
    write_json(api_path / "index.json", root_index)
    print(f"  Written: {api_path / 'index.json'}")
    
    # === Brands ===
    brands_path = api_path / "brands"
    brand_index_items = []
    
    for brand in db.brands:
        brand_products = products_by_brand.get(brand.id, [])
        
        # Count variants and spools for this brand
        variant_count = 0
        spool_count = 0
        for product in brand_products:
            product_variants = variants_by_product.get(product.id, [])
            variant_count += len(product_variants)
            for variant in product_variants:
                spool_count += len(spools_by_variant.get(variant.id, []))
        
        # Add to index
        brand_index_items.append({
            "id": brand.id,
            "slug": brand.slug,
            "name": brand.name,
            "product_count": len(brand_products),
            "variant_count": variant_count,
            "spool_count": spool_count,
            "logo_url": ensure_brand_logo_and_get_url(brand)
        })
        
        # Create individual brand file with products
        # augment brand dict with logo_url
        _brand_dict = entity_to_dict(brand)
        _brand_dict["logo_url"] = ensure_brand_logo_and_get_url(brand)
        brand_data = {
            "version": version,
            "brand": _brand_dict,
            "products": [
                {
                    **entity_to_dict(p),
                    "material": entity_to_dict(materials_map.get(p.material_family_id)) if p.material_family_id in materials_map else None,
                    "variant_count": len(variants_by_product.get(p.id, []))
                }
                for p in brand_products
            ]
        }
        write_json(brands_path / f"{brand.slug}.json", brand_data)
    
    # Write brand index
    brand_index = {
        "version": version,
        "count": len(db.brands),
        "brands": brand_index_items
    }
    write_json(brands_path / "index.json", brand_index)
    print(f"  Written: {len(db.brands)} brand files to {brands_path}")
    
    # === Materials ===
    materials_path = api_path / "materials"
    material_index_items = []
    
    products_by_material = {}
    for product in db.products:
        products_by_material.setdefault(product.material_family_id, []).append(product)
    
    for material in db.material_families:
        material_products = products_by_material.get(material.id, [])
        
        material_index_items.append({
            "id": material.id,
            "code": material.code,
            "name": material.name,
            "product_count": len(material_products)
        })
        
        # Create individual material file
        material_data = {
            "version": version,
            "material": entity_to_dict(material),
            "products": [
                {
                    **entity_to_dict(p),
                    "brand": entity_to_dict(brands_map.get(p.brand_id)) if p.brand_id in brands_map else None
                }
                for p in material_products
            ]
        }
        write_json(materials_path / f"{material.code.lower()}.json", material_data)
    
    # Write material index
    material_index = {
        "version": version,
        "count": len(db.material_families),
        "materials": material_index_items
    }
    write_json(materials_path / "index.json", material_index)
    print(f"  Written: {len(db.material_families)} material files to {materials_path}")

    # === Spools aggregates ===
    spools_path = api_path / "spools"

    def make_spool_view(spool: Spool):
        v = variants_map.get(spool.variant_id)
        p = products_map.get(v.product_id) if v else None
        b = brands_map.get(p.brand_id) if p else None
        m = materials_map.get(p.material_family_id) if p else None
        return {
            **entity_to_dict(spool),
            "variant": entity_to_dict(v) if v else None,
            "product": entity_to_dict(p) if p else None,
            "brand": entity_to_dict(b) if b else None,
            "material": entity_to_dict(m) if m else None,
        }

    # All spools
    write_json(spools_path / "index.json", {
        "version": version,
        "count": len(db.spools),
        "spools": [make_spool_view(s) for s in db.spools]
    })

    # Spools per material
    for material in db.material_families:
        mat_spools = []
        for s in db.spools:
            v = variants_map.get(s.variant_id)
            p = products_map.get(v.product_id) if v else None
            if p and p.material_family_id == material.id:
                mat_spools.append(make_spool_view(s))
        write_json(materials_path / f"{material.code.lower()}-spools.json", {
            "version": version,
            "material": entity_to_dict(material),
            "count": len(mat_spools),
            "spools": mat_spools
        })

    # Spools per brand
    for brand in db.brands:
        brand_spools = []
        for s in db.spools:
            v = variants_map.get(s.variant_id)
            p = products_map.get(v.product_id) if v else None
            if p and p.brand_id == brand.id:
                brand_spools.append(make_spool_view(s))
        write_json(brands_path / f"{brand.slug}-spools.json", {
            "version": version,
            "brand": entity_to_dict(brand),
            "count": len(brand_spools),
            "spools": brand_spools
        })
    
    # === Products ===
    products_path = api_path / "products"
    product_index_items = []
    
    for product in db.products:
        product_variants = variants_by_product.get(product.id, [])
        product_docs = documents_by_product.get(product.id, [])
        brand = brands_map.get(product.brand_id)
        material = materials_map.get(product.material_family_id)
        
        product_index_items.append({
            "id": product.id,
            "slug": product.slug,
            "name": product.name,
            "brand_slug": brand.slug if brand else None,
            "brand_name": brand.name if brand else None,
            "material_code": material.code if material else None,
            "variant_count": len(product_variants)
        })
        
        # Create individual product file with full details
        product_data = {
            "version": version,
            "product": entity_to_dict(product),
            "brand": entity_to_dict(brand) if brand else None,
            "material": entity_to_dict(material) if material else None,
            "documents": [entity_to_dict(d) for d in product_docs],
            "variants": [
                {
                    **entity_to_dict(v),
                    "spools": [entity_to_dict(s) for s in spools_by_variant.get(v.id, [])]
                }
                for v in product_variants
            ]
        }
        write_json(products_path / f"{product.id}.json", product_data)
    
    # Write product index
    product_index = {
        "version": version,
        "count": len(db.products),
        "products": product_index_items
    }
    write_json(products_path / "index.json", product_index)
    print(f"  Written: {len(db.products)} product files to {products_path}")
    
    # === Stores ===
    stores_path = api_path / "stores"
    store_index_items = []
    
    offers_by_store = {}
    for offer in db.offers:
        offers_by_store.setdefault(offer.store_id, []).append(offer)
    
    for store in db.stores:
        store_offers = offers_by_store.get(store.id, [])
        
        store_index_items.append({
            "id": store.id,
            "slug": store.slug,
            "name": store.name,
            "domain": store.domain,
            "offer_count": len(store_offers),
            "logo_url": ensure_store_logo_and_get_url(store)
        })
        
        # Create individual store file with offers
        _store_dict = entity_to_dict(store)
        _store_dict["logo_url"] = ensure_store_logo_and_get_url(store)
        store_data = {
            "version": version,
            "store": _store_dict,
            "offers": [
                {
                    **entity_to_dict(o),
                    "spool": entity_to_dict(spools_map.get(o.spool_id)) if o.spool_id and o.spool_id in spools_map else None
                }
                for o in store_offers
            ]
        }
        write_json(stores_path / f"{store.slug}.json", store_data)
    
    # Write store index
    store_index = {
        "version": version,
        "count": len(db.stores),
        "stores": store_index_items
    }
    write_json(stores_path / "index.json", store_index)
    print(f"  Written: {len(db.stores)} store files to {stores_path}")
    
    # === Search/Autocomplete ===
    search_path = api_path / "search"
    
    # Build a lightweight autocomplete index
    autocomplete_items = []
    
    # Add brands
    for brand in db.brands:
        autocomplete_items.append({
            "type": "brand",
            "id": brand.id,
            "slug": brand.slug,
            "name": brand.name,
            "search_text": brand.name.lower()
        })
    
    # Add products (with brand prefix)
    for product in db.products:
        brand = brands_map.get(product.brand_id)
        full_name = f"{brand.name} {product.name}" if brand else product.name
        autocomplete_items.append({
            "type": "product",
            "id": product.id,
            "slug": product.slug,
            "name": product.name,
            "brand_slug": brand.slug if brand else None,
            "full_name": full_name,
            "search_text": full_name.lower()
        })
    
    # Add materials
    for material in db.material_families:
        autocomplete_items.append({
            "type": "material",
            "id": material.id,
            "code": material.code,
            "name": material.name,
            "search_text": f"{material.code.lower()} {material.name.lower()}"
        })
    
    autocomplete_data = {
        "version": version,
        "count": len(autocomplete_items),
        "items": autocomplete_items
    }
    write_json(search_path / "autocomplete.json", autocomplete_data)
    print(f"  Written: {search_path / 'autocomplete.json'}")
    
    # === Catalog hierarchy ===
    catalog_path = api_path / "catalog"

    # Catalog index: list brands
    write_json(catalog_path / "index.json", {
        "version": version,
        "count": len(db.brands),
        "brands": [
            {
                "id": b.id,
                "slug": b.slug,
                "name": b.name,
                "path": f"{b.slug}/index.json"
            } for b in db.brands
        ]
    })

    # Build nested: brand → material code → product slug → variant slug
    # Precompute maps
    products_by_material = {}
    for p in db.products:
        products_by_material.setdefault(p.material_family_id, []).append(p)

    for brand in db.brands:
        brand_catalog_root = catalog_path / brand.slug
        brand_products = products_by_brand.get(brand.id, [])

        # Materials present for this brand
        brand_material_ids = sorted({p.material_family_id for p in brand_products})
        brand_materials = [materials_map[mid] for mid in brand_material_ids if mid in materials_map]

        # Brand index.json
        write_json(brand_catalog_root / "index.json", {
            "version": version,
            "brand": entity_to_dict(brand),
            "materials": [
                {
                    "id": m.id,
                    "code": m.code,
                    "name": m.name,
                    "path": f"{m.code.lower()}/index.json"
                } for m in brand_materials
            ]
        })

        for material in brand_materials:
            mat_root = brand_catalog_root / material.code.lower()
            # Products for this brand+material
            bmp = [p for p in brand_products if p.material_family_id == material.id]
            write_json(mat_root / "index.json", {
                "version": version,
                "brand": entity_to_dict(brand),
                "material": entity_to_dict(material),
                "products": [
                    {
                        "id": p.id,
                        "slug": p.slug,
                        "name": p.name,
                        "path": f"{p.slug}/index.json",
                        "variant_count": len(variants_by_product.get(p.id, []))
                    } for p in bmp
                ]
            })

            for p in bmp:
                prod_root = mat_root / p.slug
                prod_variants = variants_by_product.get(p.id, [])

                # Product index.json under catalog
                write_json(prod_root / "index.json", {
                    "version": version,
                    "brand": entity_to_dict(brand),
                    "material": entity_to_dict(material),
                    "product": entity_to_dict(p),
                    "variants": [
                        {
                            "id": v.id,
                            "slug": v.slug if hasattr(v, 'slug') else None,
                            "color_name": v.color_name,
                            "path": f"{(v.slug or '').strip() or 'variant'}.json"
                        } for v in prod_variants
                    ]
                })

                for v in prod_variants:
                    v_slug = (getattr(v, 'slug', None) or (v.color_name or '')).strip()
                    if not v_slug:
                        v_slug = v.id  # fallback
                    v_slug = (v_slug or '').lower().replace(' ', '-')

                    # Build spools with embedded offers and store info
                    spools_payload = []
                    for s in spools_by_variant.get(v.id, []) or []:
                        s_dict = entity_to_dict(s)
                        # Attach offers (aka product links) for this spool
                        s_offers = []
                        for o in offers_by_spool.get(s.id, []) or []:
                            store = stores_map.get(o.store_id)
                            s_offers.append({
                                **entity_to_dict(o),
                                "store": entity_to_dict(store) if store else None
                            })
                        if s_offers:
                            s_dict["offers"] = s_offers
                        spools_payload.append(s_dict)

                    write_json(prod_root / f"{v_slug}.json", {
                        "version": version,
                        "brand": entity_to_dict(brand),
                        "material": entity_to_dict(material),
                        "product": entity_to_dict(p),
                        "variant": entity_to_dict(v),
                        # Spools correspond to SimplyPrint FilamentVariant (size/diameter),
                        # and now include store product links under "offers" per spool
                        "spools": spools_payload
                    })

    # === Routes manifest ===
    routes = {
        "version": version,
        "generated_at": generated_at,
        "base_url": base_url,
        "routes": {
            "index": "/index.json",
            "brands": "/brands/index.json",
            "brand": "/brands/{slug}.json",
            "materials": "/materials/index.json",
            "material": "/materials/{code}.json",
            "material_spools": "/materials/{code}-spools.json",
            "products": "/products/index.json",
            "product": "/products/{id}.json",
            "stores": "/stores/index.json",
            "store": "/stores/{slug}.json",
            "search": "/search/autocomplete.json",
            "spools": "/spools/index.json",
            "brand_spools": "/brands/{slug}-spools.json",
            "catalog": "/catalog/index.json",
            "catalog_brand": "/catalog/{brand}/index.json",
            "catalog_material": "/catalog/{brand}/{material}/index.json",
            "catalog_product": "/catalog/{brand}/{material}/{product}/index.json",
            "catalog_variant": "/catalog/{brand}/{material}/{product}/{variant}.json"
        }
    }
    write_json(api_path / "routes.json", routes)
    print(f"  Written: {api_path / 'routes.json'}")
    
    print("Static API export complete!")
    
    return api_path
