"""Valida estructura y enlaces locales de todos los Markdown del proyecto."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"build", ".arduino-local", ".local-tools", ".venv-ia", ".git"}
WIKILINK = re.compile(r"\[\[([^\]|#]+)")
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md")
                  if not SKIP_PARTS.intersection(path.relative_to(ROOT).parts))


def main() -> int:
    files = markdown_files()
    stems = {path.stem.casefold() for path in files}
    errors: list[str] = []
    checked_links = 0
    for path in files:
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8-sig")
        if not text.strip():
            errors.append(f"{relative}: archivo vacío")
            continue
        if not re.search(r"^#\s+\S", text, re.MULTILINE):
            errors.append(f"{relative}: falta título H1")
        for raw in WIKILINK.findall(text):
            checked_links += 1
            target = raw.strip().replace("\\", "/").split("/")[-1]
            if target.casefold() not in stems:
                errors.append(f"{relative}: Wikilink roto [[{raw}]]")
        for raw in MD_LINK.findall(text):
            target = raw.strip().strip("<>").split(maxsplit=1)[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            checked_links += 1
            if not (path.parent / target).resolve().exists():
                errors.append(f"{relative}: enlace local roto ({raw})")
    if errors:
        for error in errors:
            print(f"ERROR_MD: {error}", file=sys.stderr)
        return 1
    print(f"MARKDOWN_OK: {len(files)} archivos, {checked_links} enlaces locales/Wikilinks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
