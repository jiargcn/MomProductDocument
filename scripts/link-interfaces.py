"""Batch-link module docs using .linkmap.json

Phase 1: Interface table CODE_NAME → module page
Phase 2: 业务分组 table first column → sub-page index.md
Phase 3: Inline module name references in 业务规则 + field table 影响业务/备注 columns
"""
import json, os, re
from pathlib import Path

DOCS = Path("docs")
LINKMAP = DOCS / ".linkmap.json"

with open(LINKMAP, encoding="utf-8") as f:
    linkmap = json.load(f)

entities = {k: v for k, v in linkmap.items() if v.get("path")}

# ── names sorted longest-first for greedy matching ──
_name_to_code = {}
for code, ent in entities.items():
    name = ent["name"]
    if len(name) >= 4:  # skip short/generic names
        _name_to_code.setdefault(name, []).append(code)

_sorted_names = sorted(_name_to_code, key=len, reverse=True)

# names we NEVER auto-link (too generic)
_GENERIC_NAMES = {"物料主数据", "供应商主数据", "客户主数据", "基础数据"}


def rel_path(source_file: Path, target: str) -> str:
    source_dir = source_file.parent
    target_path = DOCS / target
    return os.path.relpath(target_path, source_dir).replace("\\", "/")


def link_module_refs(text: str, source_file: Path) -> str:
    """Link two patterns:
    1. | CODE | Chinese desc | ... | → link Chinese desc to target page
    2. 业务分组 table: | 01-分组名 | ... | → link to 01-分组名/index.md
    """
    lines = text.split("\n")
    in_biz_group_table = False
    result = []

    for line in lines:
        # --- Pattern 1: Interface table rows: | CODE | Chinese | ... | ---
        m = re.match(r'^(\s*\|)\s+([A-Z][A-Z0-9_]+)\s+\|\s+(.+?)\s+(\|.*)', line)
        if m:
            code = m.group(2)
            chinese = m.group(3).strip()
            rest = m.group(4)
            if code in entities and "](" not in chinese:
                ent = entities[code]
                path = rel_path(source_file, ent["path"])
                line = f"{m.group(1)} {code} | [{chinese}]({path}) {rest}"
            result.append(line)
            continue

        # --- Pattern 2: 业务分组 table: | 01-Name | desc | ---
        m = re.match(r'^(\s*\|\s*)(\d{2}-[^|]+?)\s*(\|.*)', line)
        if m and in_biz_group_table:
            prefix = m.group(1)
            group_name = m.group(2).strip()
            rest = m.group(3)
            sub_index = f"{group_name}/index.md"
            target_path = source_file.parent / sub_index
            if target_path.exists():
                line = f"{prefix}[{group_name}]({sub_index}) {rest}"
            result.append(line)
            continue

        if line.strip().startswith("| 分组 |"):
            in_biz_group_table = True
        elif in_biz_group_table and line.strip().startswith("|"):
            pass
        elif in_biz_group_table:
            in_biz_group_table = False

        result.append(line)

    return "\n".join(result)


_MD_LINK_RE = re.compile(r'\[.+?\]\(.+?\)')  # match existing markdown links


def _link_names_in_text(text: str, source_file: Path) -> str:
    """Replace known module names with links, no double-replace in URLs.

    Strategy: replace ALL names with unique sentinels first, then restore
    them as final markdown links. This prevents URL text from one
    replacement being matched by a later one.
    """
    # 1. Protect existing markdown links with sentinels
    existing_links = []
    def _save_link(m):
        existing_links.append(m.group(0))
        return f"\x00LNK{len(existing_links)-1}\x00"
    protected = _MD_LINK_RE.sub(_save_link, text)

    # 2. Replace each matching name with a unique sentinel
    name_sentinels = []  # (name, path, sentinel) tuples
    for name in _sorted_names:
        if name in _GENERIC_NAMES:
            continue
        if name not in protected:
            continue
        # Also skip if this name is already inside [name](...) format
        # (would mean Phase 1/2 already linked it)
        idx = protected.find(name)
        before = protected[max(0, idx - 60):idx]
        after = protected[idx + len(name):idx + len(name) + 60]
        # Check it's not already inside a [name](...) link
        if f"[{name}](" in protected:
            continue
        sentinel = f"\x00REPL{len(name_sentinels)}\x00"
        name_sentinels.append((name, source_file, sentinel))
        protected = protected.replace(name, sentinel, 1)  # one occurrence at a time

    # 3. Restore existing links
    for i, link_text in enumerate(existing_links):
        protected = protected.replace(f"\x00LNK{i}\x00", link_text)

    # 4. Convert name sentinels to final markdown links
    for name, sf, sentinel in name_sentinels:
        codes = _name_to_code[name]
        ent = entities[codes[0]]
        path = rel_path(sf, ent["path"])
        protected = protected.replace(sentinel, f"[{name}]({path})")

    return protected


def link_inline_refs(text: str, source_file: Path) -> str:
    """Phase 3: Link module name mentions within 业务规则 sections and
    field table 影响业务/备注 columns.

    Uses longest-name-first matching. Skips generic names and existing links.
    """
    lines = text.split("\n")
    in_rules_section = False          # inside ## 业务规则 … next ##
    in_field_table = False            # inside a | field | … | 影响业务 | … | table
    affect_col_index = -1             # which pipe-column is "影响业务"
    hit_biz_rules_header = False
    result = []

    def _link_line(line: str) -> str:
        return _link_names_in_text(line, source_file)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Detect 业务规则 section boundaries ──
        if re.match(r'^#{2,3}\s+业务规则', stripped):
            in_rules_section = True
            hit_biz_rules_header = True
            result.append(line)
            i += 1
            continue

        # End of 业务规则: next ## heading (same level or above)
        if in_rules_section and re.match(r'^##\s', stripped) and not re.match(r'^###\s', stripped):
            in_rules_section = False

        # ── Detect field tables with 影响业务 column ──
        # Header row: | 字段名 | 中文名 | 类型 | 约束 | 影响业务 | 备注 |
        if re.match(r'^\|\s*字段名\s*\|', stripped) and "影响业务" in stripped:
            in_field_table = True
            cols = [c.strip() for c in stripped.split("|")]
            affect_col_index = -1
            for ci, col in enumerate(cols):
                if col == "影响业务":
                    affect_col_index = ci
                    break
            result.append(line)
            i += 1
            continue

        # Track end of field table
        if in_field_table:
            if not stripped.startswith("|"):
                in_field_table = False
                affect_col_index = -1
            elif stripped.startswith("|---"):
                # separator row, skip
                result.append(line)
                i += 1
                continue

        # ── Phase 3: Apply inline linking ──
        modified = line

        # In 业务规则: link module names in rule text
        if in_rules_section and stripped:
            modified = _link_line(modified)

        # In field table 影响业务 column
        if in_field_table and affect_col_index >= 0 and stripped.startswith("|"):
            parts = modified.split("|")
            if affect_col_index < len(parts):
                col_val = parts[affect_col_index]
                linked = _link_names_in_text(col_val, source_file)
                parts[affect_col_index] = linked
                modified = "|".join(parts)

        result.append(modified)
        i += 1

    return "\n".join(result)


def process_file(path: Path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    has_interface = "相关模块接口" in text or "接口规范" in text
    has_biz_group = "业务分组" in text
    has_rules = "业务规则" in text
    has_field_table = "影响业务" in text

    if not has_interface and not has_biz_group and not has_rules and not has_field_table:
        return False

    new_text = link_module_refs(text, path)       # Phase 1+2
    if has_rules or has_field_table:
        new_text = link_inline_refs(new_text, path)  # Phase 3

    if new_text != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        return True
    return False


files = sorted(DOCS.rglob("*.md"))
changed = 0
for f in files:
    if process_file(f):
        print(f"  LINKED: {f.relative_to(DOCS)}")
        changed += 1

print(f"\nDone. {files} files checked, {changed} files updated.")
