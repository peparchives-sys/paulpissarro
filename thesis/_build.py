#!/usr/bin/env python3
"""
Generator for paulpissarro.com/thesis and everything beneath it.

WHY THIS FILE EXISTS
Every page under /thesis shares a head block, a stylesheet, a footer and an
author string. Hand-maintaining four pages means four chances to let them
drift, and a divergent author string or title fragments the citation count
permanently. So the pages are generated. Edit the data at the top of this
file, run `python3 thesis/_build.py` from the repo root, commit the result.

Never hand-edit the generated .html files. They are overwritten.
"""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------- THE RECORD
# One source of truth. Everything downstream reads from here.
R = {
    "title_main": "The Dissertation as an Exemplar of Orthopraxy",
    "title_sub":  "Examination, Citation, and the Legal Form of Access",
    "author":     "Pissarro, Paul-Alexander Arthur",   # canonical. never vary.
    "year":       "2026",
    "publisher":  "Church of Conceptual Art",
    "base":       "https://paulpissarro.com",
    "orcid":      None,          # set once registered
    "doi":        None,          # set on deposit. irreversible.
    "doi_mirror": None,
    "licence":    None,          # CC BY, exact version to confirm
    "pdf":        None,          # must end in .pdf, text build only
    "indexable":  False,         # flip to True only at deposit
    "ledger_opened": None,       # set once,永 permanent. ISO date.
}
R["title_full"] = f'{R["title_main"]}: {R["title_sub"]}'

def pending(v, fallback):
    return v if v else f'<span class="pending">{fallback}</span>'

# ------------------------------------------------------------------ TEMPLATE
def page(slug, heading, standfirst, body, desc, is_root=False):
    """slug: '' for the landing page, else 'propositions', 'ledger'."""
    url  = f'{R["base"]}/thesis' + (f'/{slug}' if slug else '')
    up   = '../' if slug else ''
    # Highwire tags go on the landing page only. Sub-pages are parts of the
    # same work, and tagging them separately would split one record into three.
    tags = ""
    if is_root:
        tags = f'''
<!-- Highwire Press tags. Google Scholar reads these instead of the PDF.
     citation_title, citation_author and citation_publication_date are all
     three mandatory: if any one is missing or empty, Scholar treats the page
     as having no tags at all. Raw HTML only, never script-injected.
     These appear on THIS page only. Sub-pages are parts of the same record. -->
<meta name="citation_title" content="{R["title_full"]}">
<meta name="citation_author" content="{R["author"]}">
<meta name="citation_publication_date" content="{R["year"]}">
<meta name="citation_publisher" content="{R["publisher"]}">
<meta name="citation_abstract_html_url" content="{R["base"]}/thesis">'''
        if R["doi"]: tags += f'\n<meta name="citation_doi" content="{R["doi"]}">'
        if R["pdf"]: tags += f'\n<meta name="citation_pdf_url" content="{R["pdf"]}">'
    robots = "" if R["indexable"] else \
        '\n<!-- Pre-deposit. The work is not ready to be indexed, so it asks not to be.\n     Remove at deposit, not before. -->\n<meta name="robots" content="noindex, follow">'
    nav = "".join(
        f'<a href="{R["base"]}/thesis{p}"{" aria-current=\"page\"" if p==("/"+slug if slug else "") else ""}>{n}</a>'
        for p, n in [("", "Abstract"), ("/propositions", "Propositions"), ("/ledger", "Ledger")])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{heading} &middot; {R["publisher"]}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">{robots}{tags}
<meta property="og:type" content="article">
<meta property="og:title" content="{R["title_full"]}">
<meta property="og:site_name" content="{R["publisher"]}">
<meta property="og:url" content="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R["base"]}/thesis/thesis.css">
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <p class="kicker">{R["publisher"]} &middot; Dissertation</p>
    <h1>{heading}{f'<span class="sub">{R["title_sub"]}</span>' if is_root else ''}</h1>
    <p class="byline">{R["author"]}</p>
    <p class="affil">{R["publisher"]} &middot; {R["year"]}</p>
    <nav class="routes-nav">{nav}</nav>
    <div class="status">
      <strong>Pre-deposit.</strong> {standfirst}
    </div>
  </div>
</header>

<main class="wrap">
{body}
</main>

<footer>
  <div class="wrap">
    <strong>Citing this page.</strong> A draft landing page without a persistent identifier. Do not cite it. Cite the deposited record once it exists.<br><br>
    Correspondence about the apparatus, the sources or the deposit is welcome, including from readers who intend to disprove something here.<br><br>
    {R["publisher"]} &middot; Montana<br>
    {R["author"]} &middot; {R["year"]}
  </div>
</footer>

</body>
</html>
'''

# ------------------------------------------------------------------ CONTENT
ABSTRACT = [
 "Scholarship registers contribution by citation. A dissertation is examined before it can be cited. What is certified at examination is therefore a forecast of contribution rather than contribution itself. This study sets that proposition against three bodies of evidence, historical, experimental and procedural, and then acts on the result.",
 'The first is historical. The European degree ladder is a transposed craft-guild structure in which master and doctor were originally synonymous, both naming the <em>licentia docendi</em>, the licence to teach, neither certifying an original contribution to knowledge. The definition of the doctorate as certifying new knowledge is a modern retrofit, as the historiography of the German university has established: Humboldt\'s memorandum of 1810, the document usually credited with the research ideal, was left a fragment, went unpublished in his lifetime, and first appeared in print in 1903, and the attribution of the ideal to Humboldt is itself a twentieth-century invention. What has not been drawn from that record is its general form: a legitimating origin can be composed long after the fact, and the institution it explains runs unchanged either way.',
 "The second is experimental. A hypnotic induction is the ritual preamble, ordinarily relaxation and fixed attention, held to produce the state in which suggestion works. When identical suggestions are administered with and without one, the resulting effects are closely comparable, though subjects report having been hypnotised only where the induction was performed. A rite that can be removed without changing an outcome is not the cause of that outcome. It is the label attached to it.",
 "The third is procedural. Entry to the principal scholarly indexes is conditioned on the legal form of the depositor rather than on the assessed quality of the work. The index of record for dissertations accepts them only from institutions it recognises as accredited. The principal humanities archive states that it does not publish what it hosts. The registry through which citations are counted admits organisations and not individuals, and an unaffiliated author reaches them only from inside a repository that supplies the standing they lack. The exclusion of unaffiliated scholars is well documented; what follows from it is not. A gate set on legal form rather than merit is satisfied by incorporation rather than by better work, and a gate that cheap screens for nothing it claims to screen for.",
 "The argument is not that examination is worthless. Pre-circulation scrutiny catches error before it propagates, which no citation count can do. Rather, two functions, quality assurance and the registration of contribution, have been fused in one instrument and can be separated. Drawing on the history of the university, on artistic precedents for the self-constituted institution, on Adorno on theory as praxis, and on the performative utterance, it asks what it would mean to register a contribution without certifying it in advance. What emerges is an account of the doctorate as a forecast, and a demonstration of the alternative: a work constituted rather than petitioned, deposited under a persistent identifier, and submitted to a citation record published openly and dated before the first deposit.",
]

KEYWORDS = ["orthopraxy","credentialism","doctoral education","history of universities",
            "Humboldt myth","suggestion and response expectancy","scholarly indexing",
            "independent scholars","institutional repositories","open access","artistic research"]

REFS = [
 'Ash, Mitchell G. "Bachelor of What, Master of Whom? The Humboldt Myth and Historical Transformations of Higher Education in German-Speaking Europe and the US." <em>European Journal of Education</em> 41, no. 2 (2006): 245&ndash;267.',
 'Collins, Randall. <em>The Credential Society: An Historical Sociology of Education and Stratification</em>. New York: Academic Press, 1979. Reissued, New York: Columbia University Press, 2019. ISBN 9780231192347.',
 'ElSabry, ElHassan. "Unaffiliated Researchers: A Preliminary Study." <em>Challenges</em> 8, no. 2 (2017): article 20. <a href="https://doi.org/10.3390/challe8020020">https://doi.org/10.3390/challe8020020</a>',
 'Hull, Clark L. <em>Hypnosis and Suggestibility: An Experimental Approach</em>. New York: D. Appleton-Century, 1933.',
 'Humboldt, Wilhelm von. "&Uuml;ber die innere und &auml;u&szlig;ere Organisation der h&ouml;heren wissenschaftlichen Anstalten zu Berlin." Written 1810; first published in <em>Wilhelm von Humboldts gesammelte Schriften</em>, vol. 10, edited by Bruno Gebhardt. Berlin: B. Behr, 1903.',
 'Khanna, Saurabh, Jon Ball, Juan Pablo Alperin, and John Willinsky. "Recalibrating the Scope of Scholarly Publishing: A Modest Step in a Vast Decolonization Process." <em>Quantitative Science Studies</em> 3, no. 4 (2022). <a href="https://doi.org/10.1162/qss_a_00228">https://doi.org/10.1162/qss_a_00228</a>',
 'Kirsch, Irving, and Steven Jay Lynn. "The Altered State of Hypnosis: Changes in the Theoretical Landscape." <em>American Psychologist</em> 50, no. 10 (1995): 846&ndash;858.',
 'Rashdall, Hastings. <em>The Universities of Europe in the Middle Ages</em>. New edition, 3 vols. Edited by F. M. Powicke and A. B. Emden. Oxford: Clarendon Press, 1936. ISBN 9780198229810.',
 'Rasmussen, Lisa M., Alex Pearlman, Rachel Choi, and Anna Wexler. "Research Infrastructure Challenges in Non-Establishment Research During the COVID-19 Pandemic." <em>Citizen Science: Theory and Practice</em> 10, no. 1 (2025): article 26. <a href="https://doi.org/10.5334/cstp.805">https://doi.org/10.5334/cstp.805</a>',
 'Smith, Kevin L. "Examining Publishing Practices: Moving beyond the Idea of Predatory Open Access." <em>Insights</em> 30, no. 3 (2017): 4&ndash;10. <a href="https://doi.org/10.1629/uksg.388">https://doi.org/10.1629/uksg.388</a>',
 'Tennant, Jonathan P. "Web of Science and Scopus Are Not Global Databases of Knowledge." <em>European Science Editing</em> 46 (2020): e51987. <a href="https://doi.org/10.3897/ese.2020.e51987">https://doi.org/10.3897/ese.2020.e51987</a>',
 'Verger, Jacques. <em>Les universit&eacute;s au Moyen &Acirc;ge</em>. Paris: Presses Universitaires de France, 1973. R&eacute;&eacute;dition Quadrige, 1999. ISBN 9782130621294.',
 'Weber, Max. <em>Economy and Society: An Outline of Interpretive Sociology</em>. Edited by Guenther Roth and Claus Wittich. 2 vols. Berkeley: University of California Press, 1978. ISBN 9780520035003.',
]

# Propositions. Labels are permanent: append, never insert, never renumber.
# cite: "source" = somebody else's finding. "work" = claimed here.
PROPS = [
 ("A","The historical record","Findings established by others, restated for navigation."),
 ("A1","The European degree ladder is a craft-guild structure transposed onto knowledge: bachelor, master and doctor correspond to the apprentice, journeyman and master of the medieval trades.","rashdall-1936, verger-1973","source"),
 ("A2","Doctoral training was formally an apprenticeship to a guild, and the customary term of study before admission to the guild of Master of Arts was seven years, matching the apprenticeship term of other medieval occupations.","rashdall-1936","source"),
 ("A3","Master and doctor were originally synonymous. Both named a single thing, the licentia docendi, the licence to teach.","rashdall-1936, verger-1973","source"),
 ("A4","Neither degree originally certified an original contribution to knowledge. Both certified admission to the body licensed to teach.","rashdall-1936, verger-1973","source"),
 ("A5","The licentia docendi was an ecclesiastical instrument. Papal intervention in 1179 requiring that the licence be granted to the qualified centralised authority over who might teach and, by extension, over what could be taught.","rashdall-1936","source"),
 ("A6","The medieval university secured a near-monopoly over a particular kind of teaching and culture. Closure was a social function of the institution, not a later corruption of it.","verger-1973","source"),
 ("A7","The definition of the doctorate as certifying the production of new knowledge is a modern retrofit onto a medieval licence to teach. It is not inherited from the institution's founding structure.","rashdall-1936, verger-1973, humboldt-1810","work"),
 ("A8","Humboldt's memorandum on the organisation of the higher scientific institutions in Berlin, written in 1810 and the source usually credited with the research-university ideal, was left unfinished and was not published in his lifetime.","humboldt-1810","source"),
 ("A9","The memorandum was first published in 1903, in the volume of Humboldt's political writings edited by Bruno Gebhardt for the Prussian Academy of Sciences, ninety-three years after it was written. Amended October 2026: the earlier wording gave 1900 as a date of recovery, which no source supports. The claim now anchors on publication, which is documented.","humboldt-1810, verified against catalogue records","source"),
 ("A10","The founding document of the research-university ideal became publicly available approximately a century after the institution it is credited with founding, and therefore cannot have exerted the influence attributed to it during that period. Reclassified October 2026: this inference is already established in the historiography and is no longer claimed here.","ash-2006, paletschek-2001, vom-bruch-1997","source"),
 ("A11","The retrospective attribution of the research-university ideal to Humboldt is itself a recognised object of scholarship, treated in the literature as the Humboldt myth.","ash-1999, ash-2006","source"),
 ("B","The experimental record","Findings established by others, at the precision their sources support."),
 ("B1","When identical suggestions are administered with and without a hypnotic induction, the contribution of the induction to the resulting effect is small.","hull-1933","source"),
 ("B2","Hypnotic and non-hypnotic suggestibility are very highly correlated, indicating that they are not distinct capacities.","hull-1933","source"),
 ("B3","Suggestions given without any induction procedure produce substantial changes in perception, memory and voluntary action.","barber-1969","source"),
 ("B4","Hypnotic responding is accounted for by expectancy, attitude and imaginative involvement, without requiring the postulation of an altered state of consciousness.","kirsch-lynn-1995","source"),
 ("B5","Hypnotic effects persist when the procedure is fully disclosed to the subject. Disclosure of the mechanism does not abolish the mechanism.","kirsch, on non-deceptive placebo","source"),
 ("B6","Given the same suggestion with and without an induction, subjects report equivalent perceptual effects but report having been hypnotised only when an induction was performed. The ceremony reliably alters the label rather than the result.","kirsch et al.","source"),
 ("B7","A class of utterances does not describe a state of affairs but brings one into being. Naming, promising and founding are acts performed in speech rather than reports about the world.","austin-1962","source"),
 ("B8","Abstract concepts are structured by sensorimotor metaphor drawn from bodily experience. Reason is not separable from the body that carries it.","embodied-cognition","source"),
 ("B9","Perception is the resolution of prediction error against prior expectation rather than the passive reception of sensory input.","predictive-processing","source"),
 ("B10","Dopaminergic signalling encodes the difference between received and predicted reward. Salience is therefore a function of the gap between expectation and event rather than of magnitude alone.","reward-prediction-error","source"),
 ("B11","Emotion is constructed, predicted from interoceptive signals and learned conceptual categories, rather than triggered as a fixed reaction.","constructed-emotion","source"),
 ("B12","Aesthetic experiences rated most moving are accompanied by activation in medial prefrontal regions of the default mode network, the system associated with self-referential processing.","dmn-aesthetics","source"),
 ("B13","The interstitium is a fluid-filled connective-tissue space distributed throughout the body and continuous with the fascia. Injected tattoo pigment has been imaged migrating through interstitial spaces of the dermis into the subcutaneous fascia. Stated as continuity with fascia; the popular new-organ framing is contested and is not asserted here.","interstitium-2018","source"),
 ("C","Distinctions","Inferences drawn in this work from the two records above."),
 ("C1","A ceremony that can be removed without materially changing an outcome is not the cause of that outcome. Where a ritual is claimed to produce an effect, the test is subtraction.","generalised from B1, B2, B3, B6","work"),
 ("C2","Certification is issued in advance of the use it purports to warrant. It is therefore a forecast of use rather than an instance of it, and stands in the same relation to use as a promise stands to performance.","austin-1962, structural","work"),
 ("C3","A promise is a performative that can fail. Certification, being a promise about future use, inherits that liability: it can be issued correctly and still not come true.","austin-1962, derived from B7 and C2","work"),
 ("C4","Attention and citation are distinct quantities. Attention produces an audience and leaves no durable record; citation requires a persistently addressable artifact and produces a countable one. Reach is therefore not evidence of contribution under the discipline's own accounting.","structural","work"),
 ("C5","Entry to the principal scholarly indexes is conditioned on the legal form of the depositor, an accredited institution, a selected publisher, or a dues-paying member organisation, rather than on the assessed quality of the work. Access is a property of legal form. The exclusion of unaffiliated scholars is not claimed here and is credited to the authors who established it.","verified against platform documentation October 2026; exclusion per elsabry-2017, tennant-2020, khanna-2022","work"),
 ("C6","A gate set on the legal form of the depositor rather than on the merit of the work is satisfied by incorporation rather than by better work. It therefore screens for the capacity to constitute an organisation, not for the quality it is held to protect, and the cost of satisfying it is a measure of what it actually selects for.","derived from C5, structural","work"),
 ("D","The claim","One proposition. It requires the two records and the six distinctions, and nothing else."),
 ("D1","Scholarship registers contribution by citation; a dissertation is examined before it has been cited; the doctorate therefore certifies a prediction rather than a contribution.","the thesis, derived from C1 to C6","work"),
]

# ------------------------------------------------------------- PAGE BUILDERS
def build_landing():
    body = '<h2>Abstract</h2>\n<div id="abstract">\n<hr class="lede-rule">\n'
    body += "\n".join(f"<p>{p}</p>" for p in ABSTRACT) + "\n</div>\n\n"
    body += '<h2>Keywords</h2>\n<p class="keywords">' + "".join(f"<span>{k}</span>" for k in KEYWORDS) + "</p>\n\n"
    body += f'''<h2>Record</h2>
<ul class="meta">
  <li><span class="k">Title</span><span class="v">{R["title_full"]}</span></li>
  <li><span class="k">Author</span><span class="v">{R["author"]}</span></li>
  <li><span class="k">ORCID</span><span class="v">{pending(R["orcid"],"not yet registered")}</span></li>
  <li><span class="k">Publisher</span><span class="v">{R["publisher"]}</span></li>
  <li><span class="k">Year</span><span class="v">{R["year"]}</span></li>
  <li><span class="k">Canonical DOI</span><span class="v">{pending(R["doi"],"not yet minted")}</span></li>
  <li><span class="k">Mirror DOI</span><span class="v">{pending(R["doi_mirror"],"not yet minted")}</span></li>
  <li><span class="k">Licence</span><span class="v">{pending(R["licence"],"CC BY, version to be confirmed")}</span></li>
</ul>

<h2>Verification</h2>
<p class="note-block">A stage is marked complete only when a second reader has confirmed it.</p>
<ul class="meta">
  <li><span class="k">Platform claims</span><span class="v">ProQuest, JSTOR and Crossref checked against their own documentation &middot; complete, October 2026</span></li>
  <li><span class="k">Humboldt record</span><span class="v">Publication date confirmed against catalogue records; the attribution credited to Ash, Paletschek and vom Bruch &middot; complete, October 2026</span></li>
  <li><span class="k">Claim register</span><span class="v">Every assertion extracted with its attached citation &middot; in progress</span></li>
  <li><span class="k">Source acquisition</span><span class="v">The cited texts obtained in citable editions &middot; in progress</span></li>
  <li><span class="k">Experimental record</span><span class="v">{pending(None,"Hull and Kirsch not yet checked &middot; not started")}</span></li>
  <li><span class="k">Page-level check</span><span class="v">{pending(None,"Each proposition checked against the text it names &middot; not started")}</span></li>
  <li><span class="k">Deposit</span><span class="v">{pending(None,"Canonical deposit, mirrors and DOI &middot; not started")}</span></li>
</ul>

<h2>References</h2>
<div id="references"><ol>
''' + "\n".join(f"  <li>{r}</li>" for r in REFS) + "\n</ol></div>\n"
    return page("", R["title_main"],
        "No identifier has been minted. The abstract is not final and the ledger is not yet open. Nothing on this page is a claim about work already done.",
        body, "A study of what the doctoral degree certifies, set against the history of the credential, the experimental record on ceremony, and the mechanics of scholarly indexing.", is_root=True)

def build_propositions():
    body = '''<p class="note-block">Every load-bearing claim in the work, stated once and labelled permanently. Labels are assigned once and never reused: new propositions append, they do not insert, because insertion would renumber everything after it and break citations already made. A proposition later found to be wrong keeps its number and is marked withdrawn, with the reason given.</p>
<p class="note-block">A proposition marked <strong>cite source</strong> is somebody else's finding, restated here only so it can be found. Cite the source named beneath it. A proposition marked <strong>cite this work</strong> is an inference made here, and the sources beneath it are what it rests on rather than where it came from. The form is the work's identifier and the label, for example <code>Pissarro 2026, C2</code>. Cite the label rather than the page: labels are permanent, pages are not.</p>
'''
    for item in PROPS:
        if len(item) == 3:
            band, name, blurb = item
            body += f'\n<h2 id="{band}">Band {band} &middot; {name}</h2>\n<p class="note-block">{blurb}</p>\n'
        else:
            lab, text, src, cite = item
            cls = "cite-work" if cite == "work" else "cite-source"
            word = "cite this work" if cite == "work" else "cite source"
            body += f'''<div class="prop" id="{lab}">
  <a class="prop-label" href="#{lab}">{lab}</a>
  <p class="prop-text">{text}</p>
  <p class="prop-src">{src} <span class="{cls}">{word}</span></p>
</div>
'''
    return page("propositions", "Propositions",
        "Labels are permanent and already citable by label. The propositions themselves are not final until the work is deposited.",
        body, "The load-bearing claims of the work, labelled permanently, each saying whether to cite the source or to cite this work.")

def build_ledger():
    opened = R["ledger_opened"]
    if opened:
        head = f'<p class="ledger-open">Ledger opened: <strong>{opened}</strong> &middot; Entries: <strong>0</strong></p>'
    else:
        head = '<p class="ledger-open pending">Ledger not yet opened. The opening date is permanent once set, and must be set before the first deposit.</p>'
    body = f'''{head}

<p class="note-block">A public record of every citation this work receives. It is opened and dated <em>before</em> the first deposit, because an empty ledger published in advance demonstrates that the wager was made before the outcome was known, and one produced afterwards demonstrates nothing. An accruing record supports the claim; an empty one would be equally visible. That is the point of publishing it.</p>

<h2>Entries</h2>
<p class="note-block">None yet. Nothing has been deposited, so nothing can have cited it.</p>

<h2>Cadence</h2>
<p class="note-block">Sources are checked monthly by hand until volume justifies automation, so a gap reads as schedule rather than concealment. Citations that fall outside the indexes, in catalogues, syllabi and reviews, are recorded here too: those are the ones the machines miss.</p>

<h2>Sources polled</h2>
<ul class="meta">
  <li><span class="k">Crossref</span><span class="v">Registered links between DOIs. The machine-countable spine.</span></li>
  <li><span class="k">OpenAlex</span><span class="v">Open bibliographic graph with a public API.</span></li>
  <li><span class="k">Semantic Scholar</span><span class="v">A second open graph, used as a cross-check.</span></li>
  <li><span class="k">Google Scholar</span><span class="v">No API. Checked manually, and the broadest capture: books, theses and grey literature.</span></li>
  <li><span class="k">Manual</span><span class="v">Catalogues, syllabi, reviews, exhibition texts.</span></li>
</ul>

<h2>Schema</h2>
<p class="note-block">Each entry is one object in <a href="{R["base"]}/thesis/ledger/ledger.json">ledger.json</a>, keyed on the citing DOI so the same citation found in several sources is recorded once.</p>
<pre class="schema">{{
  "edge":          "cited-by",
  "citing_author": "",
  "citing_title":  "",
  "venue":         "",
  "year":          0,
  "citing_doi":    "",
  "cites_prop":    "",   // which proposition, if identifiable
  "cites_node":    "",   // which bibliography node, if identifiable
  "date_added":    "",
  "source":        ""    // crossref | openalex | semanticscholar | scholar | manual
}}</pre>
'''
    return page("ledger", "Citation ledger",
        "The ledger is published before the first deposit, empty and dated, rather than after.",
        body, "A public record of every citation this work receives, opened and dated before the first deposit.")

CSS = '''/* paulpissarro.com/thesis - shared across every page under /thesis.
   Generated context: edit here, not per page. */
:root{
  --cream:#f5f2eb; --ink:#16130f; --gold:#c9a24b;
  --rust:#b0662f; --violet:#7d5bbe; --green:#4a7a3a;
  --muted:#6b6358; --rule:#ddd6c8;
  --serif:'Fraunces',Georgia,'Times New Roman',serif;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  --mono:'JetBrains Mono',ui-monospace,'SF Mono',Menlo,monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--cream);color:var(--ink);font-family:var(--sans);
  font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased}
.wrap{max-width:46rem;margin:0 auto;padding:0 16px}

header.masthead{border-bottom:1px solid var(--rule);padding:2.5rem 0 1.75rem}
.kicker{font-family:var(--mono);font-size:.68rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--muted);margin:0 0 1.25rem}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(1.8rem,5vw,2.7rem);
  line-height:1.15;letter-spacing:-.015em;margin:0 0 .6rem}
h1 .sub{display:block;font-size:.46em;font-weight:400;font-style:italic;
  color:var(--muted);letter-spacing:0;margin-top:.5rem}
.byline{font-size:1rem;margin:0 0 .35rem}
.affil{font-size:.92rem;color:var(--muted);margin:0}

.routes-nav{margin:1.5rem 0 0;display:flex;flex-wrap:wrap;gap:1.25rem;
  font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase}
.routes-nav a{color:var(--muted);text-decoration:none;padding-bottom:.25rem;
  border-bottom:1px solid transparent}
.routes-nav a:hover{color:var(--ink);border-bottom-color:var(--gold)}
.routes-nav a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--gold)}

.status{margin-top:1.5rem;padding:.7rem .9rem;border-left:3px solid var(--rust);
  background:rgba(176,102,47,.06);font-size:.88rem;color:var(--muted)}
.status strong{color:var(--rust);font-weight:600}

main{padding:2.5rem 0 1rem}
h2{font-family:var(--mono);font-size:.7rem;font-weight:500;letter-spacing:.18em;
  text-transform:uppercase;color:var(--muted);margin:3rem 0 1rem;
  padding-bottom:.5rem;border-bottom:1px solid var(--rule);scroll-margin-top:1rem}
h2:first-of-type{margin-top:0}
#abstract p{margin:0 0 1.15rem}
#abstract p:first-of-type{font-size:1.06rem}
.lede-rule{width:3rem;height:2px;background:var(--gold);border:0;margin:0 0 1.6rem}
.note-block{font-size:.95rem;color:var(--muted);margin:0 0 1rem}
em,i{font-style:italic}
code{font-family:var(--mono);font-size:.88em}

.meta{list-style:none;margin:0;padding:0;font-family:var(--mono);font-size:.82rem}
.meta li{display:flex;gap:1rem;padding:.55rem 0;border-bottom:1px solid var(--rule)}
.meta li:last-child{border-bottom:0}
.meta .k{flex:0 0 9rem;color:var(--muted);text-transform:uppercase;
  font-size:.68rem;letter-spacing:.1em;padding-top:.15rem}
.meta .v{flex:1;word-break:break-word}
.meta .v a{color:var(--ink)}
.pending{color:var(--rust)}

.keywords{font-family:var(--mono);font-size:.82rem;color:var(--muted);line-height:2}
.keywords span{display:inline-block;padding:.12rem .5rem;margin:0 .3rem .4rem 0;
  border:1px solid var(--rule);border-radius:2px;background:rgba(255,255,255,.5)}

.prop{padding:1.1rem 0;border-bottom:1px solid var(--rule)}
.prop-label{font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:.1em;
  color:var(--gold);text-decoration:none;display:inline-block;margin-bottom:.4rem}
.prop-label:hover{color:var(--rust)}
.prop-text{margin:0 0 .5rem;font-size:.98rem}
.prop-src{margin:0;font-family:var(--mono);font-size:.72rem;color:var(--muted)}
.cite-source,.cite-work{display:inline-block;padding:.05rem .4rem;margin-left:.4rem;
  border-radius:2px;font-size:.92em;white-space:nowrap}
.cite-source{color:var(--green);border:1px solid var(--green)}
.cite-work{color:var(--rust);border:1px solid var(--rust)}

.ledger-open{font-family:var(--mono);font-size:.85rem;padding:.8rem .9rem;
  border:1px solid var(--rule);background:rgba(255,255,255,.4);margin:0 0 1.5rem}
.schema{font-family:var(--mono);font-size:.78rem;line-height:1.7;overflow-x:auto;
  padding:1rem;border:1px solid var(--rule);background:rgba(255,255,255,.4);
  color:var(--ink);white-space:pre}

#references ol{padding-left:1.3rem;margin:0;font-size:.9rem}
#references li{margin:0 0 .85rem;line-height:1.55}
#references a{color:var(--muted)}

footer{border-top:1px solid var(--rule);margin-top:3.5rem;padding:1.75rem 0 3rem;
  font-family:var(--mono);font-size:.72rem;color:var(--muted);line-height:1.9}

@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --cream:#16130f;--ink:#f0ece3;--muted:#9a9184;--rule:#302a22;
    --gold:#d4b163;--rust:#cf7f44;--green:#7aa468;
  }
  :root:not([data-theme="light"]) .keywords span,
  :root:not([data-theme="light"]) .ledger-open,
  :root:not([data-theme="light"]) .schema{background:rgba(255,255,255,.04)}
  :root:not([data-theme="light"]) .status{background:rgba(207,127,68,.08)}
}
:root[data-theme="dark"]{
  --cream:#16130f;--ink:#f0ece3;--muted:#9a9184;--rule:#302a22;
  --gold:#d4b163;--rust:#cf7f44;--green:#7aa468;
}
'''

# ----------------------------------------------------------------- EMIT
def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote thesis/{rel}  ({len(content):,} bytes)")

if __name__ == "__main__":
    print("Building /thesis ...")
    write("thesis.css", CSS)
    write("index.html", build_landing())
    write("propositions/index.html", build_propositions())
    write("ledger/index.html", build_ledger())
    write("ledger/ledger.json", json.dumps(
        {"opened": R["ledger_opened"], "entries": []}, indent=2) + "\n")

    # Sitemap for the whole domain, regenerated so /thesis is always listed.
    today = datetime.date.today().isoformat()
    pages = [("/","1.0"),("/thesis","0.9"),("/thesis/propositions","0.8"),
             ("/thesis/ledger","0.8"),("/glossary/","0.6"),("/provenance/","0.6"),
             ("/coaching/","0.5"),("/white/","0.5"),("/latamreport/","0.5")]
    urls = "\n".join(
        f"  <url>\n    <loc>{R['base']}{p}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
        for p, pr in pages)
    (ROOT.parent / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{urls}\n</urlset>\n', encoding="utf-8")
    print("  wrote sitemap.xml")
    print("Done. Do not hand-edit the generated files.")
