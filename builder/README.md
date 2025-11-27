# Open Filament Database Builder

This is the build system that transforms the human-readable filament database into multiple machine-friendly formats.

## Quick Start

```bash
# Run the builder from the project root
python -m builder.build

# Or with options
python -m builder.build --version 2025.11.0 --output-dir dist
```

## Output Formats

The builder generates the following formats in the `dist/` directory:

### 1. JSON (`dist/json/`)

- **`all.json`** - Complete dataset in one file
- **`all.json.gz`** - Gzip compressed version
- **`all.ndjson`** - Newline-delimited JSON for streaming
- **`brands/`** - Per-brand JSON files
  - `index.json` - Brand listing
  - `{brand-slug}.json` - Individual brand data

### 2. SQLite (`dist/sqlite/`)

- **`open_filament_db_v1.sqlite`** - Relational database
- **`open_filament_db_v1.sqlite.xz`** - XZ compressed version

The SQLite database includes:
- Full relational schema with foreign keys
- Indexes for common queries
- Pre-built views: `v_full_spool`, `v_spool_offers`

### 3. CSV (`dist/csv/`)

- `brands.csv`
- `material_families.csv`
- `products.csv`
- `variants.csv`
- `spools.csv`
- `stores.csv`
- `offers.csv`
- `documents.csv`
- `full_spools.csv` - Denormalized view

### 4. Static API (`dist/api/v1/`)

A GitHub Pages-friendly split API:

```
api/v1/
├── index.json          # Root with stats and endpoints
├── routes.json         # API route definitions
├── brands/
│   ├── index.json      # All brands
│   └── {slug}.json     # Individual brand + products
├── materials/
│   ├── index.json      # All materials
│   └── {code}.json     # Products by material
├── products/
│   ├── index.json      # All products
│   └── {id}.json       # Product with variants
├── stores/
│   ├── index.json      # All stores
│   └── {slug}.json     # Store with offers
 └── search/
    └── autocomplete.json  # Search index
```

Additional endpoints implemented for navigation and discovery:

```
spools/
└── index.json               # All spools (joined with variant/product/brand/material)
materials/
└── {code}-spools.json       # All spools for a material (e.g., pla-spools.json)
brands/
└── {brand}-spools.json      # All spools for a brand
catalog/
├── index.json               # Catalog entry point (lists brands)
└── {brand}/
    ├── index.json           # Brand → available material types for this brand
    └── {material}/
        ├── index.json       # Material → branded products (aka product lines) under this brand/material
        └── {product}/
            ├── index.json   # Product → color variants list
            └── {variant}.json  # Variant page with spools; each spool may embed `offers` with store links
```

Catalog hierarchy mirrors SimplyPrint schema:
- Brand
  - Material types (e.g., PLA)
    - Branded materials under the type (products like "PLA Basic", "PLA Matte")
      - Colors (variants)
        - Spools (sizes/SKUs) including embedded store offers

## Command Line Options

```
python -m builder.build [options]

Options:
  --output-dir, -o DIR    Output directory (default: dist)
  --data-dir, -d DIR      Data directory (default: data)
  --stores-dir, -s DIR    Stores directory (default: stores)
  --version, -v VERSION   Dataset version (default: auto-generated)
  --base-url, -b URL      Base URL for static API
  --skip-json             Skip JSON export
  --skip-sqlite           Skip SQLite export
  --skip-csv              Skip CSV export
  --skip-api              Skip static API export
```

## Programmatic Usage

```python
from builder import crawl_data, export_json, export_sqlite, export_csv, export_api

# Crawl the data
db = crawl_data("data", "stores")

# Export to various formats
version = "2025.11.0"
generated_at = "2025-11-27T12:00:00Z"

export_json(db, "dist", version, generated_at)
export_sqlite(db, "dist", version, generated_at)
export_csv(db, "dist", version, generated_at)
export_api(db, "dist", version, generated_at, base_url="https://example.com/api/v1")
```

## Data Model

### Entities

| Entity | Description |
|--------|-------------|
| `Brand` | Filament manufacturer (e.g., Prusament, Polymaker) |
| `MaterialFamily` | Material type (PLA, PETG, ABS, etc.) |
| `Product` | Product line (e.g., "Prusament PLA") |
| `Variant` | Color/finish variant (e.g., "Galaxy Black") |
| `Spool` | Specific SKU (e.g., 1kg spool, 1.75mm) |
| `Store` | Retail store |
| `Offer` | Price listing at a store |
| `Document` | TDS/SDS documents |
| `Tag` | Categorization tags |

### Relationships

```
Brand (1) ←── (N) Product (1) ←── (N) Variant (1) ←── (N) Spool
                     │                                      │
                     ↓                                      ↓
              MaterialFamily                         Offer ──→ Store
                     │
                     ↓
                 Document
```

## Directory Structure

```
builder/
├── __init__.py           # Package exports
├── build.py              # Main build script
├── models.py             # Data models (dataclasses)
├── utils.py              # Utility functions
├── crawler.py            # Data directory crawler
├── exporters/
│   ├── __init__.py
│   ├── json_exporter.py  # JSON/NDJSON export
│   ├── sqlite_exporter.py # SQLite export
│   ├── csv_exporter.py   # CSV export
│   └── api_exporter.py   # Static API export
└── README.md             # This file
```

## Example Queries

### SQLite

```sql
-- Find all PLA products
SELECT b.name AS brand, p.name AS product, v.color_name
FROM product p
JOIN brand b ON b.id = p.brand_id
JOIN material_family mf ON mf.id = p.material_family_id
JOIN variant v ON v.id = (SELECT id FROM variant WHERE product_id = p.id LIMIT 1)
WHERE mf.code = 'PLA'
ORDER BY b.name, p.name;

-- Using the pre-built view
SELECT * FROM v_full_spool WHERE material_code = 'PETG';
```

### Python (with JSON)

```python
import json

with open('dist/json/all.json') as f:
    data = json.load(f)

# Find all Prusament products
prusament = next(b for b in data['brands'] if b['name'] == 'Prusament')
products = [p for p in data['products'] if p['brand_id'] == prusament['id']]
print(f"Prusament has {len(products)} products")
```

### JavaScript (with Static API)

```javascript
// Fetch brand list
const brands = await fetch('https://example.com/api/v1/brands/index.json')
  .then(r => r.json());

// Fetch specific brand
const prusament = await fetch('https://example.com/api/v1/brands/prusament.json')
  .then(r => r.json());

console.log(prusament.products.length);
```

## CI/CD

The build runs automatically via GitHub Actions when:
- Changes are pushed to `main` branch affecting `data/`, `stores/`, `builder/`, or `schemas/`
- Manual workflow dispatch

On each build:
1. Data is crawled and normalized
2. All export formats are generated
3. Static API is deployed to GitHub Pages
4. Release is created with downloadable artifacts
