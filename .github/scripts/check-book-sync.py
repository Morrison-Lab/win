#!/usr/bin/env python3
"""Compare the lecture notes' section structure with the What If book's.

Reads the book's table of contents from the text that
fetch-whatif-book.sh extracts (inst/book/whatif.txt), and each chapter's
numbered section headings from the chapter files chapters/NN-*.qmd
(headings in included subfiles are not read), which take the form

    ## 12.3 Stabilized IP Weights (pp. 167-169)

and reports, per chapter:

- book sections with no matching note heading (missing),
- note headings numbered as sections the book does not have (extra),
- headings whose title differs from the book's (renamed),
- headings whose cited start page differs from the book's (page),
- headings that cite no page (no page),
- section numbers that appear twice in one file (duplicate).

Headings inside fenced code blocks and HTML comments are ignored; a fence
or comment left open at the end of a file is reported as a mismatch.

With no chapters named, a book chapter that has no notes file is also
reported. Titles are compared case-insensitively, ignoring punctuation.

Exits 0 when everything matches and 1 when any mismatch is found. Exits 2
when an input is unusable: the book text is missing or unreadable or holds
a table of contents that does not parse completely and plausibly, a chapter file is unreadable, no chapter
files exist, or a named chapter has no file. A run that examined nothing
therefore never reads as a clean one.

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


SECTION_START = re.compile(r"^\s*\d+\.\d+\s")
# Lines that end a wrapped section title: a chapter or part entry.
ENTRY_START = re.compile(r"^\s*(?:\d+|[IVX]+)\s+\S")
# Running headers in the contents: even pages read "ii   Causal Inference",
# odd pages "CONTENTS   v"; either may carry a leading form feed.
PAGE_HEADER = re.compile(
    r"^\f?\s*(?:[ivx]+\s+(?:CONTENTS\s+)?Causal Inference|CONTENTS\s+[ivx]+)\s*$"
)
FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")
MAX_CONTINUATION = 3


def read_toc(
    text: str, max_page: int | None = None
) -> dict[tuple[int, int], tuple[str, int]]:
    """Parse numbered sections from the front-matter table of contents.

    A section title may wrap onto later lines, possibly across a page
    header; the entry ends at the line carrying its page number. Every line
    that starts a numbered section must yield exactly one parsed section,
    so a title the parser cannot close is an error rather than a gap, and
    section pages must not decrease or exceed max_page.
    """
    lines = text.splitlines()
    end = next(
        (i for i, line in enumerate(lines) if "INTRODUCTION: TOWARDS" in line),
        None,
    )
    if end is None:
        raise ValueError("table of contents not found in book text")
    toc: dict[tuple[int, int], tuple[str, int]] = {}
    starts = 0
    pending = ""
    continued = 0
    for line in lines[:end]:
        if SECTION_START.match(line):
            starts += 1
            pending, continued = line.strip(), 0
        elif not pending:
            continue
        elif not line.strip() or PAGE_HEADER.match(line):
            continue
        elif ENTRY_START.match(line) or continued >= MAX_CONTINUATION:
            pending = ""
            continue
        else:
            pending = f"{pending} {line.strip()}"
            continued += 1
        match = TOC_SECTION.match(pending)
        if match:
            chapter, section, title, page = match.groups()
            toc[(int(chapter), int(section))] = (title.strip(" ."), int(page))
            pending = ""
    if not toc:
        raise ValueError("no numbered sections parsed from the table of contents")
    if len(toc) != starts:
        raise ValueError(
            f"{starts} numbered section lines in the contents but {len(toc)} parsed"
        )
    # A wrapped title whose first line ends in a number can close early with
    # that number as its page; the count check cannot see it, page order can.
    previous = 0
    for key, (title, page) in toc.items():
        if page < previous or (max_page is not None and page > max_page):
            raise ValueError(
                f"implausible page {page} for {key[0]}.{key[1]} {title!r}"
                f" (previous section: p. {previous}"
                + (f"; book has {max_page} pages)" if max_page is not None else ")")
            )
        previous = page
    return toc


def read_notes(path: Path, problems: list[str]) -> dict[tuple[int, int], tuple[str, int | None]]:
    notes = {}
    fence = None
    comment = False
    for line in path.read_text(encoding="utf-8").splitlines():
        opener = FENCE.match(line)
        if opener and not comment:
            run = opener.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not line.strip()[len(run):].strip():
                fence = None
            continue
        if fence is not None:
            continue
        # Headings inside an HTML comment are not rendered, so skip them.
        if comment:
            comment = "-->" not in line
            continue
        if line.lstrip().startswith("<!--") and "-->" not in line:
            comment = True
            continue
        match = NOTE_HEADING.match(line)
        if match:
            chapter, section, title, page = match.groups()
            key = (int(chapter), int(section))
            if key in notes:
                problems.append(f"duplicate {chapter}.{section} {title.strip()}")
            notes[key] = (title.strip(), int(page) if page else None)
    if fence is not None:
        problems.append(f"unclosed {fence} code fence; headings after it were not read")
    if comment:
        problems.append("unclosed HTML comment; headings after it were not read")
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


def book_pages() -> int | None:
    """The page count recorded in inst/book/VERSION, if any."""
    try:
        version = (REPO / "inst" / "book" / "VERSION").read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^pages:\s*(\d+)\s*$", version, re.MULTILINE)
    return int(match.group(1)) if match else None


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
        toc = read_toc(args.book_text.read_text(encoding="utf-8"), book_pages())
    except (OSError, ValueError, UnicodeDecodeError) as error:
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
    if not args.chapters:
        for chapter in sorted({key[0] for key in toc} - available):
            sections = sum(1 for key in toc if key[0] == chapter)
            print(f"Chapter {chapter:2d}: no chapters/{chapter:02d}-*.qmd file"
                  f" for its {sections} book section(s)")
            total += sections
    for path in files:
        chapter = int(path.name[:2])
        if args.chapters and chapter not in args.chapters:
            continue
        examined += 1
        problems: list[str] = []
        try:
            notes = read_notes(path, problems)
        except (OSError, UnicodeDecodeError) as error:
            print(f"cannot read {path}: {error}", file=sys.stderr)
            return 2
        problems += compare(chapter, toc, notes)
        total += len(problems)
        if problems:
            status = f"{len(problems)} mismatch(es)"
        elif notes:
            status = "ok"
        else:
            status = "nothing to compare (no numbered sections in book or notes)"
        print(f"Chapter {chapter:2d} ({path.name}): {status}")
        for problem in problems:
            print(f"    {problem}")

    print(
        f"\nExamined {examined} chapter file(s) against {len(toc)} book sections;"
        f" {total} mismatch(es)."
    )
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
