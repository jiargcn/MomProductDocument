"""Batch-link interface tables in module docs using .linkmap.json"""
import json, os, re
from pathlib import Path

DOCS = Path("docs")
LINKMAP = DOCS / ".linkmap.json"

with open(LINKMAP, encoding="utf-8") as f:
    linkmap = json.load(f)

entities = {k: v for k, v in linkmap.items() if v.get("path")}

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
        # CODE = uppercase letters/digits/underscores (not Chinese chars)
        m = re.match(r'^(\s*\|)\s+([A-Z][A-Z0-9_]+)\s+\|\s+(.+?)\s+(\|.*)', line)
        if m:
            code = m.group(2)
            chinese = m.group(3).strip()
            rest = m.group(4)
            if code in entities:
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
            # Build link to sub-page index.md
            sub_index = f"{group_name}/index.md"
            target_path = source_file.parent / sub_index
            if target_path.exists():
                line = f"{prefix}[{group_name}]({sub_index}) {rest}"
            result.append(line)
            continue

        # Track if we're inside a 业务分组 table
        if line.strip().startswith("| 分组 |"):
            in_biz_group_table = True
        elif in_biz_group_table and line.strip().startswith("|"):
            pass  # still in table
        elif in_biz_group_table:
            in_biz_group_table = False  # table ended

        result.append(line)

    return "\n".join(result)


def process_file(path: Path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    has_interface = "相关模块接口" in text or "接口规范" in text
    has_biz_group = "业务分组" in text

    if not has_interface and not has_biz_group:
        return False

    new_text = link_module_refs(text, path)
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

print(f"\nDone. {changed} files updated.")
