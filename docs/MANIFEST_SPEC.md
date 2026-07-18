# MakuLinux Package Manifest Specification

Version: 1.0

## File Location

```
manifests/<category>/<package-name>/<version>.json
```

## Required Fields

```json
{
  "schema_version": 1,
  "name": "firefox",
  "version": "126.0",
  "release": 1,
  "category": "internet",
  "summary": "Mozilla Firefox web browser",
  "license": "MPL-2.0",
  "url": "https://download-installer.cdn.mozilla.net/pub/firefox/releases/126.0/linux-x86_64/en-US/firefox-126.0.tar.bz2",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "size_bytes": 82345678,
  "architecture": "x86_64",
  "dependencies": [
    "gtk3",
    "dbus",
    "libX11"
  ],
  "install_type": "rpm",
  "maintainer": "pon4ikisdonut@gmail.com",
  "homepage": "https://www.mozilla.org/firefox/",
  "source_url": "https://hg.mozilla.org/releases/mozilla-release"
}
```

## Optional Fields

```json
{
  "description": "Full multi-line description of the package.",
  "tags": ["browser", "web", "internet"],
  "conflicts": ["chromium"],
  "provides": ["web-browser"],
  "replaces": [],
  "post_install_script": "https://pkg.kyroos.pp.ua/scripts/firefox-post.sh",
  "post_install_script_sha256": "abc123..."
}
```

## Install Types

- `rpm` — standard RPM package
- `tarball` — extract to `/opt/<name>` or custom path
- `appimage` — AppImage, placed in `/usr/local/bin`
- `flatpak` — Flatpak ref (url field is the Flatpak ref)

## SHA-256 Verification Flow

1. DNF5 plugin (or `mlx-pkg` helper) downloads manifest from this repo
2. `sha256` is cached in `/var/cache/makulinux/manifests/<name>-<version>.json`
3. Package is downloaded to `/tmp/makulinux-pkg/`
4. SHA-256 of downloaded file is computed
5. If hashes match → install proceeds
6. If hashes differ → installation aborted, error logged to `/var/log/makulinux/pkg-verify.log`
