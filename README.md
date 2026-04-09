# WikiMark

A strict superset of [GitHub Flavored Markdown](https://github.github.com/gfm/) that adds wiki functionality.

## Status

**Draft specification (v0.3) in progress.** Not yet stable.

## Design Principles

1. **Strict GFM superset.** Every valid GFM document is valid WikiMark with identical output.
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

- **Wiki links**: `[[Page]]`, `[[Page|display text]]`, namespaces, interwiki
- **YAML frontmatter**: Categories, TOC control, page variables, template inputs
- **Page variables**: `${title}`, `${star.name}`, `${moons.0}` — dot notation into frontmatter
- **Images**: Standard `![alt](url)` extended with Pandoc attributes `{.thumb width=300}`
- **Templates**: `{{name args}}` — transclusion or module-backed, with `${...}` variable substitution
- **Semantic annotations**: `[text]|property|` — structured data on any inline element
- **Redirects**: Frontmatter `redirect:` or `#REDIRECT [[Page]]`

## Files

- `spec.md` — The specification
- `examples/` — Example WikiMark documents

## File Extension

WikiMark files use the `.wm` extension.

## License

CC-BY-SA 4.0
