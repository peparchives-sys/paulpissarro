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
import datetime, html, json, pathlib, subprocess, sys, re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT.parent

# ---------------------------------------------------------------- THE RECORD
# One source of truth. Everything downstream reads from here.
R = {
    "title_main": "The Dissertation as Orthopraxy",
    "title_sub":  "Examination, Citation, and the Legal Form of Access",
    "author":     "Pissarro, Paul-Alexander Arthur",   # canonical. never vary.
    "year":       "2026",
    "publisher":  "Church of Conceptual Art",
    "base":       "https://paulpissarro.com",
    "orcid":      "0009-0000-0830-8438",
    "doi":        None,          # set on deposit. irreversible.
    "doi_mirror": None,
    "version":    "v0.1",       # public edition line. v1.0 is the first deposit.
    "licence":    None,          # CC BY, exact version to confirm
    "pdf":        None,          # must end in .pdf, text build only
    "indexable":  False,         # flip to True only at deposit
    "institution": None,         # citation_dissertation_institution. Scholar asks for it
                                 # on dissertations. Whether CoCA goes here is Paul's call.
    "ledger_opened": None,       # set once, permanent. ISO date.
}
R["title_full"] = f'{R["title_main"]}: {R["title_sub"]}'

def orcid_html():
    if not R["orcid"]:
        return pending(None, "not yet registered")
    return f'<a href="https://orcid.org/{R["orcid"]}">{R["orcid"]}</a>'

def pending(v, fallback):
    return v if v else f'<span class="pending">{fallback}</span>'

def esc(v):
    """For attribute values. The title has changed three times already."""
    return html.escape(str(v), quote=True)

def url_for(slug):
    # Pages serves /thesis/ and 301s /thesis to it. Canonical and citation
    # URLs must be the address that answers 200, not the redirect.
    return f'{R["base"]}/thesis/' + (f'{slug}/' if slug else '')

# ------------------------------------------------------------------ TEMPLATE
def page(slug, heading, standfirst, body, desc, is_root=False):
    """slug: '' for the landing page, else 'propositions', 'ledger'."""
    url  = url_for(slug)
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
<meta name="citation_title" content="{esc(R["title_full"])}">
<meta name="citation_author" content="{esc(R["author"])}">
<meta name="citation_publication_date" content="{esc(R["year"])}">
<meta name="citation_publisher" content="{esc(R["publisher"])}">
<meta name="citation_abstract_html_url" content="{url_for("")}">'''
        if R["institution"]: tags += f'\n<meta name="citation_dissertation_institution" content="{esc(R["institution"])}">'
        if R["doi"]: tags += f'\n<meta name="citation_doi" content="{esc(R["doi"])}">'
        if R["pdf"]: tags += f'\n<meta name="citation_pdf_url" content="{esc(R["pdf"])}">'
    robots = "" if R["indexable"] else \
        '\n<!-- Pre-deposit. The work is not ready to be indexed, so it asks not to be.\n     Remove at deposit, not before. -->\n<meta name="robots" content="noindex, follow">'
    # Kept outside the f-string: a backslash inside an f-string expression is
    # a SyntaxError before Python 3.12, and macOS still ships 3.9.
    cur = ' aria-current="page"'
    nav = "".join(
        f'<a href="/thesis/{p}"{cur if p == (slug + "/" if slug else "") else ""}>{n}</a>'
        for p, n in [("", "Abstract"), ("propositions/", "Propositions"), ("ledger/", "Ledger")])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{heading} &middot; {R["publisher"]}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">{robots}{tags}
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(R["title_full"])}">
<meta property="og:site_name" content="{esc(R["publisher"])}">
<meta property="og:url" content="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/thesis/thesis.css">
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

def cited_keys():
    """Every source key the propositions actually cite, in order of first use."""
    seen, out = set(), []
    for item in PROPS:
        if len(item) != 4:
            continue
        for part in re.split(r"[;,]", item[2]):
            k = part.strip()
            if k in SOURCES and k not in seen:
                seen.add(k); out.append(k)
    return out


# Propositions. Labels are permanent: append, never insert, never renumber.
# cite: "source" = somebody else's finding. "work" = claimed here.
# Every source a proposition cites, keyed. The reference list on the landing
# page is GENERATED from the keys the propositions actually use, so it cannot
# drift from the argument: a source nobody cites does not appear, and a key
# with no entry here stops the build.
#
# Scope rule: this list is the sources the propositions rest on. It is not a
# reading list. When the prose exists and cites something further, that source
# earns an entry then.
SOURCES = {
 "ash-1999": 'Ash, Mitchell G., ed. <em>Mythos Humboldt: Vergangenheit und Zukunft der deutschen Universit&auml;ten</em>. Vienna: B&ouml;hlau, 1999.',
 "ash-2006": 'Ash, Mitchell G. "Bachelor of What, Master of Whom? The Humboldt Myth and Historical Transformations of Higher Education in German-Speaking Europe and the US." <em>European Journal of Education</em> 41, no. 2 (2006): 245&ndash;267.',
 "austin-1962": 'Austin, J. L. <em>How to Do Things with Words</em>. Oxford: Clarendon Press, 1962. The William James Lectures, 1955.',
 "barber-1969": 'Barber, Theodore X. <em>Hypnosis: A Scientific Approach</em>. New York: Van Nostrand Reinhold, 1969.',
 "constructed-emotion": 'Barrett, Lisa Feldman. <em>How Emotions Are Made: The Secret Life of the Brain</em>. Boston: Houghton Mifflin Harcourt, 2017. With Antonio Damasio, <em>Descartes\' Error</em>. New York: Putnam, 1994.',
 "dmn-aesthetics": 'Vessel, Edward A., G. Gabrielle Starr, and Nava Rubin. "The Brain on Art: Intense Aesthetic Experience Activates the Default Mode Network." <em>Frontiers in Human Neuroscience</em> 6 (2012): article 66. <a href="https://doi.org/10.3389/fnhum.2012.00066">https://doi.org/10.3389/fnhum.2012.00066</a>',
 "embodied-cognition": 'Lakoff, George, and Mark Johnson. <em>Metaphors We Live By</em>. Chicago: University of Chicago Press, 1980. And <em>Philosophy in the Flesh: The Embodied Mind and Its Challenge to Western Thought</em>. New York: Basic Books, 1999.',
 "hobsbawm-ranger-1983": 'Hobsbawm, Eric, and Terence Ranger, eds. <em>The Invention of Tradition</em>. Cambridge: Cambridge University Press, 1983.',
 "hull-1933": 'Hull, Clark L. <em>Hypnosis and Suggestibility: An Experimental Approach</em>. New York: D. Appleton-Century, 1933.',
 "humboldt-1810": 'Humboldt, Wilhelm von. "&Uuml;ber die innere und &auml;u&szlig;ere Organisation der h&ouml;heren wissenschaftlichen Anstalten zu Berlin." Written 1810; first published in <em>Wilhelm von Humboldts gesammelte Schriften</em>, vol. 10, edited by Bruno Gebhardt. Berlin: B. Behr, 1903.',
 "khanna-2022": 'Khanna, Saurabh, Jon Ball, Juan Pablo Alperin, and John Willinsky. "Recalibrating the Scope of Scholarly Publishing: A Modest Step in a Vast Decolonization Process." <em>Quantitative Science Studies</em> 3, no. 4 (2022). <a href="https://doi.org/10.1162/qss_a_00228">https://doi.org/10.1162/qss_a_00228</a>',
 "barber-calverley-1964": 'Barber, Theodore X., and David S. Calverley. "An Experimental Study of &lsquo;Hypnotic&rsquo; (Auditory and Visual) Hallucinations." <em>Journal of Abnormal and Social Psychology</em> 68, no. 1 (1964): 13&ndash;20.',
 "braffman-kirsch-1999": 'Braffman, Wayne, and Irving Kirsch. "Imaginative Suggestibility and Hypnotizability: An Empirical Analysis." <em>Journal of Personality and Social Psychology</em> 77, no. 3 (1999): 578&ndash;587. <a href="https://doi.org/10.1037/0022-3514.77.3.578">https://doi.org/10.1037/0022-3514.77.3.578</a>',
 "dienes-perner-2007": 'Dienes, Zolt&aacute;n, and Josef Perner. "Executive Control without Conscious Awareness: The Cold Control Theory of Hypnosis." In <em>Hypnosis and Conscious States: The Cognitive Neuroscience Perspective</em>, edited by Graham A. Jamieson. Oxford: Oxford University Press, 2007.',
 "fendel-et-al-2025": 'Fendel, Johannes C., Carolin Tiersch, Pauline S&ouml;lder, Jens Gaab, and Stefan Schmidt. "Effects of Open-Label Placebos across Outcomes and Populations: An Updated Systematic Review and Meta-Analysis of Randomized Controlled Trials." <em>Scientific Reports</em> (2025). <a href="https://doi.org/10.1038/s41598-025-14895-z">https://doi.org/10.1038/s41598-025-14895-z</a>',
 "gandhi-oakley-2005": 'Gandhi, Bhaskar, and David A. Oakley. "Does &lsquo;Hypnosis&rsquo; by Any Other Name Smell as Sweet? The Efficacy of &lsquo;Hypnotic&rsquo; Inductions Depends on the Label &lsquo;Hypnosis&rsquo;." <em>Consciousness and Cognition</em> 14, no. 2 (2005): 304&ndash;315. <span class="pending">Sample size and statistics not yet verified against the published paper.</span>',
 "glass-barber-1961": 'Glass, Lowell B., and Theodore X. Barber. "A Note on Hypnotic Behavior, the Definition of the Situation and the Placebo Effect." <em>Journal of Nervous and Mental Disease</em> 132 (1961): 539&ndash;541.',
 "kekecs-et-al-2024": 'Kekecs, Zolt&aacute;n, Bence Nyiri, Cameron Alldredge, Barnab&aacute;s Cserni, Pietro Rizzo, Bal&aacute;zs Domok, Viktor Vizkievicz, Adri&aacute;n Takacs, Kinga Giran, Judit K. Nagy, and Gary Elkins. "The Effectiveness of Hypnoanalgesia Using Conventional and Placebo Hypnosis Induction." <em>Journal of Pain</em> 25, no. 8 (2024): 104519. <a href="https://doi.org/10.1016/j.jpain.2024.03.015">https://doi.org/10.1016/j.jpain.2024.03.015</a>',
 "kihlstrom-2008": 'Kihlstrom, John F. "The Domain of Hypnosis, Revisited." In <em>The Oxford Handbook of Hypnosis: Theory, Research, and Practice</em>, edited by Michael R. Nash and Amanda J. Barnier, 21&ndash;52. Oxford: Oxford University Press, 2008. <a href="https://doi.org/10.1093/oxfordhb/9780198570097.013.0002">https://doi.org/10.1093/oxfordhb/9780198570097.013.0002</a>',
 "kihlstrom-2018": 'Kihlstrom, John F. "Hypnosis as an Altered State of Consciousness." <em>Journal of Consciousness Studies</em> 25, nos. 11&ndash;12 (2018): 53&ndash;72.',
 "juliani-mohl-2016": 'Juliani, Sidney, and Jeffrey Mohl. "Increased Suggestibility May Occur Following a Waking Suggestion: A Finding Contrary to Clark Hull&rsquo;s Conclusion on the Nature of Heteroactive Hypersuggestibility." <em>Contemporary Hypnosis and Integrative Therapy</em> 31, no. 1 (2016): 28&ndash;40.',
 "kirsch-1996": 'Kirsch, Irving. "Hypnosis in Psychotherapy: Efficacy and Mechanisms." <em>Contemporary Hypnosis</em> 13, no. 2 (1996): 109&ndash;114.',
 "kirsch-et-al-2008": 'Kirsch, Irving, Giuliana Mazzoni, Carlo Mondaini, Angela Falcone, Katia Vannucchi, and Luciano Scattina. "Slipping into Trance." <em>Contemporary Hypnosis</em> 25, nos. 3&ndash;4 (2008): 202&ndash;209. <a href="https://doi.org/10.1002/ch.361">https://doi.org/10.1002/ch.361</a>',
 "kirsch-et-al-2011": 'Kirsch, Irving, Etzel Carde&ntilde;a, Stuart Derbyshire, Zolt&aacute;n Dienes, Michael Heap, Sakari Kallio, Giuliana Mazzoni, Peter Naish, David Oakley, Catherine Potter, Vince Walters, and Matthew Whalley. "Definitions of Hypnosis and Hypnotizability and Their Relation to Suggestion and Suggestibility: A Consensus Statement." <em>Contemporary Hypnosis and Integrative Therapy</em> 28, no. 2 (2011): 107&ndash;115.',
 "kirsch-lynn-1995": 'Kirsch, Irving, and Steven Jay Lynn. "The Altered State of Hypnosis: Changes in the Theoretical Landscape." <em>American Psychologist</em> 50, no. 10 (1995): 846&ndash;858. <span class="pending">DOI not yet verified; the argument is cited here from the secondary literature and not yet from the paper itself.</span>',
 "kirsch-mazzoni-montgomery-2007": 'Kirsch, Irving, Giuliana Mazzoni, and Guy H. Montgomery. "Remembrance of Hypnosis Past." <em>American Journal of Clinical Hypnosis</em> 49, no. 3 (2007): 171&ndash;178. <a href="https://doi.org/10.1080/00029157.2007.10401574">https://doi.org/10.1080/00029157.2007.10401574</a>',
 "locher-et-al-2017": 'Locher, Cosima, Antje Frey Nascimento, Irving Kirsch, Joe Kossowsky, Andrea Meyer, and Jens Gaab. "Is the Rationale More Important Than Deception? A Randomized Controlled Trial of Open-Label Placebo Analgesia." <em>Pain</em> 158, no. 12 (2017): 2320&ndash;2328.',
 "lynn-et-al-2002": 'Lynn, Steven Jay, Hollace Vanderhoff, Kelley Shindler, and Jamie Stafford. "Defining Hypnosis as a Trance vs. Cooperation: Hypnotic Inductions, Suggestibility, and Performance Standards." <em>American Journal of Clinical Hypnosis</em> 44, nos. 3&ndash;4 (2002): 231&ndash;240. <a href="https://doi.org/10.1080/00029157.2002.10403483">https://doi.org/10.1080/00029157.2002.10403483</a>',
 "lynn-et-al-2020": 'Lynn, Steven Jay, Irving Kirsch, Devin B. Terhune, and Joseph P. Green. "Myths and Misconceptions about Hypnosis and Suggestion: Separating Fact and Fiction." <em>Applied Cognitive Psychology</em> 34, no. 6 (2020): 1253&ndash;1264. <a href="https://doi.org/10.1002/acp.3730">https://doi.org/10.1002/acp.3730</a>',
 "martin-dienes-2019": 'Martin, Jean-R&eacute;my, and Zolt&aacute;n Dienes. "Bayes to the Rescue: Does the Type of Hypnotic Induction Matter?" <em>Psychology of Consciousness: Theory, Research, and Practice</em> (2019). <span class="pending">Volume, issue, pages and DOI not yet verified.</span>',
 "mcgeown-et-al-2012": 'McGeown, William J., Annalena Venneri, Irving Kirsch, Luca Nocetti, Kelly Roberts, Lisa Foan, and Giuliana Mazzoni. "Suggested Visual Hallucination without Hypnosis Enhances Activity in Visual Areas of the Brain." <em>Consciousness and Cognition</em> 21, no. 1 (2012): 100&ndash;116. <a href="https://doi.org/10.1016/j.concog.2011.10.015">https://doi.org/10.1016/j.concog.2011.10.015</a>',
 "milling-et-al-2010": 'Milling, Leonard S., Elizabeth L. Coursen, Jessica S. Shores, and Jolanta A. Waszkiewicz. "Imaginative Suggestibility and Hypnotizability: Deconstructing Hypnotic Suggestibility." <em>Contemporary Hypnosis</em> 27, no. 4 (2010): 233&ndash;256. <span class="pending">DOI not yet verified.</span>',
 "terhune-2024": 'Terhune, Devin B. "Hypnosis." <em>Open Encyclopedia of Cognitive Science</em>. Cambridge, MA: MIT Press, 2024. <a href="https://doi.org/10.21428/e2759450.971dd787">https://doi.org/10.21428/e2759450.971dd787</a>',
 "wagstaff-1977": 'Wagstaff, Graham F. "Goal-Directed Fantasy, the Experience of Nonvolition, and Compliance." <em>Social Behavior and Personality</em> 5, no. 2 (1977): 389&ndash;394. <a href="https://doi.org/10.2224/sbp.1977.5.2.389">https://doi.org/10.2224/sbp.1977.5.2.389</a>',
 "wagstaff-1981": 'Wagstaff, Graham F. <em>Hypnosis, Compliance and Belief</em>. Brighton, Sussex: The Harvester Press, 1981.',
 "wagstaff-altered-state": 'Wagstaff, Graham F. "On the Centrality of the Concept of an Altered State to Definitions of Hypnosis." <em>The Journal of Mind-Body Regulation</em> 2, no. 2: 90&ndash;106. <span class="pending">Year given as 2013 in the article text and 2014 in the secondary literature; end page given as 106 and 108. Unresolved.</span>',
 "zahedi-lynn-sommer-2024": 'Zahedi, Anoushiravan, Steven Jay Lynn, and Werner Sommer. "How Hypnotic Suggestions Work: A Systematic Review of Prominent Theories of Hypnosis." <em>Consciousness and Cognition</em> 123 (2024): 103730. <a href="https://doi.org/10.1016/j.concog.2024.103730">https://doi.org/10.1016/j.concog.2024.103730</a>',
 "paletschek-2001": 'Paletschek, Sylvia. "The Invention of Humboldt and the Impact of National Socialism: The German University Idea in the First Half of the Twentieth Century." 2001. <span class="pending">Volume and pages not yet verified against a catalogue record.</span>',
 "predictive-processing": 'Clark, Andy. <em>Surfing Uncertainty: Prediction, Action, and the Embodied Mind</em>. Oxford: Oxford University Press, 2016. And Karl Friston, "The Free-Energy Principle: A Unified Brain Theory?" <em>Nature Reviews Neuroscience</em> 11 (2010): 127&ndash;138. <a href="https://doi.org/10.1038/nrn2787">https://doi.org/10.1038/nrn2787</a>',
 "rashdall-1936": 'Rashdall, Hastings. <em>The Universities of Europe in the Middle Ages</em>. New edition, 3 vols. Edited by F. M. Powicke and A. B. Emden. Oxford: Clarendon Press, 1936.',
 "reward-prediction-error": 'Schultz, Wolfram, Peter Dayan, and P. Read Montague. "A Neural Substrate of Prediction and Reward." <em>Science</em> 275 (1997): 1593&ndash;1599. <a href="https://doi.org/10.1126/science.275.5306.1593">https://doi.org/10.1126/science.275.5306.1593</a>',
 "tennant-2020": 'Tennant, Jonathan P. "Web of Science and Scopus Are Not Global Databases of Knowledge." <em>European Science Editing</em> 46 (2020): e51987. <a href="https://doi.org/10.3897/ese.2020.e51987">https://doi.org/10.3897/ese.2020.e51987</a>',
 "verger-1973": 'Verger, Jacques. <em>Les universit&eacute;s au Moyen &Acirc;ge</em>. Paris: Presses Universitaires de France, 1973. R&eacute;&eacute;dition Quadrige, 1999.',
 "vom-bruch-1997": 'vom Bruch, R&uuml;diger. On the Humboldt tradition as an invention of around 1900. 1997. <span class="pending">Full record not yet verified; cited here because Ash (2006) credits it.</span>',
}

PROPS = [
 ("A","The historical record","Findings established by others, restated for navigation."),
 ("A1","The European degree ladder is a craft-guild structure transposed onto knowledge: bachelor, master and doctor correspond to the apprentice, journeyman and master of the medieval trades.","rashdall-1936, verger-1973","source"),
 ("A2","Doctoral training was formally an apprenticeship to a guild, and the customary term of study before admission to the guild of Master of Arts was seven years, matching the apprenticeship term of other medieval occupations.","rashdall-1936","source"),
 ("A3","Master and doctor were originally synonymous. Both named a single thing, the licentia docendi, the licence to teach.","rashdall-1936, verger-1973","source"),
 ("A4","Neither degree originally certified an original contribution to knowledge. Both certified admission to the body licensed to teach.","rashdall-1936, verger-1973","source"),
 ("A5","The licentia docendi was an ecclesiastical instrument. Papal intervention in 1179 requiring that the licence be granted to the qualified centralised authority over who might teach and, by extension, over what could be taught.","rashdall-1936","source"),
 ("A6","The medieval university secured a near-monopoly over a particular kind of teaching and culture. Closure was a social function of the institution, not a later corruption of it.","verger-1973","source"),
 ("A7","The definition of the doctorate as certifying the production of new knowledge is a modern retrofit onto a medieval licence to teach. It is not inherited from the institution's founding structure.","derived from A1 to A6; rashdall-1936, verger-1973, humboldt-1810","work"),
 ("A8","Humboldt's memorandum on the organisation of the higher scientific institutions in Berlin, written in 1810 and the source usually credited with the research-university ideal, was left unfinished and was not published in his lifetime.","humboldt-1810","source"),
 ("A9","The memorandum was first published in 1903, in the volume of Humboldt's political writings edited by Bruno Gebhardt for the Prussian Academy of Sciences, ninety-three years after it was written. Amended October 2026: the earlier wording gave 1900 as a date of recovery, which no source supports. The claim now anchors on publication, which is documented.","humboldt-1810, verified against catalogue records","source"),
 ("A10","The founding document of the research-university ideal became publicly available approximately a century after the institution it is credited with founding, and therefore cannot have exerted the influence attributed to it during that period. Reclassified October 2026: this inference is already established in the historiography and is no longer claimed here.","ash-2006, paletschek-2001, vom-bruch-1997","source"),
 ("A11","The retrospective attribution of the research-university ideal to Humboldt is itself a recognised object of scholarship, treated in the literature as the Humboldt myth.","ash-1999, ash-2006","source"),
 ("A12","The attribution of a legitimating origin to an institution is a general and recognised phenomenon. Traditions presented as ancient are frequently of recent origin and deliberately composed.","hobsbawm-ranger-1983","source"),
 ("A13","The comparison of identical suggestions given with and without an induction was first run systematically by Hull in 1933. The largest study in that line had thirteen subjects, the dependent measure was response latency on ideomotor suggestions, and subjects in the hypnosis condition had passed an additional screen that those in the waking condition had not. Hull reported that the induction facilitated responses and stated no conclusion about the magnitude of its contribution. A later recomputation of the Hull-era data reports a large effect for one 1930 study, which is the standing objection to B1. Added October 2026 to hold the historical claim that B1 previously carried.","hull-1933, juliani-mohl-2016","source"),
 ("B","The experimental record","Findings established by others, at the precision their sources support."),
 ("B1","When identical suggestions are administered with and without a hypnotic induction, the induction's contribution to measured response is small and reliably non-zero: pooled across four studies, 1.46 suggestions out of ten, standard error 0.20. Amended October 2026: the earlier wording cited Hull alone and credited him with a conclusion about magnitude that he did not state. The characterisation is Kirsch's, reading a literature that begins in 1961; the number is Martin and Dienes's. Hull ran the first version of the design, which is a historical claim and is now held at A13, together with the objection to this one.","martin-dienes-2019, kirsch-mazzoni-montgomery-2007, glass-barber-1961, barber-calverley-1964","source"),
 ("B2","Hypnotic and non-hypnotic suggestibility are very highly correlated, almost as highly as the scales correlate with themselves on retest, indicating that they are not distinct capacities. Reported coefficients run from 0.53 to 0.82. Amended October 2026: the phrase and the finding are the 2011 consensus statement's, not Hull's; no coefficient of Hull's own could be established.","kirsch-et-al-2011, braffman-kirsch-1999, milling-et-al-2010","source"),
 ("B3","Suggestions given without any induction procedure produce substantial changes in perception, memory and voluntary action.","barber-1969","source"),
 ("B4","Hypnotic responding is accounted for by expectancy, attitude and imaginative involvement, without requiring the postulation of an altered state of consciousness.","kirsch-lynn-1995","source"),
 ("B5","Placebo analgesia and symptom relief survive explicit disclosure that the agent is inert, provided the disclosure is accompanied by a plausible account of why an inert agent may work. The one trial isolating disclosure from rationale found that disclosure alone produced no effect. Pooled open-label placebo effects are moderate on self-report, 0.36 standardised mean difference, and null on objective outcomes, 0.02. Amended October 2026: the earlier wording asserted that disclosure does not abolish the mechanism, which the evidence does not support at that strength, and cited no publication. No controlled test of disclosure against concealment exists in hypnosis research; the inference from placebo to suggestion is an argument from analogy and is marked as one.","locher-et-al-2017, fendel-et-al-2025, kirsch-1996","source"),
 ("B6","Given the same suggestion with and without an induction, subjects report comparable perceptual effects, but report having been hypnotised only where an induction was performed, and the sense that the response was involuntary rises measurably with it. In three independent datasets the induction is inert for the outcome and not inert for the phenomenology. Amended October 2026: the earlier wording said the ceremony alters the label rather than the result, which understates its own evidence. The shift in reported involuntariness is measurable and significant.","kirsch-et-al-2008, milling-et-al-2010, kekecs-et-al-2024","source"),
 ("B7","A class of utterances does not describe a state of affairs but brings one into being. Naming, promising and founding are acts performed in speech rather than reports about the world.","austin-1962","source"),
 ("B8","Abstract concepts are structured by sensorimotor metaphor drawn from bodily experience. Reason is not separable from the body that carries it.","embodied-cognition","source"),
 ("B9","Perception is the resolution of prediction error against prior expectation rather than the passive reception of sensory input.","predictive-processing","source"),
 ("B10","Dopaminergic signalling encodes the difference between received and predicted reward. Salience is therefore a function of the gap between expectation and event rather than of magnitude alone.","reward-prediction-error","source"),
 ("B11","Emotion is constructed, predicted from interoceptive signals and learned conceptual categories, rather than triggered as a fixed reaction.","constructed-emotion","source"),
 ("B12","Aesthetic experiences rated most moving are accompanied by activation in medial prefrontal regions of the default mode network, the system associated with self-referential processing.","dmn-aesthetics","source"),
 ("B14","The felt trance state is treated in the consensus literature as an epiphenomenon: a response to the suggestion to enter hypnosis, with no direct causal effect on other suggestions. The experience of nonvolition is not conferred by a trance but is a characteristic of response to suggestion. Markers for the hypothesised state have not been found. B13 was withdrawn before publication and its label is not reused.","kirsch-et-al-2011, lynn-et-al-2020, zahedi-lynn-sommer-2024","source"),
 ("B15","The induction is described in the reference literature as a feature of the hypnotic ritual, and its form does not matter: indirect wording is no more effective than standard, and a doubled induction is no more effective than a single one.","terhune-2024, martin-dienes-2019","source"),
 ("B16","Where the same induction is labelled hypnosis rather than relaxation, subjects are significantly more suggestible. Where subjects are told that hypnotic ability requires achieving a trance, they respond to fewer suggestions. The designation is not inert, and what the designation is taken to mean changes the outcome. Recorded October 2026; the distinction that draws on it is not yet written.","gandhi-oakley-2005, lynn-et-al-2002","source"),
 ("B17","In a four-condition experiment, removing the induction had no appreciable effect on any dimension of responding, while removing the references to cooperation lowered objective responding. The cooperative framing does measurable work where the ritual does not.","lynn-et-al-2002","source"),
 ("B18","Hypnotic responding requires the subject's active participation, and without it nothing happens. The responding is characterised in the literature as a strategic enactment shaped by the subject's understanding of the task, negotiated with the operator. This is the position of a state theorist, who also holds that for highly responsive subjects the induction procedure may be unnecessary.","kihlstrom-2008","source"),
 ("B19","Against B15 and B16: it is argued that the concept of an altered state should be central to any definition of hypnosis, that a relaxation procedure without the label of hypnosis is simply a relaxation procedure, and that hypnosis is therefore not reducible to suggestion. On this account the designation is constitutive rather than descriptive, and the subtraction test does not apply to it, because what remains when the ceremony is removed is a different procedure rather than the same one diminished. It is further argued that a share of hypnotic responding is social compliance rather than co-production. Recorded here because it is the strongest objection to the inferences in Band C and is held by a non-state theorist.","wagstaff-altered-state, wagstaff-1981, wagstaff-1977","source"),
 ("B20","Against B15: highly responsive subjects alter perception with or without an induction, with a small additional benefit from hypnosis, while subjects low in suggestibility succeed in neither condition. Suggestion without ceremony does not produce the phenomena in most people, and trait differences are not abolished by removing the ritual.","mcgeown-et-al-2012, braffman-kirsch-1999","source"),
 ("B21","Against the account of involuntariness in B14: an alternative theory explains the experience of nonvolition through inaccurate higher-order thoughts about intending, without expectancy carrying the explanatory load. No current theory of hypnosis commands assent, and the most recent systematic review calls for new accounts rather than ratifying an existing one.","dienes-perner-2007, zahedi-lynn-sommer-2024","source"),
 ("B22","Against the subtraction inferences generally: the absence of specific neural correlates is held not in itself to argue against classifying hypnosis as an altered state of consciousness.","kihlstrom-2018","source"),
 ("C","Distinctions","Inferences drawn in this work from the two records above. Each states what it serves. Seven of them support the claim in Band D; the others support the historical argument, the method, or Pillar IV. A distinction that served nothing would be a defect, not a spare part."),
 ("C1","A ceremony that can be removed without changing the capacity it is said to produce is not the cause of that capacity, whatever else its removal changes. Where a ritual is claimed to produce an effect, the test is subtraction, and the test requires naming which effect. Amended October 2026: the earlier wording said &ldquo;without materially changing an outcome,&rdquo; which B6 and B14 falsify. Removing the induction leaves the responding intact and removes the reported trance and part of the reported involuntariness. The ceremony does change an outcome. It does not change the capacity.","generalised from B1, B2, B3, B4, B6, B14, B15, B17, B18; contested by B19, B20, B21, B22","work"),
 ("C2","Certification is issued in advance of the use it purports to warrant. It is therefore a forecast of use rather than an instance of it, and stands in the same relation to use as a promise stands to performance.","austin-1962, structural","work"),
 ("C3","A promise is a performative that can fail. Certification, being a promise about future use, inherits that liability: it can be issued correctly and still not come true.","austin-1962, derived from B7 and C2","work"),
 ("C4","Attention and citation are distinct quantities. Attention produces an audience and leaves no durable record; citation requires a persistently addressable artifact and produces a countable one. Reach is therefore not evidence of contribution under the discipline's own accounting.","structural","work"),
 ("C5","Entry to the principal scholarly indexes is conditioned on the legal form of the depositor, an accredited institution, a selected publisher, or a dues-paying member organisation, rather than on the assessed quality of the work. Access is a property of legal form. The exclusion of unaffiliated scholars is not claimed here and is credited to the authors who established it.","verified against platform documentation October 2026; exclusion per elsabry-2017, tennant-2020, khanna-2022","work"),
 ("C6","A gate set on the legal form of the depositor rather than on the merit of the work is satisfied by incorporation rather than by better work. It therefore screens for the capacity to constitute an organisation, not for the quality it is held to protect, and the cost of satisfying it is a measure of what it actually selects for.","derived from C5, structural","work"),
 ("C7","The doctorate's certifying function was added to an instrument designed to license teaching. Certification of contribution is a historical accretion rather than the credential's founding purpose, and cannot therefore be defended by appeal to that purpose.","derived from A1 to A7","work"),
 ("C8","A legitimating origin can be composed after the institution it explains, and the institution's operation is unchanged by its absence. An origin story is therefore subject to the same subtraction test as any other ceremony.","derived from A8 to A12 and C1","work"),
 ("C9","Even where concealment adds to an effect, what it adds is purchased with the subject's ability to refuse, and that is not a permissible purchase. Disclosure is therefore required whether or not it is costless, and whatever cost it carries is the price of consent rather than a defect in the method. Amended October 2026: the earlier wording asserted that concealment adds nothing to the effect, which the evidence does not support. The argument is now ethical rather than empirical and does not depend on B5 going either way.","structural; B5 and B16 bear on the cost, not on the requirement","work"),
 ("C10","A performative utterance's effect is realised as a change in bodily state, not only as a change in belief. If concepts are structured by sensorimotor experience, perception is the resolution of prediction error, and feeling is predicted from interoceptive signal, then an utterance that alters expectation alters the body that holds it. Stated as this work's synthesis: no source named below makes this inference.","derived from B7, B8, B9, B11","work"),
 ("C11","Attention is allocated by prediction error, and material processed as self-relevant recruits the self-referential network. A work that breaks an expected pattern is therefore both more noticeable and more likely to be processed as being about its reader.","derived from B10, B12","work"),
 ("D","The claim","One proposition. It requires the two records and the seven distinctions that serve it, and nothing else."),
 ("D1","Scholarship registers contribution by citation; a dissertation is examined before it has been cited; the doctorate therefore certifies a prediction rather than a contribution.","the thesis, derived from C1 to C7","work"),
]

# What each distinction supports. A distinction that serves nothing is a defect:
# the registry exists so a reader can trace every claim to the one it bears on.
SERVES = {
 "C1": "D1", "C2": "D1", "C3": "D1", "C4": "D1", "C5": "D1", "C6": "D1", "C7": "D1",
 "C8": "the historical argument, Band A",
 "C9": "the method, and the register the work is written in",
 "C10": "Pillar IV", "C11": "Pillar IV",
}

# ------------------------------------------------------------- PAGE BUILDERS
def build_landing():
    body = '<h2>Abstract</h2>\n<div id="abstract">\n<hr class="lede-rule">\n'
    body += "\n".join(f"<p>{p}</p>" for p in ABSTRACT) + "\n</div>\n\n"
    body += '<h2>Keywords</h2>\n<p class="keywords">' + "".join(f"<span>{k}</span>" for k in KEYWORDS) + "</p>\n\n"
    body += f'''<h2>Record</h2>
<ul class="meta">
  <li><span class="k">Title</span><span class="v">{R["title_full"]}</span></li>
  <li><span class="k">Author</span><span class="v">{R["author"]}</span></li>
  <li><span class="k">ORCID</span><span class="v">{orcid_html()}</span></li>
  <li><span class="k">Publisher</span><span class="v">{R["publisher"]}</span></li>
  <li><span class="k">Year</span><span class="v">{R["year"]}</span></li>
  <li><span class="k">Version</span><span class="v">{R["version"]} &middot; pre-deposit, not indexed</span></li>
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
  <li><span class="k">Experimental record</span><span class="v">{pending(None,"checked October 2026 &middot; B1, B2, B5 and B6 amended, nine propositions added, four of them objections &middot; Kekecs et al. 2025 and Tripp outstanding")}</span></li>
  <li><span class="k">Page-level check</span><span class="v">{pending(None,"Each proposition checked against the text it names &middot; not started")}</span></li>
  <li><span class="k">Deposit</span><span class="v">{pending(None,"Canonical deposit, mirrors and DOI &middot; not started")}</span></li>
</ul>

<h2>References</h2>
<p class="note-block">The sources the propositions rest on, generated from the labels that cite them. Not a reading list: a work earns an entry here by being cited above.</p>
<div id="references"><ol>
''' + "\n".join(f"  <li>{SOURCES[k]}</li>" for k in sorted(cited_keys(), key=lambda k: SOURCES[k])) + "\n</ol></div>\n"
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
            serves = SERVES.get(lab)
            serves_html = f'<p class="prop-serves">serves {serves}</p>' if serves else ""
            body += f'''<div class="prop" id="{lab}">
  <a class="prop-label" href="#{lab}">{lab}</a>
  <p class="prop-text">{text}</p>
  <p class="prop-src">{src} <span class="{cls}">{word}</span></p>
  {serves_html}
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
<p class="note-block">Each entry is one object in <a href="/thesis/ledger/ledger.json">ledger.json</a>, keyed on the citing DOI so the same citation found in several sources is recorded once.</p>
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
.prop-serves{margin:.35rem 0 0;font-family:var(--mono);font-size:.68rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--gold)}
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

# ---------------------------------------------------------------- CHECKS
REQUIRED = ("citation_title", "citation_author", "citation_publication_date")

def fail(msg):
    sys.exit(f"BUILD REFUSED: {msg}")

def audit(out):
    """Refuse to write pages that break the record. Cheaper than remembering the rules."""
    root = out["index.html"]
    for tag in REQUIRED:
        if f'<meta name="{tag}" content="' not in root or f'<meta name="{tag}" content="">' in root:
            fail(f"{tag} missing or empty on /thesis. Scholar would ignore every tag.")
    for rel, doc in out.items():
        if not rel.endswith(".html"):
            continue
        if rel != "index.html" and 'name="citation_' in doc:
            fail(f"Highwire tags on thesis/{rel}. Sub-pages carry none.")
        if esc(R["author"]) not in doc:
            fail(f"author string missing from thesis/{rel}")
        if not R["indexable"] and 'content="noindex, follow"' not in doc:
            fail(f"thesis/{rel} lost its noindex before deposit")
    labels = [p[0] for p in PROPS]
    dupes = sorted({l for l in labels if labels.count(l) > 1})
    if dupes:
        fail(f"duplicate labels: {dupes}")
    # Written once by --lock, the day the propositions go public. From then on
    # a label can be added but never dropped.
    lock = ROOT / "labels.lock"
    if lock.exists():
        gone = [l for l in lock.read_text(encoding="utf-8").split() if l not in labels]
        if gone:
            fail(f"labels removed: {gone}. Keep the number and mark it withdrawn.")

# ----------------------------------------------------------------- SITEMAP
def lastmod(f):
    """Date the file last changed in git, not the date of the build."""
    try:
        d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(f)],
                           cwd=SITE, capture_output=True, text=True).stdout.strip()
    except OSError:
        d = ""
    return d or datetime.date.fromtimestamp(f.stat().st_mtime).isoformat()

def build_sitemap():
    # Found rather than listed, so a page added on main is never dropped (the
    # hardcoded list lost all eleven language pages). /thesis stays out while
    # it is noindex: listing a page that asks not to be indexed is a
    # contradiction Search Console reports.
    urls = []
    for f in sorted(SITE.glob("**/index.html")):
        rel = f.parent.relative_to(SITE).as_posix()
        top = rel.split("/")[0]
        if rel != "." and top.startswith((".", "_")) or (top == "thesis" and not R["indexable"]):
            continue
        loc = f'{R["base"]}/' + ("" if rel == "." else f"{rel}/")
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod(f)}</lastmod>\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")

# ----------------------------------------------------------------- EMIT
def outputs():
    return {
        "thesis.css": CSS,
        "index.html": build_landing(),
        "propositions/index.html": build_propositions(),
        "ledger/index.html": build_ledger(),
        "ledger/ledger.json": json.dumps(
            {"opened": R["ledger_opened"], "entries": []}, indent=2) + "\n",
    }

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote thesis/{rel}  ({len(content):,} bytes)")

def check_sources():
    missing = sorted({k for item in PROPS if len(item) == 4
                      for k in (p.strip() for p in re.split(r"[;,]", item[2]))
                      if re.fullmatch(r"[a-z][a-z0-9\-]*", k or "x")
                      and not k.startswith(("derived", "generalised", "structural"))
                      and k not in SOURCES})
    if missing:
        raise SystemExit("BUILD REFUSED: propositions cite sources with no reference entry: " + ", ".join(missing))

def check_serves():
    missing = [l for l, *_ in (x for x in PROPS if len(x) == 4) if l.startswith("C") and l not in SERVES]
    if missing:
        raise SystemExit("BUILD REFUSED: distinctions with nothing to serve: " + ", ".join(missing))

if __name__ == "__main__":
    check_serves()
    check_sources()
    out = outputs()
    audit(out)
    if "--check" in sys.argv:
        stale = [rel for rel, c in out.items()
                 if not (ROOT / rel).exists() or (ROOT / rel).read_text(encoding="utf-8") != c]
        if stale:
            sys.exit("Out of date (hand-edited or not rebuilt): "
                     + ", ".join(f"thesis/{s}" for s in stale))
        print("thesis/ matches _build.py.")
        sys.exit(0)
    if "--lock" in sys.argv:
        write("labels.lock", "\n".join(p[0] for p in PROPS) + "\n")
    print("Building /thesis ...")
    for rel, content in out.items():
        write(rel, content)
    (SITE / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    print("  wrote sitemap.xml")
    print("Done. Do not hand-edit the generated files.")
