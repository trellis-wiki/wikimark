#!/usr/bin/env python3
"""WikiMark test runner.

Runs test suites against a WikiMark processor and reports results.

Usage:
  python3 run_tests.py <processor_command> [options]

  <processor_command>  A command that reads WikiMark on stdin and writes HTML
                       on stdout. Example: "wikimark --to html"

Options:
  --suite SUITE        Run a specific suite: commonmark, gfm-spec,
                       gfm-extensions, wikimark-spec, wikimark-extra, or all
                       (default: all)
  --section PATTERN    Only run tests whose section matches PATTERN (substring)
  --example N          Run only example number N from the selected suite
  --source SOURCE      Only run tests from a specific source
  --fail-fast          Stop on first failure
  --verbose            Show passing tests too
  --json               Output results as JSON
  --normalize          Normalize HTML whitespace before comparing
  --list               List available tests without running them

Examples:
  # Run all WikiMark-specific tests
  python3 run_tests.py "./wikimark" --suite wikimark-spec

  # Run only wiki link tests
  python3 run_tests.py "./wikimark" --section "Wiki links"

  # Run CommonMark compliance tests
  python3 run_tests.py "./wikimark" --suite commonmark

  # List all tests
  python3 run_tests.py --list
"""

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent

SUITE_FILES = {
    "commonmark": "upstream/commonmark-spec.json",
    "gfm-spec": "upstream/gfm-spec.json",
    "gfm-extensions": "upstream/gfm-extensions.json",
    "wikimark-spec": "wikimark-spec.json",
    "wikimark-extra": "wikimark-extra.json",
}


def load_suite(name: str) -> list[dict]:
    path = TESTS_DIR / SUITE_FILES[name]
    if not path.exists():
        print(f"Warning: suite file {path} not found, skipping", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        tests = json.load(f)
    for t in tests:
        t.setdefault("source", name)
    return tests


def normalize_html(s: str) -> str:
    """Normalize HTML whitespace for comparison."""
    # Collapse runs of whitespace to single space
    s = re.sub(r"\s+", " ", s.strip())
    # Normalize self-closing tags
    s = re.sub(r"\s*/>", " />", s)
    return s


def run_processor(command: str, markdown: str, timeout: int = 10) -> tuple[str, str]:
    """Run the processor command with markdown input, return (stdout, stderr)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            input=markdown,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT"
    except Exception as e:
        return "", str(e)


def compare(expected: str, actual: str, do_normalize: bool) -> bool:
    if do_normalize:
        return normalize_html(expected) == normalize_html(actual)
    return expected == actual


def main():
    parser = argparse.ArgumentParser(description="WikiMark test runner")
    parser.add_argument("command", nargs="?", help="Processor command")
    parser.add_argument("--suite", default="all", help="Suite to run")
    parser.add_argument("--section", default=None, help="Filter by section")
    parser.add_argument("--example", type=int, default=None, help="Run single example")
    parser.add_argument("--source", default=None, help="Filter by source")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    # Determine which suites to load
    if args.suite == "all":
        suite_names = list(SUITE_FILES.keys())
    else:
        suite_names = [s.strip() for s in args.suite.split(",")]

    # Load tests
    all_tests = []
    for name in suite_names:
        if name not in SUITE_FILES:
            print(f"Unknown suite: {name}", file=sys.stderr)
            print(f"Available: {', '.join(SUITE_FILES.keys())}", file=sys.stderr)
            sys.exit(1)
        all_tests.extend(load_suite(name))

    # Apply filters
    if args.section:
        all_tests = [t for t in all_tests if args.section.lower() in t["section"].lower()]
    if args.example is not None:
        all_tests = [t for t in all_tests if t["example"] == args.example]
    if args.source:
        all_tests = [t for t in all_tests if t.get("source") == args.source]

    if not all_tests:
        print("No tests matched the filters.", file=sys.stderr)
        sys.exit(1)

    # List mode
    if args.list:
        current_source = None
        for t in all_tests:
            source = t.get("source", "unknown")
            if source != current_source:
                current_source = source
                print(f"\n=== {source} ===")
            desc = t.get("description", "")
            desc_str = f" — {desc}" if desc else ""
            print(f"  Example {t['example']:4d}  [{t['section']}]{desc_str}")
        print(f"\nTotal: {len(all_tests)} tests")
        sys.exit(0)

    # Run mode requires a command
    if not args.command:
        print("Error: processor command required (or use --list)", file=sys.stderr)
        sys.exit(1)

    # Run tests
    passed = 0
    failed = 0
    errors = 0
    results = []

    for t in all_tests:
        actual, stderr = run_processor(args.command, t["markdown"])

        if stderr == "TIMEOUT":
            status = "error"
            errors += 1
            message = "Timed out"
        elif compare(t["html"], actual, args.normalize):
            status = "pass"
            passed += 1
            message = None
        else:
            status = "fail"
            failed += 1
            message = None

        result = {
            "example": t["example"],
            "section": t["section"],
            "source": t.get("source", "unknown"),
            "status": status,
        }

        if status == "fail":
            result["expected"] = t["html"]
            result["actual"] = actual
            if not args.json:
                desc = t.get("description", "")
                desc_str = f" — {desc}" if desc else ""
                print(f"FAIL  Example {t['example']} [{t['section']}]{desc_str}")
                print(f"  Input:    {t['markdown']!r}")
                print(f"  Expected: {t['html']!r}")
                print(f"  Actual:   {actual!r}")
                if stderr:
                    print(f"  Stderr:   {stderr.strip()}")
                print()
        elif status == "error":
            result["message"] = message
            if not args.json:
                print(f"ERROR Example {t['example']} [{t['section']}]: {message}")
        elif args.verbose and not args.json:
            print(f"PASS  Example {t['example']} [{t['section']}]")

        results.append(result)

        if args.fail_fast and status in ("fail", "error"):
            break

    # Summary
    total = passed + failed + errors
    if args.json:
        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "results": results,
        }
        json.dump(summary, sys.stdout, indent=2)
        print()
    else:
        print(f"\n{'=' * 60}")
        print(f"Results: {passed} passed, {failed} failed, {errors} errors, {total} total")
        if failed == 0 and errors == 0:
            print("All tests passed!")
        print(f"{'=' * 60}")

    sys.exit(1 if (failed > 0 or errors > 0) else 0)


if __name__ == "__main__":
    main()
