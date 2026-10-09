#!/usr/bin/env python3
"""Fail when a Quarto crossref id is defined more than once in the book.

Crossref ids (#def-..., #thm-..., #fig-..., #sec-..., and so on) must be
unique across every chapter, because Quarto resolves @refs book-wide.
The script reads index.qmd and chapters/*.qmd and collects

- ids in attribute blocks, such as `::: {#def-foo}` or `## Title {#sec-foo}`,
- ids from chunk options of the form `#| label: fig-foo`.

Ids inside fenced code blocks (other than chunk options) and HTML comments
are ignored.
Exits 0 when every id is unique and 1 when any id is defined twice.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

PREFIXES = "def|thm|lem|prp|cor|exm|exr|alg|rem|cnj|fig|tbl|eq|sec|lst"
ATTR_ID = re.compile(r"\{[^{}]*?#((?:%s)-[A-Za-z0-9_-]+)" % PREFIXES)
CHUNK_ID = re.compile(r"^#\|\s*label:\s*((?:%s)-[A-Za-z0-9_-]+)" % PREFIXES)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def ids_in(path):
    in_fence = False
    in_comment = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if in_comment:
            in_comment = "-->" not in line
            continue
        if line.lstrip().startswith("<!--") and "-->" not in line:
            in_comment = True
            continue
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            match = CHUNK_ID.match(line)
            if match:
                yield match.group(1), number
            continue
        for match in ATTR_ID.finditer(re.sub(r"<!--.*?-->", "", line)):
            yield match.group(1), number


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    files = sorted(root.glob("chapters/*.qmd")) + sorted(root.glob("index.qmd"))
    seen = defaultdict(list)
    for path in files:
        for crossref_id, number in ids_in(path):
            seen[crossref_id].append(f"{path.relative_to(root)}:{number}")
    duplicates = {key: where for key, where in seen.items() if len(where) > 1}
    for key, where in sorted(duplicates.items()):
        print(f"::error::Duplicate crossref id #{key}: {', '.join(where)}")
    if duplicates:
        print(
            "Rename one side with a chapter suffix (for example #def-foo-ch12) "
            "and update the @refs that mean it."
        )
        return 1
    print(f"No duplicate crossref ids in {len(files)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
