import json
import os

# Load the JSON mapping file
_json_path = os.path.join(os.path.dirname(__file__), 'open_print_tag.json')
with open(_json_path, 'r', encoding='utf-8') as f:
    _data = json.load(f)

# Expose maps
TRAITS_MAP = _data.get('tags', {})
CERTIFICATIONS_MAP = _data.get('certifications', {})
MATERIAL_TYPES_MAP = _data.get('material_types', {})
MATERIAL_CLASS_MAP = _data.get('material_class', {})

# Reverse maps (ID -> Name) if needed
TRAITS_ID_MAP = {v: k for k, v in TRAITS_MAP.items()}
CERTIFICATIONS_ID_MAP = {v: k for k, v in CERTIFICATIONS_MAP.items()}
MATERIAL_TYPES_ID_MAP = {v: k for k, v in MATERIAL_TYPES_MAP.items()}
MATERIAL_CLASS_ID_MAP = {v: k for k, v in MATERIAL_CLASS_MAP.items()}
