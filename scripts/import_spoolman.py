import os
import json
import glob
import subprocess
from collections import defaultdict

SPOOLMANDIR = "SpoolmanDB"
SPOOLMAN_REPO = "https://github.com/Donkie/SpoolmanDB.git"
SPOOLMAN_FILAMENTS_PATH = os.path.join(SPOOLMANDIR, "filaments")
OPEN_DB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

illegal_characters = [
  "#","%","&","{","}","\\","<",
  ">","*","?","/","$","!","'",
  '"',":","@","`","|","="
] # TODO: Add emojis and alt codes
# This should at all times be the same as /data_validator.py

def slugify(name):
    tempName = name

    for char in illegal_characters:
        tempName = tempName.replace(char, "").rstrip()
    
    return tempName

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def update_or_clone_repo():
    if not os.path.isdir(SPOOLMANDIR):
        print("Cloning SpoolmanDB repository...")
        subprocess.check_call(["git", "clone", SPOOLMAN_REPO, SPOOLMANDIR])
    else:
        print("Updating SpoolmanDB repository...")
        subprocess.check_call(["git", "-C", SPOOLMANDIR, "pull"])

def main():
    update_or_clone_repo()
    filament_files = glob.glob(os.path.join(SPOOLMAN_FILAMENTS_PATH, "*.json"))

    for file_path in filament_files:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        manufacturer = data.get("manufacturer", "Unknown")
        filaments = data.get("filaments", [])

        mfg_dir = os.path.join(OPEN_DB_ROOT, slugify(manufacturer))
        ensure_dir(mfg_dir)
        write_json(os.path.join(mfg_dir, "brand.json"), {
            "brand": manufacturer,
            "website": "",
            "origin": ""
        })

        material_map = defaultdict(list)
        for f in filaments:
            material_map[f["material"]].append(f)

        for material, material_filaments in material_map.items():
            mat_dir = os.path.join(mfg_dir, slugify(material))
            ensure_dir(mat_dir)
            write_json(os.path.join(mat_dir, "material.json"), {
                "material": material
            })

            # Group by filament name (not including material!)
            filament_map = defaultdict(list)
            for f in material_filaments:
                base_name = f["name"]
                base_name = base_name.replace("{color_name}", "").replace(" {color_name}", "")
                if base_name == "":
                    base_name = material
                filament_map[base_name].append(f)

            for filament_name, variants in filament_map.items():
                fil_dir = os.path.join(mat_dir, slugify(filament_name))
                ensure_dir(fil_dir)
                density = 1.24
                for f in material_filaments:
                    if f["name"] == filament_name:
                        density = f["density"]
                
                write_json(os.path.join(fil_dir, "filament.json"), {
                    "filament": filament_name,
                    "diameter_tolerance": 0.02, # We need a way to get this... It's not present in the DB sadly
                    "density": density
                })

                for v in variants:
                    for color in v["colors"]:
                        color_name = color["name"]
                        color_dir = os.path.join(fil_dir, slugify(color_name))
                        ensure_dir(color_dir)

                        traits_json = {
                            "translucent": color.get("translucent") or v.get("translucent"),
                            "glow": color.get("glow") or v.get("glow"),
                        }

                        # Write variant.json
                        variant_json = {
                            "color_name": color_name,
                            "color_hex": f"#{color.get("hex") or (color.get("hexes")[0] if "hexes" in color else "")}",
                        }

                        for k, tv in traits_json.items():
                            if tv:
                                if not variant_json.get("traits"):
                                    variant_json["traits"] = {}

                                variant_json["traits"][k] = tv

                        write_json(os.path.join(color_dir, "variant.json"), variant_json)

                        # Write sizes.json: all (diameter, weight, spool_weight, spool_type) combos
                        sizes = []
                        for d in v.get("diameters", []):
                            for w in v.get("weights", []):
                                sizes.append({
                                    "filament_weight": w.get("weight"),
                                    "diameter": d,
                                    "empty_spool_weight": w.get("spool_weight"),
                                })
                        write_json(os.path.join(color_dir, "sizes.json"), sizes)
    print("Import complete! Check your data/ directory.")

if __name__ == "__main__":
    main()