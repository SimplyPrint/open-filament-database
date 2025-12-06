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
class Filament:
    """Filament product line (e.g., Prusament PLA)."""
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
    """Color/finish variant of a filament."""
    id: str
    filament_id: str
    slug: Optional[str] = None
    color_name: Optional[str] = None
    finish: Optional[str] = None
    color_value: Optional[str] = None  # HEX color
    colorants: Optional[list[str]] = None
    images: Optional[list[str]] = None
    source_path: Optional[str] = None


@dataclass
class Size:
    """Individual size/SKU from sizes.json."""
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
    storefront_url: Optional[str] = None
    ships_from: Optional[str] = None
    ships_to: Optional[str] = None
    logo: Optional[str] = None
    # Path within the stores directory to the store folder (for asset resolution)
    source_path: Optional[str] = None


@dataclass
class Document:
    """TDS/SDS or other document."""
    id: str
    filament_id: str
    type: str  # TDS, SDS, PrintProfile, etc.
    url: str
    language: Optional[str] = None


@dataclass
class PurchaseLink:
    """Purchase link for a specific size at a store."""
    id: str
    size_id: str
    store_id: str
    url: str
    spool_refill: bool = False
    ships_from: Optional[list[str]] = None
    ships_to: Optional[list[str]] = None


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
    filaments: list[Filament] = field(default_factory=list)
    variants: list[Variant] = field(default_factory=list)
    sizes: list[Size] = field(default_factory=list)
    stores: list[Store] = field(default_factory=list)
    purchase_links: list[PurchaseLink] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
