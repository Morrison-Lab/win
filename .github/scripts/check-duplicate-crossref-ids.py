#!/usr/bin/env python3
"""Fail when a Quarto crossref id is defined more than once in the book.

Crossref ids (#def-..., #thm-..., #fig-..., #sec-..., and so on) must be
unique across every chapter, because Quarto resolves @refs book-wide.
The script reads index.qmd and chapters/*.qmd and collects

- ids in attribute blocks, such as `::: {#def-foo}` or `## Title {#sec-foo}`,
- ids from chunk options of the form `#| label: fig-foo` in executable cells.

Ids inside other fenced code blocks, inline code, and HTML comments are
ignored.
Exits 0 when every id is unique and 1 when any id is defined twice.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

PREFIXES = "def|thm|lem|prp|cor|exm|exr|alg|rem|cnj|prf|sol|fig|tbl|eq|sec|lst"
ATTR_ID = re.compile(r"\{[^{}]*?#((?:%s)-[A-Za-z0-9_-]+)" % PREFIXES)
CHUNK_ID = re.compile(r"^#\|\s*label:\s*((?:%s)-[A-Za-z0-9_-]+)" % PREFIXES)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"`[^`]*`")


def strip_comments(line, in_comment):
    """Return the line without HTML comments and whether one is still open."""
    text = ""
    pos = 0
    while pos < len(line):
        if in_comment:
            end = line.find("-->", pos)
            if end < 0:
                return text, True
            in_comment = False
            pos = end + 3
        else:
            start = line.find("<!--", pos)
            if start < 0:
                text += line[pos:]
                break
            text += line[pos:start]
            in_comment = True
            pos = start + 4
    return text, in_comment


def ids_in(path):
    fence = None  # (character, length, is_executable_cell) while inside a fence
    in_comment = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = FENCE.match(line)
        if fence:
            if (
                match
                and match.group(1)[0] == fence[0]
                and len(match.group(1)) >= fence[1]
                and not match.group(2).strip()
            ):
                fence = None
            elif fence[2]:
                chunk = CHUNK_ID.match(line)
                if chunk:
                    yield chunk.group(1), number
            continue
        if match and not in_comment:
            fence = (
                match.group(1)[0],
                len(match.group(1)),
                match.group(2).lstrip().startswith("{"),
            )
            continue
        text, in_comment = strip_comments(line, in_comment)
        for found in ATTR_ID.finditer(INLINE_CODE.sub("", text)):
            yield found.group(1), number


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    files = sorted(root.glob("chapters/**/*.qmd")) + sorted(root.glob("index.qmd"))
    seen = defaultdict(list)
    for path in files:
        for crossref_id, number in ids_in(path):
            seen[crossref_id].append((str(path.relative_to(root)), number))
    duplicates = {key: where for key, where in seen.items() if len(where) > 1}
    for key, where in sorted(duplicates.items()):
        first_file, first_line = where[0]
        places = ", ".join(f"{name}:{line}" for name, line in where)
        print(
            f"::error file={first_file},line={first_line}::"
            f"Duplicate crossref id #{key}: {places}"
        )
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
