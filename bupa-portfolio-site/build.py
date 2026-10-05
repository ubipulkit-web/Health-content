#!/usr/bin/env python3
"""Static site generator for Dr Pulkit Mandal's health content portfolio.

Usage:  python build.py          # rebuilds index.html and /articles/*.html from /content/*.md
Requires: pip install markdown
Deploy:   push the repository to GitHub and enable Pages (Settings > Pages > main branch, / root).
"""
import html, re, pathlib
import markdown

ROOT = pathlib.Path(__file__).parent
SITE_NAME = "Dr Pulkit Mandal"
SITE_TITLE = "Health Content Portfolio"
EMAIL = "ubipulkit@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/dr-pulkit-mandal-b4a585284"
FULL_PORTFOLIO = "https://ubipulkit-web.github.io/MedWriting/"

ARTICLES = [
    {"slug": "high-blood-pressure", "short": "High blood pressure",
     "blurb": "A plain-English condition article explaining blood pressure numbers, risk, self-monitoring and when to seek urgent help.",
     "skills": ["Plain English", "Health literacy", "Safety-netting"]},
    {"slug": "how-much-exercise", "short": "How much exercise?",
     "blurb": "A behaviour-focused prevention article that turns national activity guidance into realistic, achievable weekly choices.",
     "skills": ["Behaviour change", "Accessible structure", "Guideline translation"]},
    {"slug": "semaglutide-weight-loss", "short": "Semaglutide for weight loss",
     "blurb": "A medicines explainer balancing benefits, side effects, eligibility and uncertainty, with questions to ask a prescriber.",
     "skills": ["Evidence appraisal", "Risk communication", "Medicines safety"]},
]

SKILLS = [
    ("Critical appraisal and hierarchy of evidence",
     "Each sample is built from named UK guidance (NHS, NICE, UK Chief Medical Officers). Trial results are described as population averages, not promises to an individual."),
    ("Plain English and health literacy",
     "Short sentences, defined terms and everyday examples. Numbers such as 140/90 mmHg or 150 minutes are explained, not just stated."),
    ("User-centred structure",
     "Question-style headings, a contents list, key points at the end, practical checklists and a worked weekly plan so readers can find what they need."),
    ("Accessibility",
     "Semantic headings, descriptive link text, real lists and tables, no content locked in images, and sensible contrast. This site follows the same rules."),
    ("Safety-netting and risk communication",
     "Every article says clearly when to seek urgent help, avoids overstating benefit, and tells readers not to stop prescribed medicines on their own."),
    ("Content lifecycle",
     "Each piece lists its sources, shows a last-reviewed date and carries a medical information notice, ready for scheduled review."),
]

PROCESS = [
    ("Brief", "Clarify the audience, the question they are asking and what action they should take."),
    ("Appraise", "Find the strongest current guidance and check each claim against it."),
    ("Write", "Draft in plain English with clear structure, then simplify."),
    ("Clinical check", "Route to an expert clinician for feedback and sign-off."),
    ("Review", "Record sources and a review date so the content can be kept current."),
]

def esc(s): return html.escape(s, quote=True)

def head(title, desc, depth=0):
    p = "../" * depth
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{SITE_NAME}">
<link rel="stylesheet" href="{p}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="{p}index.html">Dr Pulkit <span>Mandal</span></a>
  <nav aria-label="Main"><ul>
    <li><a href="{p}index.html#samples">Writing samples</a></li>
    <li><a href="{p}index.html#approach">Approach</a></li>
    <li><a href="{p}index.html#about">About</a></li>
    <li><a href="{p}index.html#contact">Contact</a></li>
  </ul></nav>
</div></header>
"""

def foot():
    return f"""<footer class="site"><div class="wrap">
<p>Independent writing samples by {SITE_NAME}. Not commissioned by, or affiliated with, any organisation. The articles give general information only and are not medical advice.</p>
</div></footer>
</body></html>
"""

def parse_article(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = re.sub(r"^#\s*\d+\.\s*", "", lines[0]).strip()
    i = 1
    while not lines[i].strip(): i += 1
    tag = lines[i].strip()
    body_md = "\n".join(lines[i+1:]).strip()
    return title, tag, body_md

def render_body(body_md):
    md = markdown.Markdown(extensions=["tables", "sane_lists", "toc"], extension_configs={"toc": {"toc_depth": "2"}})
    h = md.convert(body_md)
    toc = [(t["id"], t["name"]) for t in md.toc_tokens]
    # Key points panel
    h = re.sub(r'(<h2 id="key-points">.*?)(?=<h2 id="sources">|\Z)', r'<div class="keypoints">\1</div>', h, flags=re.S)
    # Sources block
    h = re.sub(r'(<h2 id="sources">.*)', r'<div class="sources">\1</div>', h, flags=re.S)
    # Urgent callouts
    h = re.sub(r"<p><strong>(Call 999.*?)</strong></p>", r'<div class="callout-urgent" role="note"><p><strong>\1</strong></p></div>', h, flags=re.S)
    # external links open normally but are labelled
    h = h.replace('<a href="http', '<a rel="noopener" href="http')
    return h, toc

def build_article(idx, meta):
    path = ROOT / "content" / f"{meta['slug']}.md"
    title, tag, body_md = parse_article(path)
    body_html, toc = render_body(body_md)
    words = len(re.findall(r"\w+", body_md))
    mins = max(1, round(words / 220))
    toc_html = "".join(f'<li><a href="#{i}">{esc(n)}</a></li>' for i, n in toc if n not in ("Sources",))
    prev_a = ARTICLES[idx-1] if idx > 0 else None
    next_a = ARTICLES[idx+1] if idx < len(ARTICLES)-1 else None
    pager = '<nav class="pager" aria-label="More samples">'
    pager += f'<a href="{prev_a["slug"]}.html">&larr; {esc(prev_a["short"])}</a>' if prev_a else '<a href="../index.html#samples">&larr; All samples</a>'
    pager += f'<a href="{next_a["slug"]}.html">{esc(next_a["short"])} &rarr;</a>' if next_a else '<a href="../index.html#samples">All samples &rarr;</a>'
    pager += "</nav>"
    out = head(f"{title} | {SITE_NAME}", meta["blurb"], depth=1)
    out += f"""<main id="main">
<div class="wrap">
<div class="article-head">
  <div class="crumbs"><a href="../index.html#samples">&larr; Writing samples</a></div>
  <span class="eyebrow">{esc(tag.split('|')[0].strip())}</span>
  <h1>{esc(title)}</h1>
  <p class="deck">{esc(tag.split('|')[1].strip()) if '|' in tag else ''}</p>
  <p class="meta">Sample article &middot; About {mins} min read &middot; By {SITE_NAME}</p>
</div>
<div class="layout">
  <aside class="toc" aria-label="On this page"><h2>On this page</h2><ul>{toc_html}</ul></aside>
  <article class="body">
{body_html}
{pager}
  </article>
</div>
</div>
</main>
"""
    out += foot()
    (ROOT / "articles").mkdir(exist_ok=True)
    (ROOT / "articles" / f"{meta['slug']}.html").write_text(out, encoding="utf-8")
    return title, tag, mins

def build_index(infos):
    cards = ""
    for meta, (title, tag, mins) in zip(ARTICLES, infos):
        chips = " &middot; ".join(esc(s) for s in meta["skills"])
        cards += f"""<article class="card sample-card">
  <span class="tag">{esc(tag.split('|')[0].strip())}</span>
  <h3>{esc(title)}</h3>
  <p>{esc(meta['blurb'])}</p>
  <p class="meta">{chips}<br>About {mins} min read</p>
  <a class="more" href="articles/{meta['slug']}.html" aria-label="Read sample: {esc(title)}">Read the sample &rarr;</a>
</article>
"""
    skills = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in SKILLS)
    steps = "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in PROCESS)
    out = head(f"{SITE_NAME} | {SITE_TITLE}", "Consumer health writing samples demonstrating plain-English medical communication, evidence appraisal and safety-netting.")
    out += f"""<main id="main">
<div class="wrap">
<section class="hero">
  <span class="eyebrow">Health content portfolio</span>
  <h1>Clear, evidence-led health writing for real readers</h1>
  <p class="lead">Three consumer health articles showing how complex medical evidence can be turned into accurate, accessible, plain-English content, with safety-netting and sources built in. Written by {SITE_NAME}, a medical doctor and MSc Sports and Exercise Medicine student.</p>
  <div class="btns">
    <a class="btn primary" href="#samples">Read the samples</a>
    <a class="btn ghost" href="#contact">Get in touch</a>
  </div>
</section>

<section id="samples" aria-labelledby="h-samples">
  <h2 id="h-samples">Writing samples</h2>
  <p class="sub">A condition article, a lifestyle and prevention article, and a medicines explainer, each written for a general UK audience.</p>
  <div class="grid cols-3">
{cards}  </div>
</section>

<section id="skills" aria-labelledby="h-skills">
  <h2 id="h-skills">What the samples demonstrate</h2>
  <p class="sub">The skills a health content editor uses every day, shown in the work itself.</p>
  <div class="card"><dl class="skills">{skills}</dl></div>
</section>

<section id="approach" aria-labelledby="h-approach">
  <h2 id="h-approach">How I approach health content</h2>
  <p class="sub">A repeatable process from brief to review, designed to fit into clinician sign-off and content lifecycle workflows.</p>
  <ol class="steps">{steps}</ol>
</section>

<section id="about" aria-labelledby="h-about">
  <h2 id="h-about">About</h2>
  <div class="about">
    <div>
      <p>I am a GMC-recognised medical doctor (MD, O.O. Bogomolets National Medical University) completing an MSc in Sports and Exercise Medicine at Manchester Metropolitan University. My MSc dissertation is a PROSPERO-registered systematic review, which gave me hands-on practice of searching, appraising and weighing evidence.</p>
      <p>I have written health content as a part-time Medical Writer since 2023, and I completed a 13-month hospital internship across 16 specialties, where explaining diagnoses and plans clearly to patients and families was part of every day. I enjoy turning guidelines and trial data into content that people can understand and act on.</p>
      <p class="notice">These articles are independent writing samples prepared for a portfolio. They are not published or endorsed by any employer and are not a substitute for medical advice.</p>
    </div>
    <ul class="facts card" aria-label="Quick facts">
      <li><b>Qualification:</b> MD; PLAB 1 and PLAB 2 passed</li>
      <li><b>Studying:</b> MSc Sports and Exercise Medicine, Manchester Metropolitan University</li>
      <li><b>Experience:</b> Medical Writer (part-time, since 2023); hospital internship; clinic coordination</li>
      <li><b>Research:</b> PROSPERO-registered systematic review; peer-reviewed lead-author publication (2020)</li>
      <li><b>Based in:</b> Manchester, UK</li>
    </ul>
  </div>
</section>

<section id="contact" aria-labelledby="h-contact">
  <h2 id="h-contact">Contact</h2>
  <p class="sub">Happy to discuss these samples or how I could contribute to a health content team.</p>
  <div class="btns">
    <a class="btn primary" href="mailto:{EMAIL}">Email me</a>
    <a class="btn ghost" rel="noopener" href="{LINKEDIN}">LinkedIn</a>
    <a class="btn ghost" rel="noopener" href="{FULL_PORTFOLIO}">Full medical writing portfolio</a>
  </div>
</section>
</div>
</main>
"""
    out += foot()
    (ROOT / "index.html").write_text(out, encoding="utf-8")

def main():
    infos = [build_article(i, m) for i, m in enumerate(ARTICLES)]
    build_index(infos)
    (ROOT / ".nojekyll").write_text("")
    print("Built index.html and", len(ARTICLES), "articles")

if __name__ == "__main__":
    main()
