"""
Pydantic models for the Open Filament Database schemas.

This module defines all data models used in the database, which are also used
to generate the JSON schemas automatically.
"""

from typing import Literal, Optional, Union, List, Dict, Annotated
from pydantic import BaseModel, Field, ConfigDict, StringConstraints, RootModel
import json
from pathlib import Path


# String length constraint used across all schemas
MAX_STRING_LENGTH = 1000

# Custom type annotations using Pydantic's built-in constraints:
class LimitedString(RootModel):
    """String type with a maximum length constraint."""
    root: Annotated[str, StringConstraints(max_length=MAX_STRING_LENGTH)]

class CountryCode(RootModel):
    """String type for ISO 3166-1 alpha-2 country codes."""
    root: Annotated[str, StringConstraints(min_length=2, max_length=2, pattern=r"^([A-Z]{2})$")] | Literal['Unknown']

class Color(RootModel):
    """String or list of strings representing hex color codes."""
    root: Annotated[str, StringConstraints(pattern=r"^#?[a-fA-F0-9]{6}$")]

class Colors(RootModel):
    """Either a single hex color code string or a list of such strings."""
    root: Union[Color, List[Color]]

class Store(BaseModel):
    """Store information for purchase links."""
    model_config = ConfigDict(extra='forbid')

    id: LimitedString = Field(..., description="The ID for this store")
    name: LimitedString = Field(..., description="The name of this store")
    storefront_url: LimitedString = Field(..., description="A link to the storefront of this store")
    storefront_affiliate_link: Optional[LimitedString] = Field(None, description="An affiliate link to the storefront of this store")
    logo: LimitedString = Field(..., description="A link to the logo for this store")

    ships_from: Union[List[CountryCode], CountryCode] = Field(..., description="A list of locations the shop linked ships from")
    ships_to: Union[List[CountryCode], CountryCode] = Field(..., description="A list of locations the shop linked ships to")


class Brand(BaseModel):
    """Brand/manufacturer information."""
    model_config = ConfigDict(extra='forbid')

    brand: LimitedString = Field(..., description="The name of the filament manufacture")
    website: LimitedString = Field(..., description="The website of the filament manufacture")
    logo: LimitedString = Field(..., description="A link to the logo for this brand")
    origin: CountryCode = Field(..., description="The country of origin")


class GenericSlicerSettings(BaseModel):
    """Generic slicer settings that map to specific slicer configurations."""
    model_config = ConfigDict(extra='forbid')

    first_layer_bed_temp: Optional[int] = None
    first_layer_nozzle_temp: Optional[int] = None
    bed_temp: Optional[int] = None
    nozzle_temp: Optional[int] = None


class SpecificSlicerSettings(BaseModel):
    """Settings for a specific slicer application."""

    profile_name: LimitedString = Field(
        ...,
        description="The name of the profile for this filament. If there is a profile specifically for this filament, that is what should be specified, even if it is printer specific. For slic3r variants, data after the '@' does not need to be included and will be removed when loading into python."
    )
    overrides: Optional[Dict[str, Union[str, List[str]]]] = Field(
        None,
        description="Key-value pairs for settings that should be overridden for this filament"
    )


class SlicerSettings(BaseModel):
    """Settings for various slicer applications."""
    model_config = ConfigDict(extra='forbid')

    prusaslicer: Optional[SpecificSlicerSettings] = None
    bambustudio: Optional[SpecificSlicerSettings] = None
    orcaslicer: Optional[SpecificSlicerSettings] = None
    cura: Optional[SpecificSlicerSettings] = None
    generic: Optional[GenericSlicerSettings] = Field(
        None,
        description="Generic options that will automatically be mapped to the correct config definition for each slicer. Slicer specific settings are applied first, then these are applied on top."
    )



class Material(BaseModel):
    """Material type information."""
    model_config = ConfigDict(extra='forbid')

    material: LimitedString = Field(..., description="The material type of the filament")
    default_max_dry_temperature: Optional[int] = None
    default_slicer_settings: Optional[SlicerSettings] = Field(
        None,
        description="The default slicer settings that should be used for this type of filament material. This will be used in any case where a filament does not specify its own \"slicer_settings\""
    )



class SlicerIDs(BaseModel):
    """Slicer-specific IDs for the filament."""

    prusaslicer: Optional[LimitedString] = None
    bambustudio: Optional[LimitedString] = None
    orcaslicer: Optional[LimitedString] = None
    cura: Optional[LimitedString] = None


class Filament(BaseModel):
    """Filament product line information."""
    model_config = ConfigDict(extra='forbid')

    name: LimitedString = Field(..., description="The manufacture's name for this filament")
    diameter_tolerance: float = Field(..., description="The diameter tolerance of the filament (in mm)")
    density: float = Field(default=1.24, description="The density of the filament (in g/cm³)")
    max_dry_temperature: Optional[int] = None
    data_sheet_url: Optional[LimitedString] = None
    safety_sheet_url: Optional[LimitedString] = None
    discontinued: Optional[bool] = None
    slicer_ids: Optional[SlicerIDs] = None
    slicer_settings: Optional[SlicerSettings] = Field(
        None,
        description="The slicer settings that should be used for this filament. This will override what is set in \"default_slicer_settings\""
    )



class ColorStandards(BaseModel):
    """Standard color system identifiers."""

    ral: Optional[LimitedString] = None
    ncs: Optional[LimitedString] = None
    pantone: Optional[LimitedString] = None
    bs: Optional[LimitedString] = None
    munsell: Optional[LimitedString] = None


class Traits(BaseModel):
    """Physical and environmental traits of the filament."""
    model_config = ConfigDict(extra='forbid')

    translucent: Optional[bool] = Field(None, description="Indicates that the filament is translucent")
    glow: Optional[bool] = Field(None, description="Indicates that the filament glows in the dark")
    matte: Optional[bool] = Field(None, description="Indicates that the filament has a matte finish")
    recycled: Optional[bool] = Field(None, description="Indicates that the filament was made of recycled materials")
    recyclable: Optional[bool] = Field(None, description="Indicates that the filament can be recycled")
    biodegradable: Optional[bool] = Field(None, description="Indicates if the filament will biodegrade")


class Variant(BaseModel):
    """Color variant of a filament."""
    model_config = ConfigDict(extra='forbid')

    color_name: LimitedString = Field(..., description="The manufacturer's name for this filament color")
    color_hex: Colors = Field(..., description="The official hex color code for this filament")
    hex_variants: Optional[List[Color]] = Field(
        None,
        description="Alternative hex color codes that this filament is known to report or be identified as (e.g., via NFC)"
    )
    discontinued: Optional[bool] = None
    color_standards: Optional[ColorStandards] = None
    traits: Optional[Traits] = None



class PurchaseLink(BaseModel):
    """Purchase link for a specific size."""

    store_id: LimitedString
    url: LimitedString
    affiliate: bool
    spool_refill: bool = Field(default=False, description="Indicates if this is a refill for a reusable spool")
    ships_from: Optional[Union[List[CountryCode], CountryCode]] = Field(
        None,
        description="A list of locations the shop ships from. Defining this here will override the definition from the shop."
    )
    ships_to: Optional[Union[List[CountryCode], CountryCode]] = Field(
        None,
        description="A list of locations the shop ships to. Defining this here will override the definition from the shop."
    )


class FilamentSize(BaseModel):
    """Size/weight variant of a filament color."""
    model_config = ConfigDict(extra='forbid')

    filament_weight: float = Field(default=1000, description="The weight of the filament alone (in grams)")
    diameter: float = Field(default=1.75, description="The diameter of the filament (in mm)")
    empty_spool_weight: Optional[float] = Field(None, description="The weight of a spool with no filament (in grams)")
    spool_core_diameter: Optional[float] = Field(None, description="The diameter of the core of the spool")
    ean: Optional[LimitedString] = None
    article_number: Optional[LimitedString] = None
    barcode_identifier: Optional[LimitedString] = None
    nfc_identifier: Optional[LimitedString] = None
    qr_identifier: Optional[LimitedString] = None
    discontinued: Optional[bool] = None
    purchase_links: Optional[List[PurchaseLink]] = Field(
        None,
        description="A list of places to purchase this filament"
    )


# RootModel for sizes array schema
class FilamentSizeArray(RootModel[List[FilamentSize]]):
    """Array of filament sizes - models the sizes.json schema."""
    root: List[FilamentSize] = Field(..., min_length=1)


def generate_json_schemas(output_dir: Optional[Path] = None) -> Dict[str, dict]:
    schemas = {
        'store_schema.json': Store.model_json_schema(mode='validation'),
        'brand_schema.json': Brand.model_json_schema(mode='validation'),
        'material_schema.json': Material.model_json_schema(mode='validation'),
        'filament_schema.json': Filament.model_json_schema(mode='validation'),
        'variant_schema.json': Variant.model_json_schema(mode='validation'),
        'sizes_schema.json': FilamentSizeArray.model_json_schema(mode='validation')
    }

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for schema_name, schema_def in schemas.items():
            output_file = output_dir / schema_name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schema_def, f, indent=4)
            print(f"Generated: {output_file}")

    return schemas


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Generate JSON schemas from Pydantic models.")
    parser.add_argument("--dry-run", action="store_true", help="Print schemas to console instead of writing to files")
    parser.add_argument('--generate', action='store_true', help="Generate JSON schemas to the specified directory")
    parser.add_argument('dir', nargs='?', default=None, help="Output directory for generated schemas")
    args = parser.parse_args()

    if args.dry_run:
        schemas = generate_json_schemas()
        for name, schema in schemas.items():
            print(f"Schema: {name}")
            print(json.dumps(schema, indent=4))
            print("\n")
    elif args.generate:
        output_dir = Path(__file__).parent if args.dir is None else Path(args.dir)
        generate_json_schemas(output_dir)
    else:
        parser.print_help()
        exit(1)