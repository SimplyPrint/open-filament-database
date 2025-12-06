"""
Static API exporter that creates a split, GitHub Pages-friendly API structure.
"""

import json
from pathlib import Path
import shutil
from typing import Any

from ..models import Database, Brand, Filament, Variant, Size, PurchaseLink


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


def make_brand_ref(brand) -> dict:
    """Create a lightweight brand reference with id, name, and slug."""
    if not brand:
        return {"brand_id": None, "brand_name": None, "brand_slug": None}
    return {
        "brand_id": brand.id,
        "brand_name": brand.name,
        "brand_slug": brand.slug,
    }


def make_material_ref(material) -> dict:
    """Create a lightweight material reference with id, code, and name."""
    if not material:
        return {"material_id": None, "material_code": None, "material_name": None}
    return {
        "material_id": material.id,
        "material_code": material.code,
        "material_name": material.name,
    }


def make_filament_ref(filament) -> dict:
    """Create a lightweight filament reference with id, name, and slug."""
    if not filament:
        return {"filament_id": None, "filament_name": None, "filament_slug": None}
    return {
        "filament_id": filament.id,
        "filament_name": filament.name,
        "filament_slug": filament.slug,
    }


def make_variant_ref(variant) -> dict:
    """Create a lightweight variant reference with id, color_name, and slug."""
    if not variant:
        return {"variant_id": None, "variant_name": None, "variant_slug": None}
    return {
        "variant_id": variant.id,
        "variant_name": variant.color_name,
        "variant_slug": variant.slug,
    }


def make_store_ref(store) -> dict:
    """Create a lightweight store reference with id, name, slug, and storefront_url."""
    if not store:
        return {"store_id": None, "store_name": None, "store_slug": None, "storefront_url": None}
    return {
        "store_id": store.id,
        "store_name": store.name,
        "store_slug": store.slug,
        "storefront_url": store.storefront_url,
    }


def make_size_ref(size) -> dict:
    """Create a lightweight size reference with id and key identifiers."""
    if not size:
        return {"size_id": None, "size_weight_g": None, "size_diameter_mm": None}
    return {
        "size_id": size.id,
        "size_weight_g": size.weight_g,
        "size_diameter_mm": size.diameter_mm,
    }


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
    filaments_by_brand = {}
    for filament in db.filaments:
        filaments_by_brand.setdefault(filament.brand_id, []).append(filament)

    variants_by_filament = {}
    for variant in db.variants:
        variants_by_filament.setdefault(variant.filament_id, []).append(variant)

    sizes_by_variant = {}
    for size in db.sizes:
        sizes_by_variant.setdefault(size.variant_id, []).append(size)

    documents_by_filament = {}
    for doc in db.documents:
        documents_by_filament.setdefault(doc.filament_id, []).append(doc)

    purchase_links_by_size = {}
    for pl in db.purchase_links:
        purchase_links_by_size.setdefault(pl.size_id, []).append(pl)

    materials_map = {m.id: m for m in db.material_families}
    brands_map = {b.id: b for b in db.brands}
    filaments_map = {f.id: f for f in db.filaments}
    variants_map = {v.id: v for v in db.variants}
    sizes_map = {s.id: s for s in db.sizes}
    stores_map = {s.id: s for s in db.stores}
    # Also map stores by slug for purchase_link lookups (store_id may be a slug)
    stores_by_slug = {s.slug: s for s in db.stores}
    
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
            "filaments": "filaments/index.json",
            "stores": "stores/index.json",
            "search": "search/autocomplete.json",
            "catalog": "catalog/index.json",
            "sizes": "sizes/index.json"
        },
        "stats": {
            "brands": len(db.brands),
            "material_families": len(db.material_families),
            "filaments": len(db.filaments),
            "variants": len(db.variants),
            "sizes": len(db.sizes),
            "stores": len(db.stores),
            "purchase_links": len(db.purchase_links)
        }
    }
    write_json(api_path / "index.json", root_index)
    print(f"  Written: {api_path / 'index.json'}")

    # === Brands ===
    brands_path = api_path / "brands"
    brand_index_items = []

    for brand in db.brands:
        brand_filaments = filaments_by_brand.get(brand.id, [])

        # Count variants and sizes for this brand
        variant_count = 0
        size_count = 0
        for filament in brand_filaments:
            filament_variants = variants_by_filament.get(filament.id, [])
            variant_count += len(filament_variants)
            for variant in filament_variants:
                size_count += len(sizes_by_variant.get(variant.id, []))

        # Add to index
        brand_index_items.append({
            "id": brand.id,
            "slug": brand.slug,
            "name": brand.name,
            "filament_count": len(brand_filaments),
            "variant_count": variant_count,
            "size_count": size_count,
            "logo_url": ensure_brand_logo_and_get_url(brand)
        })

        # Create individual brand file with filaments
        # augment brand dict with logo_url
        _brand_dict = entity_to_dict(brand)
        _brand_dict["logo_url"] = ensure_brand_logo_and_get_url(brand)
        brand_data = {
            "version": version,
            "brand": _brand_dict,
            "filaments": [
                {
                    **entity_to_dict(f),
                    **make_material_ref(materials_map.get(f.material_family_id)),
                    "variant_count": len(variants_by_filament.get(f.id, []))
                }
                for f in brand_filaments
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

    filaments_by_material = {}
    for filament in db.filaments:
        filaments_by_material.setdefault(filament.material_family_id, []).append(filament)

    for material in db.material_families:
        material_filaments = filaments_by_material.get(material.id, [])

        material_index_items.append({
            "id": material.id,
            "code": material.code,
            "name": material.name,
            "filament_count": len(material_filaments)
        })

        # Create individual material file
        material_data = {
            "version": version,
            "material": entity_to_dict(material),
            "filaments": [
                {
                    **entity_to_dict(f),
                    **make_brand_ref(brands_map.get(f.brand_id)),
                }
                for f in material_filaments
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

    # === Sizes (individual files + sitemap index) ===
    sizes_path = api_path / "sizes"

    def make_size_view(size: Size):
        """Create full size view with all related references."""
        v = variants_map.get(size.variant_id)
        f = filaments_map.get(v.filament_id) if v else None
        b = brands_map.get(f.brand_id) if f else None
        m = materials_map.get(f.material_family_id) if f else None
        size_purchase_links = purchase_links_by_size.get(size.id, [])
        return {
            **entity_to_dict(size),
            "brand_id": b.id if b else None,
            "material_id": m.id if m else None,
            "purchase_links": [
                {
                    **entity_to_dict(pl),
                    # Try looking up store by ID first, then by slug (store_id may be a slug)
                    **make_store_ref(stores_map.get(pl.store_id) or stores_by_slug.get(pl.store_id))
                }
                for pl in size_purchase_links
            ]
        }

    def make_size_index_entry(size: Size) -> dict:
        """Create a lightweight size reference for sitemap-style index."""
        v = variants_map.get(size.variant_id)
        f = filaments_map.get(v.filament_id) if v else None
        b = brands_map.get(f.brand_id) if f else None
        m = materials_map.get(f.material_family_id) if f else None
        return {
            "id": size.id,
            "variant_name": v.color_name if v else None,
            "filament_name": f.name if f else None,
            "brand_id": b.id if b else None,
            "material_id": m.id if m else None
        }

    # Write individual size files
    for size in db.sizes:
        size_data = {
            "version": version,
            "size": make_size_view(size)
        }
        write_json(sizes_path / f"{size.id}.json", size_data)

    # Sizes index (sitemap style - references only)
    write_json(sizes_path / "index.json", {
        "version": version,
        "count": len(db.sizes),
        "sizes": [make_size_index_entry(s) for s in db.sizes]
    })
    print(f"  Written: {len(db.sizes)} size files to {sizes_path}")

    # Sizes per material (sitemap style)
    for material in db.material_families:
        mat_size_entries = []
        for s in db.sizes:
            v = variants_map.get(s.variant_id)
            f = filaments_map.get(v.filament_id) if v else None
            if f and f.material_family_id == material.id:
                mat_size_entries.append(make_size_index_entry(s))
        write_json(materials_path / f"{material.code.lower()}-sizes.json", {
            "version": version,
            "material": entity_to_dict(material),
            "count": len(mat_size_entries),
            "sizes": mat_size_entries
        })

    # Sizes per brand (sitemap style)
    for brand in db.brands:
        brand_size_entries = []
        for s in db.sizes:
            v = variants_map.get(s.variant_id)
            f = filaments_map.get(v.filament_id) if v else None
            if f and f.brand_id == brand.id:
                brand_size_entries.append(make_size_index_entry(s))
        write_json(brands_path / f"{brand.slug}-sizes.json", {
            "version": version,
            "brand": entity_to_dict(brand),
            "count": len(brand_size_entries),
            "sizes": brand_size_entries
        })
    
    # === Filaments ===
    filaments_path = api_path / "filaments"
    filament_index_items = []

    for filament in db.filaments:
        filament_variants = variants_by_filament.get(filament.id, [])
        filament_docs = documents_by_filament.get(filament.id, [])
        brand = brands_map.get(filament.brand_id)
        material = materials_map.get(filament.material_family_id)

        filament_index_items.append({
            "id": filament.id,
            "slug": filament.slug,
            "name": filament.name,
            "brand_slug": brand.slug if brand else None,
            "brand_name": brand.name if brand else None,
            "material_code": material.code if material else None,
            "variant_count": len(filament_variants)
        })

        # Create individual filament file with full details
        # Sizes are referenced (not embedded) - data lives in /sizes/{id}.json
        filament_data = {
            "version": version,
            "filament": entity_to_dict(filament),
            **make_brand_ref(brand),
            **make_material_ref(material),
            "documents": [entity_to_dict(d) for d in filament_docs],
            "variants": [
                {
                    **entity_to_dict(v),
                    "sizes": [
                        {
                            **make_size_ref(s),
                            "sku": s.sku,
                            "gtin": s.gtin,
                            "path": f"../../sizes/{s.id}.json"
                        }
                        for s in sizes_by_variant.get(v.id, [])
                    ]
                }
                for v in filament_variants
            ]
        }
        write_json(filaments_path / f"{filament.id}.json", filament_data)

    # Write filament index
    filament_index = {
        "version": version,
        "count": len(db.filaments),
        "filaments": filament_index_items
    }
    write_json(filaments_path / "index.json", filament_index)
    print(f"  Written: {len(db.filaments)} filament files to {filaments_path}")
    
    # === Stores ===
    stores_path = api_path / "stores"
    store_index_items = []
    
    for store in db.stores:
        store_index_items.append({
            "id": store.id,
            "slug": store.slug,
            "name": store.name,
        })
        
        # Create individual store file with full details
        _store_dict = entity_to_dict(store)
        _store_dict["logo_url"] = ensure_store_logo_and_get_url(store)
        store_data = {
            "version": version,
            "store": _store_dict,
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
    
    # Add filaments (with brand prefix)
    for filament in db.filaments:
        brand = brands_map.get(filament.brand_id)
        full_name = f"{brand.name} {filament.name}" if brand else filament.name
        autocomplete_items.append({
            "type": "filament",
            "id": filament.id,
            "slug": filament.slug,
            "name": filament.name,
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

    # Build nested: brand → material code → filament slug → variant slug
    for brand in db.brands:
        brand_catalog_root = catalog_path / brand.slug
        brand_filaments = filaments_by_brand.get(brand.id, [])

        # Materials present for this brand
        brand_material_ids = sorted({f.material_family_id for f in brand_filaments})
        brand_materials = [materials_map[mid] for mid in brand_material_ids if mid in materials_map]

        # Brand index.json
        write_json(brand_catalog_root / "index.json", {
            "version": version,
            **make_brand_ref(brand),
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
            # Filaments for this brand+material
            bmf = [f for f in brand_filaments if f.material_family_id == material.id]
            write_json(mat_root / "index.json", {
                "version": version,
                **make_brand_ref(brand),
                **make_material_ref(material),
                "filaments": [
                    {
                        "id": f.id,
                        "slug": f.slug,
                        "name": f.name,
                        "path": f"{f.slug}/index.json",
                        "variant_count": len(variants_by_filament.get(f.id, []))
                    } for f in bmf
                ]
            })

            for f in bmf:
                filament_root = mat_root / f.slug
                filament_variants = variants_by_filament.get(f.id, [])

                # Filament index.json under catalog
                write_json(filament_root / "index.json", {
                    "version": version,
                    **make_brand_ref(brand),
                    **make_material_ref(material),
                    **make_filament_ref(f),
                    "variants": [
                        {
                            "id": v.id,
                            "slug": v.slug if hasattr(v, 'slug') else None,
                            "color_name": v.color_name,
                            "path": f"{(v.slug or '').strip() or 'variant'}.json"
                        } for v in filament_variants
                    ]
                })

                for v in filament_variants:
                    v_slug = (getattr(v, 'slug', None) or (v.color_name or '')).strip()
                    if not v_slug:
                        v_slug = v.id  # fallback
                    v_slug = (v_slug or '').lower().replace(' ', '-')

                    # Build size references (not embedded) - full data lives in /sizes/{id}.json
                    sizes_payload = []
                    for s in sizes_by_variant.get(v.id, []) or []:
                        size_ref = {
                            **make_size_ref(s),
                            "sku": s.sku,
                            "gtin": s.gtin,
                            "path": f"../../../../sizes/{s.id}.json"
                        }
                        sizes_payload.append(size_ref)

                    write_json(filament_root / f"{v_slug}.json", {
                        "version": version,
                        **make_brand_ref(brand),
                        **make_material_ref(material),
                        **make_filament_ref(f),
                        "variant": entity_to_dict(v),
                        # Sizes are referenced (not embedded) - data lives in /sizes/{id}.json
                        "sizes": sizes_payload
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
            "material_sizes": "/materials/{code}-sizes.json",
            "filaments": "/filaments/index.json",
            "filament": "/filaments/{id}.json",
            "stores": "/stores/index.json",
            "store": "/stores/{slug}.json",
            "search": "/search/autocomplete.json",
            "sizes": "/sizes/index.json",
            "size": "/sizes/{id}.json",
            "brand_sizes": "/brands/{slug}-sizes.json",
            "catalog": "/catalog/index.json",
            "catalog_brand": "/catalog/{brand}/index.json",
            "catalog_material": "/catalog/{brand}/{material}/index.json",
            "catalog_filament": "/catalog/{brand}/{material}/{filament}/index.json",
            "catalog_variant": "/catalog/{brand}/{material}/{filament}/{variant}.json"
        }
    }
    write_json(api_path / "routes.json", routes)
    print(f"  Written: {api_path / 'routes.json'}")
    
    print("Static API export complete!")
    
    return api_path
