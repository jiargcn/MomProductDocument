# -*- coding: utf-8 -*-
"""Find and fix GFM tables whose separator column count != header column count."""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SEP_CELL = re.compile(r"^:?-{3,}:?$")


def split_row(line: str) -> list[str] | None:
    s = line.strip()
    if not s.startswith("|"):
        return None
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_sep_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(SEP_CELL.match(c.replace(" ", "")) for c in cells if c is not None)


def scan(path: Path) -> list[tuple[int, int, int, str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[tuple[int, int, int, str, str]] = []
    i = 0
    while i < len(lines) - 1:
        cells = split_row(lines[i])
        sep = split_row(lines[i + 1])
        if cells is None or sep is None or not is_sep_row(sep):
            i += 1
            continue
        if len(cells) != len(sep):
            out.append((i + 1, len(cells), len(sep), lines[i], lines[i + 1]))
        i += 2
    return out


def fix_file(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    fixed = 0
    i = 0
    while i < len(lines) - 1:
        cells = split_row(lines[i])
        sep = split_row(lines[i + 1])
        if cells is None or sep is None or not is_sep_row(sep):
            i += 1
            continue
        width = len(cells)
        if len(sep) != width:
            lines[i + 1] = "| " + " | ".join("---" for _ in cells) + " |"
            fixed += 1
        # also pad/truncate? only fix separator; body rows reported separately
        i += 2
    if fixed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return fixed


def scan_body_mismatches(path: Path) -> list[tuple[int, int, int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[tuple[int, int, int, str]] = []
    i = 0
    while i < len(lines) - 1:
        cells = split_row(lines[i])
        sep = split_row(lines[i + 1])
        if cells is None or sep is None or not is_sep_row(sep):
            i += 1
            continue
        width = len(cells)
        j = i + 2
        while j < len(lines):
            row = split_row(lines[j])
            if row is None or not lines[j].strip():
                break
            if is_sep_row(row):
                break
            if len(row) != width:
                out.append((j + 1, width, len(row), lines[j]))
            j += 1
        i = j
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()

    issues: list[tuple[str, int, int, int]] = []
    for path in sorted(DOCS.rglob("*.md")):
        for ln, hc, sc, _h, _s in scan(path):
            issues.append((path.as_posix(), ln, hc, sc))

    print(f"mismatched_tables={len(issues)}")
    print(f"files={len({p for p, *_ in issues})}")
    for p, ln, hc, sc in issues[:30]:
        print(f"  {p}:{ln} header={hc} sep={sc}")
    if len(issues) > 30:
        print(f"  ... +{len(issues) - 30} more")

    if not args.fix:
        return

    total = 0
    by_file = Counter()
    for path in sorted(DOCS.rglob("*.md")):
        n = fix_file(path)
        if n:
            by_file[path.as_posix()] = n
            total += n
    print(f"fixed_tables={total}")
    for f, n in by_file.most_common():
        print(f"  {n}  {f}")

    # verify
    left = sum(len(scan(p)) for p in DOCS.rglob("*.md"))
    print(f"remaining={left}")
    body = []
    for path in sorted(DOCS.rglob("*.md")):
        for item in scan_body_mismatches(path):
            body.append((path.as_posix(), *item))
    print(f"body_col_mismatch={len(body)}")
    for p, ln, exp, got, row in body[:20]:
        print(f"  {p}:{ln} expect={exp} got={got}")
        print(f"    {row[:100]}")


if __name__ == "__main__":
    main()
