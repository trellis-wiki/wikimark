# WikiMark Specification

Version 0.5 (Draft)

## 1 Introduction

### 1.1 What is WikiMark?

WikiMark is a markup language that extends [GitHub Flavored Markdown][GFM]
with wiki-oriented features including wiki links, templates, semantic
annotations, page-level variables, and structured page metadata.

WikiMark is a **strict superset** of GFM. Every conforming GFM document
is a conforming WikiMark document, and a conforming WikiMark processor
MUST produce output identical to a conforming GFM processor for any input
that contains no WikiMark extensions.

[GFM]: https://github.github.com/gfm/

### 1.2 Design principles

1. **Strict superset.** WikiMark MUST NOT change the meaning of any valid
   GFM construct. All extensions use syntax that has no defined meaning
   in GFM.

2. **GFM first.** Where GFM already provides a feature, WikiMark uses it
   as-is. For example, WikiMark uses GFM footnotes (`[^id]`) for
   references, GFM tables for tabular data, and standard Markdown images
   (`![alt](url)`) for media embedding.

3. **Adopt established conventions.** Where GFM has no equivalent,
   WikiMark adopts syntax from widely-used Markdown extensions: YAML
   frontmatter for page metadata, Pandoc-style attributes (`{key=value}`)
   for presentation, and wiki links (`[[page]]`) from the knowledge
   management ecosystem (Obsidian, Foam, Dendron, etc.).

4. **Templates as the extension mechanism.** Rather than baking special
   functions into the syntax, WikiMark provides a template system that
   supports simple text transclusion through to module-backed code
   execution. New capabilities are added by installing modules, not by
   extending the spec.

5. **Four bracket types, four concerns.** WikiMark assigns a distinct
   role to each bracket type:
   - `[text]` — display content
   - `(url)` — link target
   - `{.class key=value}` — presentation attributes
   - `|property key=value|` — semantic data

6. **Formally specified.** Every construct is defined with prose rules and
   numbered examples showing input and expected HTML output.

### 1.3 Relationship to GFM

WikiMark inherits the full [GFM specification (version 0.29)][GFM]
unchanged. Sections of this specification that describe inherited behavior
say "inherits GFM" and do not reproduce the GFM rules. Implementors MUST
also implement GFM 0.29.

WikiMark adds new syntax in positions that are unambiguous in GFM:

- `[[...]]` and `![[...]]` (double brackets) are not valid GFM syntax.
- `{{...}}` (double braces) has no GFM meaning.
- `${...}` (dollar-brace) has no GFM meaning. The `$` character alone
  is NOT special; only the two-character sequence `${` triggers variable
  parsing. This avoids conflict with LaTeX math syntax (`$x^{2}$`).
- `{key=value}` after inline elements follows the Pandoc attribute
  convention, which has no GFM meaning.
- `|...|` after `]`, `)`, or `}` as semantic data has no GFM inline
  meaning (`|` is only meaningful at the block level for tables).
- YAML frontmatter (`---` delimited) is widely supported but not part of
  the GFM spec; it has no GFM meaning.
WikiMark redefines the behavior of one GFM construct:

- **Relative links.** In GFM, `[text](target)` where `target` has no
  URI scheme creates a relative filesystem link. In WikiMark, such links
  are **wiki page links**: the target is a page name within the wiki's
  namespace. There are no relative filesystem links in a wiki context —
  the wiki namespace is the context. Links with an RFC 3986 scheme
  (`https:`, `mailto:`, etc.), fragment anchors (`#`), or explicit
  path prefixes (`/`, `./`, `../`) retain their standard GFM meaning.

This is the only intentional deviation from GFM behavior. All other GFM
constructs are preserved unchanged.

### 1.4 Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in [RFC 2119].

[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119

### 1.5 Examples

Examples are numbered sequentially throughout this specification. Each
example shows WikiMark input and the expected HTML output, separated by a
period on its own line:

```````````````````````````````` example
[[Example Page]]
.
<p><a href="Example_Page">Example Page</a></p>
````````````````````````````````

Whitespace in HTML output is insignificant unless otherwise noted.

### 1.6 File extension

WikiMark files SHOULD use the `.wm` extension.

---

## 2 Preliminaries

### 2.1 Characters, lines, tabs, and insecure characters

WikiMark inherits GFM sections 2.1–2.3 unchanged.

### 2.2 WikiMark processing model

A conforming WikiMark processor operates in four phases:

**Phase 1: Frontmatter extraction.** If the document begins with a `---`
line, the processor extracts the YAML frontmatter block (see
[section 8](#8-page-metadata-frontmatter)). The frontmatter is removed
from the document body before further processing. If the frontmatter
contains an `inputs` block, provided input values (or defaults) are
promoted to top-level frontmatter keys (see
[section 8.8](#88-the-inputs-block)).

**Phase 2: Block structure.** The remaining input is parsed line-by-line
into a tree of block-level elements, following the GFM block-parsing
algorithm.

**Phase 3: Inline structure.** The text content of each leaf block is
parsed into inline elements, following the GFM inline-parsing algorithm.
In addition to GFM inline types, WikiMark recognizes:

- [Variable references](#82-variable-references) (`${...}`) (section 8.2)
- [Wiki links](#7-wiki-links) (`[[...]]`) (section 7)
- [Template transclusions](#11-templates) (`{{...}}`) (section 11)
- [Presentation attributes](#10-images-and-media) (`{...}`) on images
  and other elements (section 10)
- [Semantic annotations](#12-semantic-annotations) (`|...|`) (section 12)

**Phase 4: Expansion.** Variable references and template transclusions
are expanded. Each is processed as WikiMark in its own context (variables
resolved, wiki links parsed, etc.) to produce output. That output is then
inserted **literally** into the calling document — it is NOT re-parsed
for WikiMark constructs. This prevents injection of closing delimiters
and ensures templates and variables are self-contained.

Processors MUST enforce a maximum expansion depth (see
[section 11.9](#119-recursion-and-depth-limits)).

After all four phases, the processor emits the final HTML output.

### 2.3 Inline parsing precedence

When multiple WikiMark inline constructs could match at the same
position, the following precedence rules apply (highest to lowest):

1. Code spans (`` ` ``) — inherited from GFM; content is literal.
2. Autolinks (`<...>`) — inherited from GFM.
3. Raw HTML tags — inherited from GFM.
4. Wiki links (`[[...]]`).
5. Template transclusions (`{{...}}`).
6. Variable references (`${...}`).
7. All other GFM inlines (emphasis, links, images, etc.).
8. Presentation attributes (`{...}`) — attach to the preceding element.
9. Semantic annotations (`|...|`) — attach to the preceding element.

Within a `[[...]]` or `{{...}}` span, the opening delimiter takes
precedence: the processor MUST scan for the matching closing delimiter
(`]]` or `}}`) before attempting to parse the interior as other
constructs.

### 2.4 Quote-aware scanning

All delimiter scanners (`]]`, `}}`, `}`, `|`) MUST be **quote-aware**.
Content inside double-quoted strings (`"..."`) is treated as literal text
and MUST NOT be scanned for closing delimiters. This applies to:

- Template arguments: `{{template arg="value}}not closed"}}`
- Presentation attributes: `{caption="photo} nice"}`
- Semantic annotations: `|property="a|b"|`

A `"` inside a quoted string MAY be escaped with a backslash: `\"`.

### 2.5 Unclosed delimiters

A `[[` that is not closed by a matching `]]` within the same block
element MUST be treated as literal text. The same applies to unmatched
`{{`, `${`, `{` in attribute position, and `|` in annotation position.
This is consistent with how GFM handles unclosed constructs.

### 2.6 The `$` character

The `$` character is only special when immediately followed by `{`,
forming the two-character sequence `${`. A lone `$` is literal text.
This preserves compatibility with LaTeX math syntax:

```````````````````````````````` example
---
title: Earth
---

The equation $x^{2}$ uses ${title}.
.
<p>The equation $x^{2}$ uses Earth.</p>
````````````````````````````````

In this example, `$x^{2}$` is literal text (the `$` is not followed by
`{` in a way that forms a valid variable reference), while `${title}`
is a variable reference.

---

## 3 Blocks and inlines

### 3.1 Inherited block and inline types

WikiMark inherits all GFM block and inline types unchanged. See [GFM
section 3][GFM].

### 3.2 Wiki block elements

WikiMark adds the following block-level constructs:

- **Callout** (container block): A block quote beginning with `[!TYPE]`.
  See [section 5.1](#51-callouts-admonitions).
- **Page embed** (leaf block): `![[page]]` transcludes another page's
  content. See [section 7.9](#79-page-embeds-).

### 3.3 Wiki inline elements

WikiMark adds the following inline constructs:

- **Variable reference**: `${key}` or `${path.to.key}`. See
  [section 8.2](#82-variable-references).
- **Wiki link**: `[[target]]`. See [section 7](#7-wiki-links).
- **Template transclusion**: `{{name args}}`. See
  [section 11](#11-templates).
- **Semantic annotation**: `|property|` or `|property key=value|`
  attached to a preceding element. See
  [section 12](#12-semantic-annotations).

### 3.4 Extended elements

WikiMark extends GFM elements with optional trailing modifiers:

- **Images**: `![alt](url)` MAY be followed by `{attributes}` for
  presentation and/or `|annotations|` for semantic data.
  See [section 10](#10-images-and-media).
- **Links**: `[text](url)` MAY be followed by `{attributes}` and/or
  `|annotations|`.
- **Wiki links**: `[[target]]` MAY be followed by `{attributes}` and/or
  `|annotations|`.

### 3.5 Spans

A bare `[text]` with no following `(url)`, `{attributes}`, or
`|annotations|` is **not** a WikiMark construct — it follows standard
GFM behavior (treated as a link reference attempt; if no reference
definition matches, it is literal text).

A `[text]` immediately followed by `{...}` or `|...|` becomes a
**WikiMark span**: `[text]` provides the display content, and the
trailing modifier provides attributes or annotations.

```````````````````````````````` example
[highlighted]{.highlight}
.
<p><span class="highlight">highlighted</span></p>
````````````````````````````````

```````````````````````````````` example
[Paris]|capital|
.
<p><span data-wm-property="capital">Paris</span></p>
````````````````````````````````

```````````````````````````````` example
[Paris]{.highlight}|capital|
.
<p><span class="highlight" data-wm-property="capital">Paris</span></p>
````````````````````````````````

A bare `[text]` with nothing following is literal:

```````````````````````````````` example
This is [just text] in brackets.
.
<p>This is [just text] in brackets.</p>
````````````````````````````````

---

## 4 Leaf blocks

### 4.1–4.10 Inherited leaf blocks

WikiMark inherits GFM leaf blocks (thematic breaks, ATX headings, setext
headings, indented code blocks, fenced code blocks, link reference
definitions, paragraphs, blank lines, HTML blocks, and tables) unchanged.

---

## 5 Container blocks

WikiMark inherits all GFM container blocks (block quotes, list items,
lists) unchanged.

### 5.1 Callouts (admonitions)

WikiMark adopts the GitHub / Obsidian callout syntax. A **callout** is a
block quote whose first line contains a callout type marker:

```````````````````````````````` example
> [!NOTE]
> This is a note.
.
<div class="wm-callout wm-callout-note">
<p class="wm-callout-title">Note</p>
<p>This is a note.</p>
</div>
````````````````````````````````

#### 5.1.1 Callout types

The following callout types are RECOMMENDED:

| Type | Description |
| --- | --- |
| `NOTE` | Informational note |
| `TIP` | Helpful tip |
| `IMPORTANT` | Important information |
| `WARNING` | Warning |
| `CAUTION` | Dangerous or destructive action |

Implementations MAY support additional callout types. Unrecognized types
SHOULD be rendered as generic callouts.

#### 5.1.2 Custom titles

A callout MAY include a custom title after the type marker:

```````````````````````````````` example
> [!WARNING] Do not delete this file
> It contains critical configuration.
.
<div class="wm-callout wm-callout-warning">
<p class="wm-callout-title">Do not delete this file</p>
<p>It contains critical configuration.</p>
</div>
````````````````````````````````

#### 5.1.3 Callout content

Callout content follows standard block quote rules. It MAY contain any
WikiMark block or inline content:

```````````````````````````````` example
> [!TIP]
> Use [[wiki links]] and `${variables}` in callouts.
>
> They support **all** WikiMark features.
.
<div class="wm-callout wm-callout-tip">
<p class="wm-callout-title">Tip</p>
<p>Use <a href="wiki_links">wiki links</a> and <code>${variables}</code> in callouts.</p>
<p>They support <strong>all</strong> WikiMark features.</p>
</div>
````````````````````````````````

#### 5.1.4 Strict superset compatibility

A GFM processor renders callout syntax as a regular block quote with
`[!TYPE]` as literal text. WikiMark gives it additional meaning (styled
rendering), but the content remains accessible. This is consistent with
the strict-superset property: the content is not lost, only enhanced.

---

## 6 Inlines

### 6.1–6.14 Inherited inlines

WikiMark inherits all GFM inline constructs (backslash escapes, entity
and numeric character references, code spans, emphasis and strong
emphasis, strikethrough, links, images, autolinks, autolinks extension,
raw HTML, hard line breaks, soft line breaks, and textual content)
unchanged.

### 6.15 Variable reference inlines

See [section 8.2](#82-variable-references).

### 6.16 Wiki link inlines

See [section 7](#7-wiki-links).

### 6.17 Template transclusion inlines

See [section 11](#11-templates).

### 6.18 Semantic annotation inlines

See [section 12](#12-semantic-annotations).

---

## 7 Wiki links

A **wiki link** is an inline construct that creates a hyperlink to
another page within the same wiki or knowledge base.

### 7.1 Basic wiki links

A wiki link consists of an opening `[[`, a **link target**, and a closing
`]]`. The link target MUST NOT be empty, MUST NOT contain `]]`, `[`,
or `]` characters, and MUST NOT contain line endings.

The link target is [normalized](#13-normalization-rules) to produce a URL.
The display text is the original link target.

```````````````````````````````` example
[[Main Page]]
.
<p><a href="Main_Page">Main Page</a></p>
````````````````````````````````

```````````````````````````````` example
[[hello world]]
.
<p><a href="hello_world">hello world</a></p>
````````````````````````````````

Multiple wiki links can appear in the same paragraph:

```````````````````````````````` example
See [[Alpha]] and [[Beta]].
.
<p>See <a href="Alpha">Alpha</a> and <a href="Beta">Beta</a>.</p>
````````````````````````````````

An empty wiki link is treated as literal text:

```````````````````````````````` example
[[]]
.
<p>[[]]</p>
````````````````````````````````

An unclosed wiki link is treated as literal text:

```````````````````````````````` example
[[Main Page
.
<p>[[Main Page</p>
````````````````````````````````

### 7.2 Wiki-style Markdown links (custom display text)

To display custom text for a wiki link, use standard Markdown link syntax
with a wiki page target. In WikiMark, all Markdown links without a URI
scheme resolve to wiki pages — there are no relative filesystem links in
a wiki context (see [section 1.3](#13-relationship-to-gfm)). Use
underscores for spaces in the target:

```````````````````````````````` example
[go home](Main_Page)
.
<p><a href="Main_Page">go home</a></p>
````````````````````````````````

A Markdown link is treated as a wiki link unless the URL:
- Has an RFC 3986 scheme (`https:`, `mailto:`, `tel:`, etc.)
- Starts with `#` (fragment anchor)
- Starts with `/` (absolute path)
- Starts with `./` or `../` (explicit relative path)

Wiki targets are [normalized](#13-normalization-rules) the same way as
`[[...]]` wiki link targets.

```````````````````````````````` example
[go **home**](Main_Page)
.
<p><a href="Main_Page">go <strong>home</strong></a></p>
````````````````````````````````

Links with a protocol are standard GFM links, not wiki links:

```````````````````````````````` example
[external](https://example.com)
.
<p><a href="https://example.com">external</a></p>
````````````````````````````````

Anchors and explicit paths are also standard links, not wiki links:

```````````````````````````````` example
[section](#introduction)
.
<p><a href="#introduction">section</a></p>
````````````````````````````````

```````````````````````````````` example
[email](mailto:user@example.com)
.
<p><a href="mailto:user@example.com">email</a></p>
````````````````````````````````

### 7.3 Namespace-prefixed links

A wiki link target MAY begin with a namespace prefix: an identifier
followed by `:`. The namespace becomes part of the URL path.

```````````````````````````````` example
[[Help:Editing]]
.
<p><a href="Help:Editing">Help:Editing</a></p>
````````````````````````````````

For custom display text with namespaced targets, use wiki-style Markdown
links:

```````````````````````````````` example
[how to edit](Help:Editing)
.
<p><a href="Help:Editing">how to edit</a></p>
````````````````````````````````

### 7.4 Interwiki links

An interwiki link uses a registered prefix followed by `:` and a page
name. The set of interwiki prefixes is implementation-defined.

```````````````````````````````` example
[[wikipedia:Markdown]]
.
<p><a href="https://en.wikipedia.org/wiki/Markdown">wikipedia:Markdown</a></p>
````````````````````````````````

The URL template for each interwiki prefix is configured by the
implementation. Implementations MUST NOT treat unknown prefixes as
interwiki links; they SHOULD be treated as namespace-prefixed links.

### 7.5 Wiki links vs. Markdown links

Wiki links (`[[...]]`) and GFM links (`[text](url)`) are distinct
constructs. They MAY coexist in the same document. Wiki links are parsed
at higher precedence than GFM links (see
[section 2.3](#23-inline-parsing-precedence)).

```````````````````````````````` example
See [[Main Page]] and [external](https://example.com).
.
<p>See <a href="Main_Page">Main Page</a> and <a href="https://example.com">external</a>.</p>
````````````````````````````````

### 7.6 Escaping wiki link syntax

A backslash before `[` prevents wiki link parsing, following GFM's
backslash escape rules:

```````````````````````````````` example
\[\[not a link]]
.
<p>[[not a link]]</p>
````````````````````````````````

Wiki links inside code spans are not parsed:

```````````````````````````````` example
`[[not a link]]`
.
<p><code>[[not a link]]</code></p>
````````````````````````````````

### 7.7 Wiki links in GFM tables

Wiki links work inside GFM table cells without conflict, since wiki
links do not use `|`:

```````````````````````````````` example
| Column A | Column B |
| --- | --- |
| [[Page]] | text |
.
<table>
<thead>
<tr>
<th>Column A</th>
<th>Column B</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="Page">Page</a></td>
<td>text</td>
</tr>
</tbody>
</table>
````````````````````````````````

### 7.8 Modifiers on wiki links

Wiki links MAY be followed by presentation attributes and/or semantic
annotations, in that order:

```````````````````````````````` example
[[Paris]]{.highlight}
.
<p><a href="Paris" class="highlight">Paris</a></p>
````````````````````````````````

```````````````````````````````` example
[[Paris]]|capital|
.
<p><a href="Paris" data-wm-property="capital">Paris</a></p>
````````````````````````````````

```````````````````````````````` example
[[Paris]]{.highlight}|capital|
.
<p><a href="Paris" class="highlight" data-wm-property="capital">Paris</a></p>
````````````````````````````````

See [section 10](#10-images-and-media) for presentation attributes and
[section 12](#12-semantic-annotations) for semantic annotation syntax.

### 7.9 Page embeds (`![[...]]`)

A **page embed** transcludes another page's content inline, analogous to
how `!` turns a Markdown link into an image. The syntax is `![[target]]`.

```````````````````````````````` example
![[greeting]]
.
<div class="wm-embed">Hello, world!</div>
````````````````````````````````

In this example, the page "greeting" contains `Hello, world!`. The
page's content is processed as WikiMark in its own context and the
output is inserted literally (same expansion model as templates and
variables).

#### 7.9.1 Section embeds

A page embed MAY target a specific section using `#`:

```````````````````````````````` example
![[Main Page#History]]
.
<div class="wm-embed">Content of the History section.</div>
````````````````````````````````

The section is identified by heading text, matched case-insensitively
after normalization. The embed includes the heading and all content up
to the next heading of equal or higher level.

#### 7.9.2 Embed with display fallback

If the target page does not exist, the embed MUST produce an error
indicator:

```````````````````````````````` example
![[nonexistent]]
.
<p><span class="wm-error">![[nonexistent]]</span></p>
````````````````````````````````

#### 7.9.3 Embed vs. template

`![[page]]` and `{{template}}` are distinct:

- `![[page]]` includes a page's rendered content as-is. No arguments.
  The page is processed in its own context.
- `{{template args}}` invokes a template with arguments. The template's
  `inputs` block maps arguments to variables.

Both produce literal output that is not re-parsed by the calling page.

#### 7.9.4 Embed depth limits

Embeds follow the same recursion and depth limits as templates (see
[section 11.9](#119-recursion-and-depth-limits)). An embed that
exceeds the depth limit MUST produce an error indicator.

### 7.10 Wiki links inside GFM link text

A wiki link MUST NOT appear inside the text of a GFM link, because this
would produce nested `<a>` elements (invalid HTML). If `[[` appears
inside GFM link text, it MUST be treated as literal text:

```````````````````````````````` example
[click [[here]]](https://example.com)
.
<p><a href="https://example.com">click [[here]]</a></p>
````````````````````````````````

---

## 8 Page metadata (frontmatter)

WikiMark uses YAML frontmatter for page-level metadata and variables.
Frontmatter is a YAML block delimited by `---` lines at the very
beginning of the document.

### 8.1 Basic frontmatter

```````````````````````````````` example
---
title: My Page
---

Some content.
.
<p>Some content.</p>
````````````````````````````````

Frontmatter is not rendered as visible content. It is extracted during
phase 1 of processing (see [section 2.2](#22-wikimark-processing-model))
and made available as structured metadata.

### 8.2 Variable references

Any frontmatter value can be referenced inline using `${...}` syntax
with dot notation for nested access:

```````````````````````````````` example
---
title: Earth
radius_km: 6371
---

# ${title}

${title} has a radius of ${radius_km} km.
.
<h1>Earth</h1>
<p>Earth has a radius of 6371 km.</p>
````````````````````````````````

Dot notation traverses nested YAML structures:

```````````````````````````````` example
---
star:
  name: Sol
  type: G2V
---

Orbits ${star.name}, a ${star.type} star.
.
<p>Orbits Sol, a G2V star.</p>
````````````````````````````````

Array elements are accessed by zero-based index:

```````````````````````````````` example
---
moons:
  - Luna
  - Deimos
---

Primary moon: ${moons.0}.
.
<p>Primary moon: Luna.</p>
````````````````````````````````

### 8.3 Expansion model

When a variable reference `${key}` is resolved, the retrieved value is
processed as WikiMark in its own context (wiki links parsed, nested
variable references resolved, etc.) to produce output. That output is
then inserted **literally** into the document — it is not re-parsed by
the calling page. This is the same expansion model used by templates
(see [section 11](#11-templates)).

```````````````````````````````` example
---
title: "See [[Main Page]] for details"
---

${title}
.
<p>See <a href="Main_Page">Main Page</a> for details</p>
````````````````````````````````

The wiki link inside the frontmatter value is parsed during expansion.
The resulting HTML is inserted literally.

### 8.4 Undefined variables

If a variable reference cannot be resolved (the key does not exist in the
frontmatter), it MUST be replaced with an empty string:

```````````````````````````````` example
---
title: Earth
---

Author: ${author}.
.
<p>Author: .</p>
````````````````````````````````

An empty variable reference `${}` is treated as an undefined variable
and resolves to an empty string.

### 8.5 Escaping variable references

To include a literal `${` in output, use a backslash escape:

```````````````````````````````` example
The syntax is \${variable}.
.
<p>The syntax is ${variable}.</p>
````````````````````````````````

Variable references inside code spans are not expanded:

```````````````````````````````` example
Use `${title}` to reference the title.
.
<p>Use <code>${title}</code> to reference the title.</p>
````````````````````````````````

The `$` character alone is not special — only `${` triggers variable
parsing (see [section 2.6](#26-the--character)):

```````````````````````````````` example
---
title: Earth
---

The cost is $50 and ${title} is the page.
.
<p>The cost is $50 and Earth is the page.</p>
````````````````````````````````

### 8.6 Categories

Pages declare category membership in frontmatter:

```````````````````````````````` example
---
categories:
  - Planets
  - Solar System
---

Earth is a planet.
.
<p>Earth is a planet.</p>
````````````````````````````````

Implementations SHOULD collect categories and MAY render them in a
standard location (e.g., the bottom of the page):

    <nav class="wm-categories">
      <span class="wm-category"><a href="Category:Planets">Planets</a></span>
      <span class="wm-category"><a href="Category:Solar_System">Solar System</a></span>
    </nav>

### 8.7 Table of contents control

```yaml
---
toc: true       # Force TOC
toc: false      # Suppress TOC
---
```

When `toc` is omitted, the implementation decides whether to generate a
TOC based on its own heuristics (e.g., number of headings).

To place the TOC at a specific location, use a built-in template:

```````````````````````````````` example
---
toc: true
---

## Section One

{{toc}}

## Section Two
.
<h2>Section One</h2>
<nav class="toc"><!-- table of contents --></nav>
<h2>Section Two</h2>
````````````````````````````````

### 8.8 The `inputs` block

The `inputs` block in frontmatter defines externally-provided values.
When a page is used as a template (see [section 11](#11-templates)),
callers pass arguments that are matched against the `inputs` block.
Provided values (or their defaults) are promoted to top-level frontmatter
keys, making them accessible via `${...}`.

```yaml
---
type: transclusion
greeting: "Hello"
inputs:
  name:
    default: "stranger"
    description: "Name to greet"
---
${greeting}, ${name}!
```

When called as `{{greet name="Alice"}}`:

1. The `inputs` block maps `name="Alice"` to a top-level key.
2. `${greeting}` resolves to `"Hello"` (regular frontmatter).
3. `${name}` resolves to `"Alice"` (promoted from inputs).

When called as `{{greet}}` (no arguments):

1. `${name}` resolves to `"stranger"` (default from inputs).

The `inputs` block is itself accessible via `${...}`:

```````````````````````````````` example
---
inputs:
  name:
    default: stranger
---

Default name is ${inputs.name.default}.
.
<p>Default name is stranger.</p>
````````````````````````````````

### 8.9 Other metadata

The following frontmatter keys are RECOMMENDED but not required:

| Key | Type | Description |
| --- | --- | --- |
| `title` | string | Page title (overrides filename-derived title) |
| `categories` | list | Category memberships |
| `sort_key` | string | Sort key for category listings |
| `toc` | boolean | TOC control |
| `redirect` | string | Redirect target (see [section 9](#9-redirects)) |
| `tags` | list | Arbitrary tags (not categories) |
| `date` | string | Publication or creation date |
| `author` | string | Page author |
| `type` | string | Template type (see [section 11.4](#114-template-types)) |
| `inputs` | object | Template input definitions (see [section 8.8](#88-the-inputs-block)) |

Implementations MAY define additional frontmatter keys.

### 8.10 Frontmatter is not GFM

YAML frontmatter is not part of the GFM specification. A GFM processor
will render `---` as a thematic break and the YAML content as a
paragraph. Because WikiMark extracts frontmatter before GFM block parsing
begins (phase 1), this does not violate the strict-superset property: the
frontmatter is simply not present in the input that the GFM-compatible
block parser sees.

---

## 9 Redirects

A **redirect** is a page whose sole purpose is to forward readers to
another page. Redirects are declared in frontmatter using the `redirect`
key.

### 9.1 Redirect syntax

```````````````````````````````` example
---
redirect: Main Page
---
.
<p>Redirecting to <a href="Main_Page">Main Page</a>.</p>
````````````````````````````````

The redirect target is [normalized](#13-normalization-rules) as a page
title.

### 9.2 Redirect with namespace

```````````````````````````````` example
---
redirect: Help:Main Page
---
.
<p>Redirecting to <a href="Help:Main_Page">Help:Main Page</a>.</p>
````````````````````````````````

### 9.3 Redirect behavior

When a page has a `redirect` key in its frontmatter, the page body is
ignored and replaced with a redirect notice. Implementations SHOULD
perform the redirect automatically (e.g., via HTTP 301/302) rather than
displaying the notice.

---

## 10 Images and media

WikiMark extends GFM's image syntax (`![alt](url)`) with Pandoc-style
attributes for layout control. WikiMark does NOT introduce a separate
file embedding syntax — standard Markdown images are the only way to
embed media.

### 10.1 Basic images (inherited from GFM)

```````````````````````````````` example
![A sunset](photo.jpg)
.
<p><img src="photo.jpg" alt="A sunset" /></p>
````````````````````````````````

This is standard GFM behavior, unchanged.

### 10.2 Presentation attributes on images

An image MAY be followed immediately (no space) by a curly-brace
attribute block for presentation control:

```````````````````````````````` example
![A sunset](photo.jpg){width=300}
.
<p><img src="photo.jpg" alt="A sunset" width="300" /></p>
````````````````````````````````

```````````````````````````````` example
![A sunset](photo.jpg){width=300 height=200}
.
<p><img src="photo.jpg" alt="A sunset" width="300" height="200" /></p>
````````````````````````````````

### 10.3 CSS classes

Classes are specified with a `.` prefix:

```````````````````````````````` example
![A sunset](photo.jpg){.thumb}
.
<figure class="thumb"><img src="photo.jpg" alt="A sunset" /><figcaption>A sunset</figcaption></figure>
````````````````````````````````

The following class names have defined rendering behavior:

| Class | Effect |
| --- | --- |
| `.thumb` | Reduced-size image with frame and caption |
| `.frame` | Full-size image with frame and caption |
| `.frameless` | Reduced-size image without frame |
| `.border` | Thin border around the image |
| `.align-left` | Float left |
| `.align-right` | Float right |
| `.align-center` | Center, no float |

When `.thumb` or `.frame` is present, the image is wrapped in a
`<figure>` element and the alt text is used as the `<figcaption>`.

```````````````````````````````` example
![A beautiful sunset](photo.jpg){.thumb .align-right width=300}
.
<figure class="thumb align-right"><img src="photo.jpg" alt="A beautiful sunset" width="300" /><figcaption>A beautiful sunset</figcaption></figure>
````````````````````````````````

### 10.4 Caption attribute

For cases where the caption should differ from the alt text:

```````````````````````````````` example
![Sunset over ocean](photo.jpg){.thumb caption="A beautiful sunset"}
.
<figure class="thumb"><img src="photo.jpg" alt="Sunset over ocean" /><figcaption>A beautiful sunset</figcaption></figure>
````````````````````````````````

### 10.5 ID attribute

```````````````````````````````` example
![A sunset](photo.jpg){#hero-image}
.
<p><img src="photo.jpg" alt="A sunset" id="hero-image" /></p>
````````````````````````````````

### 10.6 Semantic annotations on images

Images MAY also carry semantic annotations using `|...|` after the
presentation attributes (or directly after the image if no attributes):

```````````````````````````````` example
![Sunset](photo.jpg){.thumb}|subject=sunset location=Malibu|
.
<figure class="thumb" data-wm-subject="sunset" data-wm-location="Malibu"><img src="photo.jpg" alt="Sunset" /><figcaption>Sunset</figcaption></figure>
````````````````````````````````

```````````````````````````````` example
![Sunset](photo.jpg)|subject=sunset|
.
<p><img src="photo.jpg" alt="Sunset" data-wm-subject="sunset" /></p>
````````````````````````````````

### 10.7 Multiple attribute blocks

Multiple attribute blocks on the same element are merged. Attributes
are combined; if the same key appears in both blocks, the later value
takes precedence. Classes are accumulated.

```````````````````````````````` example
![alt](photo.jpg){.thumb}{.border width=300}
.
<figure class="thumb border"><img src="photo.jpg" alt="alt" width="300" /><figcaption>alt</figcaption></figure>
````````````````````````````````

### 10.8 Attribute syntax rules

An attribute block:

1. MUST begin with `{` immediately after the closing `)` of the image
   (no whitespace).
2. MUST end with `}`.
3. Contains space-separated attributes:
   - `.classname` — adds a CSS class
   - `#id` — sets the element ID
   - `key=value` — sets an attribute; values containing spaces MUST be
     quoted with `"`.
4. If `{` does not immediately follow `)`, it is treated as literal
   text (standard GFM behavior).

```````````````````````````````` example
![alt](img.jpg) {width=300}
.
<p><img src="img.jpg" alt="alt" /> {width=300}</p>
````````````````````````````````

---

## 11 Templates

A **template** is a reusable WikiMark document that can be transcluded
into other pages, or a module-backed function that produces output.
Templates are the primary extension mechanism in WikiMark.

### 11.1 Overview

Template transclusion is an inline construct using `{{...}}` syntax.
During the expansion phase (see
[section 2.2](#22-wikimark-processing-model)), each template transclusion
is replaced with the template's output.

### 11.2 Basic transclusion

A template transclusion consists of `{{`, a template name, and `}}`:

```````````````````````````````` example
{{greeting}}
.
<p>Hello, world!</p>
````````````````````````````````

In this example, the template "greeting" contains the text `Hello,
world!`.

The template name MUST be a single token: it MUST NOT contain whitespace,
`{`, `}`, `[`, or `]`. Template names SHOULD use lowercase with hyphens
or underscores as separators.

### 11.3 Arguments

Arguments follow the template name, separated by whitespace:

**Positional arguments:**

```````````````````````````````` example
{{greeting "Alice"}}
.
<p>Hello, Alice!</p>
````````````````````````````````

In this example, the template "greeting" references `${1}` for the first
positional argument.

**Named arguments:**

```````````````````````````````` example
{{greeting name="Alice"}}
.
<p>Hello, Alice!</p>
````````````````````````````````

**Mixed arguments:**

```````````````````````````````` example
{{user-card "Alice" role="admin"}}
.
<p><div class="user-card"><strong>Alice</strong> (admin)</div></p>
````````````````````````````````

**Unquoted values** are supported for single-token values (no
whitespace):

```````````````````````````````` example
{{greeting name=Alice}}
.
<p>Hello, Alice!</p>
````````````````````````````````

Values containing whitespace MUST be quoted:

```````````````````````````````` example
{{greeting name="Alice Smith"}}
.
<p>Hello, Alice Smith!</p>
````````````````````````````````

### 11.4 Template types

A template is a WikiMark document whose frontmatter defines its behavior.
The `type` field determines how the body is processed:

| Type | Description |
| --- | --- |
| `transclusion` | The body is WikiMark text with `${...}` variable substitution. This is the default if `type` is omitted. |
| `python` | The template is backed by a Python module. The `module` field specifies the module path. |

Implementations MAY support additional template types.

#### 11.4.1 Transclusion templates

For `type: transclusion`, the template body is WikiMark text. Arguments
are mapped through the `inputs` block to frontmatter keys and accessed
via `${...}`:

```yaml
---
type: transclusion
inputs:
  1:
    description: "URL"
    required: true
  2:
    description: "Link text"
    required: true
---
[${2}](${1})
```

Invoking `{{link "https://example.com" "Example"}}` produces
`[Example](https://example.com)`, which is then parsed as a standard
Markdown link.

#### 11.4.2 Module-backed templates

For `type: python` (or other module types), the frontmatter specifies
the module:

```yaml
---
type: python
module: wikimark.builtins.timeformat
inputs:
  format:
    required: true
    description: "Date format string"
  timestamp:
    default: null
    description: "ISO 8601 timestamp; current time if omitted"
---
```

The module receives the arguments as a dictionary and returns a string.
The module interface is implementation-defined.

### 11.5 The template as a page

Because templates are WikiMark documents with frontmatter, they use the
same `${...}` variable system as any page (see
[section 8.2](#82-variable-references)). The `inputs` block promotes
caller-provided arguments to top-level frontmatter, and `${...}`
references resolve against the full frontmatter tree.

A template can reference its own metadata:

```yaml
---
type: transclusion
version: "1.2"
inputs:
  name:
    default: "stranger"
---
Hello, ${name}! (Template v${version})
```

### 11.6 Template resolution

Template resolution is implementation-defined. Implementations MUST
document their resolution strategy. Common strategies include:

- **File-based**: `{{name}}` resolves to a file such as
  `_templates/name.wm` in the project directory.
- **Page-based**: `{{name}}` resolves to a wiki page in a designated
  template namespace.

Template names MUST be validated against path traversal attacks (see
[Appendix D](#appendix-d-security-considerations)).

### 11.7 Expansion model

Templates follow the same expansion model as variables (see
[section 8.3](#83-expansion-model)): the template body is processed as
WikiMark in its own context (variables resolved, wiki links parsed, etc.)
to produce output. That output is then inserted **literally** into the
calling document — it is NOT re-parsed for WikiMark constructs.

This means a template cannot inject closing delimiters (`]]`, `}}`) that
break the calling page's syntax. Template output is self-contained.

### 11.8 Nested template calls

Template arguments MAY contain other template transclusions:

```````````````````````````````` example
{{outer {{inner}}}}
.
<p>Result of outer with inner.</p>
````````````````````````````````

When a template argument is itself a template transclusion, the inner
template is expanded first (innermost-first evaluation). The inner
template's output is literal text that becomes the argument value for the
outer template.

### 11.9 Recursion and depth limits

Implementations MUST enforce a maximum expansion depth to prevent
infinite recursion. The RECOMMENDED maximum depth is 40.

When the depth limit is reached, the unresolved template transclusion
MUST be rendered as an error indicator:

```````````````````````````````` example
{{recursive}}
.
<p><span class="wm-error">{{recursive}}</span></p>
````````````````````````````````

Implementations SHOULD also enforce a maximum total number of template
expansions per page (RECOMMENDED: 500) to prevent expansion bombs.

### 11.10 Unresolved templates

If a template cannot be resolved (e.g., the file does not exist), the
transclusion MUST be rendered as an error indicator:

```````````````````````````````` example
{{nonexistent}}
.
<p><span class="wm-error">{{nonexistent}}</span></p>
````````````````````````````````

If a required input is missing, the template MUST produce an error
indicator:

```````````````````````````````` example
{{link}}
.
<p><span class="wm-error">{{link}}: missing required input "1"</span></p>
````````````````````````````````

### 11.11 Template frontmatter and the `include` key

By default, a template's frontmatter is its own namespace — it is NOT
merged with the calling page's frontmatter. Templates receive explicit
inputs and return rendered output. This is a clean boundary.

However, a template MAY declare frontmatter keys to be **included** into
the calling page's frontmatter using the `include` key:

```yaml
---
type: transclusion
include:
  categories:
    - Science
  tags:
    - physics
inputs:
  topic:
    required: true
---
${topic} is a branch of science.
```

When this template is transcluded, the values under `include` are merged
into the calling page's frontmatter:

- **Lists** (like `categories` and `tags`) are merged additively — the
  template's values are appended to the page's existing values.
- **Scalar values** are set only if the key does not already exist in the
  calling page's frontmatter (page values take precedence).

The `include` key is ONLY processed during template transclusion
(`{{...}}`). Page embeds (`![[...]]`) include the full rendered content
but do NOT merge frontmatter.

### 11.12 Page embeds vs. templates

`![[page]]` and `{{template}}` differ in frontmatter handling:

| | `![[page]]` | `{{template args}}` |
| --- | --- | --- |
| Content | Full rendered page | Template body only |
| Arguments | None | Via `inputs` block |
| Frontmatter merge | No | Via `include` key |
| Use case | Embedding content | Reusable components |

---

## 12 Semantic annotations

**Semantic annotations** attach structured, machine-readable metadata to
inline content. They use pipe-delimited blocks (`|...|`) that attach to
a preceding element.

### 12.1 Basic property annotation

A semantic annotation is a `|...|` block immediately following a
bracketed element (`[text]`, `[text](url)`, `![alt](url)`, `[[link]]`,
etc.). A bare word inside the pipes is the property name, with the
preceding element's text as the value:

```````````````````````````````` example
The capital is [Paris]|capital|.
.
<p>The capital is <span data-wm-property="capital">Paris</span>.</p>
````````````````````````````````

### 12.2 Key-value annotations

Annotations MAY contain `key=value` pairs for richer metadata:

```````````````````````````````` example
[67.39 million]|property=population value=67390000|
.
<p><span data-wm-property="population" data-wm-value="67390000">67.39 million</span></p>
````````````````````````````````

```````````````````````````````` example
[1789-07-14]|property=founded type=Date|
.
<p><span data-wm-property="founded" data-wm-type="Date">1789-07-14</span></p>
````````````````````````````````

### 12.3 Annotations on wiki links

```````````````````````````````` example
[[Paris]]|capital|
.
<p><a href="Paris" data-wm-property="capital">Paris</a></p>
````````````````````````````````

```````````````````````````````` example
[City of Light](Paris)|capital|
.
<p><a href="Paris" data-wm-property="capital">City of Light</a></p>
````````````````````````````````

### 12.4 Annotations on standard Markdown links

```````````````````````````````` example
[Paris](https://en.wikipedia.org/wiki/Paris)|capital|
.
<p><a href="https://en.wikipedia.org/wiki/Paris" data-wm-property="capital">Paris</a></p>
````````````````````````````````

### 12.5 Annotations with presentation attributes

Semantic annotations and presentation attributes can coexist on the same
element. Presentation attributes (`{...}`) MUST come before semantic
annotations (`|...|`):

```````````````````````````````` example
[Paris]{.highlight}|capital|
.
<p><span class="highlight" data-wm-property="capital">Paris</span></p>
````````````````````````````````

```````````````````````````````` example
![Sunset](photo.jpg){.thumb width=300}|subject=sunset location=Malibu|
.
<figure class="thumb" data-wm-subject="sunset" data-wm-location="Malibu"><img src="photo.jpg" alt="Sunset" width="300" /><figcaption>Sunset</figcaption></figure>
````````````````````````````````

### 12.6 Multiple properties

A single annotation block MAY contain multiple properties:

```````````````````````````````` example
[Paris]|capital country=France population=2161000|
.
<p><span data-wm-property="capital" data-wm-country="France" data-wm-population="2161000">Paris</span></p>
````````````````````````````````

### 12.7 Multiple values for one property

Use multiple annotated spans:

```````````````````````````````` example
Speaks [English]|language| and [French]|language|.
.
<p>Speaks <span data-wm-property="language">English</span> and <span data-wm-property="language">French</span>.</p>
````````````````````````````````

### 12.8 Silent annotations

To annotate without visible text, use an empty span:

```````````````````````````````` example
[]|category-type="Sovereign state"|Some text.
.
<p><span data-wm-category-type="Sovereign state" class="wm-silent"></span>Some text.</p>
````````````````````````````````

### 12.9 Annotation parsing rules

1. `|` opens a semantic annotation only when it immediately follows a
   **recognized WikiMark element** that ends with `]`, `)`, or `}`.
   Recognized elements include: wiki links (`[[...]]`), GFM links
   (`[text](url)`), images (`![alt](url)`), WikiMark spans
   (`[text]{...}`), and elements with presentation attributes (`...}`).
   A literal `]` in body text (e.g., from a bare `[text]` with no
   paired brackets) does NOT trigger annotation parsing.
2. The annotation extends to the next `|`, respecting quoted strings
   (see [section 2.4](#24-quote-aware-scanning)). Content inside `"..."`
   is literal and not scanned for `|`.
3. Content inside is parsed as space-separated tokens: bare words are
   property names, `key=value` pairs are named attributes. Values
   containing spaces MUST be quoted with `"`.
4. If `|` does not follow a recognized element, it is treated as
   literal text.
5. An empty annotation (`||` with no content) is a no-op and produces
   no semantic attributes.

```````````````````````````````` example
This | is | just text.
.
<p>This | is | just text.</p>
````````````````````````````````

Bare `[text]` followed by `|` is literal because `[text]` alone is not
a recognized element:

```````````````````````````````` example
[text]| is just literal.
.
<p>[text]| is just literal.</p>
````````````````````````````````

### 12.10 Semantic annotations in GFM tables

Inside GFM table cells, semantic `|` characters conflict with cell
boundary `|` characters. To use semantic annotations in tables, escape
the semantic pipes using GFM's existing `\|` mechanism:

```markdown
| City | Country |
| --- | --- |
| [Paris]\|capital\| | France |
```

The table parser treats `\|` as literal `|` in the cell content. The
inline parser then recognizes `[Paris]|capital|` as a semantic
annotation.

### 12.11 Semantic annotations on template output

When a template transclusion is followed by a semantic annotation:

```````````````````````````````` example
{{greeting}}|semantic=hello|
.
<p><span data-wm-semantic="hello">Hello, world!</span></p>
````````````````````````````````

The template is expanded first, producing output (e.g., "Hello,
world!"). The semantic annotation then wraps that output, equivalent to
`[Hello, world!]|semantic=hello|`.

### 12.12 Inline queries

Inline queries retrieve semantic property values from other pages. They
are implemented as module-backed templates (see
[section 11](#11-templates)), not as special syntax:

```````````````````````````````` example
{{ask source="Category:Countries" property="capital" limit=1}}
.
<table class="wm-query-result">
<thead><tr><th>Page</th><th>Capital</th></tr></thead>
<tbody><tr><td><a href="France">France</a></td><td>Paris</td></tr></tbody>
</table>
````````````````````````````````

The query language and output format are implementation-defined.

---

## 13 Normalization rules

WikiMark defines normalization rules for page titles and other
identifiers used in wiki links.

### 13.1 Whitespace normalization

Leading and trailing whitespace MUST be stripped. Sequences of internal
whitespace (spaces, tabs) MUST be collapsed to a single space.

```````````````````````````````` example
[[  Main   Page  ]]
.
<p><a href="Main_Page">Main Page</a></p>
````````````````````````````````

### 13.2 Underscore/space equivalence

In URLs generated from wiki link targets, spaces MUST be replaced with
underscores. In display text, underscores SHOULD be displayed as spaces.

```````````````````````````````` example
[[Main_Page]]
.
<p><a href="Main_Page">Main Page</a></p>
````````````````````````````````

### 13.3 Case preservation

Page titles are **case-preserving**. The case of the original text is
maintained in the generated URL. WikiMark does not perform first-letter
capitalization — that is a MediaWiki convention that does not fit
Markdown's plain-text philosophy.

```````````````````````````````` example
[[main page]]
.
<p><a href="main_page">main page</a></p>
````````````````````````````````

### 13.4 Unicode normalization

Page titles MUST be normalized to Unicode NFC (Canonical Decomposition,
followed by Canonical Composition) before URL generation.

### 13.5 Namespace normalization

Namespace prefixes that match implementation-defined reserved namespaces
are case-insensitive. The canonical form uses initial capitalization.

### 13.6 Forbidden characters

The following characters MUST NOT appear in page titles (after
normalization): `#`, `<`, `>`, `[`, `]`, `{`, `}`, `|`. A wiki link
containing forbidden characters in the target MUST be treated as literal
text.

---

## 14 Error handling and fallback behavior

WikiMark defines consistent error behavior for malformed or unresolvable
constructs.

### 14.1 Unclosed delimiters

Consistent with GFM's handling of unclosed constructs, all unclosed
WikiMark delimiters MUST be treated as literal text:

- `[[` without matching `]]` → literal `[[`
- `{{` without matching `}}` → literal `{{`
- `${` without matching `}` → literal `${`
- `{` in attribute position without matching `}` → literal `{`
- `|` in annotation position without matching `|` → literal `|`

```````````````````````````````` example
This is [[unclosed
.
<p>This is [[unclosed</p>
````````````````````````````````

```````````````````````````````` example
This is {{unclosed
.
<p>This is {{unclosed</p>
````````````````````````````````

```````````````````````````````` example
This is ${unclosed
.
<p>This is ${unclosed</p>
````````````````````````````````

```````````````````````````````` example
![alt](img.jpg){unclosed
.
<p><img src="img.jpg" alt="alt" />{unclosed</p>
````````````````````````````````

### 14.2 Unresolved references

Templates that cannot be resolved MUST produce an error indicator (see
[section 11.10](#1110-unresolved-templates)).

Undefined variable references are replaced with an empty string (see
[section 8.4](#84-undefined-variables)).

### 14.3 Error indicator format

Error indicators MUST be rendered as:

    <span class="wm-error">description</span>

where "description" is the original source text or a descriptive error
message.

---

## Appendix A: Parsing strategy

### A.1 Overview

This appendix describes a recommended parsing strategy. Conforming
implementations are not required to follow this strategy, but MUST
produce output consistent with the specification.

### A.2 Phase 1: Frontmatter extraction

If the document begins with `---` on its own line, read lines until a
closing `---` is found. Parse the enclosed content as YAML. Process the
`inputs` block if present: for each input, if a value was provided by
the caller, promote it to a top-level key; otherwise, promote the
default value. Remove the frontmatter (including delimiters) from the
document body.

### A.3 Phase 2: Block structure

Follow the GFM block-parsing algorithm unchanged. Redirects are handled
in frontmatter (phase 1), not as block-level constructs.

### A.4 Phase 3: Inline structure

Follow the GFM inline-parsing algorithm with these additions to the
left-to-right scan:

1. When encountering `$` followed by `{`, attempt to parse a variable
   reference (`${...}`). Match to the closing `}`, supporting dot
   notation. If well-formed, emit a variable-reference node. If not,
   emit a literal `$`.

2. When encountering `[`, look ahead for a second `[`. If found, attempt
   to parse a wiki link (`[[...]]`). If well-formed, emit a wiki-link
   node. If not, emit a literal `[` and backtrack.

3. When encountering `{`, look ahead for `{{`. If found, attempt to
   parse a template transclusion. If not well-formed, emit literal
   braces and backtrack.

4. After emitting any element that ends with `]`, `)`, or `}`, check
   whether the next character is `{`. If so, attempt to parse a
   presentation attribute block.

5. After emitting any element that ends with `]`, `)`, or `}` (including
   after an attribute block), check whether the next character is `|`.
   If so, attempt to parse a semantic annotation block — scan to the
   next `|` on the same line.

### A.5 Phase 4: Expansion

Process the document in order:

1. Resolve all `${...}` variable references: retrieve the frontmatter
   value, process it as WikiMark in its own context, and insert the
   resulting output literally.
2. Expand template transclusions (innermost first for nested template
   calls): process each template as WikiMark in its own context, and
   insert the resulting output literally.
3. Expansion output is NOT re-parsed by the calling document. Each
   expansion is self-contained.

### A.6 Precedence and conflict rules

When constructs overlap or nest ambiguously:

1. **Code spans and fenced code blocks** take absolute precedence. No
   WikiMark constructs are parsed inside them.

2. **`[[...]]` is greedy**: once `[[` is encountered, the parser scans
   for the matching `]]`. The content is the page target only (no `|`
   separator). Wiki links do not contain display text; use wiki-style
   Markdown links (`[display](target)`) for custom display text.

3. **`{{...}}` is greedy**: once `{{` is encountered, the parser scans
   for the matching `}}`. Nested `{{...}}` pairs are tracked for proper
   matching.

4. **Modifier attachment order**: After any recognized element ending
   in `]`, `)`, or `}`, optional modifiers attach in order: `{...}`
   (presentation), then `|...|` (semantic). This order is fixed.
   Multiple `{...}` blocks on the same element are merged (attributes
   combined, later values overriding earlier ones for the same key).

5. **Semantic `|` only after recognized elements**: A `|` after a
   literal `]` (e.g., bare `[text]` with no paired brackets) does NOT
   trigger annotation parsing. The preceding construct must be a
   recognized WikiMark or GFM element (wiki link, GFM link, image,
   span with attributes, template transclusion).

6. **No links inside links**: A wiki link (`[[...]]`) MUST NOT appear
   inside the text of a GFM link. If `[[` appears in GFM link text, it
   is treated as literal.

7. **Literal expansion**: Template and variable expansion output is
   inserted literally. It cannot inject closing delimiters (`]]`, `}}`),
   open new constructs, or otherwise affect the calling document's parse
   tree.

8. **Semantic `|` vs. table `|`**: At the block level, `|` is a table
   cell delimiter. At the inline level, `|` after a recognized element
   opens a semantic annotation. In table cells, use `\|` to escape
   semantic pipes so the block-level table parser passes them through
   as literal `|` to the inline parser.

---

## Appendix B: HTML output conventions

This appendix defines the HTML elements and attributes used in the
normative examples. Conforming implementations MUST produce semantically
equivalent HTML; exact whitespace and attribute order MAY differ.

### B.1 Wiki links

    <a href="Normalized_Target">display text</a>

The `href` value is the normalized page title (see
[section 13](#13-normalization-rules)). Implementations MAY prepend a
base URL or path prefix.

### B.2 Categories

Category metadata produces no inline HTML. Implementations MAY render a
category list:

    <nav class="wm-categories">
      <span class="wm-category"><a href="Category:Name">Name</a></span>
    </nav>

### B.3 Images with attributes

Without `.thumb` or `.frame`:

    <img src="url" alt="text" [width="N"] [height="N"] [class="..."] [id="..."] />

With `.thumb` or `.frame`:

    <figure class="[classes]" [id="..."]>
      <img src="url" alt="text" [width="N"] [height="N"] />
      <figcaption>caption</figcaption>
    </figure>

### B.4 Semantic annotations

Single property (bare word):

    <span data-wm-property="name">text</span>

On a link:

    <a href="url" data-wm-property="name">text</a>

Key-value pairs:

    <span data-wm-key="value" ...>text</span>

All semantic keys are prefixed with `data-wm-` in the HTML output.

### B.5 Presentation spans

    <span [class="..."] [id="..."] [key="value"]>text</span>

### B.6 Error indicators

    <span class="wm-error">description</span>

### B.7 Output sanitization

Implementations MUST sanitize all user-provided values that appear in
HTML attributes (link targets, property names, property values, alt text)
by escaping `<`, `>`, `"`, `'`, and `&`.

Template expansion output MUST be treated as WikiMark source, not raw
HTML, unless the template explicitly contains raw HTML blocks (which are
then subject to GFM's raw HTML rules).

Implementations MUST NOT allow template expansion to inject arbitrary
HTML attributes or JavaScript.

---

## Appendix C: Differences from MediaWiki

### C.1 Features not adopted

| MediaWiki feature | WikiMark approach |
| --- | --- |
| `<ref>` / `<references>` tags | GFM footnotes (`[^id]`) |
| Wikitext tables (`{\| ... \|}`) | GFM pipe tables |
| Wikitext headings (`== ... ==`) | GFM ATX headings (`## ...`) |
| Wikitext bold/italic (`'''`/`''`) | GFM emphasis (`**`/`*`) |
| Wikitext lists (`*`, `#`, `;`, `:`) | GFM lists (`-`, `1.`) |
| `<nowiki>` tags | GFM code spans / fenced code blocks |
| `[[File:...]]` embedding | `![alt](url){attributes}` |
| `[[Category:...]]` inline | Frontmatter `categories: [...]` |
| `__TOC__` / `__NOTOC__` | Frontmatter `toc: true/false` |
| Parser functions (`#if`, etc.) | Module-backed templates |
| `[[Property::Value]]` | `[Value]\|property\|` semantic annotations |
| Signatures (`~~~`, `~~~~`) | Not applicable |
| Template args with `\|` | Space-separated, `key=value` |
| Parameter refs `{{{param}}}` | `${param}` frontmatter variables |
| Magic words (`{{PAGENAME}}`) | `${title}` frontmatter variables |

### C.2 Behavioral differences

| Area | MediaWiki | WikiMark |
| --- | --- | --- |
| Base markup | Wikitext | GitHub Flavored Markdown |
| Page metadata | Magic words, inline categories | YAML frontmatter |
| Template arguments | Pipe-separated | Space-separated |
| Parameter references | `{{{param\|default}}}` | `${param}` with frontmatter defaults |
| Template resolution | Database (wiki pages) | Implementation-defined (typically files) |
| Template capabilities | Fixed parser functions | Extensible module system |
| Image options | `[[File:...\|options]]` | `![alt](url){attributes}` |
| Semantic data | `[[Property::Value]]` | `[Value]\|property\|` pipe annotations |
| Raw HTML | Restricted allow-list | GFM raw HTML rules |

### C.3 Migration from MediaWiki

1. Convert headings: `== Heading ==` → `## Heading`
2. Convert emphasis: `'''bold'''` → `**bold**`, `''italic''` → `*italic*`
3. Convert lists: `*` → `-`, `#` → `1.`
4. Convert tables: wikitext table syntax → GFM pipe tables
5. Convert references: `<ref>` → `[^id]` footnotes
6. Convert images: `[[File:img.jpg|thumb|300px|caption]]` →
   `![caption](img.jpg){.thumb width=300}`
7. Convert categories: `[[Category:X]]` → frontmatter
   `categories: [X]`
8. Convert templates: `{{name|arg1|key=val}}` →
   `{{name "arg1" key="val"}}`
9. Convert parameter refs: `{{{param|default}}}` → `${param}` with
   frontmatter `inputs:` defaults
10. Convert parser functions: `{{#if:...}}` → module-backed templates
11. Convert semantic data: `[[Property::Value]]` →
    `[Value]|property|`
12. Convert magic words: `{{PAGENAME}}` → `${title}` in frontmatter

---

## Appendix D: Security considerations

### D.1 Template expansion

Template expansion is the primary attack surface. Implementations MUST:

1. Enforce a maximum recursion depth (RECOMMENDED: 40).
2. Enforce a maximum total expansion count per page (RECOMMENDED: 500).
3. Enforce a maximum expanded output size (RECOMMENDED: 2 MB).

### D.2 Template resolution path traversal

File-based template resolution MUST prevent path traversal. Template
names containing `..`, absolute paths, or path separators beyond the
configured template directory MUST be rejected.

### D.3 Module safety

Module-backed templates execute code. Implementations MUST:

1. Document which module types are supported and how they are sandboxed.
2. Restrict module execution to a configured set of trusted modules
   or directories.
3. Enforce time and memory limits on module execution.

### D.4 Variable injection

The `${...}` variable system reads from frontmatter only. It MUST NOT
access environment variables, filesystem paths, or other process state.
All variable values are treated as text and MUST be sanitized before
insertion into HTML attributes.

### D.5 Output escaping

See [Appendix B.7](#b7-output-sanitization).

### D.6 Denial of service

Implementations SHOULD enforce time limits on page rendering to prevent
denial of service via pathological inputs (e.g., deeply nested templates,
exponential expansion patterns).
