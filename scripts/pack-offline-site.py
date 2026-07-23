# -*- coding: utf-8 -*-
"""Offline pack entrypoint — builds PDF + HTML + MD single-file handbooks.

Default (no args): all three artifacts under dist/
  MOM产品文档-YYYYMMDD.pdf
  MOM产品文档-YYYYMMDD.html
  MOM产品文档-YYYYMMDD.md

Optional args to build a subset, e.g.:
  python scripts/pack-offline-site.py html md
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    # Delegate to build-pdf.pack_all via its __main__ (argv targets preserved)
    runpy.run_path(str(Path(__file__).with_name("build-pdf.py")), run_name="__main__")
