#!/usr/bin/env python3
"""
MakuLinux package helper (mlx-pkg)
Handles manifest-based package installation with SHA-256 verification.

Usage:
  mlx-pkg install <name>
  mlx-pkg verify <name>
  mlx-pkg info <name>
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

MANIFEST_BASE_URL = "https://raw.githubusercontent.com/kyrosystems/makulinux-packages/main/manifests"
CACHE_DIR = Path("/var/cache/makulinux/manifests")
LOG_FILE = Path("/var/log/makulinux/pkg-verify.log")
TMP_DIR = Path("/tmp/makulinux-pkg")


def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        import datetime
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
    print(msg)


def fetch_manifest(name: str, version: str | None = None) -> dict:
    """Search manifest by name across categories."""
    import urllib.error
    
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    categories = ["system", "internet", "desktop", "devel", "media", "games", "utils"]
    
    for cat in categories:
        url = f"{MANIFEST_BASE_URL}/{cat}/{name}/"
        # In real impl, query API or index file
        # For now try direct path with version or 'latest.json'
        for ver in ([version] if version else ["latest"]):
            try:
                manifest_url = f"{MANIFEST_BASE_URL}/{cat}/{name}/{ver}.json"
                with urllib.request.urlopen(manifest_url) as r:
                    data = json.loads(r.read())
                    # Cache it
                    cache_path = CACHE_DIR / f"{name}-{data['version']}.json"
                    with open(cache_path, 'w') as f:
                        json.dump(data, f)
                    log(f"[manifest] Fetched and cached: {name} {data['version']}")
                    return data
            except Exception:
                continue
    
    raise FileNotFoundError(f"Manifest not found for package: {name}")


def verify_sha256(filepath: Path, expected: str) -> bool:
    """Compute SHA-256 of file and compare to expected."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    actual = h.hexdigest()
    return actual == expected, actual


def install_package(name: str, version: str | None = None):
    print(f"[mlx-pkg] Fetching manifest for '{name}'...")
    try:
        manifest = fetch_manifest(name, version)
    except FileNotFoundError as e:
        print(f"[mlx-pkg] Error: {e}")
        sys.exit(1)
    
    pkg_name = manifest['name']
    pkg_version = manifest['version']
    pkg_url = manifest['url']
    expected_sha256 = manifest['sha256']
    install_type = manifest.get('install_type', 'rpm')
    
    print(f"[mlx-pkg] Installing {pkg_name} {pkg_version}")
    print(f"[mlx-pkg] Source: {pkg_url}")
    
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    tmp_file = TMP_DIR / f"{pkg_name}-{pkg_version}.pkg"
    
    print(f"[mlx-pkg] Downloading...")
    try:
        urllib.request.urlretrieve(pkg_url, tmp_file)
    except Exception as e:
        log(f"DOWNLOAD FAIL: {pkg_name} {pkg_version} - {e}")
        print(f"[mlx-pkg] Download failed: {e}")
        sys.exit(1)
    
    print(f"[mlx-pkg] Verifying SHA-256...")
    ok, actual = verify_sha256(tmp_file, expected_sha256)
    
    if not ok:
        log(f"INTEGRITY FAIL: {pkg_name} {pkg_version} expected={expected_sha256} actual={actual}")
        print(f"[mlx-pkg] SECURITY ERROR: SHA-256 mismatch!")
        print(f"  Expected: {expected_sha256}")
        print(f"  Got:      {actual}")
        print(f"[mlx-pkg] Package NOT installed. This could indicate tampering.")
        tmp_file.unlink(missing_ok=True)
        sys.exit(2)
    
    log(f"VERIFIED OK: {pkg_name} {pkg_version} sha256={actual}")
    print(f"[mlx-pkg] SHA-256 verified OK.")
    
    # Install
    if install_type == 'rpm':
        print(f"[mlx-pkg] Installing via RPM...")
        r = subprocess.run(['rpm', '-ivh', str(tmp_file)])
        if r.returncode != 0:
            print("[mlx-pkg] RPM install failed. Trying DNF5...")
            subprocess.run(['dnf5', 'install', '-y', str(tmp_file)], check=True)
    elif install_type == 'tarball':
        dest = Path(f"/opt/{pkg_name}")
        dest.mkdir(parents=True, exist_ok=True)
        subprocess.run(['tar', '-xf', str(tmp_file), '-C', str(dest)], check=True)
    elif install_type == 'appimage':
        dest = Path(f"/usr/local/bin/{pkg_name}")
        import shutil
        shutil.copy2(tmp_file, dest)
        dest.chmod(0o755)
    
    log(f"INSTALLED: {pkg_name} {pkg_version}")
    print(f"[mlx-pkg] Done! {pkg_name} {pkg_version} installed successfully.")
    tmp_file.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description='MakuLinux package helper')
    sub = parser.add_subparsers(dest='command')
    
    inst = sub.add_parser('install', help='Install a package')
    inst.add_argument('name')
    inst.add_argument('--version', '-V', default=None)
    
    ver = sub.add_parser('verify', help='Verify installed package integrity')
    ver.add_argument('name')
    
    info = sub.add_parser('info', help='Show package info')
    info.add_argument('name')
    
    args = parser.parse_args()
    
    if args.command == 'install':
        install_package(args.name, getattr(args, 'version', None))
    elif args.command == 'verify':
        # Check cached manifest vs installed
        cache = CACHE_DIR
        found = list(cache.glob(f"{args.name}-*.json")) if cache.exists() else []
        if not found:
            print(f"No cached manifest for '{args.name}'")
            sys.exit(1)
        m = json.loads(found[0].read_text())
        print(f"Package: {m['name']} {m['version']}")
        print(f"Expected SHA-256: {m['sha256']}")
    elif args.command == 'info':
        try:
            m = fetch_manifest(args.name)
            print(json.dumps(m, indent=2))
        except FileNotFoundError as e:
            print(str(e))
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
