#!/usr/bin/env bash
# Download the current revision of Hernan & Robins, "Causal Inference: What If",
# into inst/book/ and extract its text for local reference.
#
# The book is "All rights reserved" (see its copyright page), so nothing this
# script writes is committed: inst/book/ is gitignored apart from README.md and
# VERSION. The authors distribute the PDF free of charge from
# https://miguelhernan.org/whatifbook, which is where a newer revision's URL
# should be taken from.
#
# Usage:
#   .github/scripts/fetch-whatif-book.sh            # revision named in VERSION
#   BOOK_URL=<pdf url> .github/scripts/fetch-whatif-book.sh
#
# Requires curl, pdftotext (poppler-utils), and sha256sum or shasum.

set -euo pipefail

for tool in curl pdftotext; do
  if ! command -v "$tool" >/dev/null; then
    echo "Required tool not found: $tool" >&2
    exit 2
  fi
done

if command -v sha256sum >/dev/null; then
  sha256() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null; then
  sha256() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
  echo "Required tool not found: sha256sum or shasum" >&2
  exit 2
fi

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
book_dir="$repo_root/inst/book"
version_file="$book_dir/VERSION"

read_field() {
  sed -n "s/^$1: *//p" "$version_file"
}

# A caller-supplied URL is a new revision, so there is no checksum to hold it to.
if [[ -n ${BOOK_URL:-} ]]; then
  url=$BOOK_URL
  expected_sha=
else
  url=$(read_field url)
  expected_sha=$(read_field sha256)
  if [[ -z $expected_sha ]]; then
    echo "No 'sha256:' line in $version_file; refusing to fetch unverified." >&2
    exit 2
  fi
fi

if [[ -z $url ]]; then
  echo "No URL: set BOOK_URL or fill in 'url:' in $version_file" >&2
  exit 2
fi

pdf="$book_dir/$(basename "${url%%\?*}")"
tmp=$(mktemp)
tmp_txt=$(mktemp)
trap 'rm -f "$tmp" "$tmp_txt"' EXIT

echo "Downloading $url"
curl --fail --location --silent --show-error --output "$tmp" "$url"

if [[ $(head -c 5 "$tmp") != "%PDF-" ]]; then
  echo "Downloaded file is not a PDF: $url" >&2
  exit 1
fi

actual_sha=$(sha256 "$tmp")
if [[ -n $expected_sha && $actual_sha != "$expected_sha" ]]; then
  # Keep the download so it can be compared with a known-good copy.
  chmod 644 "$tmp"
  mv "$tmp" "$pdf.unverified"
  echo "The download from $url differs from the recorded checksum." >&2
  echo "  expected $expected_sha" >&2
  echo "  got      $actual_sha" >&2
  echo "Kept it as $pdf.unverified; compare it with a known-good copy" >&2
  echo "before updating $version_file." >&2
  exit 1
fi

# Extract before moving anything into place, so a failed extraction leaves the
# previous files untouched. The text moves first: the checker reads only the
# text, so if the second move fails the text is already the new revision's.
pdftotext -layout "$tmp" "$tmp_txt"
chmod 644 "$tmp" "$tmp_txt"  # mktemp creates files readable only by their owner
mv "$tmp_txt" "$book_dir/whatif.txt"
mv "$tmp" "$pdf"
trap - EXIT

echo "Saved $pdf"
echo "Extracted text to $book_dir/whatif.txt"
echo "sha256: $actual_sha"
if [[ -n ${BOOK_URL:-} ]]; then
  echo "New revision: update date, url, sha256 and pages in $version_file." >&2
fi
