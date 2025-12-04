"""
Utility functions for the Open Filament Database builder.
"""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple


# UUID namespace for generating deterministic IDs
NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace


def generate_uuid5(name: str) -> str:
    """Generate a deterministic UUID5 from a name."""
    return str(uuid.uuid5(NAMESPACE, name))


def generate_brand_id(name: str) -> str:
    """Generate a stable ID for a brand."""
    return generate_uuid5(f"Brand::{name.lower().strip()}")


def generate_material_family_id(code: str) -> str:
    """Generate a stable ID for a material family."""
    return generate_uuid5(f"MaterialFamily::{code.upper().strip()}")


def generate_product_id(path: str) -> str:
    """Generate a stable ID for a product based on its path."""
    return generate_uuid5(f"Product::{path}")


def generate_variant_id(path: str) -> str:
    """Generate a stable ID for a variant based on its path."""
    return generate_uuid5(f"Variant::{path}")


def generate_spool_id(key: str) -> str:
    """Generate a stable ID for a spool."""
    return generate_uuid5(f"Spool::{key}")


def generate_store_id(name: str) -> str:
    """Generate a stable ID for a store."""
    return generate_uuid5(f"Store::{name.lower().strip()}")


def generate_document_id(key: str) -> str:
    """Generate a stable ID for a document."""
    return generate_uuid5(f"Document::{key}")


def generate_tag_id(name: str) -> str:
    """Generate a stable ID for a tag."""
    return generate_uuid5(f"Tag::{name.lower().strip()}")


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    return text


def normalize_color_hex(color: str) -> Optional[str]:
    """Normalize a color value to #RRGGBB format."""
    if not color:
        return None
    
    # Remove any whitespace
    color = color.strip()
    
    # If already in correct format, return as-is
    if re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return color.upper()
    
    # Handle 3-digit hex
    if re.match(r'^#[0-9A-Fa-f]{3}$', color):
        r, g, b = color[1], color[2], color[3]
        return f'#{r}{r}{g}{g}{b}{b}'.upper()
    
    # Handle hex without #
    if re.match(r'^[0-9A-Fa-f]{6}$', color):
        return f'#{color}'.upper()
    
    if re.match(r'^[0-9A-Fa-f]{3}$', color):
        r, g, b = color[0], color[1], color[2]
        return f'#{r}{r}{g}{g}{b}{b}'.upper()
    
    # Return as-is if we can't parse it
    return color


def get_current_timestamp() -> str:
    """Get the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_price(price_str: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a price string like "$19.99" or "€24,99" or "19.99 USD".
    
    Returns:
        Tuple of (amount, currency) where amount is a string decimal
    """
    if not price_str:
        return None, None
    
    price_str = price_str.strip()
    
    # Common currency symbols
    currency_symbols = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR',
        'kr': 'SEK',  # Could also be NOK, DKK
    }
    
    # Check for currency symbol at start
    for symbol, code in currency_symbols.items():
        if price_str.startswith(symbol):
            amount = price_str[len(symbol):].strip()
            # Normalize decimal separator
            amount = amount.replace(',', '.')
            # Remove any thousands separators
            if '.' in amount:
                parts = amount.split('.')
                if len(parts) == 2 and len(parts[-1]) == 2:
                    # Likely a decimal
                    amount = amount.replace(' ', '')
            return amount, code
    
    # Check for currency code at end (e.g., "19.99 USD")
    match = re.match(r'^([\d.,\s]+)\s*([A-Z]{3})$', price_str)
    if match:
        amount = match.group(1).strip().replace(',', '.').replace(' ', '')
        currency = match.group(2)
        return amount, currency
    
    # Check for currency code at start (e.g., "USD 19.99")
    match = re.match(r'^([A-Z]{3})\s*([\d.,]+)$', price_str)
    if match:
        currency = match.group(1)
        amount = match.group(2).replace(',', '.')
        return amount, currency
    
    # Just a number
    match = re.match(r'^[\d.,]+$', price_str)
    if match:
        amount = price_str.replace(',', '.')
        return amount, None
    
    return None, None


def calculate_sha256(data: bytes) -> str:
    """Calculate SHA256 hash of data."""
    return hashlib.sha256(data).hexdigest()


def normalize_url(url: str) -> str:
    """Normalize a URL by removing tracking parameters etc."""
    if not url:
        return url
    
    # Remove common tracking parameters
    tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'ref', 'fbclid', 'gclid']
    
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove tracking params
        filtered_params = {k: v for k, v in query_params.items() if k.lower() not in tracking_params}
        
        # Rebuild URL
        new_query = urlencode(filtered_params, doseq=True)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            ''  # Remove fragment
        ))
        
        return normalized
    except Exception:
        return url
