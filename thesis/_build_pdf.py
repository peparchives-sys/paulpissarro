#!/usr/bin/env python3
"""
Builds the deposit PDF from _build.py, which is the single source of truth.

Nothing here restates the record. Title, author, abstract, keywords, propositions
and references are all imported, so the deposited document and the live pages
cannot disagree. If they ever do, this script is the bug.

    python3 thesis/_build_pdf.py

Output: thesis/pissarro-2026-orthopraxy-v0.1.pdf

Why a PDF at all: Humanities Commons CORE deposits a document, not a website, and
Google Scholar wants a text PDF behind the citation_pdf_url tag. This is that file.
"""
import html, importlib.util, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                    Paragraph, Spacer, KeepTogether, HRFlowable)
except ImportError:
    sys.exit("BUILD REFUSED: reportlab is not installed. pip install --break-system-packages reportlab")


def record():
    """Import _build.py without running its page build."""
    spec = importlib.util.spec_from_file_location("_thesis_build", HERE / "_build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ text
# The record is written as HTML. reportlab's Paragraph takes a small XML
# subset, so tags are narrowed to <i>, entities are resolved to real
# characters, and the XML specials are re-escaped. Order matters: resolving
# entities before stripping tags would turn a literal &lt; into a fake tag.
def clean(s):
    s = re.sub(r'<span class="pending">(.*?)</span>', r"[\1]", s, flags=re.S)
    s = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", s, flags=re.S)
    s = s.replace("<em>", "\x01i\x02").replace("</em>", "\x01/i\x02")
    s = s.replace("<strong>", "\x01b\x02").replace("</strong>", "\x01/b\x02")
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (s.replace("\x01i\x02", "<i>").replace("\x01/i\x02", "</i>")
             .replace("\x01b\x02", "<b>").replace("\x01/b\x02", "</b>"))


SERIF, BOLD, ITAL = "Times-Roman", "Times-Bold", "Times-Italic"

S = {
 "title":   ParagraphStyle("title", fontName=BOLD, fontSize=19, leading=23, spaceAfter=5),
 "sub":     ParagraphStyle("sub", fontName=ITAL, fontSize=13.5, leading=17, spaceAfter=20),
 "author":  ParagraphStyle("author", fontName=SERIF, fontSize=12, leading=16, spaceAfter=3),
 "meta":    ParagraphStyle("meta", fontName=SERIF, fontSize=9.5, leading=14,
                           spaceAfter=1.5, leftIndent=0),
 "status":  ParagraphStyle("status", fontName=ITAL, fontSize=9.5, leading=13.5,
                           spaceBefore=13, spaceAfter=13, leftIndent=9, rightIndent=9),
 "h1":      ParagraphStyle("h1", fontName=BOLD, fontSize=12.5, leading=16,
                           spaceBefore=22, spaceAfter=7),
 "h2":      ParagraphStyle("h2", fontName=BOLD, fontSize=11, leading=14,
                           spaceBefore=18, spaceAfter=5),
 "body":    ParagraphStyle("body", fontName=SERIF, fontSize=10.5, leading=15,
                           spaceAfter=9, alignment=TA_JUSTIFY),
 "note":    ParagraphStyle("note", fontName=SERIF, fontSize=9.5, leading=13.5,
                           spaceAfter=9, alignment=TA_JUSTIFY),
 "label":   ParagraphStyle("label", fontName=BOLD, fontSize=9, leading=12, spaceAfter=2.5),
 "prop":    ParagraphStyle("prop", fontName=SERIF, fontSize=10.5, leading=15,
                           spaceAfter=3, alignment=TA_JUSTIFY, leftIndent=15),
 "src":     ParagraphStyle("src", fontName=ITAL, fontSize=8.5, leading=12,
                           spaceAfter=11, leftIndent=15),
 "ref":     ParagraphStyle("ref", fontName=SERIF, fontSize=9, leading=12.5,
                           spaceAfter=6.5, leftIndent=15, firstLineIndent=-15),
}


def footer(canvas, doc, R):
    canvas.saveState()
    canvas.setFont(SERIF, 8)
    canvas.setFillGray(0.4)
    short = f'{R["author"].split(",")[0]} {R["year"]}  ·  {R["version"]}'
    canvas.drawString(22 * mm, 14 * mm, short)
    canvas.drawRightString(A4[0] - 22 * mm, 14 * mm, str(doc.page))
    canvas.restoreState()


def build(parts="full"):
    """parts="abstract" builds the standalone abstract; "full" adds the registry."""
    m = record()
    R, out = m.R, []
    P = lambda t, s: Paragraph(t, S[s])
    short = parts == "abstract"

    # ---------------------------------------------------------- title page
    out += [Spacer(1, 16 * mm),
            P(clean(R["title_main"]), "title"),
            P(clean(R["title_sub"]) + ("<br/><br/>Abstract and statement of method"
                                       if short else ""), "sub"),
            P(f'<b>{clean(R["author"])}</b>', "author"),
            P(f'ORCID iD <a href="https://orcid.org/{R["orcid"]}">'
              f'{R["orcid"]}</a>', "meta"),
            Spacer(1, 7 * mm),
            HRFlowable(width="100%", thickness=0.5, color="#999999",
                       spaceBefore=0, spaceAfter=9)]

    rows = [("Publisher", R["publisher"]),
            ("Year", R["year"]),
            ("Version", R["version"]),
            ("Licence", f'{R["licence"]}. Applies to the text of this work only.'),
            ("Canonical address", f'{R["base"]}/thesis/'),
            ("Propositions", f'{R["base"]}/thesis/propositions/'),
            ("Citation ledger", f'{R["base"]}/thesis/ledger/ '
                                f'· opened empty {R["ledger_opened"]}'),
            ("DOI", R["doi"] or "not yet minted")]
    for k, v in rows:
        out.append(P(f"<b>{k}</b>&nbsp;&nbsp;{clean(str(v))}", "meta"))

    out += [HRFlowable(width="100%", thickness=0.5, color="#999999",
                       spaceBefore=9, spaceAfter=0),
            P("Pre-deposit. No identifier has been minted and the abstract is not "
              "final. The citation ledger was opened empty and dated before any "
              "deposit, and independently timestamped the same day by the Internet "
              "Archive. Nothing in this document is a claim about work already done.",
              "status")]

    # ---------------------------------------------------------- abstract
    out.append(P("Abstract", "h1"))
    out += [P(clean(p), "body") for p in m.ABSTRACT]

    out.append(P("Keywords", "h2"))
    out.append(P(clean("; ".join(m.KEYWORDS)), "note"))

    if short:
        out.append(P("Scope of this deposit", "h2"))
        out.append(P(
            "This deposit is the abstract and nothing further. The argument it "
            "summarises rests on a registry of labelled propositions, each stating "
            "the source it rests on and the claim it serves, which is published "
            f'openly at {R["base"]}/thesis/propositions/ and is deposited separately. '
            "Where a reader wants the evidence behind a sentence here, that registry "
            "is where it is held. A record of the infrastructure through which this "
            "work was deposited, including the applications made and refused, is also "
            "deposited separately.", "note"))
        out.append(P(
            "Depositing the abstract alone is deliberate rather than provisional. The "
            "abstract has been read and cleared; the registry had not been at the time "
            "of this deposit. Publishing the two together would have extended one "
            "reader's approval to material they had not seen.", "note"))

    # ---------------------------------------------------------- how to cite
    out.append(P("How to cite this work", "h2"))
    out.append(P(
        f'Cite the proposition label rather than the page. Labels are permanent and '
        f'pages are not. The form is the author, the year and the label, for example '
        f'<b>{clean(R["author"].split(",")[0])} {R["year"]}, C13</b>. Every '
        f'proposition carries a permanent anchor on the propositions page, so C13 '
        f'resolves at {R["base"]}/thesis/propositions/#C13 and will continue to. A '
        f'proposition later found to be wrong keeps its number and is marked '
        f'withdrawn with the reason given; it is never renumbered or reused.', "note"))

    # ---------------------------------------------------------- propositions
    if not short:
      out.append(P("Propositions", "h1"))
      out.append(P(
        "Every load-bearing claim in the work, stated once and labelled permanently. "
        "A proposition marked <i>cite source</i> is somebody else's finding, restated "
        "here only so that it can be found; cite the source named beneath it. A "
        "proposition marked <i>cite this work</i> is an inference made here, and the "
        "sources beneath it are what it rests on rather than where it came from.",
        "note"))

      for item in m.PROPS:
        if len(item) == 3:
            band, name, blurb = item
            out.append(P(f"Band {band} &nbsp;·&nbsp; {clean(name)}", "h2"))
            out.append(P(clean(blurb), "note"))
        else:
            lab, text, src, cite = item
            word = "cite this work" if cite == "work" else "cite source"
            serves = m.SERVES.get(lab)
            tail = f"{clean(src)} &nbsp;·&nbsp; {word}"
            if serves:
                tail += f" &nbsp;·&nbsp; serves {clean(serves)}"
            out.append(KeepTogether([P(lab, "label"),
                                     P(clean(text), "prop"),
                                     P(tail, "src")]))

      # ---------------------------------------------------------- references
      out.append(P("References", "h1"))
      out.append(P(
        "Generated from the propositions that cite them, in order of first use. This "
        "is not a reading list: a work earns an entry here by being cited above. A "
        "bracketed note records what about a record remains unverified.", "note"))
      for key in m.cited_keys():
        out.append(P(clean(m.SOURCES[key]), "ref"))

    # ---------------------------------------------------------- render
    stem = "orthopraxy-abstract" if short else "orthopraxy-registry"
    name = f'pissarro-{R["year"]}-{stem}-{R["version"]}.pdf'
    path = HERE / name
    doc = BaseDocTemplate(
        str(path), pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=20 * mm, bottomMargin=22 * mm,
        title=R["title_full"] + (" (abstract)" if short else ""),
        author=R["author"],
        subject=f'{R["publisher"]}, {R["year"]}, {R["version"]}',
        keywords=", ".join(m.KEYWORDS), creator=R["publisher"],
    )
    doc.addPageTemplates([PageTemplate(
        id="page",
        frames=[Frame(doc.leftMargin, doc.bottomMargin,
                      doc.width, doc.height, id="body")],
        onPage=lambda c, d: footer(c, d, R))])
    doc.build(out)
    print(f"  wrote thesis/{name}  ({path.stat().st_size:,} bytes, {doc.page} pages)")
    return path


if __name__ == "__main__":
    mode = "abstract" if "--abstract" in sys.argv else "full"
    print(f"Building the {mode} deposit PDF from _build.py ...")
    build(mode)
    print("Done. Do not hand-edit it: rebuild from _build.py so it cannot drift.")
