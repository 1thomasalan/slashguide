#!/usr/bin/env python3
"""Slash Guide static site generator.

Reads the PDF edition data (editions/beginners_data.py, editions/knowledge_data.py)
plus sitegen/apps_data.py and sitegen/shorts.py, and writes a plain static site to
site/. Every link is relative, so the same output works at
https://1thomasalan.github.io/slashguide/ and later at https://slashguide.com/.

Run:  PYTHONPATH=/workspace/work/pylib python3 sitegen/build.py
"""
import html, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "sitegen"
ED = ROOT / "editions"
OUT = ROOT / "site"
sys.path[:0] = [str(ED), str(GEN)]

import beginners_data as BD  # noqa: E402
import knowledge_data as KD  # noqa: E402
import apps_data as AD  # noqa: E402
import shorts as SH  # noqa: E402

e = lambda s: html.escape(str(s), quote=True)
AI_WORKS = ["ChatGPT", "Claude", "Gemini", "Copilot", "Grok"]
ACR = {}
for d in (BD.ACRONYMS, KD.ACRONYMS, AD.ACRONYMS):
    ACR.update(d)

# ---------------------------------------------------------------- data model
SECTIONS = [
    {"id": "ai", "name": "AI chat", "short": "AI", "sub": "ChatGPT, Claude, Gemini, Copilot, Grok",
     "blurb": "Words your AI already understands. Type the slash word, add two details, get a better answer. "
              "They're shortcuts the model reads as intent, not official features, so results vary a little by model.",
     "source": ""},
]
for s in AD.APP_SECTIONS:
    SECTIONS.append({"id": s["id"], "name": s["name"], "short": s["name"], "sub": s["where"],
                     "blurb": s["blurb"], "source": s["source"], "note": s["note"]})
SK = AD.SEARCH_KEY
SECTIONS.append({"id": "web", "name": "The / key on websites", "short": "Web", "sub": "YouTube, GitHub and more",
                 "blurb": SK["blurb"], "source": ""})
SEC = {s["id"]: s for s in SECTIONS}

cmds = {}    # slug -> {slug, cmd, uses:[...]}
rows = []    # one row per (section, command) for the home library
groups = []  # (section_id, group_name, edition_label, [slugs])

def add(slug, cmd, use):
    c = cmds.setdefault(slug, {"slug": slug, "cmd": cmd, "uses": []})
    c["uses"].append(use)

for mod, ed_label, ed_id in ((BD, "Everyday", "everyday"), (KD, "Work", "work")):
    for gname, gdek, items in mod.SECTIONS:
        slugs = []
        for cmd, does, addl, ex in items:
            slug = cmd.lower()
            add(slug, "/" + cmd, {"sec": "ai", "group": gname, "edition": ed_label, "ed_id": ed_id,
                                  "does": does, "add": addl, "example": ex, "works": AI_WORKS})
            slugs.append(slug)
        groups.append(("ai", gname, ed_label, slugs))

for s in AD.APP_SECTIONS:
    slugs = []
    for cmd, does, addl, ex in s["commands"]:
        slug = cmd.lower()
        add(slug, "/" + cmd, {"sec": s["id"], "group": s["name"], "edition": "", "does": does,
                              "add": addl, "example": ex, "works": [s["where"][0].upper() + s["where"][1:]]})
        slugs.append(slug)
    groups.append((s["id"], s["name"], "", slugs))

add(SK["slug"], SK["cmd"], {"sec": "web", "group": "Websites", "edition": "", "does": SK["does"],
                            "add": SK["add"], "example": SK["example"], "works": SK["works"]})
groups.append(("web", "Websites", "", [SK["slug"]]))

for sid, gname, ed, slugs in groups:
    for slug in slugs:
        c = cmds[slug]
        u = next(u for u in c["uses"] if u["sec"] == sid and u["group"] == gname)
        rows.append({"s": sid, "slug": slug, "c": c["cmd"], "d": u["does"], "g": gname, "ed": ed,
                     "a": ACR.get(slug, ""), "x": u["example"]})

def related(slug, sec, group, n=4):
    for sid, gname, ed, slugs in groups:
        if sid == sec and gname == group:
            i = slugs.index(slug)
            rot = slugs[i + 1:] + slugs[:i]
            return rot[:n]
    return []

N_TOTAL = len(cmds)
N_AI = len({r["slug"] for r in rows if r["s"] == "ai"})

# ---------------------------------------------------------------- svg icons (one stroke set, 1.75px)
def icon(name, size=18):
    paths = {
        "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
        "copy": '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/>',
        "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
        "play": '<path d="M8 5.5v13l11-6.5z" fill="currentColor" stroke="none"/>',
        "download": '<path d="M12 4v11"/><path d="m7 10.5 5 5 5-5"/><path d="M5 20h14"/>',
        "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
        "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
        "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
        "ext": '<path d="M14 5h5v5"/><path d="M19 5 10 14"/><path d="M18 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4"/>',
    }
    return (f'<svg class="i i-{name}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{paths[name]}</svg>')

# ---------------------------------------------------------------- page shell
def page(title, desc, body, rel, cls=""):
    """rel = relative prefix to the site root ('' or '../')."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#111112" media="(prefers-color-scheme: dark)">
<script>try{{var t=localStorage.getItem("sg-theme");if(t==="dark"||t==="light")document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{rel}assets/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/mono-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/style.css">
</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap nav-in">
    <a class="logo" href="{rel or './'}" aria-label="Slash Guide home"><b>/</b>slashguide</a>
    <nav class="links" aria-label="Main">
      <a href="{rel or './'}#shortcuts">Shortcuts</a>
      <a href="{rel}downloads/">Free PDFs</a>
      <a class="nav-search" href="{rel or './'}#search" aria-label="Search shortcuts">{icon('search', 20)}</a>
      <button class="theme" type="button" aria-label="Switch between light and dark mode" title="Light or dark mode">{icon('moon', 18)}{icon('sun', 18)}</button>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-in">
    <div class="otb-box">
      <a class="otb-wm" href="https://onetobetter.com" rel="noopener" aria-label="One to Better"><img class="otb-l" src="{rel}assets/otb-logo.png" width="44" height="44" alt=""><img class="otb-d" src="{rel}assets/otb-logo-dark.png" width="44" height="44" alt="" loading="lazy"><span aria-hidden="true">NE TO BETTER</span></a>
      <p class="otb-tag">In pursuit of small improvements, better thinking, and a richer life.</p>
      <a class="otb-proj" href="https://onetobetter.com" rel="noopener">A One to Better project</a>
    </div>
    <p class="fine">Shortcuts your AI understands, plus the slash commands built into everyday apps. Not affiliated with or endorsed by OpenAI, Anthropic, Google, xAI, Microsoft, GitHub, Slack, Notion, Discord or Obsidian; names are trademarks of their owners. No ads, no trackers, no cookies.</p>
  </div>
</footer>
<script src="{rel}assets/app.js" defer></script>
</body>
</html>
"""

def copy_btn(text, label="Copy", cls=""):
    return (f'<button class="copy {cls}" type="button" data-copy="{e(text)}" aria-label="{e(label)}: {e(text)}">'
            f'{icon("copy", 15)}{icon("check", 15)}<span class="copy-l">{e(label)}</span></button>')

def ex_html(ex):
    """Colour the leading /command inside an example."""
    if ex.startswith("/"):
        head, _, tail = ex.partition(" ")
        return f'<span class="m red">{e(head)}</span>{" " + e(tail) if tail else ""}'
    return e(ex)

# ---------------------------------------------------------------- home
def home():
    featured = ["tldr", "fridge", "agenda", "scamcheck"]
    feat_html = ""
    for slug in featured:
        c = cmds[slug]; u = c["uses"][0]
        meaning = f'<span class="acr">{e(ACR[slug])}</span>' if slug in ACR else ""
        feat_html += f"""<li class="feat">
  <a class="feat-link" href="{slug}/"><span class="cmd m">{e(c['cmd'])}</span>{meaning}<span class="d">{e(u['does'])}</span></a>
  <div class="feat-f"><span class="tag">{e(u['edition'])} · {e(u['group'])}</span>{copy_btn(c['cmd'])}</div>
</li>"""

    pills = '<button class="pill" type="button" data-sec="all" data-title="All shortcuts" aria-pressed="true">All</button>'
    for s in SECTIONS:
        pills += f'<button class="pill" type="button" data-sec="{s["id"]}" data-title="{e(s["short"])} shortcuts" aria-pressed="false">{e(s["short"])}</button>'

    where = ""
    for s in SECTIONS:
        n = len({r["slug"] for r in rows if r["s"] == s["id"]})
        where += (f'<li><a class="w{" ai" if s["id"]=="ai" else ""}" href="#sec-{s["id"]}" data-jump="{s["id"]}">'
                  f'<strong>{e(s["short"] if s["id"]!="ai" else "AI chat")}</strong><span>{e(s["sub"][0].upper() + s["sub"][1:])}</span>'
                  f'<em>{n} shortcut{"s" if n!=1 else ""}</em></a></li>')

    lib = ""
    for s in SECTIONS:
        src = (f'<a class="src" href="{e(s["source"])}" rel="noopener">Official list {icon("ext", 14)}</a>'
               if s.get("source") else "")
        note = f'<p class="sec-note">{e(s["note"])}</p>' if s.get("note") else ""
        lib += f'<section class="sec" id="sec-{s["id"]}" data-sec="{s["id"]}"><div class="sec-h"><h2>{e(s["name"])}</h2>{src}</div><p class="sec-blurb">{e(s["blurb"])}</p>{note}'
        for sid, gname, ed, slugs in groups:
            if sid != s["id"]:
                continue
            gh = (f'<h3 class="grp-h">{e(gname)}<span class="ed ed-{ed.lower()}">{e(ed)}</span></h3>' if sid == "ai" else "")
            lib += f'<div class="grp">{gh}<ul class="rows">'
            for slug in slugs:
                r = next(r for r in rows if r["slug"] == slug and r["s"] == sid and r["g"] == gname)
                acr = f'<span class="acr">{e(r["a"])}</span>' if r["a"] else ""
                hay = " ".join([r["c"], r["d"], r["g"], r["a"], r["x"], SEC[sid]["short"], r["ed"]]).lower()
                lib += (f'<li class="row" data-s="{sid}" data-q="{e(hay)}"><a class="row-a" href="{slug}/">'
                        f'<span class="cmd m">{e(r["c"])}</span><span class="row-t">{acr}<span class="d">{e(r["d"])}</span></span></a>'
                        f'{copy_btn(r["c"])}</li>')
            lib += "</ul></div>"
        lib += "</section>"

    body = f"""
<section class="hero wrap">
  <div class="hero-l">
    <h1>Type <span class="m red">/</span>. Get it done.</h1>
    <p class="sub">Plain-English shortcuts for AI and the apps you already use. One slash word, two details, a better result. Free, copy-ready, no sign-up.</p>
    <form class="search" id="search" role="search" onsubmit="return false">
      <label class="vh" for="q">Search shortcuts</label>
      <span class="search-slash m" aria-hidden="true">/</span>
      <input id="q" type="search" autocomplete="off" spellcheck="false" placeholder="Search {N_TOTAL} shortcuts: email, recipe, status…">
      <kbd title="Press / to search">/</kbd>
    </form>
    <div class="pills" role="group" aria-label="Filter by app">{pills}</div>
  </div>
  <figure class="demo" aria-label="Example">
    <figcaption class="demo-cap"><span>Try it</span><span>ChatGPT · Claude · Gemini · Copilot</span></figcaption>
    <div class="chat">
      <p class="u"><span class="m">/eli5</span> how inflation works</p>
      <div class="a"><p>Imagine your allowance stays $10, but the candy bar you buy goes from $1 to $1.25.</p><p class="a2">Prices creep up, so each dollar buys a little less.</p></div>
    </div>
    <p class="demo-f"><a href="eli5/" class="m red">/eli5</a> = Explain Like I'm 5. The slash word tells your AI the job.</p>
  </figure>
</section>

<section class="wrap block" aria-labelledby="start-h">
  <h2 id="start-h">Start with these</h2>
  <p class="h2s">Copy one, paste it into your AI, add your details.</p>
  <ul class="feats">{feat_html}</ul>
</section>

<section class="wrap block" aria-labelledby="where-h">
  <h2 id="where-h">The slash works everywhere</h2>
  <p class="h2s">AI chat leads, and the apps you use every day have their own.</p>
  <ul class="where">{where}</ul>
</section>

<section class="wrap block lib" id="shortcuts" aria-labelledby="lib-h">
  <div class="lib-h"><h2 id="lib-h">All shortcuts</h2><p class="count" id="count" aria-live="polite">{N_TOTAL} shortcuts</p></div>
  <p class="empty" id="empty" hidden>No shortcut matches that yet. Try a simpler word, like <button type="button" class="linkish" data-try="email">email</button> or <button type="button" class="linkish" data-try="status">status</button>.</p>
  {lib}
</section>

<section class="wrap block">
  <div class="pdfs">
    <div>
      <h2>Free PDF editions</h2>
      <p>Print them, pin them next to your desk, share them with your team. 70 shortcuts each, no email needed.</p>
      <a class="btn" href="downloads/">{icon('download', 18)} Get the free PDFs</a>
    </div>
    <div class="covers" aria-hidden="true">
      <img src="assets/cover-everyday.png" width="150" height="194" alt="">
      <img src="assets/cover-work.png" width="150" height="194" alt="">
    </div>
  </div>
</section>
"""
    return page("Slash Guide: plain-English slash shortcuts for AI and everyday apps",
                f"{N_TOTAL} copy-ready slash shortcuts for ChatGPT, Claude, Gemini and other AI chats, plus Slack, Notion, Discord, Obsidian, Teams and Copilot. Free, from One to Better.",
                body, "", "home")

# ---------------------------------------------------------------- command page
def video_slot(slug, cmd):
    vid = SH.SHORTS.get(slug)
    if vid:
        return (f'<div class="vid has" data-yt="{e(vid)}"><button type="button" class="vid-play" aria-label="Play the {e(cmd)} Short">'
                f'<img src="https://i.ytimg.com/vi/{e(vid)}/hqdefault.jpg" alt="" loading="lazy">'
                f'<span class="play">{icon("play", 22)}</span></button></div>'
                f'<p class="vid-cap">Loads from YouTube when you press play.</p>')
    return (f'<div class="vid empty-vid"><span class="big m">{e(cmd)}</span>'
            f'<span class="vid-t">Short coming soon</span><span class="vid-s">A 45-second walkthrough will play here.</span></div>')

def cmd_page(c):
    slug, cmd = c["slug"], c["cmd"]
    first = c["uses"][0]
    sec = SEC[first["sec"]]
    multi = len(c["uses"]) > 1
    acr = f'<p class="acr-l">{e(ACR[slug])}</p>' if slug in ACR else ""
    sep = ' <span aria-hidden="true">›</span> '
    crumb_tail = (sep + e(first["edition"]) + sep + e(first["group"])) if first["sec"] == "ai" else ""
    uses_html = ""
    for u in c["uses"]:
        s = SEC[u["sec"]]
        if multi:
            label = {"Everyday": "In everyday life", "Work": "At work"}.get(u["edition"], f"In {s['short']}")
            uses_html += f'<h2 class="use-h">{e(label)}</h2>'
        works = "".join(f'<li class="pill">{e(w)}</li>' for w in u["works"])
        note = ""
        if u["sec"] == "ai":
            note = "A shortcut your AI understands from the word, not an official feature. Results vary a little by model."
        elif s.get("source"):
            note = f'Built into {e(s["short"])}. <a href="{e(s["source"])}" rel="noopener">Official list {icon("ext", 13)}</a>'
            if s.get("note"):
                note = e(s["note"]) + " " + note
        uses_html += f"""<div class="use">
  <p class="does">{e(u['does'])}</p>
  <h3 class="lbl">Add</h3><p class="add">{e(u['add'])}</p>
  <h3 class="lbl">Example</h3><div class="ex"><p>{ex_html(u['example'])}</p>{copy_btn(u['example'])}</div>
  <h3 class="lbl">Works in</h3><ul class="works">{works}</ul>
  <p class="honest">{note}</p>
</div>"""

    rel = related(slug, first["sec"], first["group"])
    rel_html = ""
    for r in rel:
        rc = cmds[r]; ru = next(u for u in rc["uses"] if u["sec"] == first["sec"])
        sub = ACR.get(r) or ru["does"]
        rel_html += f'<li><a class="n" href="../{r}/"><b class="m">{e(rc["cmd"])}</b><span>{e(sub)}</span></a></li>'

    title_cmd = cmd if slug != "search-key" else "The / key"
    title = f"{title_cmd}{' (' + ACR[slug] + ')' if slug in ACR else ''}: {first['does'].rstrip('.')} | Slash Guide"
    body = f"""
<div class="wrap detail">
  <nav class="crumb" aria-label="Breadcrumb"><a href="../?s={sec['id']}#shortcuts">{e(sec['short'])}</a>{crumb_tail}</nav>
  <div class="d-grid">
    <article class="d-main">
      <div class="d-head"><h1 class="m">{e(cmd)}</h1>{copy_btn(cmd, 'Copy', 'copy-big')}</div>
      {acr}
      {uses_html}
    </article>
    <aside class="d-side">
      <h2 class="lbl">Watch · 45 sec</h2>
      {video_slot(slug, cmd)}
      <h2 class="lbl">Try next</h2>
      <ul class="next">{rel_html}</ul>
      <a class="more" href="../?s={sec['id']}#shortcuts">All {e(sec['short'])} shortcuts {icon('arrow', 16)}</a>
    </aside>
  </div>
</div>
"""
    return page(title, f"{cmd}: {first['does']} Example: {first['example']}", body, "../", "cmdpage")

# ---------------------------------------------------------------- downloads
def downloads():
    eds = []
    for mod, slug, pdf in ((BD, "everyday", "slash-guide-everyday.pdf"), (KD, "work", "slash-guide-work.pdf")):
        size = (ED / pdf).stat().st_size
        pages = subprocess.run(["pdfinfo", str(ED / pdf)], capture_output=True, text=True).stdout
        npages = next((l.split()[-1] for l in pages.splitlines() if l.startswith("Pages:")), "")
        secs = "".join(f"<li>{e(s[0])}</li>" for s in mod.SECTIONS)
        title = {"everyday": "AI shortcuts for everyday life", "work": "AI shortcuts for knowledge work"}[slug]
        eds.append(f"""<article class="ed-card">
  <img class="cover" src="../assets/cover-{slug}.png" width="300" height="388" alt="Cover of the {e(mod.EDITION['name'])}">
  <div class="ed-body">
    <h2>{e(mod.EDITION['name'])}</h2>
    <p class="ed-k">{e(title)} · {e(mod.EDITION['kicker'])}</p>
    <p class="ed-meta">70 shortcuts · {npages} pages · PDF, {round(size/1024)} KB · US Letter</p>
    <h3 class="lbl">Inside</h3>
    <ul class="ed-secs">{secs}</ul>
    <a class="btn" href="{pdf}" download>{icon('download', 18)} Download the {e(mod.EDITION['name'])}</a>
  </div>
</article>""")
    body = f"""
<div class="wrap dl">
  <h1>Free PDF editions</h1>
  <p class="sub">Every shortcut with what to add and an example, laid out to print. No email, no sign-up. Share them with anyone.</p>
  <div class="eds">{''.join(eds)}</div>
  <p class="honest">Shortcuts your AI understands, not official features of any AI product. Results vary a little by model. Never paste confidential or company data, and follow your employer's AI policy.</p>
</div>"""
    return page("Free PDF editions | Slash Guide",
                "Download the Slash Guide Everyday and Work editions: 70 AI slash shortcuts each, free to print and share.",
                body, "../", "dlpage")

# ---------------------------------------------------------------- 404 (works at any base path)
NOT_FOUND = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Not found | Slash Guide</title>
<style>body{font-family:Inter,Helvetica,Arial,sans-serif;color:#111;margin:0;display:grid;place-items:center;min-height:100vh;text-align:center;padding:24px}
h1{font-family:ui-monospace,Menlo,monospace;color:#C81018;font-size:56px;letter-spacing:-2px;margin:0}p{color:#555;font-size:18px}a{color:#C81018;text-underline-offset:3px}@media (prefers-color-scheme:dark){body{background:#111112;color:#ececea}p{color:#9c9c98}h1,a{color:#f0444c}}</style></head>
<body><main><h1>/404</h1><p>That shortcut isn't here. It may have a different name.</p><p><a id="home" href="/">Search all shortcuts</a></p></main>
<script>var p=location.pathname.split('/');if(location.hostname.endsWith('github.io')&&p[1]){document.getElementById('home').href='/'+p[1]+'/';}</script></body></html>
"""

# ---------------------------------------------------------------- assets
def assets():
    a = OUT / "assets"; (a / "fonts").mkdir(parents=True, exist_ok=True)
    from fontTools.ttLib import TTFont
    for name in ("inter-400", "inter-500", "inter-600", "inter-700", "mono-400", "mono-600"):
        f = TTFont(ED / "fonts" / f"{name}.ttf"); f.flavor = "woff2"; f.save(a / "fonts" / f"{name}.woff2")
    from PIL import Image
    im = Image.open(ED / "otb-logo.png").convert("RGBA"); im.thumbnail((88, 88), Image.LANCZOS); im.save(a / "otb-logo.png", optimize=True)
    im = Image.open(ED / "otb-logo-dark.png").convert("RGBA"); im.thumbnail((88, 88), Image.LANCZOS); im.save(a / "otb-logo-dark.png", optimize=True)
    for slug, pdf in (("everyday", "slash-guide-everyday.pdf"), ("work", "slash-guide-work.pdf")):
        tmp = GEN / f"_cover-{slug}"
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", "1", "-l", "1", "-singlefile", str(ED / pdf), str(tmp)], check=True)
        img = Image.open(f"{tmp}.png").convert("RGB"); img = img.resize((600, round(600 * img.height / img.width)), Image.LANCZOS)
        img.save(a / f"cover-{slug}.png", optimize=True); os.remove(f"{tmp}.png")
        shutil.copy(ED / pdf, OUT / "downloads" / pdf)
    (a / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#C81018"/><path d="M19.5 6 12.5 26" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>')
    shutil.copy(GEN / "style.css", a / "style.css")
    shutil.copy(GEN / "app.js", a / "app.js")

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "downloads").mkdir(parents=True)
    assets()
    (OUT / "index.html").write_text(home())
    (OUT / "downloads" / "index.html").write_text(downloads())
    for slug, c in cmds.items():
        (OUT / slug).mkdir(exist_ok=True)
        (OUT / slug / "index.html").write_text(cmd_page(c))
    (OUT / "404.html").write_text(NOT_FOUND)
    (OUT / ".nojekyll").write_text("")
    print(f"built {N_TOTAL} command pages ({N_AI} AI), {len(rows)} library rows -> {OUT}")

if __name__ == "__main__":
    main()
