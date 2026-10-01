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
- headings whose end page precedes their start page or falls after the
  next section's start or the page where the References start (end page),
- headings that cite no page (no page), or a page citation this script
  cannot read (bad page),
- section numbers that appear twice in one file (duplicate).

Headings inside fenced code blocks and HTML comments are ignored; a fence
or comment left open at the end of a file is reported as a mismatch.

With no chapters named, a book chapter that has no notes file is also
reported. Titles are compared case-insensitively, ignoring punctuation.

Exits 0 when everything matches and 1 when any mismatch is found. Exits 2
when an input is unusable: the book text is missing or unreadable or holds
a table of contents that does not parse completely and plausibly (every
contents title must also match the body's own heading for that section,
and every capitalized numbered body heading in a chapter the contents
lists needs a contents entry),
VERSION is missing or has no page count, a chapter file is unreadable, no chapter
files exist, or a named chapter has no file. A chapter file with no
numbered sections in either the book or the notes is reported as having
nothing to compare.

Usage: .github/scripts/check-book-sync.py [--book-text PATH] [CHAPTER ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO = Path(__file__).resolve().parents[2]
DEFAULT_TEXT = REPO / "inst" / "book" / "whatif.txt"

TOC_SECTION = re.compile(r"^\s*(\d+)\.(\d+)\s+(.+?)(?:\s*\.(?:\s*\.)+)?\s+(\d+)\s*$")
NOTE_HEADING = re.compile(
    r"^[ ]{0,3}##\s+(\d+)\.(\d+)\s+(.+?)\s*"
    r"(?:\((?:pp?\.)\s*(\d+)(?:\s*[-\u2013]+\s*(\d+))?\s*\))?"
    r"\s*(?:\{[^}]*\})?\s*$"
)
TOC_END_MARKER = "INTRODUCTION: TOWARDS"


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
BODY_HEADING = re.compile(r"^\f?\s*(\d+)\.(\d+)\s+(\S.*?)\s*$")
TRAILING_PAGE = re.compile(r"\s+\d+$")
# The contents entry for the back matter, which bounds the last section.
REFERENCES_ENTRY = re.compile(r"^\s*References(?:\s*\.)*\s+(\d+)\s*$")
CODE_SPAN = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
INLINE_COMMENT = re.compile(r"<!--.*?-->")
ATX_CLOSING = re.compile(r"\s+#+\s*$")
# A page citation the heading regex could not read, such as "(p. 5, Fig. 2)".
UNPARSED_PAGES = re.compile(r"\s*\((?:pp?\.)[^)]*\)\s*(?:\{[^}]*\})?\s*$")
MAX_CONTINUATION = 3


def references_page(text: str) -> int:
    """The printed page where the References start, from the contents."""
    for line in text.splitlines():
        if TOC_END_MARKER in line:
            break
        match = REFERENCES_ENTRY.match(line)
        if match:
            return int(match.group(1))
    raise ValueError("no 'References' entry in the table of contents")


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
        (i for i, line in enumerate(lines) if TOC_END_MARKER in line),
        None,
    )
    if end is None:
        raise ValueError(
            f"end of the table of contents ({TOC_END_MARKER!r}) not found in book text"
        )
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
    # A wrapped title whose first line ends in a number closes early with
    # that number as its page. Page order catches a stray number outside its
    # neighbours' pages; the body check below catches the truncated title.
    previous = 0
    for key, (title, page) in toc.items():
        if page < previous or (max_page is not None and page > max_page):
            raise ValueError(
                f"implausible page {page} for {key[0]}.{key[1]} {title!r}"
                f" (previous section: p. {previous}"
                + (f"; book has {max_page} pages)" if max_page is not None else ")")
            )
        previous = page
    check_body_headings(toc, lines[end:])
    return toc


def check_body_headings(toc, body: list[str]) -> None:
    """Require the contents and the body's section headings to agree.

    The body sets each heading on one line ("12.3 Stabilized IP weights"),
    so a contents title that closed early, or picked up a stray line, no
    longer matches it. This does not depend on the contents' layout.
    Conversely, a capitalized numbered heading in a chapter the contents
    lists must have a contents entry, so a lost contents line is caught.
    """
    headings: dict[tuple[int, int], list[str]] = {}
    capitalized: set[tuple[int, int]] = set()
    for line in body:
        match = BODY_HEADING.match(line)
        if match:
            chapter, section, title = match.groups()
            key = (int(chapter), int(section))
            title = TRAILING_PAGE.sub("", title)
            headings.setdefault(key, []).append(normalize(title))
            if title[:1].isupper():
                capitalized.add(key)
    for (chapter, section), (title, _) in toc.items():
        if normalize(title) not in headings.get((chapter, section), []):
            raise ValueError(
                f"contents title {chapter}.{section} {title!r} matches no"
                f" '{chapter}.{section}' heading in the book's body"
            )
    # The reverse direction: a contents line lost in extraction would
    # otherwise go unnoticed. Body prose that happens to start with a number
    # like "6.7" continues a sentence, so it starts lowercase or with a symbol;
    # only a capitalized title in one of the book's chapters counts here.
    chapters = {chapter for chapter, _ in toc}
    for chapter, section in sorted(capitalized):
        if chapter in chapters and (chapter, section) not in toc:
            raise ValueError(
                f"body heading {chapter}.{section} has no entry in the contents"
            )


class Note(NamedTuple):
    title: str
    page: int | None
    last: int | None
    unparsed: bool


def ends_in_comment(line: str, comment: bool) -> bool:
    """Whether an HTML comment is open at the end of line."""
    position = 0
    while True:
        marker = "-->" if comment else "<!--"
        found = line.find(marker, position)
        if found < 0:
            return comment
        comment = not comment
        position = found + len(marker)


def read_notes(path: Path, problems: list[str]) -> dict[tuple[int, int], Note]:
    notes = {}
    fence = None
    comment = False
    for line in path.read_text(encoding="utf-8").splitlines():
        opener = FENCE.match(line)
        if opener and not comment:
            run = opener.group(1)
            if fence is None:
                fence = run
            elif (
                run[0] == fence[0]
                and len(run) >= len(fence)
                and not line.strip()[len(run) :].strip()
            ):
                fence = None
            continue
        if fence is not None:
            continue
        # Headings inside an HTML comment are not rendered, so skip them.
        started_in_comment = comment
        # Code spans render literally, so markers inside them open nothing.
        comment = ends_in_comment(CODE_SPAN.sub("", line), comment)
        if started_in_comment:
            continue
        heading = ATX_CLOSING.sub("", INLINE_COMMENT.sub("", line))
        match = NOTE_HEADING.match(heading)
        if match:
            chapter, section, title, page, last = match.groups()
            key = (int(chapter), int(section))
            label = f"{chapter}.{section}"
            if key in notes:
                problems.append(f"duplicate {label} {title.strip()}")
            unparsed = UNPARSED_PAGES.search(title) if page is None else None
            if unparsed:
                problems.append(
                    f"bad page {label} cannot read {unparsed.group().strip()!r};"
                    " write (p. N) or (pp. N-M)"
                )
                title = title[: unparsed.start()]
            notes[key] = Note(
                title.strip(),
                int(page) if page else None,
                int(last) if last else None,
                bool(unparsed),
            )
    if fence is not None:
        problems.append(f"unclosed {fence} code fence; headings after it were not read")
    if comment:
        problems.append("unclosed HTML comment; headings after it were not read")
    return notes


def compare(chapter: int, toc, notes, last_page: int) -> list[str]:
    problems = []
    book = {key: value for key, value in toc.items() if key[0] == chapter}
    order = list(toc)
    # A section may end on the page where the next one starts, including the
    # first section of the next chapter; the last ends by the printed page
    # where the References start.
    next_start = {key: toc[order[i + 1]][1] for i, key in enumerate(order[:-1])}
    for key in sorted(book.keys() | notes.keys()):
        label = f"{key[0]}.{key[1]}"
        if key not in notes:
            problems.append(f"missing  {label} {book[key][0]} (p. {book[key][1]})")
        elif key not in book:
            problems.append(f"extra    {label} {notes[key][0]}")
        else:
            book_title, book_page = book[key]
            note_title, note_page, note_last, unparsed = notes[key]
            if normalize(book_title) != normalize(note_title):
                problems.append(
                    f"renamed  {label} notes: {note_title!r} / book: {book_title!r}"
                )
            if unparsed:
                continue  # already reported as a bad page
            if note_page is None:
                problems.append(
                    f"no page  {label} heading cites no page (book: p. {book_page})"
                )
            elif note_page != book_page:
                problems.append(
                    f"page     {label} notes: p. {note_page} / book: p. {book_page}"
                )
            elif note_last is not None and note_last < note_page:
                problems.append(
                    f"end page {label} notes: pp. {note_page}-{note_last}"
                    " ends before it starts"
                )
            elif note_last is not None and key in next_start:
                if note_last > next_start[key]:
                    problems.append(
                        f"end page {label} notes: pp. {note_page}-{note_last}"
                        f" / next section starts p. {next_start[key]}"
                    )
            elif note_last is not None and note_last > last_page:
                problems.append(
                    f"end page {label} notes: pp. {note_page}-{note_last}"
                    f" / References start p. {last_page}"
                )
    return problems


def book_pages() -> int:
    """The PDF page count recorded in inst/book/VERSION.

    Printed page numbers run lower than PDF pages, so this only bounds the
    contents' page numbers loosely.
    """
    version = (REPO / "inst" / "book" / "VERSION").read_text(encoding="utf-8")
    match = re.search(r"^pages:\s*(\d+)\s*$", version, re.MULTILINE)
    if not match:
        raise ValueError("no 'pages:' line in inst/book/VERSION")
    return int(match.group(1))


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
        max_page = book_pages()
    except (OSError, ValueError, UnicodeDecodeError) as error:
        print(
            f"cannot read the page count from inst/book/VERSION: {error}",
            file=sys.stderr,
        )
        return 2
    try:
        text = args.book_text.read_text(encoding="utf-8")
        toc = read_toc(text, max_page)
        last_page = references_page(text)
    except (OSError, ValueError, UnicodeDecodeError) as error:
        print(
            f"cannot read the book's contents from {args.book_text}: {error}",
            file=sys.stderr,
        )
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
            print(
                f"Chapter {chapter:2d}: no chapters/{chapter:02d}-*.qmd file"
                f" for its {sections} book section(s)"
            )
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
        problems += compare(chapter, toc, notes, last_page)
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
