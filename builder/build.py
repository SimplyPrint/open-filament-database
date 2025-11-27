#!/usr/bin/env python3
"""
Main build script for the Open Filament Database.

This script crawls the data directory, normalizes all entities,
and exports them to multiple formats:
- JSON (all.json, all.ndjson, per-brand)
- SQLite database
- CSV files
- Static API (for GitHub Pages)

Usage:
    python -m builder.build [options]
    
Options:
    --output-dir DIR    Output directory (default: dist)
    --data-dir DIR      Data directory (default: data)
    --stores-dir DIR    Stores directory (default: stores)
    --version VERSION   Dataset version (default: auto-generated)
    --base-url URL      Base URL for static API (default: empty)
    --skip-json         Skip JSON export
    --skip-sqlite       Skip SQLite export
    --skip-csv          Skip CSV export
    --skip-api          Skip static API export
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from builder.crawler import crawl_data
from builder.exporters import export_json, export_sqlite, export_csv, export_api
from builder.utils import get_current_timestamp


def generate_version() -> str:
    """Generate a version string based on current date."""
    now = datetime.utcnow()
    return f"{now.year}.{now.month}.0"


def calculate_checksums(output_dir: str) -> dict:
    """Calculate SHA256 checksums for all generated files."""
    checksums = {}
    output_path = Path(output_dir)
    
    for file_path in output_path.rglob('*'):
        if file_path.is_file() and not file_path.name.endswith('.sha256'):
            rel_path = str(file_path.relative_to(output_path))
            with open(file_path, 'rb') as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            checksums[rel_path] = sha256
    
    return checksums


def write_manifest(output_dir: str, version: str, generated_at: str, checksums: dict):
    """Write the manifest file with all artifacts."""
    output_path = Path(output_dir)
    
    artifacts = []
    for rel_path, sha256 in sorted(checksums.items()):
        file_path = output_path / rel_path
        artifacts.append({
            "path": rel_path,
            "sha256": sha256,
            "size": file_path.stat().st_size
        })
    
    manifest = {
        "dataset_version": version,
        "generated_at": generated_at,
        "artifact_count": len(artifacts),
        "artifacts": artifacts
    }
    
    manifest_file = output_path / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Written: {manifest_file}")
    return manifest_file


def main():
    parser = argparse.ArgumentParser(
        description="Build the Open Filament Database exports"
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='dist',
        help='Output directory (default: dist)'
    )
    parser.add_argument(
        '--data-dir', '-d',
        default='data',
        help='Data directory (default: data)'
    )
    parser.add_argument(
        '--stores-dir', '-s',
        default='stores',
        help='Stores directory (default: stores)'
    )
    parser.add_argument(
        '--version', '-v',
        default=None,
        help='Dataset version (default: auto-generated from date)'
    )
    parser.add_argument(
        '--base-url', '-b',
        default='',
        help='Base URL for static API'
    )
    parser.add_argument(
        '--asset-url-mode',
        choices=['auto', 'absolute', 'relative'],
        default='auto',
        help='How to emit asset URLs in the Static API: auto (default), absolute, or relative'
    )
    parser.add_argument(
        '--skip-json',
        action='store_true',
        help='Skip JSON export'
    )
    parser.add_argument(
        '--skip-sqlite',
        action='store_true',
        help='Skip SQLite export'
    )
    parser.add_argument(
        '--skip-csv',
        action='store_true',
        help='Skip CSV export'
    )
    parser.add_argument(
        '--skip-api',
        action='store_true',
        help='Skip static API export'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / args.data_dir
    stores_dir = project_root / args.stores_dir
    output_dir = project_root / args.output_dir
    
    # Generate version if not provided
    version = args.version or generate_version()
    generated_at = get_current_timestamp()
    
    print("=" * 60)
    print("Open Filament Database Builder")
    print("=" * 60)
    print(f"Version: {version}")
    print(f"Generated at: {generated_at}")
    print(f"Data directory: {data_dir}")
    print(f"Stores directory: {stores_dir}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Crawl data
    print("\n[1/5] Crawling data...")
    db = crawl_data(str(data_dir), str(stores_dir))
    
    # Step 2: Export JSON
    if not args.skip_json:
        print("\n[2/5] Exporting JSON...")
        export_json(db, str(output_dir), version, generated_at)
    else:
        print("\n[2/5] Skipping JSON export")
    
    # Step 3: Export SQLite
    if not args.skip_sqlite:
        print("\n[3/5] Exporting SQLite...")
        export_sqlite(db, str(output_dir), version, generated_at)
    else:
        print("\n[3/5] Skipping SQLite export")
    
    # Step 4: Export CSV
    if not args.skip_csv:
        print("\n[4/5] Exporting CSV...")
        export_csv(db, str(output_dir), version, generated_at)
    else:
        print("\n[4/5] Skipping CSV export")
    
    # Step 5: Export Static API
    if not args.skip_api:
        print("\n[5/5] Exporting Static API...")
        export_api(
            db,
            str(output_dir),
            version,
            generated_at,
            args.base_url,
            data_dir=str(data_dir),
            stores_dir=str(stores_dir),
            asset_url_mode=args.asset_url_mode,
        )
    else:
        print("\n[5/5] Skipping Static API export")
    
    # Calculate checksums and write manifest
    print("\nGenerating checksums and manifest...")
    checksums = calculate_checksums(str(output_dir))
    write_manifest(str(output_dir), version, generated_at, checksums)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"\nOutput files are in: {output_dir}")
    print(f"Total artifacts: {len(checksums)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
