# The What If book

The lecture notes follow
[*Causal Inference: What If*](https://miguelhernan.org/whatifbook)
by Miguel A. Hernán and James M. Robins.
`VERSION` records the revision the notes are compared against
(see the checker below for how closely they currently match it).

The book's copyright page reads "All rights reserved",
so this repository never commits the book itself.
The authors distribute the PDF free of charge from the link above.
Everything in this directory except this README and `VERSION` is gitignored.

## Getting a local copy

```bash
.github/scripts/fetch-whatif-book.sh
```

downloads the revision named in `VERSION`,
checks its sha256,
and extracts the text to `inst/book/whatif.txt`.
The recorded sha256 was taken from a local copy of the 21 November 2025 revision,
not from a download of the recorded URL,
so if the first run reports a mismatch,
compare the two files before concluding the book changed.
To move to a newer revision,
take its PDF link from the book's page and run

```bash
BOOK_URL=<pdf url> .github/scripts/fetch-whatif-book.sh
```

then update `date`, `url`, `sha256` and `pages` in `VERSION`.

## Checking the notes against the book

```bash
.github/scripts/check-book-sync.py        # every chapter
.github/scripts/check-book-sync.py 12 17  # selected chapters
```

compares each chapter's numbered `## N.M Title (pp. X-Y)` headings
with the book's table of contents,
and lists sections that are missing, extra, renamed,
cited at the wrong page or with no page, or duplicated.
With no chapters named, it also lists book chapters that have no notes file.
It exits 0 when everything matches, 1 when it finds a mismatch,
and 2 when an input is unusable:
the book text is missing, unreadable, or has no parsable table of contents,
a chapter file is unreadable,
no `chapters/NN-*.qmd` files exist,
or a named chapter has no file.
Headings in included subfiles are not read.
