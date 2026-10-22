# /thesis

Landing page and sub-pages for the dissertation. Served at `paulpissarro.com/thesis`.

## Build

```
python3 thesis/_build.py        # from the repo root
```

Writes `thesis/index.html`, `thesis/propositions/index.html`, `thesis/ledger/index.html`,
`thesis/ledger/ledger.json`, `thesis/thesis.css` and `sitemap.xml`.

Stdlib only, no dependencies, no build step. Run it, commit the output.

**Do not hand-edit the generated `.html`. It gets overwritten.** Edit the `R` dict
at the top of `_build.py`, which holds the title, author string, year, DOI,
licence and ledger date.

Reason it is generated rather than written: the author string has to be
byte-identical on every page forever. A divergent string splits the citation
count across records that never merge, and it cannot be fixed after the first
DOI is minted. Four hand-maintained files is four chances to get that wrong.

## Layout

```
/thesis                     landing. abstract, record, verification, references
/thesis/propositions        31 claims, anchored by permanent label
/thesis/ledger              citation ledger
/thesis/ledger/ledger.json  ledger data
```

Directory-index serving. Everything branches off `/thesis`; nothing sits beside it.

## Things that break if changed

**`noindex, follow` on every page is deliberate.** The work is not ready to be
indexed. It comes off at deposit by setting `indexable = True` in `_build.py`.
Not a leftover, please don't tidy it away.

**Highwire tags are on `/thesis` only.** `citation_title`, `citation_author`,
`citation_publication_date`. Sub-pages carry none and must not: they are parts
of one record, and tagging them separately splits one work into three in Google
Scholar.

**All three of those tags are mandatory.** If any one is missing or empty,
Scholar treats the page as having no tags at all, rather than as having two.

**Tags must be in raw HTML.** There is currently no `<script>` anywhere under
`/thesis`. If something later injects the tags client-side, crawlers may miss
them.

**Author string is `Pissarro, Paul-Alexander Arthur`.** Exactly that, in the tags
and in visible text. Not the short form, not first-name-first.

**Proposition anchors are permanent.** `/thesis/propositions#C2` is already a
citable address. Labels append, never insert, never renumber, because
renumbering breaks citations already made.

**`citation_pdf_url`, when added, must end in `.pdf`** and point at the
searchable-text build, never a rasterised one. A scanned PDF contributes nothing
to the citation graph.

## Still empty, and why

`orcid`, `doi`, `doi_mirror`, `licence`, `pdf` and `ledger_opened` are all `None`
in `_build.py` and render as "not yet" on the page. They fill in as they exist.

`ledger_opened` is the one with a deadline: the ledger has to be published,
empty and dated, **before** the first deposit. Published after, it proves
nothing.

## Known issue this fixed

`robots.txt` and `sitemap.xml` on `main` both described unsubscribe.llc. The
sitemap served from paulpissarro.com listed 13 unsubscribe.llc URLs and no entry
for this domain, including none for `/thesis`. Both are corrected here, but the
fix is just a corrected file, so if deploy config generates them it will come
back.
