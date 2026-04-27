# WikiMark

A superset of [GitHub Flavored Markdown](https://github.github.com/gfm/) that adds wiki functionality. WikiMark extends GFM with wiki links, templates, semantic annotations, and page metadata. All GFM syntax works unchanged except for one intentional deviation: relative links (`[text](target)` without a URI scheme) are treated as wiki page links.

## Status

**Draft specification (v0.5).** Feature-complete on paper and
validated against a C reference implementation
([libwikimark](https://github.com/trellis-wiki/libwikimark)) that
passes the full test suite. **Not yet validated against a real-world
wiki** — v1.0 is gated on migrating an existing MediaWiki instance
onto the spec via Trellis + mw2wm. See [PLAN.md](PLAN.md).

## Design Principles

1. **GFM superset.** Every valid GFM document is valid WikiMark. Output is identical except that relative links are treated as wiki page links.
2. **GFM first.** Use existing GFM features (footnotes, tables, images) as-is.
3. **Adopt established conventions.** YAML frontmatter, Pandoc attributes, Obsidian-style wiki links.
4. **Templates as the extension mechanism.** No built-in parser functions — extend via modules.
5. **Four bracket types, four concerns.**

| Bracket | Purpose | Example |
|---|---|---|
| `[text]` | Display content | `[Paris]` |
| `(url)` | Link target | `(https://example.com)` |
| `{.class key=value}` | Presentation | `{.highlight width=300}` |
| `\|property key=value\|` | Semantic data | `\|capital\|` |

## Features

- **Wiki links**: `[[Page]]`, `[display text](Page)`, namespaces, interwiki
- **YAML frontmatter**: Categories, TOC control, page variables, template inputs
- **Page variables**: `${title}`, `${star.name}`, `${moons.0}` — dot notation into frontmatter
- **Images**: Standard `![alt](url)` extended with Pandoc attributes `{.thumb width=300}`
- **Templates**: `{{name args}}` — transclusion or module-backed, with `${...}` variable substitution
- **Semantic annotations**: `[text]|property|` — structured data on any inline element
- **Redirects**: Frontmatter `redirect: Target`

## Files

- `spec.md` — The specification
- `examples/` — Example WikiMark documents
- `tests/` — Comprehensive test suite (1,556 input/output pairs: 652 CommonMark, 672 GFM, 30 GFM extensions, 92 WikiMark spec, 110 WikiMark regression)
- `PLAN.md` — Work remaining before v1.0

## File Extension

WikiMark files use the `.wm` extension.

## Acknowledgments

WikiMark builds on the work of several projects:

- **[Markdown](https://daringfireball.net/projects/markdown/)** — John Gruber's original lightweight markup language (2004).
- **[CommonMark](https://commonmark.org/)** — A strongly defined, highly compatible specification of Markdown by John MacFarlane et al. (CC-BY-SA 4.0).
- **[GitHub Flavored Markdown (GFM)](https://github.github.com/gfm/)** — GitHub's strict superset of CommonMark, which WikiMark in turn extends.

WikiMark also draws on conventions established by [MediaWiki](https://www.mediawiki.org/), [Pandoc](https://pandoc.org/), and [Obsidian](https://obsidian.md/).

## License

This specification is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

See [LICENSE](LICENSE) for the full text.

[cc-by-sa]: https://creativecommons.org/licenses/by-sa/4.0/
