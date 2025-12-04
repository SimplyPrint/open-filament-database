"""
SQLite exporter that creates a relational database with proper schema.
"""

import json
import lzma
import sqlite3
from pathlib import Path

from ..models import Database


# SQLite schema DDL
SCHEMA_DDL = """
PRAGMA foreign_keys = ON;

-- Metadata table
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Brand table
CREATE TABLE IF NOT EXISTS brand (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    website TEXT,
    logo TEXT,
    country TEXT,
    origin TEXT,
    aliases TEXT,  -- JSON array
    created_at TEXT,
    updated_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_brand_slug ON brand(slug);
CREATE UNIQUE INDEX IF NOT EXISTS ux_brand_name ON brand(name);

-- Material family table
CREATE TABLE IF NOT EXISTS material_family (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_material_code ON material_family(code);

-- Product table
CREATE TABLE IF NOT EXISTS product (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brand(id) ON DELETE CASCADE,
    material_family_id TEXT NOT NULL REFERENCES material_family(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    description TEXT,
    diameters TEXT,  -- JSON array
    specs TEXT,      -- JSON object
    images TEXT,     -- JSON array
    source_path TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_product_brand ON product(brand_id);
CREATE INDEX IF NOT EXISTS ix_product_material ON product(material_family_id);

-- Variant table
CREATE TABLE IF NOT EXISTS variant (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    color_name TEXT,
    finish TEXT,
    color_value TEXT,
    colorants TEXT,  -- JSON array
    images TEXT,     -- JSON array
    source_path TEXT
);
CREATE INDEX IF NOT EXISTS ix_variant_product ON variant(product_id);

-- Spool table
CREATE TABLE IF NOT EXISTS spool (
    id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES variant(id) ON DELETE CASCADE,
    sku TEXT,
    gtin TEXT,
    weight_g INTEGER NOT NULL,
    length_m INTEGER,
    diameter_mm REAL NOT NULL,
    msrp_amount TEXT,
    msrp_currency TEXT
);
CREATE INDEX IF NOT EXISTS ix_spool_variant ON spool(variant_id);
CREATE INDEX IF NOT EXISTS ix_spool_sku ON spool(sku);
CREATE INDEX IF NOT EXISTS ix_spool_gtin ON spool(gtin);

-- Store table
CREATE TABLE IF NOT EXISTS store (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    storefront_url TEXT,
    ships_from TEXT,
    ships_to TEXT,
    logo TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_store_slug ON store(slug);

-- Offer table
CREATE TABLE IF NOT EXISTS offer (
    id TEXT PRIMARY KEY,
    store_id TEXT NOT NULL REFERENCES store(id) ON DELETE CASCADE,
    spool_id TEXT REFERENCES spool(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    price_amount TEXT,
    price_currency TEXT,
    in_stock INTEGER,  -- 0/1/NULL
    last_seen_at TEXT,
    shipping_regions TEXT  -- JSON array
);
CREATE INDEX IF NOT EXISTS ix_offer_store ON offer(store_id);
CREATE INDEX IF NOT EXISTS ix_offer_spool ON offer(spool_id);

-- Document table
CREATE TABLE IF NOT EXISTS document (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    url TEXT NOT NULL,
    language TEXT
);
CREATE INDEX IF NOT EXISTS ix_document_product ON document(product_id);

-- Tag table
CREATE TABLE IF NOT EXISTS tag (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Product-Tag many-to-many
CREATE TABLE IF NOT EXISTS product_tag (
    product_id TEXT NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    tag_id TEXT NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

-- Variant-Tag many-to-many
CREATE TABLE IF NOT EXISTS variant_tag (
    variant_id TEXT NOT NULL REFERENCES variant(id) ON DELETE CASCADE,
    tag_id TEXT NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (variant_id, tag_id)
);

-- Useful views
CREATE VIEW IF NOT EXISTS v_full_spool AS
SELECT 
    s.id AS spool_id,
    s.sku,
    s.gtin,
    s.weight_g,
    s.length_m,
    s.diameter_mm,
    s.msrp_amount,
    s.msrp_currency,
    v.id AS variant_id,
    v.color_name,
    v.finish,
    v.color_value,
    p.id AS product_id,
    p.name AS product_name,
    p.slug AS product_slug,
    p.description AS product_description,
    mf.id AS material_family_id,
    mf.code AS material_code,
    mf.name AS material_name,
    b.id AS brand_id,
    b.name AS brand_name,
    b.slug AS brand_slug
FROM spool s
JOIN variant v ON v.id = s.variant_id
JOIN product p ON p.id = v.product_id
JOIN material_family mf ON mf.id = p.material_family_id
JOIN brand b ON b.id = p.brand_id;

CREATE VIEW IF NOT EXISTS v_spool_offers AS
SELECT 
    s.id AS spool_id,
    s.sku,
    s.weight_g,
    s.diameter_mm,
    v.color_name,
    p.name AS product_name,
    b.name AS brand_name,
    st.name AS store_name,
    st.storefront_url AS storefront_url,
    o.url AS offer_url,
    o.price_amount,
    o.price_currency,
    o.in_stock,
    o.last_seen_at
FROM offer o
JOIN store st ON st.id = o.store_id
LEFT JOIN spool s ON s.id = o.spool_id
LEFT JOIN variant v ON v.id = s.variant_id
LEFT JOIN product p ON p.id = v.product_id
LEFT JOIN brand b ON b.id = p.brand_id;
"""


def json_or_none(value):
    """Convert a value to JSON string or return None."""
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def bool_to_int(value):
    """Convert boolean to SQLite integer (0/1) or None."""
    if value is None:
        return None
    return 1 if value else 0


def export_sqlite(db: Database, output_dir: str, version: str, generated_at: str, schema_version: str = "1"):
    """Export database to SQLite file."""
    print("Exporting SQLite...")
    
    output_path = Path(output_dir) / "sqlite"
    output_path.mkdir(parents=True, exist_ok=True)
    
    db_file = output_path / f"open_filament_db_v{schema_version}.sqlite"
    
    # Remove existing file if present
    if db_file.exists():
        db_file.unlink()
    
    # Create connection
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    # Execute schema DDL
    cursor.executescript(SCHEMA_DDL)
    
    # Insert metadata
    cursor.execute("INSERT INTO meta (key, value) VALUES (?, ?)", ("schema_version", schema_version))
    cursor.execute("INSERT INTO meta (key, value) VALUES (?, ?)", ("dataset_version", version))
    cursor.execute("INSERT INTO meta (key, value) VALUES (?, ?)", ("generated_at", generated_at))
    
    # Insert brands
    for brand in db.brands:
        cursor.execute("""
            INSERT INTO brand (id, name, slug, website, logo, country, origin, aliases, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            brand.id,
            brand.name,
            brand.slug,
            brand.website,
            brand.logo,
            brand.country,
            getattr(brand, 'origin', None),
            json_or_none(brand.aliases),
            brand.created_at,
            brand.updated_at
        ))
    
    # Insert material families
    for mf in db.material_families:
        cursor.execute("""
            INSERT INTO material_family (id, code, name)
            VALUES (?, ?, ?)
        """, (mf.id, mf.code, mf.name))
    
    # Insert products
    for product in db.products:
        cursor.execute("""
            INSERT INTO product (id, brand_id, material_family_id, name, slug, description, 
                                 diameters, specs, images, source_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.id,
            product.brand_id,
            product.material_family_id,
            product.name,
            product.slug,
            product.description,
            json_or_none(product.diameters),
            json_or_none(product.specs),
            json_or_none(product.images),
            product.source_path,
            product.created_at,
            product.updated_at
        ))
    
    # Insert variants
    for variant in db.variants:
        cursor.execute("""
            INSERT INTO variant (id, product_id, color_name, finish, color_value, colorants, images, source_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            variant.id,
            variant.product_id,
            variant.color_name,
            variant.finish,
            variant.color_value,
            json_or_none(variant.colorants),
            json_or_none(variant.images),
            variant.source_path
        ))
    
    # Insert spools
    for spool in db.spools:
        cursor.execute("""
            INSERT INTO spool (id, variant_id, sku, gtin, weight_g, length_m, diameter_mm, msrp_amount, msrp_currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            spool.id,
            spool.variant_id,
            spool.sku,
            spool.gtin,
            spool.weight_g,
            spool.length_m,
            spool.diameter_mm,
            spool.msrp_amount,
            spool.msrp_currency
        ))
    
    # Insert stores
    for store in db.stores:
        cursor.execute("""
            INSERT INTO store (id, name, slug, storefront_url, ships_from, ships_to, logo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            store.id,
            store.name,
            store.slug,
            store.storefront_url,
            json_or_none(store.ships_from),
            json_or_none(store.ships_to),
            getattr(store, 'logo', None)
        ))
    
    # Insert documents
    for doc in db.documents:
        cursor.execute("""
            INSERT INTO document (id, product_id, type, url, language)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc.id,
            doc.product_id,
            doc.type,
            doc.url,
            doc.language
        ))
    
    # Insert tags
    for tag in db.tags:
        cursor.execute("""
            INSERT INTO tag (id, name)
            VALUES (?, ?)
        """, (tag.id, tag.name))
    
    # Commit and close
    conn.commit()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM brand")
    brand_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM product")
    product_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM variant")
    variant_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM spool")
    spool_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"  Written: {db_file}")
    print(f"    Brands: {brand_count}, Products: {product_count}, Variants: {variant_count}, Spools: {spool_count}")
    
    # Create compressed version
    xz_file = output_path / f"open_filament_db_v{schema_version}.sqlite.xz"
    with open(db_file, 'rb') as f_in:
        with lzma.open(xz_file, 'wb', preset=6) as f_out:
            f_out.write(f_in.read())
    print(f"  Written: {xz_file}")
    
    print("SQLite export complete!")
    
    return db_file, xz_file
