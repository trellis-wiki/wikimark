# WikiMark

The WikiMark specification (`spec.md`) and its language-independent test suite
(`tests/`). See `README.md` for the design principles and `PLAN.md` for what is
left before v1.0.

- Sibling repos in the `trellis-wiki` org: `libwikimark` (C reference
  implementation, runs this suite), `wikimark-python` (bindings) and `mw2wm`
  (MediaWiki converter). Trellis (`trellis-wiki/trellis`) is the wiki engine
  built on them. On a DSKY satellite they sit next to this repo as `../<name>/`.
- A behavior change goes into `spec.md` and gets test cases in
  `tests/wikimark-extra.json` (regressions and edge cases) or
  `tests/wikimark-spec.json` (examples extracted from the spec with
  `tests/extract_tests.py`). Run them through libwikimark: `ctest` in
  `../libwikimark/build` uses `tests/run_tests.py` from this repo.
- This repo is public. Never put content from Nick's wiki in it; use invented
  names in examples and tests.
