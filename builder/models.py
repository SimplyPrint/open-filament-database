"""
Data models for the Open Filament Database.

These dataclasses represent the normalized entities in the database.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Brand:
    """Filament manufacturer/brand."""
    id: str
    name: str
    slug: str
    website: Optional[str] = None
    logo: Optional[str] = None
    country: Optional[str] = None
    origin: Optional[str] = None
    aliases: Optional[list[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Path within the data directory to the brand folder (for asset resolution)
    source_path: Optional[str] = None


@dataclass
class MaterialFamily:
    """Material type (PLA, PETG, ABS, etc.)."""
    id: str
    code: str
    name: str


@dataclass
class Product:
    """Product line (e.g., Prusament PLA)."""
    id: str
    brand_id: str
    material_family_id: str
    name: str
    slug: str
    description: Optional[str] = None
    diameters: Optional[list[float]] = None
    specs: Optional[dict] = None
    images: Optional[list[str]] = None
    source_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Variant:
    """Color/finish variant of a product."""
    id: str
    product_id: str
    slug: Optional[str] = None
    color_name: Optional[str] = None
    finish: Optional[str] = None
    color_value: Optional[str] = None  # HEX color
    colorants: Optional[list[str]] = None
    images: Optional[list[str]] = None
    source_path: Optional[str] = None


@dataclass
class Spool:
    """Individual spool/SKU."""
    id: str
    variant_id: str
    weight_g: int
    diameter_mm: float
    sku: Optional[str] = None
    gtin: Optional[str] = None  # EAN/UPC
    length_m: Optional[int] = None
    msrp_amount: Optional[str] = None
    msrp_currency: Optional[str] = None


@dataclass
class Store:
    """Retail store."""
    id: str
    name: str
    slug: str
    domain: Optional[str] = None
    country: Optional[str] = None
    logo: Optional[str] = None
    # Path within the stores directory to the store folder (for asset resolution)
    source_path: Optional[str] = None


@dataclass
class Offer:
    """Price listing at a store."""
    id: str
    store_id: str
    url: str
    spool_id: Optional[str] = None
    price_amount: Optional[str] = None
    price_currency: Optional[str] = None
    in_stock: Optional[bool] = None
    last_seen_at: Optional[str] = None
    shipping_regions: Optional[list[str]] = None


@dataclass
class Document:
    """TDS/SDS or other document."""
    id: str
    product_id: str
    type: str  # TDS, SDS, PrintProfile, etc.
    url: str
    language: Optional[str] = None


@dataclass
class Tag:
    """Categorization tag."""
    id: str
    name: str


@dataclass
class Database:
    """Container for all database entities."""
    brands: list[Brand] = field(default_factory=list)
    material_families: list[MaterialFamily] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)
    variants: list[Variant] = field(default_factory=list)
    spools: list[Spool] = field(default_factory=list)
    stores: list[Store] = field(default_factory=list)
    offers: list[Offer] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
