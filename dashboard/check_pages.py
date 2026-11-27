"""Open the three dashboard pages in Playwright (Chromium), screenshot every scene and section at desktop
and phone width, check every number against the data, module rows against the totals, and every link.
Usage (from the work folder):
  python dashboard/check_pages.py dashboard dashboard/screenshots                                  (local files)
  python dashboard/check_pages.py https://fscr-gap-dashboard.vercel.app dashboard/screenshots live-  (live site)"""
import json, os, sys, pathlib
from playwright.sync_api import sync_playwright

base, shots = sys.argv[1], sys.argv[2]
prefix = sys.argv[3] if len(sys.argv) > 3 else ""
local = not base.startswith("http")
data_dir = pathlib.Path(base)
def url(p):
    return (data_dir / p).resolve().as_uri() if local else base.rstrip("/") + "/" + p

os.makedirs(shots, exist_ok=True)
problems = []
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for vw, vh, tag in [(1440, 900, "desktop"), (390, 844, "phone")]:
        ctx = br.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=1)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        # data the dashboard uses
        pg.goto(url("index.html")); pg.wait_for_timeout(1500)
        d = pg.evaluate("window.DASHBOARD_DATA")
        if not local:
            d = pg.evaluate("fetch('data/data.json',{cache:'no-store'}).then(r=>r.json())")
        s = d["summary"]
        dash = pg.evaluate("({b:document.getElementById('hBefore').textContent,n:document.getElementById('hNow').textContent})")
        if dash["b"] != f"{s['before']:,}" or dash["n"] != f"{s['available']:,}":
            problems.append(f"{tag} index headline {dash} vs {s['before']},{s['available']}")
        pg.screenshot(path=f"{shots}/{prefix}index-{tag}.png")
        # story: a slideshow; check it moves on by itself, then shoot every slide
        pg.goto(url("story.html")); pg.wait_for_timeout(7400)
        if pg.evaluate("document.body.dataset.slide") != "1": problems.append(f"{tag} story did not auto-advance")
        n = pg.evaluate("document.querySelectorAll('.slide').length")
        vals = {}
        for i in range(n):
            pg.evaluate(f"storyPause(); storyGo({i})"); pg.wait_for_timeout(4200)
            sid = pg.evaluate("document.querySelector('.slide.active').getAttribute('aria-label')").lower().replace(" ", "-")
            pg.screenshot(path=f"{shots}/{prefix}story-{tag}-{i+1}-{sid}.png")
            clip = pg.evaluate("(()=>{const a=document.querySelector('.slide.active');return a.scrollHeight-a.clientHeight})()")
            if clip > 2: problems.append(f"{tag} story slide {i+1} is cut off by {clip}px")
            vals.update(pg.evaluate("({n1:n1.textContent,n2:n2.textContent,n3:n3.textContent,n4:n4.textContent})"))
            if i == 0: vals = {}
            if i == 1: v1 = vals["n1"]
            if i == 2: v2 = vals["n2"]
            if i == 4: v3 = vals["n3"]
            if i == 5: v4 = vals["n4"]
        nums = pg.evaluate("""({gain:gainWords.textContent,txt:document.getElementById('stage').innerText.toLowerCase(),
            ks:[...document.querySelectorAll('[data-k]')].map(e=>[e.dataset.k,e.textContent])})""")
        for k, got, v in [("before", v1, s["before"]), ("missing", v2, s["missing"]), ("available", v3, s["available"]), ("open", v4, s["open"])]:
            if got != f"{v:,}": problems.append(f"{tag} story {k}={got} expected {v}")
        for w in ["written", "failed", "screen"]:
            if w in nums["txt"]: problems.append(f"{tag} story still mentions '{w}'")
        g = f"+{s['gain']} skills, {round(1000*s['gain']/s['before'])/10:g}% more"
        if nums["gain"] != g: problems.append(f"{tag} story gain '{nums['gain']}' expected '{g}'")
        for k, t in nums["ks"]:
            if t != f"{s[k]:,}": problems.append(f"{tag} story data-k {k}={t} expected {s[k]}")
        ow = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        if ow > 0: problems.append(f"{tag} story horizontal overflow {ow}px")
        # technical: each section
        pg.goto(url("technical.html")); pg.wait_for_timeout(800)
        secs = pg.evaluate("['top',...[...document.querySelectorAll('section.blk')].map(s=>s.id)]")
        for i, sid in enumerate(secs):
            if sid != "top":
                pg.evaluate(f"document.getElementById('{sid}').scrollIntoView({{behavior:'auto'}})")
            pg.wait_for_timeout(2600)
            pg.screenshot(path=f"{shots}/{prefix}technical-{tag}-{i+1}-{sid}.png")
        t = pg.evaluate("""({ks:[...document.querySelectorAll('[data-k]')].map(e=>[e.dataset.k,e.textContent]),
            foot:[...document.querySelectorAll('#tfoot td')].map(e=>e.textContent),
            rows:[...document.querySelectorAll('#tbody tr')].map(r=>[...r.cells].slice(0,7).map(c=>c.textContent)),
            bars:[...document.querySelectorAll('.mbar')].filter(b=>b.getBoundingClientRect().width<1 && b.dataset.w>0).length})""")
        for k, v in t["ks"]:
            if v != f"{s[k]:,}": problems.append(f"{tag} technical data-k {k}={v} expected {s[k]}")
        cols = ["missing", "tested", "written", "failed", "screen_only", "open"]
        sums = [0] * 6
        mods = {m["name"]: m for m in d["modules"]}
        for r in t["rows"]:
            m = mods[r[0]]
            for j, c in enumerate(cols):
                v = int(r[j+1].replace(",", "")); sums[j] += v
                if v != m[c]: problems.append(f"{tag} row {r[0]} {c}={v} expected {m[c]}")
        for j, c in enumerate(cols):
            if sums[j] != s[c]: problems.append(f"{tag} rows sum {c}={sums[j]} vs total {s[c]}")
            if t["foot"][j+1].replace(",", "") != str(s[c]): problems.append(f"{tag} footer {c}={t['foot'][j+1]}")
        if t["bars"]: problems.append(f"{tag} technical {t['bars']} empty bars")
        ow = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        if ow > 0: problems.append(f"{tag} technical horizontal overflow {ow}px")
        pg.screenshot(path=f"{shots}/{prefix}technical-{tag}-full.png", full_page=True)
        # links: every href on every page resolves
        for p in ["index.html", "story.html", "technical.html"]:
            pg.goto(url(p)); pg.wait_for_timeout(300)
            hrefs = pg.evaluate("[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))")
            for h in hrefs:
                if h.startswith("#"):
                    if not pg.evaluate(f"!!document.getElementById('{h[1:]}')"): problems.append(f"{p} anchor {h} missing")
                    continue
                if "://" in h or h.startswith("/"): problems.append(f"{p} non-relative link {h}")
                target = h.split("#")[0]
                if local:
                    if not (data_dir / target).is_file(): problems.append(f"{p} link {h} missing file")
                else:
                    st = pg.evaluate(f"fetch('{target}').then(r=>r.status)")
                    if st != 200: problems.append(f"{p} link {h} status {st}")
            # click each nav link and check where it lands
            for h in ["index.html", "story.html", "technical.html"]:
                pg.goto(url(p)); pg.click(f".topnav a.lnk[href='{h}']"); pg.wait_for_load_state()
                if not pg.url.split("?")[0].split("#")[0].endswith(h): problems.append(f"nav from {p} to {h} landed on {pg.url}")
        pg.goto(url("index.html")); pg.click("a.howbtn"); pg.wait_for_load_state()
        if not pg.url.split("#")[0].endswith("story.html"): problems.append("See how it works button broken")
        pg.goto(url("story.html")); pg.evaluate("storyPause(); storyGo(5)"); pg.wait_for_timeout(1500)
        pg.click("a.btn.primary"); pg.wait_for_load_state()
        if not pg.url.endswith("technical.html"): problems.append("technical details button broken")
        if errs: problems.append(f"{tag} console errors: {errs[:5]}")
        ctx.close()
    # reduced motion: numbers final straight away
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page(); pg.goto(url("story.html")); pg.wait_for_timeout(500)
    pg.evaluate("storyGo(4)"); pg.wait_for_timeout(400)
    if pg.evaluate("n3.textContent") != f"{s['available']:,}": problems.append("reduced motion: n3 not final")
    pg.screenshot(path=f"{shots}/{prefix}story-reduced-motion-after.png")
    ctx.close()
    # every page in every theme; the picker; the choice is kept across pages
    BG = {"night": "rgb(7, 11, 24)", "dusk": "rgb(16, 8, 24)", "light": "rgb(246, 245, 242)"}
    for theme in ["night", "dusk", "light"]:
        for vw, vh, tag in [(1440, 900, "desktop"), (390, 844, "phone")]:
            ctx = br.new_context(viewport={"width": vw, "height": vh})
            ctx.add_init_script(f"try{{localStorage.setItem('fscr-theme','{theme}')}}catch(e){{}}")
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            for page in ["index.html", "story.html", "technical.html"]:
                pg.goto(url(page)); pg.wait_for_timeout(900)
                got = pg.evaluate("[document.documentElement.dataset.theme, getComputedStyle(document.documentElement).backgroundColor, !!document.querySelector('.bg canvas'), !!document.querySelector('.themepick')]")
                if got[0] != theme or got[1] != BG[theme]: problems.append(f"{theme} {tag} {page}: theme {got[0]} bg {got[1]}")
                if not got[2] or not got[3]: problems.append(f"{theme} {tag} {page}: background or picker missing")
                ow = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                if ow > 0: problems.append(f"{theme} {tag} {page}: sideways overflow {ow}px")
            pg.goto(url("index.html")); pg.wait_for_timeout(1500)
            pg.screenshot(path=f"{shots}/{prefix}theme-{theme}-{tag}-index.png")
            pg.click("#headline"); pg.wait_for_timeout(1500); pg.click("#rows .row"); pg.wait_for_timeout(900)
            pg.screenshot(path=f"{shots}/{prefix}theme-{theme}-{tag}-index-modules.png", full_page=True)
            pg.goto(url("story.html")); pg.wait_for_timeout(500)
            for i in [0, 3, 4]:
                pg.evaluate(f"storyPause(); storyGo({i})"); pg.wait_for_timeout(4000)
                pg.screenshot(path=f"{shots}/{prefix}theme-{theme}-{tag}-story-{i+1}.png")
            pg.goto(url("technical.html")); pg.wait_for_timeout(800)
            for sid in ["outcomes", "modules"]:
                pg.evaluate(f"document.getElementById('{sid}').scrollIntoView()"); pg.wait_for_timeout(2200)
                pg.screenshot(path=f"{shots}/{prefix}theme-{theme}-{tag}-technical-{sid}.png")
            if errs: problems.append(f"{theme} {tag} page errors: {errs[:3]}")
            ctx.close()
    # picker: open it, choose Dusk, then Light; the choice must follow to the next page
    ctx = br.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    pg.goto(url("index.html")); pg.wait_for_timeout(600)
    if pg.evaluate("document.documentElement.dataset.theme") != "night": problems.append("default theme is not night")
    pg.click(".themepick"); pg.wait_for_timeout(300)
    pg.screenshot(path=f"{shots}/{prefix}theme-picker-open.png", clip={"x": 1040, "y": 0, "width": 400, "height": 230})
    pg.click(".thememenu button[data-t='dusk']"); pg.wait_for_timeout(300)
    if pg.evaluate("document.documentElement.dataset.theme") != "dusk": problems.append("picker did not set dusk")
    pg.click(".topnav a.lnk[href='technical.html']"); pg.wait_for_load_state(); pg.wait_for_timeout(300)
    if pg.evaluate("document.documentElement.dataset.theme") != "dusk": problems.append("dusk not kept on the next page")
    pg.click(".themepick"); pg.keyboard.press("ArrowDown"); pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
    if pg.evaluate("document.documentElement.dataset.theme") != "light": problems.append("keyboard choice in picker failed")
    pg.click(".themepick"); pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    if pg.evaluate("document.querySelector('.thememenu').classList.contains('open')"): problems.append("Escape did not close the picker")
    ctx.close()
    br.close()

print(json.dumps({"before": s["before"], "available": s["available"], "tested": s["tested"],
                  "written": s["written"], "missing": s["missing"]}))
print("PROBLEMS:" if problems else "ALL CHECKS PASSED")
for p in problems: print(" -", p)
