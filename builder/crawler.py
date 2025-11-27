"""
Data crawler that scans the canonical data structure and builds normalized entities.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from .models import (
    Brand, MaterialFamily, Product, Variant, Spool, Store, Offer, Document, Tag, Database
)
from .utils import (
    generate_brand_id, generate_material_family_id, generate_product_id,
    generate_variant_id, generate_spool_id, generate_store_id, generate_offer_id,
    generate_document_id, generate_tag_id, normalize_color_hex, slugify,
    get_current_timestamp, parse_price
)


# Known material family mappings
MATERIAL_FAMILIES = {
    "PLA": ("PLA", "Polylactic Acid"),
    "PLA+": ("PLA", "Polylactic Acid"),
    "PLA Pro": ("PLA", "Polylactic Acid"),
    "PETG": ("PETG", "Polyethylene Terephthalate Glycol"),
    "ABS": ("ABS", "Acrylonitrile Butadiene Styrene"),
    "ASA": ("ASA", "Acrylonitrile Styrene Acrylate"),
    "TPU": ("TPU", "Thermoplastic Polyurethane"),
    "TPE": ("TPE", "Thermoplastic Elastomer"),
    "PA": ("PA", "Polyamide (Nylon)"),
    "PA6": ("PA", "Polyamide (Nylon)"),
    "PA12": ("PA", "Polyamide (Nylon)"),
    "PC": ("PC", "Polycarbonate"),
    "PP": ("PP", "Polypropylene"),
    "HIPS": ("HIPS", "High Impact Polystyrene"),
    "PVA": ("PVA", "Polyvinyl Alcohol"),
    "PVB": ("PVB", "Polyvinyl Butyral"),
    "PEEK": ("PEEK", "Polyether Ether Ketone"),
    "PEI": ("PEI", "Polyetherimide"),
    "CF": ("CF", "Carbon Fiber Composite"),
    "GF": ("GF", "Glass Fiber Composite"),
    "Wood": ("WOOD", "Wood Composite"),
    "Metal": ("METAL", "Metal Composite"),
}


def get_material_family_code(material_name: str) -> tuple[str, str]:
    """Get material family code and name from material directory name."""
    # Check direct mapping first
    if material_name in MATERIAL_FAMILIES:
        return MATERIAL_FAMILIES[material_name]
    
    # Check if it contains a known base material
    for key, (code, name) in MATERIAL_FAMILIES.items():
        if key in material_name:
            return (code, name)
    
    # Default: use the material name itself
    return (material_name.upper(), material_name)


class DataCrawler:
    """Crawls the data directory structure and builds normalized database."""
    
    def __init__(self, data_dir: str, stores_dir: str):
        self.data_dir = Path(data_dir)
        self.stores_dir = Path(stores_dir)
        self.db = Database()
        self.timestamp = get_current_timestamp()
        
        # Caches for deduplication
        self._brand_cache: dict[str, str] = {}  # name -> id
        self._material_cache: dict[str, str] = {}  # code -> id
        self._product_cache: dict[str, str] = {}  # path -> id
        self._variant_cache: dict[str, str] = {}  # path -> id
        self._store_cache: dict[str, str] = {}  # name -> id
        
    def crawl(self) -> Database:
        """Crawl all data and return the populated database."""
        print("Starting data crawl...")
        
        # Crawl main data directory (brands/materials/products/variants)
        self._crawl_data_directory()
        
        # Crawl stores directory
        self._crawl_stores_directory()
        
        # Print summary
        print(f"\nCrawl complete!")
        print(f"  Brands: {len(self.db.brands)}")
        print(f"  Material Families: {len(self.db.material_families)}")
        print(f"  Products: {len(self.db.products)}")
        print(f"  Variants: {len(self.db.variants)}")
        print(f"  Spools: {len(self.db.spools)}")
        print(f"  Stores: {len(self.db.stores)}")
        print(f"  Offers: {len(self.db.offers)}")
        print(f"  Documents: {len(self.db.documents)}")
        
        return self.db
    
    def _crawl_data_directory(self):
        """Crawl the data/ directory for brands, products, variants."""
        if not self.data_dir.exists():
            print(f"Warning: Data directory {self.data_dir} does not exist")
            return
        
        # Each subdirectory of data/ is a brand
        for brand_dir in sorted(self.data_dir.iterdir()):
            if not brand_dir.is_dir():
                continue
            if brand_dir.name.startswith('.'):
                continue
                
            self._process_brand_directory(brand_dir)
    
    def _process_brand_directory(self, brand_dir: Path):
        """Process a brand directory."""
        brand_name = brand_dir.name
        
        # Get or create brand
        brand_id = self._get_or_create_brand(brand_name, brand_dir)
        
        # Each subdirectory is a material type
        for material_dir in sorted(brand_dir.iterdir()):
            if not material_dir.is_dir():
                continue
            if material_dir.name.startswith('.'):
                continue
            
            self._process_material_directory(material_dir, brand_id)
    
    def _process_material_directory(self, material_dir: Path, brand_id: str):
        """Process a material directory under a brand."""
        material_name = material_dir.name
        
        # Get or create material family
        material_family_id = self._get_or_create_material_family(material_name)
        
        # Each subdirectory is a product line
        for product_dir in sorted(material_dir.iterdir()):
            if not product_dir.is_dir():
                continue
            if product_dir.name.startswith('.'):
                continue
            
            self._process_product_directory(product_dir, brand_id, material_family_id)
    
    def _process_product_directory(self, product_dir: Path, brand_id: str, material_family_id: str):
        """Process a product directory."""
        product_name = product_dir.name
        
        # Check for filament.json at product level
        filament_json = product_dir / "filament.json"
        product_meta = {}
        if filament_json.exists():
            try:
                with open(filament_json, 'r', encoding='utf-8') as f:
                    product_meta = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to parse {filament_json}: {e}")
        
        # Create product
        product_id = self._create_product(
            product_dir, product_name, brand_id, material_family_id, product_meta
        )
        
        # Each subdirectory is a color variant
        for variant_dir in sorted(product_dir.iterdir()):
            if not variant_dir.is_dir():
                continue
            if variant_dir.name.startswith('.'):
                continue
            
            self._process_variant_directory(variant_dir, product_id)
    
    def _process_variant_directory(self, variant_dir: Path, product_id: str):
        """Process a variant (color) directory."""
        variant_name = variant_dir.name
        
        # Check for filament.json at variant level
        filament_json = variant_dir / "filament.json"
        variant_meta = {}
        if filament_json.exists():
            try:
                with open(filament_json, 'r', encoding='utf-8') as f:
                    variant_meta = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to parse {filament_json}: {e}")
        
        # Create variant
        variant_id = self._create_variant(variant_dir, variant_name, product_id, variant_meta)
        
        # Check for sizes.json
        sizes_json = variant_dir / "sizes.json"
        if sizes_json.exists():
            self._process_sizes_file(sizes_json, variant_id)
    
    def _process_sizes_file(self, sizes_json: Path, variant_id: str):
        """Process sizes.json file to create spools."""
        try:
            with open(sizes_json, 'r', encoding='utf-8') as f:
                sizes_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to parse {sizes_json}: {e}")
            return
        
        if not isinstance(sizes_data, list):
            sizes_data = [sizes_data]
        
        for idx, size_entry in enumerate(sizes_data):
            self._create_spool_from_size(size_entry, variant_id, sizes_json.parent, idx)
    
    def _get_or_create_brand(self, name: str, brand_dir: Path) -> str:
        """Get existing brand ID or create new brand."""
        normalized_name = name.strip()
        
        if normalized_name in self._brand_cache:
            return self._brand_cache[normalized_name]
        
        brand_id = generate_brand_id(normalized_name)
        
        # Try to load brand metadata if exists
        brand_json = brand_dir / "brand.json"
        website = None
        country = None
        origin = None
        logo = None
        aliases = []
        
        if brand_json.exists():
            try:
                with open(brand_json, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    website = meta.get("website")
                    # Support both keys; prefer explicit country, fallback to origin
                    country = meta.get("country") or meta.get("origin")
                    origin = meta.get("origin")
                    logo = meta.get("logo")
                    aliases = meta.get("aliases", [])
            except (json.JSONDecodeError, IOError):
                pass
        
        brand = Brand(
            id=brand_id,
            name=normalized_name,
            slug=slugify(normalized_name),
            website=website,
            logo=logo,
            country=country,
            origin=origin,
            aliases=aliases if aliases else None,
            created_at=self.timestamp,
            updated_at=self.timestamp,
            source_path=str(brand_dir.relative_to(self.data_dir))
        )
        
        self.db.brands.append(brand)
        self._brand_cache[normalized_name] = brand_id
        
        return brand_id
    
    def _get_or_create_material_family(self, material_name: str) -> str:
        """Get existing material family ID or create new one."""
        code, full_name = get_material_family_code(material_name)
        
        if code in self._material_cache:
            return self._material_cache[code]
        
        material_id = generate_material_family_id(code)
        
        material = MaterialFamily(
            id=material_id,
            code=code,
            name=full_name
        )
        
        self.db.material_families.append(material)
        self._material_cache[code] = material_id
        
        return material_id
    
    def _create_product(
        self, product_dir: Path, name: str, brand_id: str, 
        material_family_id: str, meta: dict
    ) -> str:
        """Create a product entity."""
        # Use relative path for stable ID generation
        rel_path = str(product_dir.relative_to(self.data_dir))
        
        if rel_path in self._product_cache:
            return self._product_cache[rel_path]
        
        product_id = generate_product_id(rel_path)
        
        # Extract diameters from meta or use defaults
        diameters = meta.get("diameters", [1.75])
        if isinstance(diameters, (int, float)):
            diameters = [diameters]
        
        # Extract specs
        specs = {}
        for key in ["nozzle_temp", "bed_temp", "density", "printing_speed", "properties"]:
            if key in meta:
                specs[key] = meta[key]
        
        # Look for images
        images = []
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            for img_file in product_dir.glob(f'*{ext}'):
                if not img_file.name.startswith('.'):
                    images.append(img_file.name)
        
        product = Product(
            id=product_id,
            brand_id=brand_id,
            material_family_id=material_family_id,
            name=name,
            slug=slugify(name),
            description=meta.get("description"),
            diameters=diameters,
            specs=specs if specs else None,
            images=images if images else None,
            source_path=rel_path,
            created_at=self.timestamp,
            updated_at=self.timestamp
        )
        
        self.db.products.append(product)
        self._product_cache[rel_path] = product_id
        
        # Handle documents (TDS, SDS, etc.)
        self._extract_documents(product_dir, product_id, meta)
        
        return product_id
    
    def _create_variant(
        self, variant_dir: Path, color_name: str, product_id: str, meta: dict
    ) -> str:
        """Create a variant entity."""
        rel_path = str(variant_dir.relative_to(self.data_dir))
        
        if rel_path in self._variant_cache:
            return self._variant_cache[rel_path]
        
        variant_id = generate_variant_id(rel_path)
        
        # Extract color information
        color_value = meta.get("color_hex") or meta.get("color")
        if color_value:
            color_value = normalize_color_hex(color_value)
        
        finish = meta.get("finish")
        colorants = meta.get("colorants")
        # Determine a slug for the variant (color)
        from .utils import slugify
        variant_slug = meta.get("slug")
        if not variant_slug:
            # Prefer explicit color_name from meta if provided
            name_for_slug = meta.get("color_name") or color_name or variant_dir.name
            variant_slug = slugify(str(name_for_slug))
        
        # Look for images
        images = []
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            for img_file in variant_dir.glob(f'*{ext}'):
                if not img_file.name.startswith('.'):
                    images.append(img_file.name)
        
        variant = Variant(
            id=variant_id,
            product_id=product_id,
            slug=variant_slug,
            color_name=color_name,
            finish=finish,
            color_value=color_value,
            colorants=colorants,
            images=images if images else None,
            source_path=rel_path
        )
        
        self.db.variants.append(variant)
        self._variant_cache[rel_path] = variant_id
        
        return variant_id
    
    def _create_spool_from_size(self, size_entry: dict, variant_id: str, variant_dir: Path, index: int = 0):
        """Create a spool from a sizes.json entry."""
        # Extract weight - try multiple field names
        weight_g = (
            size_entry.get("weight_g") or 
            size_entry.get("weight") or 
            size_entry.get("filament_weight") or
            size_entry.get("net_weight") or
            size_entry.get("spool_weight")
        )
        if weight_g is None:
            # Try to parse from string like "1kg"
            weight_str = size_entry.get("size", "")
            match = re.match(r'(\d+(?:\.\d+)?)\s*(g|kg)', weight_str.lower())
            if match:
                value, unit = match.groups()
                weight_g = int(float(value) * 1000 if unit == 'kg' else float(value))
        
        if not weight_g:
            print(f"Warning: No weight found in size entry: {size_entry}")
            return
        
        # Get diameter
        diameter = size_entry.get("diameter_mm") or size_entry.get("diameter", 1.75)
        if isinstance(diameter, str):
            diameter = float(diameter.replace("mm", "").strip())
        
        # Generate stable ID - include SKU or index for uniqueness
        sku = size_entry.get("sku") or ""
        spool_key = f"{variant_id}:{weight_g}:{diameter}:{sku}:{index}"
        spool_id = generate_spool_id(spool_key)
        
        # Extract other fields
        sku = size_entry.get("sku")
        gtin = size_entry.get("gtin") or size_entry.get("ean") or size_entry.get("upc")
        length_m = size_entry.get("length_m") or size_entry.get("length")
        
        # Parse MSRP
        msrp_amount = None
        msrp_currency = None
        if "msrp" in size_entry:
            msrp = size_entry["msrp"]
            if isinstance(msrp, dict):
                msrp_amount = msrp.get("amount")
                msrp_currency = msrp.get("currency")
            elif isinstance(msrp, (int, float)):
                msrp_amount = str(msrp)
            elif isinstance(msrp, str):
                msrp_amount, msrp_currency = parse_price(msrp)
        elif "price" in size_entry:
            price_str = size_entry["price"]
            if isinstance(price_str, str):
                msrp_amount, msrp_currency = parse_price(price_str)
        
        spool = Spool(
            id=spool_id,
            variant_id=variant_id,
            sku=sku,
            gtin=gtin,
            weight_g=int(weight_g),
            length_m=int(length_m) if length_m else None,
            diameter_mm=float(diameter),
            msrp_amount=msrp_amount,
            msrp_currency=msrp_currency
        )
        
        self.db.spools.append(spool)
    
    def _extract_documents(self, product_dir: Path, product_id: str, meta: dict):
        """Extract document references from product metadata."""
        doc_types = ["tds", "sds", "profile", "datasheet"]
        
        for doc_type in doc_types:
            url = meta.get(doc_type) or meta.get(f"{doc_type}_url")
            if url:
                doc_id = generate_document_id(f"{product_id}:{doc_type}")
                doc = Document(
                    id=doc_id,
                    product_id=product_id,
                    type=doc_type.upper(),
                    url=url,
                    language=meta.get(f"{doc_type}_language", "en")
                )
                self.db.documents.append(doc)
    
    def _crawl_stores_directory(self):
        """Crawl the stores/ directory."""
        if not self.stores_dir.exists():
            print(f"Warning: Stores directory {self.stores_dir} does not exist")
            return
        
        for store_dir in sorted(self.stores_dir.iterdir()):
            if not store_dir.is_dir():
                continue
            if store_dir.name.startswith('.'):
                continue
            
            self._process_store_directory(store_dir)
    
    def _process_store_directory(self, store_dir: Path):
        """Process a store directory."""
        store_json = store_dir / "store.json"
        if not store_json.exists():
            return
        
        try:
            with open(store_json, 'r', encoding='utf-8') as f:
                store_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to parse {store_json}: {e}")
            return
        
        store_name = store_data.get("name", store_dir.name)
        store_id = self._get_or_create_store(store_name, store_data, source_path=str(store_dir.relative_to(self.stores_dir)))
        
        # Process products/offers in store data
        products = store_data.get("products", [])
        for product_entry in products:
            self._process_store_product(product_entry, store_id)
    
    def _get_or_create_store(self, name: str, data: dict, source_path: Optional[str] = None) -> str:
        """Get existing store ID or create new store."""
        if name in self._store_cache:
            return self._store_cache[name]
        
        store_id = generate_store_id(name)
        
        store = Store(
            id=store_id,
            name=name,
            slug=slugify(name),
            domain=data.get("domain") or data.get("website"),
            country=data.get("country"),
            logo=data.get("logo"),
            source_path=source_path
        )
        
        self.db.stores.append(store)
        self._store_cache[name] = store_id
        
        return store_id
    
    def _process_store_product(self, product_entry: dict, store_id: str):
        """Process a product entry from store.json to create offers."""
        # Try to match with existing spool by SKU or other identifier
        sku = product_entry.get("sku")
        url = product_entry.get("url")
        
        if not url:
            return
        
        # Parse price
        price_amount = None
        price_currency = None
        price_data = product_entry.get("price")
        if price_data:
            if isinstance(price_data, dict):
                price_amount = price_data.get("amount")
                price_currency = price_data.get("currency")
            elif isinstance(price_data, str):
                price_amount, price_currency = parse_price(price_data)
            elif isinstance(price_data, (int, float)):
                price_amount = str(price_data)
        
        # Try to find matching spool
        spool_id = None
        if sku:
            for spool in self.db.spools:
                if spool.sku == sku:
                    spool_id = spool.id
                    break
        
        # Create offer even without matched spool (for reference)
        offer_id = generate_offer_id(f"{store_id}:{url}")
        
        offer = Offer(
            id=offer_id,
            store_id=store_id,
            spool_id=spool_id,
            url=url,
            price_amount=price_amount,
            price_currency=price_currency,
            in_stock=product_entry.get("in_stock"),
            last_seen_at=self.timestamp,
            shipping_regions=product_entry.get("shipping_regions")
        )
        
        self.db.offers.append(offer)


def crawl_data(data_dir: str, stores_dir: str) -> Database:
    """Main entry point to crawl data and return populated database."""
    crawler = DataCrawler(data_dir, stores_dir)
    return crawler.crawl()
