# MakuLinux Package Repository

> Manifest-based package repository for MakuLinux — winget-like structure with SHA-256 verification

[![CI](https://github.com/kyrosystems/makulinux-packages/actions/workflows/validate.yml/badge.svg)](https://github.com/kyrosystems/makulinux-packages/actions/workflows/validate.yml)

Packages are **not stored here**. Only manifests with metadata and download URLs.

The package manager downloads the actual package from the URL in the manifest, then **verifies the SHA-256 hash** before installing.

## Manifest Format

See [MANIFEST_SPEC.md](docs/MANIFEST_SPEC.md) for the full specification.

## Contributing a Package

1. Fork this repo
2. Create `manifests/<category>/<name>/<version>.json`
3. Fill in all required fields including exact SHA-256
4. Open a Pull Request
5. GitHub Actions will automatically:
   - Validate manifest schema
   - Download the package and verify SHA-256
   - Scan with ClamAV for malware
   - Check VirusTotal (if API key configured)
6. A maintainer reviews and approves

## Directory Structure

```
manifests/
  system/
    bash/
      5.2.21.json
  desktop/
    firefox/
      126.0.json
  devel/
    git/
      2.45.1.json
docs/
  MANIFEST_SPEC.md
.github/
  workflows/
    validate.yml
```
