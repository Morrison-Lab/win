#!/usr/bin/env python3
"""Fail when a Quarto crossref id is defined more than once in the book.

Crossref ids (#def-..., #thm-..., #fig-..., #sec-..., and so on) must be
unique across every chapter, because Quarto resolves @refs book-wide.
The script reads index.qmd and chapters/*.qmd and collects

- ids in attribute blocks, such as `::: {#def-foo}` or `## Title {#sec-foo}`,
- ids from chunk options of the form `#| label: fig-foo` (optionally quoted)
  in executable cells,
- ids in the attributes of an opening fence, such as `{#lst-foo .python}`.

Ids inside the body of other fenced code blocks, inline code spans
(including spans that cross lines), and HTML comments are ignored.
Exits 0 when every id is unique and 1 when any id is defined twice.
"""
import re
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

PREFIXES = "def|thm|lem|prp|cor|exm|exr|alg|rem|cnj|prf|sol|fig|tbl|eq|sec|lst"
ATTR_BLOCK = re.compile(r"\{[^{}]*")
QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'")
ATTR_ID = re.compile(r"(?:(?<=\{)|(?<=\s))#((?:%s)-[A-Za-z0-9_-]+)" % PREFIXES)
LIST_ITEM = re.compile(r"^ {0,3}(?:[-*+]|\d{1,9}[.)])(?:\s|$)")
CHUNK_ID = re.compile(
    r"""^\s*#\|\s*label:\s*["']?((?:%s)-[A-Za-z0-9_-]+)["']?\s*(?:\s#.*)?$""" % PREFIXES
)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
NOT_NEWLINE = re.compile(r"[^\n]")


@lru_cache(maxsize=None)
def closing_run(width):
    """Compiled pattern for a backtick run of exactly `width` characters."""
    return re.compile(r"(?<!`)`{%d}(?!`)" % width)


def attribute_ids(text):
    """Yield the crossref ids defined in the attribute blocks of one line.

    An id counts only when it follows the opening brace or whitespace, and
    text inside quoted attribute values is ignored, so
    `{fig-alt="see #fig-x"}` defines nothing.
    """
    for block in ATTR_BLOCK.finditer(text):
        for found in ATTR_ID.finditer(QUOTED.sub('""', block.group())):
            yield found.group(1)


def blank(text):
    """Replace every character but newlines with a space, keeping line numbers."""
    return NOT_NEWLINE.sub(" ", text)


def clean_block(lines, in_comment):
    """Blank out code spans and HTML comments in one run of prose lines.

    A code span closes on a backtick run of equal length and may cross
    lines, but not a blank line, so the caller passes one paragraph at a
    time.
    A comment may cross blank lines, so its state is carried between calls.
    Whichever construct opens first hides the other's delimiters.
    Returns the cleaned lines and whether a comment is still open.
    """
    text = "\n".join(lines)
    out = []
    pos = 0
    while pos < len(text):
        if in_comment:
            end = text.find("-->", pos)
            if end < 0:
                out.append(blank(text[pos:]))
                break
            out.append(blank(text[pos : end + 3]))
            pos = end + 3
            in_comment = False
        elif text[pos] == "`":
            run_end = pos
            while run_end < len(text) and text[run_end] == "`":
                run_end += 1
            width = run_end - pos
            close = closing_run(width).search(text, run_end)
            if close:
                out.append(blank(text[pos : close.end()]))
                pos = close.end()
            else:
                out.append(text[pos:run_end])
                pos = run_end
        elif text.startswith("<!--", pos):
            out.append("    ")
            pos += 4
            in_comment = True
        else:
            out.append(text[pos])
            pos += 1
    return "".join(out).split("\n"), in_comment


def ids_in(path):
    """Yield (id, line number) for every crossref id the file defines."""
    fence = None  # (character, length, is_executable_cell) while inside a fence
    in_comment = False
    block = []  # (line number, line) of the paragraph being collected

    def flush():
        nonlocal in_comment
        if not block:
            return []
        cleaned, in_comment = clean_block([line for _, line in block], in_comment)
        found = [
            (crossref_id, number)
            for (number, _), text in zip(block, cleaned)
            for crossref_id in attribute_ids(text)
        ]
        block.clear()
        return found

    after_blank = True  # the previous line was blank, or this is the first
    in_list = False  # the current top-level block is a list item
    in_indented_code = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not fence:
            expanded = line.expandtabs(4)
            indent = len(expanded) - len(expanded.lstrip(" "))
            if not line.strip():
                yield from flush()
                after_blank = True
                continue
            if in_indented_code and indent >= 4:
                continue
            in_indented_code = False
            if after_blank and indent >= 4 and not in_list and not in_comment:
                in_indented_code = True  # an indented code block is not markup
                after_blank = False
                continue
            if LIST_ITEM.match(expanded):
                in_list = True
            elif indent == 0:
                in_list = False
            after_blank = False
        match = FENCE.match(line)
        if match and not fence and match.group(1)[0] == "`" and "`" in match.group(2):
            match = None  # a backtick fence's info string has no backticks: inline code
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
        if match:
            yield from flush()
            if not in_comment:
                info = match.group(2)
                fence = (
                    match.group(1)[0],
                    len(match.group(1)),
                    re.match(r"\{[A-Za-z]", info.lstrip()) is not None,
                )
                for crossref_id in attribute_ids(info):
                    yield crossref_id, number
                continue
        block.append((number, line))
    yield from flush()


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
