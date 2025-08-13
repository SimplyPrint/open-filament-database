import json
import os
from json import JSONDecodeError
from pathlib import Path
from typing import Union

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

PathLike = Union[str, os.PathLike[str]]

# Global variable that denotes the last json file that was read
# This is used to for json validation error messages
last_json_file_loaded = ""

illegal_characters = [
  "#","%","&","{","}","\\","<",
  ">","*","?","/","$","!","'",
  '"',":","@","+","`","|","="
] # TODO: Add emojis and alt codes
# This should at all times be the same as /webui/src/lib/server/helpers.ts:26

def get_json_from_file(json_path: PathLike):
    """
    Attempt to load JSON from the specified path
    :returns Loaded JSON as a dict or None if there is an error
    """
    try:
        global last_json_file_loaded
        last_json_file_loaded = json_path.__str__()
        with open(json_path, mode="r", encoding="utf8") as file:
            return json.load(file)
    except JSONDecodeError:
        print(f"Failed to import JSON from file: {json_path}")
    except OSError:
        print(f"Failed to open the provided JSON file: {json_path}")
    return None


def validate_json(json_data, schema) -> bool:
    """
    Validate the json data with the provided schema
    If valid, returns true.
    If not valid, returns false and emits an error message
    """
    try:
        validate(json_data, schema)
        return True
    except ValidationError as error:
        print(
            f"Failed to validate json. JSON path: {error.json_path}, Error: {error.message}, JSON file: {last_json_file_loaded}")
        return False


def validate_json_file(json_path: PathLike, schema: dict):
    return validate_json(get_json_from_file(json_path), schema)


def cleanse_folder_name(name: str) -> str:
    return name.replace("/", " ").strip()


STORE_SCHEMA = get_json_from_file("schemas/store_schema.json")
BRAND_SCHEMA = get_json_from_file("schemas/brand_schema.json")
MATERIAL_SCHEMA = get_json_from_file("schemas/material_schema.json")
FILAMENT_SCHEMA = get_json_from_file("schemas/filament_schema.json")
VARIANT_SCHEMA = get_json_from_file("schemas/variant_schema.json")
SIZE_SCHEMA = get_json_from_file("schemas/sizes_schema.json")

failed_validation = False


# -------------------------
# Validate against JSON schemas
# -------------------------

def validate_json_files():
    global failed_validation
    for _brand_dir in Path("./data").iterdir():
        if not _brand_dir.is_dir():
            continue

        # Validate brand.json
        brand_file = _brand_dir.joinpath("brand.json")
        if brand_file.exists():
            failed_validation |= not validate_json_file(brand_file, BRAND_SCHEMA)
            brandData = get_json_from_file(brand_file)
            logoName = brandData["logo"]

            if "/" in logoName:
                print("/ exists in logo path, only use file name.", brandData)
                failed_validation = True
            
            logoFile = _brand_dir.joinpath(logoName)

            if not logoFile.exists():
                print("Missing", logoFile)
                failed_validation = True
        else:
            print("Missing", brand_file)
            failed_validation = True

        for _material_dir in _brand_dir.iterdir():
            if not _material_dir.is_dir():
                continue

            # Validate material.json
            material_file = _material_dir.joinpath("material.json")
            if material_file.exists():
                failed_validation |= not validate_json_file(material_file, MATERIAL_SCHEMA)
            else:
                print("Missing", material_file)
                failed_validation = True

            for _filament_dir in _material_dir.iterdir():
                if not _filament_dir.is_dir():
                    continue

                # Validate filament.json
                filament_file = _filament_dir.joinpath("filament.json")
                if filament_file.exists():
                    failed_validation |= not validate_json_file(filament_file, FILAMENT_SCHEMA)
                else:
                    print("Missing", filament_file)
                    failed_validation = True

                for _variant_dir in _filament_dir.iterdir():
                    if not _variant_dir.is_dir():
                        continue

                    # Validate variant.json
                    variant_file = _variant_dir.joinpath("variant.json")
                    if variant_file.exists():
                        failed_validation |= not validate_json_file(variant_file, VARIANT_SCHEMA)
                    else:
                        print("Missing", variant_file)
                        failed_validation = True

                    # Validate sizes.json
                    sizes_file = _variant_dir.joinpath("sizes.json")
                    if sizes_file.exists():
                        failed_validation |= not validate_json_file(sizes_file, SIZE_SCHEMA)
                    else:
                        print("Missing", sizes_file)
                        failed_validation = True

    for _store_dir in Path("./stores").iterdir():
        if not _store_dir.is_dir():
            continue

        # Validate sizes.json
        store_file = _store_dir.joinpath("store.json")
        if store_file.exists():
            failed_validation |= not validate_json_file(store_file, STORE_SCHEMA)
        else:
            print("Missing", store_file)
            failed_validation = True


# -------------------------
# Validate folder names
# -------------------------

def validate_folder_names():
    global failed_validation
    for _brand_dir in Path("./data").iterdir():
        if not _brand_dir.is_dir():
            continue

        # Validate brand folder name
        brand_file = _brand_dir.joinpath("brand.json")
        if brand_file.exists():
            brand_data = get_json_from_file(brand_file)
            brand_name = cleanse_folder_name(brand_data.get("brand", ""))
            if _brand_dir.name != brand_name:
                is_error_illegal_char = False

                for char in brand_name:
                    if char in illegal_characters:
                        is_error_illegal_char = True

                if not is_error_illegal_char:
                    print("The name of the folder", _brand_dir,
                        f"does not match the value of 'brand' ({brand_name}) of", brand_file.name)
                    failed_validation = True

        for _material_dir in _brand_dir.iterdir():
            if not _material_dir.is_dir():
                continue

            # Validate material folder name
            material_file = _material_dir.joinpath("material.json")
            if material_file.exists():
                material_data = get_json_from_file(material_file)
                material_name = cleanse_folder_name(material_data.get("material", ""))
                if _material_dir.name != material_name:
                    print("The name of the folder", _material_dir,
                          f"does not match the value of 'material' ({material_name}) of", material_file.name)
                    failed_validation = True

            for _filament_dir in _material_dir.iterdir():
                if not _filament_dir.is_dir():
                    continue

                # Validate filament folder name
                filament_file = _filament_dir.joinpath("filament.json")
                if filament_file.exists():
                    filament_data = get_json_from_file(filament_file)
                    filament_name = cleanse_folder_name(filament_data.get("name", ""))
                    if _filament_dir.name != filament_name:
                        print("The name of the folder", _filament_dir,
                              f"does not match the value of 'name' ({filament_name}) of", filament_file.name)
                        failed_validation = True

                for _variant_dir in _filament_dir.iterdir():
                    if not _variant_dir.is_dir():
                        continue

                    # Validate variant folder name
                    variant_file = _variant_dir.joinpath("variant.json")
                    if variant_file.exists():
                        variant_data = get_json_from_file(variant_file)
                        variant_name = cleanse_folder_name(variant_data.get("color_name", ""))
                        if _variant_dir.name != variant_name:
                            print("The name of the folder", _variant_dir,
                                  f"does not match the value of 'color_name' ({variant_name}) of", variant_file.name)
                            failed_validation = True

    for _store_dir in Path("./stores").iterdir():
        if not _store_dir.is_dir():
            continue

        # Validate brand folder name
        store_file = _store_dir.joinpath("store.json")

        if store_file.exists():
            store_data = get_json_from_file(store_file)
            store_id = cleanse_folder_name(store_data.get("id", ""))
            if _store_dir.name != store_id:
                print("The name of the folder", _store_dir,
                    f"does not match the value of 'id' ({store_id}) of", brand_file.name)
                failed_validation = True

def validate_store_ids():
    global failed_validation

    valid_store_ids = []

    # Get the valid IDs
    for _store_file in Path("./stores").glob("*/store.json"):
        if _store_file.exists():
            store_data = get_json_from_file(_store_file)
            if "id" in store_data:
                valid_store_ids.append(store_data["id"])

    # Make sure referenced IDs in sizes.json files are valid
    for _sizes_file in Path("./data").glob("**/sizes.json"):
        sizes_data = get_json_from_file(_sizes_file)
        for size_idx, size in enumerate(sizes_data):
            for purchase_link_idx, purchase_link in enumerate(size.get("purchase_links", [])):
                if "store_id" in purchase_link:
                    if purchase_link["store_id"] not in valid_store_ids:
                        print(
                            f"'{purchase_link['store_id']}' is not a valid store ID. Found in {_sizes_file} at location $[{size_idx}].purchase_links[{purchase_link_idx}]")
                        failed_validation = True


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--json-files", action="store_true")
    parser.add_argument("--folder-names", action="store_true")
    parser.add_argument("--store-ids", action="store_true")

    args = parser.parse_args()
    if args.json_files:
        validate_json_files()

    if args.folder_names:
        validate_folder_names()

    if args.store_ids:
        validate_store_ids()

    if failed_validation:
        exit(-1)
