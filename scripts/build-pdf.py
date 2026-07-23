# -*- coding: utf-8 -*-
"""Build offline single-file handbooks from MkDocs nav + remaining docs pages.

Default pack outputs (via pack-offline-site.py / pack_all):
  dist/MOM产品文档-YYYYMMDD.pdf
  dist/MOM产品文档-YYYYMMDD.html
  dist/MOM产品文档-YYYYMMDD.md
"""
from __future__ import annotations

import base64
import html
import mimetypes
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DIST = ROOT / "dist"
BUILD = DIST / "_pdf_build"
MERMAID_DIR = BUILD / "mermaid"
TODAY = date.today().strftime("%Y%m%d")
ARTIFACT_STEM = f"MOM产品文档-{TODAY}"
PDF_NAME = f"{ARTIFACT_STEM}.pdf"
HTML_NAME = f"{ARTIFACT_STEM}.html"
MD_NAME = f"{ARTIFACT_STEM}.md"
MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.S)
FILE_URI_RE = re.compile(r"file:///[^\s\"'<>]+", re.I)
MMDC = shutil.which("mmdc") or shutil.which("mmdc.cmd")

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

MD = markdown.Markdown(
    extensions=[
        "admonition",
        "attr_list",
        "fenced_code",
        "tables",
        "sane_lists",
        "nl2br",
        "toc",
    ],
    extension_configs={"toc": {"permalink": False}},
)


def load_mkdocs_config() -> dict:
    raw = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    # mkdocs.yml embeds a Python slugify object; neutralize for safe_load
    raw = re.sub(
        r"slugify:\s*!!python/object/apply:pymdownx\.slugs\.slugify\s*\n"
        r"\s*kwds:\s*\n\s*case:\s*lower",
        "slugify: null",
        raw,
    )
    return yaml.safe_load(raw)


def walk_nav(node, trail: list[str] | None = None) -> list[tuple[list[str], str, str]]:
    """Return [(section_trail, title, rel_md_path), ...] in nav order."""
    trail = trail or []
    out: list[tuple[list[str], str, str]] = []
    if isinstance(node, list):
        for item in node:
            out.extend(walk_nav(item, trail))
        return out
    if isinstance(node, dict):
        for title, child in node.items():
            if isinstance(child, str):
                out.append((trail, title, child.replace("\\", "/")))
            else:
                out.extend(walk_nav(child, trail + [title]))
        return out
    return out


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", text, flags=re.UNICODE)
    s = re.sub(r"-{2,}", "-", s).strip("-").lower()
    return s or "section"


class MermaidBaker:
    """Collect Mermaid blocks, render to PNG via mmdc, then embed as images."""

    def __init__(self, out_dir: Path) -> None:
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: list[tuple[str, str]] = []  # (id, source)
        self.ok: dict[str, Path] = {}
        self.failed: list[str] = []
        self._n = 0

    def stash(self, text: str) -> str:
        def _repl(m: re.Match) -> str:
            self._n += 1
            mid = f"m{self._n:04d}"
            self.jobs.append((mid, m.group(1).strip()))
            return f"\n\n![图示](MERMAID:{mid})\n\n"

        return MERMAID_RE.sub(_repl, text)

    def _render_one(self, mid: str, source: str) -> tuple[str, Path | None, str]:
        mmd = self.out_dir / f"{mid}.mmd"
        png = self.out_dir / f"{mid}.png"
        mmd.write_text(source + "\n", encoding="utf-8")
        assert MMDC, "mmdc not found"
        try:
            proc = subprocess.run(
                [
                    MMDC,
                    "-i",
                    str(mmd),
                    "-o",
                    str(png),
                    "-b",
                    "white",
                    "-w",
                    "1400",
                    "-s",
                    "2",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return mid, None, "timeout"
        if proc.returncode != 0 or not png.exists():
            err = (proc.stderr or proc.stdout or "mmdc failed").strip()
            return mid, None, err[:300]
        return mid, png, ""

    def render_all(self, workers: int = 4) -> None:
        if not self.jobs:
            print("Mermaid diagrams: 0", flush=True)
            return
        if not MMDC:
            raise SystemExit(
                "mmdc not found. Install: npm i -g @mermaid-js/mermaid-cli"
            )
        total = len(self.jobs)
        print(f"Rendering {total} Mermaid diagrams via mmdc …", flush=True)
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = {
                pool.submit(self._render_one, mid, src): mid for mid, src in self.jobs
            }
            for fut in as_completed(futs):
                mid, png, err = fut.result()
                done += 1
                if png is None:
                    self.failed.append(mid)
                    print(f"  FAIL {mid}: {err}", file=sys.stderr, flush=True)
                else:
                    self.ok[mid] = png
                if done % 20 == 0 or done == total:
                    print(
                        f"  mermaid {done}/{total} "
                        f"(ok={len(self.ok)} fail={len(self.failed)})",
                        flush=True,
                    )
        if self.failed:
            print(
                f"WARN: {len(self.failed)} Mermaid diagram(s) failed; "
                "those stay as source fallback.",
                file=sys.stderr,
                flush=True,
            )

    def resolve_markdown(self, text: str) -> str:
        def _repl(m: re.Match) -> str:
            mid = m.group(1)
            png = self.ok.get(mid)
            if png and png.exists():
                return f"![图示]({png.resolve().as_uri()})"
            # fallback: keep source if render failed
            src = next((s for i, s in self.jobs if i == mid), "")
            body = html.escape(src)
            return (
                '\n\n<div class="mermaid-fallback">'
                f"<p><strong>图示渲染失败（{html.escape(mid)}）</strong></p>"
                f"<pre>{body}</pre></div>\n\n"
            )

        return re.sub(r"!\[图示\]\(MERMAID:([m\d]+)\)", _repl, text)


def preprocess_md(text: str, page_dir: Path, baker: MermaidBaker) -> str:
    text = text.replace("\r\n", "\n")
    text = baker.stash(text)

    # Rewrite local image paths to file URIs so Chrome can load them
    def _img(m: re.Match) -> str:
        alt, path = m.group(1), m.group(2)
        if path.startswith(("http://", "https://", "data:", "file:", "MERMAID:")):
            return m.group(0)
        img_path = (page_dir / path).resolve()
        if not img_path.exists():
            img_path = (DOCS / path).resolve()
        if img_path.exists():
            return f"![{alt}]({img_path.as_uri()})"
        return m.group(0)

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _img, text)
    return text


def md_to_html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def find_chrome() -> Path:
    for p in CHROME_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit("Chrome/Edge not found; cannot print PDF")


def collect_pages(cfg: dict) -> list[dict]:
    nav_pages = walk_nav(cfg["nav"])
    seen: set[str] = set()
    pages: list[dict] = []
    for trail, title, rel in nav_pages:
        path = DOCS / rel
        if not path.exists():
            print(f"WARN missing nav page: {rel}", file=sys.stderr)
            continue
        key = rel.replace("\\", "/")
        if key in seen:
            continue
        seen.add(key)
        pages.append(
            {
                "title": title,
                "rel": key,
                "path": path,
                "trail": trail,
                "kind": "nav",
                "anchor": "p-" + slugify("-".join(trail + [title, key])),
            }
        )

    # Remaining product docs (e.g. 维护与查询参考) not in nav
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(DOCS).as_posix()
        if rel in seen:
            continue
        # skip pure stubs that are English redirects if empty-ish? include all
        title = path.stem
        pages.append(
            {
                "title": title,
                "rel": rel,
                "path": path,
                "trail": ["附录", "未入侧栏页面"],
                "kind": "appendix",
                "anchor": "p-" + slugify(rel),
            }
        )
    return pages


COVER_HTML = """
<section class="cover">
  <div class="cover-inner">
    <p class="cover-eyebrow">MOM 制造运营管理系统</p>
    <h1>产品文档手册</h1>
    <p class="cover-sub">离线完整版 · 含封面、目录与全部文档正文</p>
    <p class="cover-meta">构建日期：{build_date}</p>
    <p class="cover-meta">站点：{site_url}</p>
  </div>
</section>
"""

CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
}
* { box-sizing: border-box; }
html, body {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1a1a1a;
}
a { color: #1a56db; text-decoration: none; }
.cover {
  page-break-after: always;
  min-height: 240mm;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.cover-inner { max-width: 140mm; }
.cover-eyebrow {
  letter-spacing: 0.2em;
  color: #4b5563;
  font-size: 11pt;
  margin-bottom: 18pt;
}
.cover h1 {
  font-size: 28pt;
  margin: 0 0 16pt;
  font-weight: 700;
}
.cover-sub { color: #374151; margin: 0 0 28pt; }
.cover-meta { color: #6b7280; margin: 4pt 0; font-size: 10pt; }
.toc {
  page-break-after: always;
}
.toc h1 { font-size: 18pt; margin-bottom: 12pt; }
.toc-list { list-style: none; padding: 0; margin: 0; }
.toc-list ul { list-style: none; padding-left: 14pt; margin: 2pt 0; }
.toc-list li { margin: 3pt 0; }
.toc-sec { font-weight: 700; margin-top: 8pt; color: #111827; }
.toc-page a { color: #1f2937; }
.doc {
  page-break-before: always;
}
.doc:first-of-type { page-break-before: auto; }
.doc-header {
  border-bottom: 1px solid #d1d5db;
  margin-bottom: 12pt;
  padding-bottom: 6pt;
}
.doc-trail {
  color: #6b7280;
  font-size: 9pt;
  margin: 0 0 4pt;
}
.doc-header h1 {
  font-size: 16pt;
  margin: 0;
}
.doc-rel {
  color: #9ca3af;
  font-size: 8pt;
  margin: 4pt 0 0;
}
.doc-body h1 { font-size: 14pt; }
.doc-body h2 { font-size: 12.5pt; margin-top: 14pt; }
.doc-body h3 { font-size: 11.5pt; margin-top: 12pt; }
.doc-body h4 { font-size: 10.5pt; }
.doc-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 8pt 0;
  font-size: 9pt;
}
.doc-body th, .doc-body td {
  border: 1px solid #d1d5db;
  padding: 4pt 6pt;
  vertical-align: top;
}
.doc-body th { background: #f3f4f6; }
.doc-body pre, .doc-body code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 8.5pt;
}
.doc-body pre {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 8pt;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
.doc-body blockquote {
  margin: 8pt 0;
  padding: 4pt 10pt;
  border-left: 3px solid #93c5fd;
  background: #f8fafc;
  color: #374151;
}
.admonition {
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  padding: 8pt 10pt;
  margin: 10pt 0;
  page-break-inside: avoid;
}
.admonition-title { font-weight: 700; margin-bottom: 4pt; }
.mermaid-fallback {
  border: 1px dashed #cbd5e1;
  background: #f8fafc;
  padding: 8pt;
  margin: 10pt 0;
}
.doc-body img.mermaid-img,
.doc-body img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 10pt auto;
  page-break-inside: avoid;
}
hr { border: none; border-top: 1px solid #e5e7eb; margin: 14pt 0; }
"""
PAGE_MARK_RE = re.compile(r"PDFPAGE:(\d{4})")


def build_toc_html(pages: list[dict]) -> str:
    lines = ['<nav class="toc"><h1>目录</h1><ul class="toc-list">']
    last_prefix: tuple[str, ...] = ()
    for p in pages:
        trail = tuple(p["trail"])
        if trail != last_prefix:
            # emit only newly entered trail segments
            for i in range(len(trail)):
                prefix = trail[: i + 1]
                if last_prefix[: i + 1] != prefix:
                    lines.append(
                        f'<li class="toc-sec">{" / ".join(prefix)}</li>'
                    )
            last_prefix = trail
        label = p["title"]
        lines.append(
            f'<li class="toc-page"><a href="#{p["anchor"]}">{html.escape(label)}</a></li>'
        )
    lines.append("</ul></nav>")
    return "\n".join(lines)


def build_book_html(cfg: dict, pages: list[dict], baker: MermaidBaker) -> str:
    site_name = cfg.get("site_name", "MOM 产品文档")
    site_url = cfg.get("site_url", "")

    prepared: list[tuple[dict, str]] = []
    print("Collecting Mermaid blocks …", flush=True)
    for i, p in enumerate(pages):
        raw = p["path"].read_text(encoding="utf-8")
        raw = preprocess_md(raw, p["path"].parent, baker)
        prepared.append((p, raw))
        if (i + 1) % 40 == 0:
            print(f"  scanned {i + 1}/{len(pages)} pages...", flush=True)

    baker.render_all(workers=4)

    parts: list[str] = [
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>",
        f"<title>{html.escape(site_name)}</title>",
        f"<style>{CSS}</style></head><body>",
        COVER_HTML.format(
            build_date=date.today().isoformat(),
            site_url=html.escape(site_url or ""),
        ),
        build_toc_html(pages),
    ]

    print("Building combined HTML …", flush=True)
    for i, (p, raw) in enumerate(prepared):
        raw = baker.resolve_markdown(raw)
        body = md_to_html(raw)
        # mark mermaid images for CSS targeting
        body = body.replace("<img alt=\"图示\"", '<img class="mermaid-img" alt="图示"')
        trail = " / ".join(p["trail"]) if p["trail"] else "首页"
        mark = f"PDFPAGE:{i:04d}"
        p["pdf_mark"] = mark
        parts.append(
            f'<article class="doc" id="{p["anchor"]}">'
            f'<header class="doc-header">'
            f'<p class="doc-trail">{html.escape(trail)}</p>'
            f'<h1>{html.escape(p["title"])}</h1>'
            f'<p class="doc-rel">{mark} · {html.escape(p["rel"])}</p>'
            f"</header>"
            f'<div class="doc-body">{body}</div>'
            f"</article>"
        )
        if (i + 1) % 40 == 0:
            print(f"  rendered {i + 1}/{len(pages)} pages...", flush=True)

    parts.append("</body></html>")
    return "\n".join(parts)


def chrome_print_pdf(chrome: Path, html_path: Path, pdf_path: Path) -> Path:
    # Chrome on Windows is unreliable with non-ASCII --print-to-pdf paths.
    tmp_pdf = BUILD / "handbook-print.pdf"
    if tmp_pdf.exists():
        tmp_pdf.unlink()
    html_uri = html_path.resolve().as_uri()
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--disable-extensions",
        "--allow-file-access-from-files",
        f"--print-to-pdf={tmp_pdf.resolve()}",
        html_uri,
    ]
    print("Printing via:", chrome.name, flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    if proc.returncode != 0 or not tmp_pdf.exists():
        sys.stderr.write(proc.stdout or "")
        sys.stderr.write(proc.stderr or "")
        raise SystemExit(f"Chrome print failed (code={proc.returncode})")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        try:
            pdf_path.unlink()
        except PermissionError:
            from datetime import datetime

            pdf_path = pdf_path.with_name(
                f"{pdf_path.stem}-{datetime.now().strftime('%H%M%S')}{pdf_path.suffix}"
            )
            print(f"WARN: target locked, writing {pdf_path.name}", flush=True)
    shutil.move(str(tmp_pdf), str(pdf_path))
    return pdf_path


def locate_mark_pages(pdf_path: Path) -> dict[int, int]:
    """Map page list index -> 0-based PDF page number via PDFPAGE:NNNN markers."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    found: dict[int, int] = {}
    for pdf_i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for m in PAGE_MARK_RE.finditer(text):
            idx = int(m.group(1))
            if idx not in found:
                found[idx] = pdf_i
    return found


def recompute_outline_counts(writer, open_depth: int = 1) -> None:
    """Fix /Count on outline nodes so readers expand multi-level bookmarks.

    PDF viewers treat Count=0 as \"no children\" even if /First exists.
    Keep the top ``open_depth`` levels expanded (positive Count).
    """
    from pypdf.generic import NameObject, NumberObject

    root = writer._root_object
    if NameObject("/Outlines") not in root:
        return
    outlines = root[NameObject("/Outlines")].get_object()
    if NameObject("/First") not in outlines:
        return

    def walk(node, depth: int) -> int:
        if NameObject("/First") not in node:
            node[NameObject("/Count")] = NumberObject(0)
            return 0
        total = 0
        child_ref = node[NameObject("/First")]
        while True:
            child = child_ref.get_object()
            total += 1 + walk(child, depth + 1)
            if NameObject("/Next") not in child:
                break
            child_ref = child[NameObject("/Next")]
        node[NameObject("/Count")] = NumberObject(
            total if depth < open_depth else -total
        )
        return total

    top_total = 0
    ref = outlines[NameObject("/First")]
    while True:
        node = ref.get_object()
        top_total += 1 + walk(node, 0)
        if NameObject("/Next") not in node:
            break
        ref = node[NameObject("/Next")]
    outlines[NameObject("/Count")] = NumberObject(top_total)


def embed_nav_outline(
    pdf_path: Path, pages: list[dict], site_name: str
) -> Path:
    """Rewrite PDF with multi-level bookmarks matching MkDocs nav trails."""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject

    print("Building PDF outline (bookmarks) …", flush=True)
    mark_pages = locate_mark_pages(pdf_path)
    missing = [i for i in range(len(pages)) if i not in mark_pages]
    if missing:
        print(
            f"WARN: {len(missing)}/{len(pages)} page markers not found in PDF text; "
            "those bookmarks will be skipped.",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(f"  located all {len(pages)} page markers", flush=True)

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.append(reader)
    # Chrome PDF has no outline; clear any residual before rebuilding
    if NameObject("/Outlines") in writer._root_object:
        del writer._root_object[NameObject("/Outlines")]
    writer.add_metadata({"/Title": site_name, "/Creator": "MOM build-pdf"})

    # cache: trail tuple -> outline item; () is root (parent=None)
    cache: dict[tuple[str, ...], object] = {(): None}
    outline_n = 0
    for i, p in enumerate(pages):
        pdf_page = mark_pages.get(i)
        if pdf_page is None:
            continue
        trail = list(p["trail"])
        for depth in range(len(trail)):
            key = tuple(trail[: depth + 1])
            if key in cache:
                continue
            parent = cache[tuple(trail[:depth])]
            cache[key] = writer.add_outline_item(
                trail[depth],
                pdf_page,
                parent=parent,
                is_open=True,
            )
            outline_n += 1
        parent = cache[tuple(trail)]
        writer.add_outline_item(p["title"], pdf_page, parent=parent, is_open=True)
        outline_n += 1

    recompute_outline_counts(writer, open_depth=1)

    out_tmp = BUILD / "handbook-outlined.pdf"
    with out_tmp.open("wb") as f:
        writer.write(f)

    final = pdf_path
    if final.exists():
        try:
            final.unlink()
        except PermissionError:
            from datetime import datetime

            final = final.with_name(
                f"{final.stem}-outline-{datetime.now().strftime('%H%M%S')}{final.suffix}"
            )
            print(f"WARN: target locked, writing {final.name}", flush=True)
    shutil.move(str(out_tmp), str(final))
    print(f"  outline entries={outline_n}", flush=True)
    return final


def _safe_dist_path(path: Path) -> Path:
    if not path.exists():
        return path
    try:
        path.unlink()
        return path
    except PermissionError:
        from datetime import datetime

        alt = path.with_name(
            f"{path.stem}-{datetime.now().strftime('%H%M%S')}{path.suffix}"
        )
        print(f"WARN: target locked, writing {alt.name}", flush=True)
        return alt


def file_uri_to_path(uri: str) -> Path | None:
    try:
        parsed = urlparse(uri)
        if parsed.scheme != "file":
            return None
        path = Path(url2pathname(unquote(parsed.path)))
        # url2pathname on Windows may yield \D:\... — normalize
        if re.match(r"^[\\/][A-Za-z]:[\\/]", str(path)):
            path = Path(str(path)[1:])
        return path if path.exists() else None
    except Exception:
        return None


def embed_file_uris_as_data(html_text: str) -> str:
    """Replace file:// image/object URIs with base64 data URIs for portability."""

    def _repl(m: re.Match) -> str:
        uri = m.group(0).rstrip(").,;]")
        path = file_uri_to_path(uri)
        if path is None:
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{data}"

    return FILE_URI_RE.sub(_repl, html_text)


def rewrite_md_images_to_docs_rel(text: str, page_dir: Path) -> str:
    def _img(m: re.Match) -> str:
        alt, path = m.group(1), m.group(2)
        if path.startswith(("http://", "https://", "data:", "#")):
            return m.group(0)
        img_path = (page_dir / path).resolve()
        if not img_path.exists():
            img_path = (DOCS / path).resolve()
        if img_path.exists() and (
            DOCS in img_path.parents or img_path.parent == DOCS
        ):
            try:
                rel = img_path.relative_to(ROOT).as_posix()
                return f"![{alt}]({rel})"
            except ValueError:
                pass
        return m.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _img, text)


def build_book_md(cfg: dict, pages: list[dict]) -> str:
    site_name = cfg.get("site_name", "MOM 产品文档")
    site_url = cfg.get("site_url", "")
    lines: list[str] = [
        f"# {site_name}",
        "",
        f"> 离线单文件 Markdown · 构建日期：{date.today().isoformat()}",
        f"> 站点：{site_url}" if site_url else "",
        "",
        "按 `mkdocs.yml` 导航顺序合并；未入侧栏页面在「附录」。",
        "正文中的本地图片路径相对于仓库根目录（如 `docs/...`）；Mermaid 保留源码块。",
        "",
        "## 目录",
        "",
    ]
    lines = [ln for ln in lines if ln is not None]

    for p in pages:
        label = " / ".join([*p["trail"], p["title"]]) if p["trail"] else p["title"]
        lines.append(f"- [{label}](#{p['anchor']})")
    lines.append("")

    for p in pages:
        raw = p["path"].read_text(encoding="utf-8").replace("\r\n", "\n")
        raw = rewrite_md_images_to_docs_rel(raw, p["path"].parent)
        heading = " / ".join([*p["trail"], p["title"]]) if p["trail"] else p["title"]
        lines.extend(
            [
                "",
                "---",
                "",
                f'<a id="{p["anchor"]}"></a>',
                "",
                f"# {heading}",
                "",
                f"`{p['rel']}`",
                "",
                raw.strip(),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def clear_old_artifacts(targets: set[str]) -> None:
    patterns: list[str] = []
    if "pdf" in targets:
        patterns.append("MOM产品文档-*.pdf")
    if "html" in targets:
        patterns.append("MOM产品文档-*.html")
    if "md" in targets:
        patterns.append("MOM产品文档-*.md")
    patterns.append("MOM产品文档-离线-*.zip")
    for pat in patterns:
        for old in DIST.glob(pat):
            try:
                old.unlink()
            except PermissionError:
                print(f"WARN: cannot delete locked file: {old.name}", flush=True)


def pack_all(targets: set[str] | None = None) -> dict[str, Path]:
    """Build offline artifacts. Default targets: pdf + html + md."""
    targets = targets or {"pdf", "html", "md"}
    unknown = targets - {"pdf", "html", "md"}
    if unknown:
        raise SystemExit(f"Unknown pack targets: {sorted(unknown)}")

    DIST.mkdir(exist_ok=True)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    clear_old_artifacts(targets)

    print("Loading mkdocs.yml …", flush=True)
    cfg = load_mkdocs_config()
    pages = collect_pages(cfg)
    nav_n = sum(1 for p in pages if p["kind"] == "nav")
    app_n = sum(1 for p in pages if p["kind"] == "appendix")
    print(f"Pages: nav={nav_n}, appendix={app_n}, total={len(pages)}", flush=True)

    outputs: dict[str, Path] = {}
    site_name = cfg.get("site_name", "MOM 产品文档")

    need_html_pipeline = bool(targets & {"pdf", "html"})
    book = ""
    html_path = BUILD / "book.html"
    baker: MermaidBaker | None = None

    if need_html_pipeline:
        baker = MermaidBaker(MERMAID_DIR)
        book = build_book_html(cfg, pages, baker)
        html_path.write_text(book, encoding="utf-8")
        print(
            f"HTML workcopy size_mb={(html_path.stat().st_size / 1024 / 1024):.2f}",
            flush=True,
        )
        print(
            f"Mermaid embedded: ok={len(baker.ok)} fail={len(baker.failed)}",
            flush=True,
        )

    if "html" in targets:
        print("Writing standalone HTML …", flush=True)
        standalone = embed_file_uris_as_data(book)
        # Prefer browser reading (not print): slightly looser page-break CSS already ok
        html_out = _safe_dist_path(DIST / HTML_NAME)
        html_out.write_text(standalone, encoding="utf-8")
        outputs["html"] = html_out
        print(
            f"  {html_out.name}  size_mb={html_out.stat().st_size / 1024 / 1024:.2f}",
            flush=True,
        )

    if "pdf" in targets:
        pdf_path = _safe_dist_path(DIST / PDF_NAME)
        chrome = find_chrome()
        pdf_path = chrome_print_pdf(chrome, html_path, pdf_path)
        pdf_path = embed_nav_outline(pdf_path, pages, site_name)
        outputs["pdf"] = pdf_path
        print(
            f"  {pdf_path.name}  size_mb={pdf_path.stat().st_size / 1024 / 1024:.2f}",
            flush=True,
        )

    if "md" in targets:
        print("Writing standalone Markdown …", flush=True)
        md_text = build_book_md(cfg, pages)
        md_out = _safe_dist_path(DIST / MD_NAME)
        md_out.write_text(md_text, encoding="utf-8")
        outputs["md"] = md_out
        print(
            f"  {md_out.name}  size_mb={md_out.stat().st_size / 1024 / 1024:.2f}",
            flush=True,
        )

    print("ok")
    for kind, path in outputs.items():
        print(f"{kind}: {path}")
    return outputs


def main() -> None:
    # CLI: python scripts/build-pdf.py [pdf|html|md]...
    # No args → all three (same as pack-offline-site.py)
    args = [a.lower() for a in sys.argv[1:] if not a.startswith("-")]
    targets = set(args) if args else None
    pack_all(targets)


if __name__ == "__main__":
    main()
