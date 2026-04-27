#!/usr/bin/env python3
"""Extract test cases from CommonMark/GFM-style spec files and WikiMark spec.md.

Outputs JSON in CommonMark spec.json format:
  { "markdown": "...", "html": "...", "example": N, "section": "...",
    "start_line": N, "end_line": N, "source": "..." }

Usage:
  python3 extract_tests.py                    # extract all, write to tests/
  python3 extract_tests.py --spec-only        # only WikiMark spec tests
  python3 extract_tests.py --upstream-only    # only GFM spec + extensions
"""

import json
import re
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
SPEC_FILE = TESTS_DIR.parent / "spec.md"
GFM_SPEC = TESTS_DIR / "upstream" / "gfm-spec.txt"
GFM_EXT = TESTS_DIR / "upstream" / "gfm-extensions.txt"

EXAMPLE_FENCE = re.compile(r"^`{32} example\s*(.*)?$")
CLOSE_FENCE = re.compile(r"^`{32}$")
SECTION_RE = re.compile(r"^#{1,6}\s+(.+)$")


def extract_from_spec_txt(path: Path, source: str, start_example: int = 1):
    """Extract examples from a CommonMark/GFM-style spec.txt file."""
    tests = []
    section = ""
    example = start_example

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        # Track current section heading
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1).strip()

        # Look for example fences
        m = EXAMPLE_FENCE.match(line)
        if m:
            extensions = m.group(1).strip() if m.group(1) else ""
            start_line = i + 1  # 1-based
            i += 1
            markdown_lines = []
            html_lines = []
            in_html = False

            while i < len(lines):
                eline = lines[i].rstrip("\n")
                if CLOSE_FENCE.match(eline):
                    break
                if eline == "." and not in_html:
                    in_html = True
                    i += 1
                    continue
                # Replace → with tab (CommonMark convention)
                eline = eline.replace("→", "\t")
                if in_html:
                    html_lines.append(eline)
                else:
                    markdown_lines.append(eline)
                i += 1

            end_line = i + 1  # 1-based
            test = {
                "markdown": "\n".join(markdown_lines) + "\n",
                "html": "\n".join(html_lines) + "\n",
                "example": example,
                "start_line": start_line,
                "end_line": end_line,
                "section": section,
                "source": source,
            }
            if extensions:
                test["extensions"] = extensions.split()
            tests.append(test)
            example += 1

        i += 1

    return tests


def extract_from_wikimark_spec(path: Path, start_example: int = 1):
    """Extract examples from WikiMark spec.md (same fence format)."""
    return extract_from_spec_txt(path, source="wikimark", start_example=start_example)


def main():
    spec_only = "--spec-only" in sys.argv
    upstream_only = "--upstream-only" in sys.argv

    # Extract upstream tests
    if not spec_only:
        gfm_tests = []
        if GFM_SPEC.exists():
            gfm_tests = extract_from_spec_txt(GFM_SPEC, source="gfm-spec")
            out = TESTS_DIR / "upstream" / "gfm-spec.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(gfm_tests, f, indent=2, ensure_ascii=False)
            print(f"Extracted {len(gfm_tests)} tests from GFM spec → {out}")

        gfm_ext_tests = []
        if GFM_EXT.exists():
            start = len(gfm_tests) + 1
            gfm_ext_tests = extract_from_spec_txt(GFM_EXT, source="gfm-extensions", start_example=start)
            out = TESTS_DIR / "upstream" / "gfm-extensions.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(gfm_ext_tests, f, indent=2, ensure_ascii=False)
            print(f"Extracted {len(gfm_ext_tests)} tests from GFM extensions → {out}")

    # Extract WikiMark spec tests
    if not upstream_only:
        if SPEC_FILE.exists():
            wm_tests = extract_from_wikimark_spec(SPEC_FILE)
            out = TESTS_DIR / "wikimark-spec.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(wm_tests, f, indent=2, ensure_ascii=False)
            print(f"Extracted {len(wm_tests)} tests from WikiMark spec → {out}")

    # Build combined index
    if not spec_only and not upstream_only:
        cm_path = TESTS_DIR / "upstream" / "commonmark-spec.json"
        cm_tests = []
        if cm_path.exists():
            with open(cm_path, encoding="utf-8") as f:
                cm_tests = json.load(f)
            # Add source field
            for t in cm_tests:
                t.setdefault("source", "commonmark")

        summary = {
            "description": "WikiMark test suite index",
            "suites": {
                "commonmark": {
                    "file": "upstream/commonmark-spec.json",
                    "count": len(cm_tests),
                    "description": "CommonMark 0.31.2 specification tests",
                },
                "gfm-spec": {
                    "file": "upstream/gfm-spec.json",
                    "count": len(gfm_tests),
                    "description": "GFM specification tests (includes CommonMark)",
                },
                "gfm-extensions": {
                    "file": "upstream/gfm-extensions.json",
                    "count": len(gfm_ext_tests),
                    "description": "GFM extension tests (tables, strikethrough, autolinks, task lists)",
                },
                "wikimark-spec": {
                    "file": "wikimark-spec.json",
                    "count": len(wm_tests),
                    "description": "WikiMark specification examples",
                },
            },
        }
        out = TESTS_DIR / "index.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\nWrote suite index → {out}")
        for name, info in summary["suites"].items():
            print(f"  {name}: {info['count']} tests")


if __name__ == "__main__":
    main()
