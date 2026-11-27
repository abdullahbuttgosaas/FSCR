"""Measure how smooth the three pages run (frames per second and slow frames) in Chromium.
Usage (from the work folder): python dashboard/perf_check.py dashboard [label]
Headless Chromium draws without the graphics card, so heavy effects show up clearly here.
Each page runs 4 s with its normal animations; index and technical also scroll during the run."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright

base = pathlib.Path(sys.argv[1]); label = sys.argv[2] if len(sys.argv) > 2 else ""
MEASURE = """async (scroll) => {
  const frames = []; let last = performance.now(); const t0 = last;
  const H = document.documentElement.scrollHeight - innerHeight;
  await new Promise(res => { function f(t){ frames.push(t - last); last = t;
      if (scroll && H > 0) window.scrollTo(0, H * ((t - t0) / 4000));
      if (t - t0 < 4000) requestAnimationFrame(f); else res(); } requestAnimationFrame(f); });
  frames.shift();
  const ms = frames.reduce((a, b) => a + b, 0);
  return {fps: Math.round(1000 * frames.length / ms), slow: frames.filter(x => x > 34).length, worst: Math.round(Math.max(...frames))};
}"""
CASES = [("index", "index.html", True, None), ("story-title", "story.html", False, 0), ("story-gaps", "story.html", False, 2),
         ("story-hub", "story.html", False, 3), ("story-after", "story.html", False, 4), ("technical", "technical.html", True, None)]
out = {}
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for theme in ["night", "light"]:
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script(f"try{{localStorage.setItem('fscr-theme','{theme}')}}catch(e){{}}")
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); cdp.send("Performance.enable")
        for name, page, scroll, slide in CASES:
            pg.goto((base / page).resolve().as_uri()); pg.wait_for_timeout(1200)
            if page == "index.html": pg.click("#headline"); pg.wait_for_timeout(1500)
            if slide is not None:
                pg.evaluate(f"storyPause(); storyGo({slide})"); pg.wait_for_timeout(300)
            m0 = {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics")["metrics"]}
            r = pg.evaluate(MEASURE, scroll)
            m1 = {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics")["metrics"]}
            r["busy_ms"] = round(1000 * (m1["TaskDuration"] - m0["TaskDuration"]))
            out[f"{theme}:{name}"] = r
        ctx.close()
    br.close()
print(label)
for k, v in out.items():
    print(f"  {k:22s} fps {v['fps']:3d}  slow frames {v['slow']:3d}  worst {v['worst']:4d} ms  main-thread busy {v['busy_ms']:5d} ms / 4000")
