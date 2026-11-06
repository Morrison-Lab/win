"""Tests for check-duplicate-crossref-ids.py.

Run with `python3 -m unittest discover -s .github/scripts`.
"""
import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-duplicate-crossref-ids.py")
spec = importlib.util.spec_from_file_location("check_duplicate_crossref_ids", SCRIPT)
assert spec is not None and spec.loader is not None, f"cannot load {SCRIPT}"
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

FENCE3 = "`" * 3


def found_ids(text):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "page.qmd"
        path.write_text(text, encoding="utf-8")
        return [crossref_id for crossref_id, _ in module.ids_in(path)]


class IdsInTest(unittest.TestCase):
    def test_attribute_block_id(self):
        self.assertEqual(found_ids("::: {#def-foo}\ntext\n:::\n"), ["def-foo"])

    def test_unquoted_chunk_label(self):
        text = f"{FENCE3}{{r}}\n#| label: fig-a\n{FENCE3}\n"
        self.assertEqual(found_ids(text), ["fig-a"])

    def test_quoted_chunk_labels(self):
        text = (
            f"{FENCE3}{{r}}\n#| label: \"fig-a\"\n{FENCE3}\n"
            f"{FENCE3}{{r}}\n#| label: 'tbl-b'\n{FENCE3}\n"
        )
        self.assertEqual(found_ids(text), ["fig-a", "tbl-b"])

    def test_chunk_label_with_trailing_yaml_comment(self):
        text = (
            f"{FENCE3}{{r}}\n#| label: fig-a # the first plot\n{FENCE3}\n"
            f"{FENCE3}{{r}}\n#| label: \"tbl-b\"   # quoted\n{FENCE3}\n"
        )
        self.assertEqual(found_ids(text), ["fig-a", "tbl-b"])

    def test_indented_chunk_label_in_list_item(self):
        text = f"- item\n\n  {FENCE3}{{r}}\n  #| label: fig-a\n  {FENCE3}\n"
        self.assertEqual(found_ids(text), ["fig-a"])

    def test_triple_backtick_inline_span_is_not_a_fence(self):
        text = f"See {FENCE3}{{#def-example}}{FENCE3} here.\n\n::: {{#def-real}}\n"
        self.assertEqual(found_ids(text), ["def-real"])

    def test_line_starting_with_inline_triple_backticks_is_not_a_fence(self):
        text = f"{FENCE3}{{#def-example}}{FENCE3}\n\n::: {{#def-real}}\n"
        self.assertEqual(found_ids(text), ["def-real"])

    def test_chunk_label_with_trailing_text_is_not_an_id(self):
        text = f"{FENCE3}{{r}}\n#| label: fig-a extra\n{FENCE3}\n"
        self.assertEqual(found_ids(text), [])

    def test_opening_fence_attributes(self):
        text = f"{FENCE3}{{#lst-ex .python lst-cap=\"Example\"}}\nx = 1\n{FENCE3}\n"
        self.assertEqual(found_ids(text), ["lst-ex"])

    def test_plain_fence_body_is_ignored(self):
        text = f"{FENCE3}\n::: {{#def-foo}}\n{FENCE3}\n"
        self.assertEqual(found_ids(text), [])

    def test_inline_code_is_ignored(self):
        self.assertEqual(found_ids("Write `{#def-foo}` for an id.\n"), [])

    def test_comment_is_ignored(self):
        self.assertEqual(found_ids("<!-- ::: {#def-foo} -->\n"), [])

    def test_comment_marker_inside_code_span_does_not_hide_later_ids(self):
        text = "Open a comment with `<!--` first.\n\n::: {#def-foo}\n"
        self.assertEqual(found_ids(text), ["def-foo"])

    def test_code_span_crossing_lines_hides_its_id(self):
        text = "Write `the id\n{#def-foo}` here.\n"
        self.assertEqual(found_ids(text), [])

    def test_unclosed_backtick_is_literal(self):
        self.assertEqual(found_ids("A stray ` here {#sec-x}\n"), ["sec-x"])

    def test_comment_crossing_blank_lines(self):
        text = "<!-- start\n\n{#def-foo}\n\nend -->\n{#def-bar}\n"
        self.assertEqual(found_ids(text), ["def-bar"])

    def test_double_backtick_span(self):
        self.assertEqual(found_ids("``a ` {#def-foo}`` {#def-bar}\n"), ["def-bar"])


def run_main(files):
    """Run main() on a temporary book tree; return (exit code, stdout)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        argv, sys.argv = sys.argv, ["check", str(root)]
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code = module.main()
        finally:
            sys.argv = argv
        return code, out.getvalue()


class MainTest(unittest.TestCase):
    def test_duplicate_across_files_fails_with_annotation(self):
        code, out = run_main(
            {
                "index.qmd": "::: {#def-foo}\n:::\n",
                "chapters/02-a.qmd": "text\n\n::: {#def-foo}\n:::\n",
            }
        )
        self.assertEqual(code, 1)
        self.assertIn(
            "::error file=chapters/02-a.qmd,line=3::Duplicate crossref id #def-foo: "
            "chapters/02-a.qmd:3, index.qmd:1",
            out,
        )
        self.assertIn("Rename one side", out)

    def test_unique_ids_pass(self):
        code, out = run_main(
            {
                "index.qmd": "::: {#def-foo}\n:::\n",
                "chapters/02-a.qmd": "::: {#def-bar}\n:::\n",
            }
        )
        self.assertEqual(code, 0)
        self.assertIn("No duplicate crossref ids in 2 files.", out)


if __name__ == "__main__":
    unittest.main()
