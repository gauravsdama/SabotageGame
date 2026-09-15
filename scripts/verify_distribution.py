#!/usr/bin/env python3
"""Verify built archives contain the game source and exclude local data."""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

dist = Path(__file__).resolve().parents[1] / "dist"
archives = sorted(dist.glob("*"))
if not archives:
    raise SystemExit("No distribution archives found; run `uv build` first.")

for archive in archives:
    if archive.suffix == ".whl":
        with zipfile.ZipFile(archive) as package:
            names = package.namelist()
    elif archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:gz") as package:
            names = package.getnames()
    else:
        continue
    required = {"sabotageGame.py", "LICENSE"}
    if archive.name.endswith(".tar.gz"):
        required.add("README.md")
    missing = {item for item in required if not any(name.endswith(item) for name in names)}
    blocked = [name for name in names if "/.env" in name]
    if missing or blocked:
        raise SystemExit(f"{archive.name}: missing={sorted(missing)} blocked={blocked}")
    print(f"Verified {archive.name}: {len(names)} members")
