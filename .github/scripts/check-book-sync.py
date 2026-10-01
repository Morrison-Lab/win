#!/usr/bin/env python3
"""Compare the lecture notes' section structure with the What If book's.

Reads the book's table of contents from the text that
fetch-whatif-book.sh extracts (inst/book/whatif.txt), and each chapter's
numbered section headings from chapters/*.qmd, which take the form

    ## 12.3 Stabilized IP Weights (pp. 167-169)

and reports, per chapter:

- book sections with no matching note heading (missing),
- note headings numbered as sections the book does not have (extra),
- headings whose title differs from the book's (renamed),
- headings whose cited start page differs from the book's (page).

Titles are compared case-insensitively, ignoring punctuation.
Exits 1 when any mismatch is found and 2 when an input is missing,
so a run that examined nothing never reads as a clean one.

Usage: .github/scripts/check-book-sync.py [--book-text PATH] [CHAPTER ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_TEXT = REPO / "inst" / "book" / "whatif.txt"

TOC_SECTION = re.compile(
    r"^\s*(\d+)\.(\d+)\s+(.+?)(?:\s*\.(?:\s*\.)+)?\s+(\d+)\s*$"
)
NOTE_HEADING = re.compile(
    r"^##\s+(\d+)\.(\d+)\s+(.+?)\s*(?:\((?:pp?\.)\s*(\d+)[^)]*\))?"
    r"\s*(?:\{[^}]*\})?\s*$"
)


def normalize(title: str) -> str:
    title = title.lower().replace("versus", "vs")
    return re.sub(r"[^a-z0-9]+", " ", title).strip()


def read_toc(text: str) -> dict[tuple[int, int], tuple[str, int]]:
    """Parse numbered sections from the front-matter table of contents."""
    lines = text.splitlines()
    end = next(
        (i for i, line in enumerate(lines) if "INTRODUCTION: TOWARDS" in line),
        None,
    )
    if end is None:
        raise ValueError("table of contents not found in book text")
    toc: dict[tuple[int, int], tuple[str, int]] = {}
    pending = ""
    for line in lines[:end]:
        line = re.sub(r"^\s*(?:CONTENTS|[ivx]+)\s{2,}.*Causal Inference\s*$", "", line)
        candidate = f"{pending} {line.strip()}".strip() if pending else line
        match = TOC_SECTION.match(candidate)
        if match:
            chapter, section, title, page = match.groups()
            toc[(int(chapter), int(section))] = (title.strip(" ."), int(page))
            pending = ""
        elif re.match(r"^\s*\d+\.\d+\s", line):
            # A title that wraps onto the next line in the contents.
            pending = line.strip()
        else:
            pending = ""
    if not toc:
        raise ValueError("no numbered sections parsed from the table of contents")
    return toc


def read_notes(path: Path, problems: list[str]) -> dict[tuple[int, int], tuple[str, int | None]]:
    notes = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = NOTE_HEADING.match(line)
        if match:
            chapter, section, title, page = match.groups()
            key = (int(chapter), int(section))
            if key in notes:
                problems.append(f"duplicate {chapter}.{section} {title.strip()}")
            notes[key] = (title.strip(), int(page) if page else None)
    return notes


def compare(chapter: int, toc, notes) -> list[str]:
    problems = []
    book = {key: value for key, value in toc.items() if key[0] == chapter}
    for key in sorted(book.keys() | notes.keys()):
        label = f"{key[0]}.{key[1]}"
        if key not in notes:
            problems.append(f"missing  {label} {book[key][0]} (p. {book[key][1]})")
        elif key not in book:
            problems.append(f"extra    {label} {notes[key][0]}")
        else:
            book_title, book_page = book[key]
            note_title, note_page = notes[key]
            if normalize(book_title) != normalize(note_title):
                problems.append(
                    f"renamed  {label} notes: {note_title!r} / book: {book_title!r}"
                )
            if note_page is None:
                problems.append(f"no page  {label} heading cites no page (book: p. {book_page})")
            elif note_page != book_page:
                problems.append(
                    f"page     {label} notes: p. {note_page} / book: p. {book_page}"
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--book-text", type=Path, default=DEFAULT_TEXT)
    parser.add_argument("chapters", nargs="*", type=int)
    args = parser.parse_args()

    if not args.book_text.exists():
        print(
            f"{args.book_text} not found; run .github/scripts/fetch-whatif-book.sh",
            file=sys.stderr,
        )
        return 2
    try:
        toc = read_toc(args.book_text.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        print(f"cannot read the book's contents from {args.book_text}: {error}", file=sys.stderr)
        return 2

    files = sorted((REPO / "chapters").glob("[0-9][0-9]-*.qmd"))
    if not files:
        print("no chapters/NN-*.qmd files found", file=sys.stderr)
        return 2

    available = {int(path.name[:2]) for path in files}
    unmatched = sorted(set(args.chapters) - available)
    if unmatched:
        print(f"no chapter file for: {', '.join(map(str, unmatched))}", file=sys.stderr)
        return 2

    total = 0
    examined = 0
    for path in files:
        chapter = int(path.name[:2])
        if args.chapters and chapter not in args.chapters:
            continue
        examined += 1
        problems: list[str] = []
        notes = read_notes(path, problems)
        problems += compare(chapter, toc, notes)
        total += len(problems)
        status = "ok" if not problems else f"{len(problems)} mismatch(es)"
        print(f"Chapter {chapter:2d} ({path.name}): {status}")
        for problem in problems:
            print(f"    {problem}")

    print(
        f"\nExamined {examined} chapter file(s) against {len(toc)} book sections;"
        f" {total} mismatch(es)."
    )
    if examined == 0:
        return 2
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
