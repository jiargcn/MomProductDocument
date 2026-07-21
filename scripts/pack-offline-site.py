# -*- coding: utf-8 -*-
"""Build offline zip of the MkDocs site/ output."""
from __future__ import annotations

import shutil
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIST = ROOT / "dist"
STAGE_NAME = "MOM产品文档"
TODAY = date.today().strftime("%Y%m%d")
ZIP_NAME = f"MOM产品文档-离线-{TODAY}.zip"

README = f"""MOM 产品文档 — 离线包
====================
构建日期：{date.today().isoformat()}
内容：MkDocs 静态站点（解压后即可本地浏览）

推荐打开方式（搜索/导航最完整）
--------------------------------
1. 解压本 zip
2. 进入「{STAGE_NAME}」目录
3. 双击「启动本地预览.bat」，或在该目录执行：
   python -m http.server 8000
4. 浏览器打开 http://127.0.0.1:8000/

也可直接双击 index.html
------------------------
多数页面可打开，但 Material 主题的搜索、部分相对链接在 file:// 下可能异常。
若侧栏/搜索异常，请改用上面的本地服务方式。

说明
----
本包为静态 HTML，不需要安装 MkDocs。
正式文档以仓库 docs/ 源稿为准；本包便于分享只读浏览。
"""

BAT = r"""@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo Starting local preview: http://127.0.0.1:8000/
echo Open that URL in your browser. Press Ctrl+C to stop.
echo.
python -m http.server 8000
if errorlevel 1 (
  echo.
  echo Python not found. You can still try opening index.html directly.
  pause
)
"""


def main() -> None:
    if not SITE.exists():
        raise SystemExit("site/ missing; run `mkdocs build` first")

    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("*.zip"):
        old.unlink()

    stage = DIST / "_stage"
    if stage.exists():
        shutil.rmtree(stage)
    root = stage / STAGE_NAME
    shutil.copytree(SITE, root)
    (root / "离线打开说明.txt").write_text(README, encoding="utf-8")
    (root / "启动本地预览.bat").write_text(BAT, encoding="ascii")

    zip_path = DIST / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in root.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(stage).as_posix())

    shutil.rmtree(stage)
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(zip_path)
    print(f"size_mb={size_mb:.2f}")
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        print(f"entries={len(names)}")
        for n in names[:6]:
            print(f"  {n}")
        print("has_readme=", any(n.endswith("离线打开说明.txt") for n in names))
        print("has_index=", f"{STAGE_NAME}/index.html" in names)


if __name__ == "__main__":
    main()
