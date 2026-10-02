# The What If book

The lecture notes follow
[*Causal Inference: What If*](https://miguelhernan.org/whatifbook)
by Miguel A.&nbsp;Hernán and James M.&nbsp;Robins.
`VERSION` records the revision the notes are compared against
([the checker](#checking-the-notes-against-the-book) reports how closely they match it).

The book's copyright page reads "All rights reserved",
and the authors distribute the PDF free of charge from the link above.
Everything in this directory except this README and `VERSION` is gitignored,
so new downloads and the extracted text are not committed.
An older 21 November 2025 PDF was tracked here from commit 8ffa8bd
until this directory stopped tracking book files.
It remains in the repository's history.

## Getting a local copy

```bash
.github/scripts/fetch-whatif-book.sh
```

downloads the revision named in `VERSION`,
checks its sha256,
and extracts the text to `inst/book/whatif.txt`.
The recorded sha256 matched a download of the recorded URL on 2026-10-01.
If a later run reports a mismatch,
compare the download it keeps as `<name>.pdf.unverified`
with a known-good copy before concluding the book changed.
To move to a newer revision,
take its PDF link from the book's page and run

```bash
BOOK_URL=<pdf url> .github/scripts/fetch-whatif-book.sh
```

then update `date`, `url`, `sha256` and `pages` (the PDF's page count) in `VERSION`.
With `BOOK_URL` set, if a different PDF already has the new file's name,
the script keeps that file and saves the new one as `<name>-<first 12 hex digits of its sha256>.pdf`.
Either way, `whatif.txt` holds the text of the newest download.
Once `VERSION` names the new revision, the next default run saves it under the URL's own file name,
so the checksum-named copy can then be deleted.
The script fetches over HTTPS only, redirects included.

## Checking the notes against the book

```bash
.github/scripts/check-book-sync.py        # every chapter
.github/scripts/check-book-sync.py 12 17  # selected chapters
```

compares each chapter's numbered `## N.M Title (pp. X-Y)` headings
with the book's table of contents,
and lists sections that are missing, extra, renamed,
cited at the wrong start page, with no page or with a page citation it cannot read,
cited with an end page before the start page,
or after the next section's start or the page where the References start,
or duplicated.
With no chapters named, it also lists book chapters that have no notes file.
It exits 0 when everything matches, 1 when it finds a mismatch,
and 2 when an input is unusable:

- the book text is missing or unreadable;
- its table of contents does not parse completely,
  a section's page is out of order or past the page count in `VERSION`,
  a contents title does not match the section's own heading in the book's body,
  a capitalized numbered heading in a chapter the contents lists has no contents entry,
  or the contents has no `References` entry;
- `VERSION` is missing or has no `pages:` line;
- a chapter file is unreadable;
- no `chapters/NN-*.qmd` files exist;
- a named chapter has no file.

Headings in included subfiles, fenced code blocks and HTML comments are not read;
a fence or comment left open at the end of a file is reported as a mismatch.
