# WikiMark Test Suite

Comprehensive input/output test cases for WikiMark implementations. All tests follow the [CommonMark spec.json format](https://spec.commonmark.org/0.31.2/spec.json): each test has a `markdown` input, an expected `html` output, an `example` number, and a `section` name.

## Test suites

| Suite | File | Tests | Description |
| --- | --- | --- | --- |
| CommonMark | `upstream/commonmark-spec.json` | 652 | [CommonMark 0.31.2](https://spec.commonmark.org/) — baseline Markdown compliance |
| GFM spec | `upstream/gfm-spec.json` | 672 | [GFM 0.29](https://github.github.com/gfm/) — full GFM spec (superset of CommonMark) |
| GFM extensions | `upstream/gfm-extensions.json` | 30 | GFM extension tests (tables, strikethrough, autolinks, task lists) |
| WikiMark spec | `wikimark-spec.json` | 92 | Examples extracted from [spec.md](../spec.md) |
| WikiMark extra | `wikimark-extra.json` | 100 | Additional edge cases and regression tests |

**Total: 1,546 tests** (894 unique — CommonMark tests overlap between `commonmark-spec.json` and `gfm-spec.json`).

## Test format

Each test is a JSON object:

```json
{
  "markdown": "[[Main Page]]\n",
  "html": "<p><a href=\"Main_Page\">Main Page</a></p>\n",
  "example": 1,
  "section": "7.1 Basic wiki links",
  "source": "wikimark-spec",
  "description": "Basic wiki link with space in target"
}
```

- **`markdown`** — Input WikiMark/Markdown source
- **`html`** — Expected HTML output
- **`example`** — Sequential test number within the suite
- **`section`** — Spec section the test belongs to
- **`source`** — Which suite the test came from
- **`description`** (optional) — Human-readable description

## Running tests

The test runner (`run_tests.py`) takes any command that reads WikiMark on stdin and writes HTML on stdout:

```bash
# Run all tests against your implementation
python3 tests/run_tests.py "./your-wikimark-processor"

# Run only WikiMark-specific tests
python3 tests/run_tests.py "./your-processor" --suite wikimark-spec,wikimark-extra

# Run CommonMark compliance
python3 tests/run_tests.py "./your-processor" --suite commonmark

# Run only wiki link tests
python3 tests/run_tests.py "./your-processor" --section "Wiki links"

# Run a single test
python3 tests/run_tests.py "./your-processor" --suite wikimark-spec --example 5

# List all tests without running
python3 tests/run_tests.py --list

# Normalize whitespace for comparison
python3 tests/run_tests.py "./your-processor" --normalize

# JSON output for CI
python3 tests/run_tests.py "./your-processor" --json
```

## Regenerating spec tests

If `spec.md` is updated, regenerate the extracted tests:

```bash
python3 tests/extract_tests.py
```

This re-extracts examples from `spec.md` and the upstream GFM spec files, and rebuilds `index.json`.

## Upstream sources

- **CommonMark 0.31.2**: Downloaded from [spec.commonmark.org](https://spec.commonmark.org/0.31.2/spec.json)
- **GFM 0.29**: Extracted from [github/cmark-gfm](https://github.com/github/cmark-gfm) (`test/spec.txt` and `test/extensions.txt`)

Since WikiMark is a strict superset of GFM (which is a strict superset of CommonMark), a conforming WikiMark processor **must pass all upstream tests** in addition to the WikiMark-specific tests.

## License

Upstream test suites retain their original licenses (CC-BY-SA 4.0 for CommonMark, CC-BY-SA 4.0 for GFM). WikiMark-specific tests are licensed under CC-BY-SA 4.0, matching the spec.
