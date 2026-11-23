/* The page: setup checklist, then one thing: upload a filled-in sheet, check it, preview it,
   create it in Oracle, show progress and the result. Plain JavaScript, no outside libraries.
   Talks only to the local server. The look (2026-10-26) is the approved mockup: a 4-station rail
   (Upload, Check, Create, Done) driven only by the page's real state (setStage), module cards,
   and a sticky bottom bar. Behaviour, endpoints and every question / repair rule are unchanged. */
"use strict";

const app = document.getElementById("app");
const S = { env: null, testMode: false, timers: [], previews: {}, ui: { open: null, filter: "All", q: "", closed: {} },
            watch: {}, last: null };

/* ---------------------------------------------------------------- helpers */

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const $ = (sel, root = document) => root.querySelector(sel);
const api = async (path, body) => {
  const r = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json();
};
function clearTimers() { S.timers.forEach(clearTimeout); S.timers = []; }
function later(fn, ms) { S.timers.push(setTimeout(fn, ms)); }
const store = {                       /* localStorage only for small conveniences; never required */
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* the page works without it */ } },
};
function counted(n, word) { return `${n} ${word}${n === 1 ? "" : "s"}`; }

/* the mockup's modules: the mono letters and the one-line description of each */
const MODS = {
  "Customers": { mono: "CU", sub: "Organization, person, address purposes" },
  "Order Types": { mono: "OT", sub: "Order types and their setup" },
  "Payment Terms": { mono: "PT", sub: "Terms, lines, installments" },
  "Lookup Types": { mono: "LT", sub: "Types and their codes" },
  "Business Units": { mono: "BU", sub: "Units, manager, default set" },
  "Price Lists": { mono: "PL", sub: "Lists and currency" },
};
const WHAT_MOD = { "customer": "Customers", "order type": "Order Types", "payment term": "Payment Terms",
  "lookup type": "Lookup Types", "codes for lookup type": "Lookup Types", "business unit": "Business Units",
  "price list": "Price Lists" };
const modOf = (what) => WHAT_MOD[what] || (what ? what.replace(/^./, (c) => c.toUpperCase()) + "s" : "Items");
const titleCase = (s) => String(s || "").replace(/\b\w/g, (c) => c.toUpperCase());
const KIND = { good: ["var(--glowA)", "var(--accent)"], warn: ["var(--warnBg)", "var(--warn)"], bad: ["var(--badBg)", "var(--bad)"],
  run: ["var(--surface3)", "var(--text)"], idle: ["var(--surface3)", "var(--muted)"] };
const pillStyle = (k) => "background:" + KIND[k][0] + ";color:" + KIND[k][1];

/* ---------------------------------------------------------------- theme */

function theme() { return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark"; }
function paintTheme() { document.getElementById("theme-label").textContent = theme() === "dark" ? "Light" : "Dark"; }
document.getElementById("theme-toggle").addEventListener("click", () => {
  const t = theme() === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", t);
  store.set("sa-theme", t);
  paintTheme();
});
paintTheme();

/* ---------------------------------------------------------------- the progress rail */

const RAIL = document.getElementById("rail");
function setStage(stage) {
  if (stage === null) { RAIL.hidden = true; return; }
  RAIL.hidden = false;
  const pct = (stage / 3) * 100;
  document.getElementById("rail-fill").style.width = pct + "%";
  document.getElementById("rail-orb").style.left = pct + "%";
  RAIL.querySelectorAll("[data-node]").forEach((li) => {
    const i = Number(li.dataset.node);
    const done = i < stage || (stage === 3 && i === 3);
    const cur = i === stage && stage !== 3;
    const n = li.querySelector(".node");
    n.style.background = done ? "var(--accent)" : (cur ? "var(--surface)" : "var(--surface2)");
    n.style.color = done ? "var(--accentInk)" : (cur ? "var(--accent)" : "var(--muted)");
    n.style.border = "2px solid " + (done || cur ? "var(--accent)" : "var(--line)");
    n.style.boxShadow = cur ? "0 0 0 6px var(--glowA)" : "none";
    n.style.transform = cur ? "rotate(-6deg) scale(1.06)" : "none";
    li.querySelector(".node-t").style.color = done || cur ? "var(--text)" : "var(--muted)";
    if (cur) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current");
  });
}

/* ---------------------------------------------------------------- notify when a run finishes */

function notifyOn() { return store.get("sa-notify") !== "off"; }
function askNotifyPermission() {
  try {
    if ("Notification" in window && Notification.permission === "default") {
      const p = Notification.requestPermission();
      if (p && p.catch) p.catch(() => {});
    }
  } catch (e) { /* no notifications on this browser */ }
}
function chime() {
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    const ctx = new Ctx();
    [[660, 0], [880, 0.16]].forEach(([f, at]) => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = "sine"; o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, ctx.currentTime + at);
      g.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + at + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + at + 0.35);
      o.connect(g); g.connect(ctx.destination);
      o.start(ctx.currentTime + at); o.stop(ctx.currentTime + at + 0.4);
    });
    setTimeout(() => { try { ctx.close(); } catch (e) { /* closed */ } }, 1200);
  } catch (e) { /* no sound */ }
}
function notifyFinished(id, job, seconds) {
  if (!notifyOn() || seconds <= 60) return;
  if (!document.hidden && document.hasFocus()) return;
  try {
    if ("Notification" in window && Notification.permission === "granted") {
      const created = job.created || 0, skipped = (job.items || []).filter((it) => (it.question || {}).state === "skipped").length
        + (job.skipped || 0);
      new Notification("Setup run finished: " + created + " created, " + skipped + " skipped");
    }
  } catch (e) { /* nothing */ }
  chime();
}
function watchRun(id, job, final) {        /* a run seen running on this page that ends now */
  const w = S.watch[id] || (S.watch[id] = { seen: Date.now(), running: false, notified: false });
  if (!final) { w.running = true; return; }
  if (!w.running || w.notified) return;
  w.notified = true;
  const sec = ((job.summary || {}).numbers || {}).seconds;
  notifyFinished(id, job, sec != null ? sec : (Date.now() - w.seen) / 1000);
}
function notifyRow() {
  const on = notifyOn();
  return `<div style="display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:14px 16px;border-radius:14px;background:var(--surface2);border:1px solid var(--line)">
<div style="display:flex;gap:12px;align-items:center"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8a6 6 0 0112 0c0 7 3 9 3 9H3s3-2 3-9zM10.3 21a1.9 1.9 0 003.4 0"/></svg><div><div style="font-weight:800;font-size:14px">Tell me when it finishes</div><div style="font-size:12.5px;color:var(--muted);font-weight:600">Browser notification and a short chime</div></div></div>
<button id="notify-toggle" aria-pressed="${on}" aria-label="Notify when the run finishes" style="flex:none;width:52px;height:30px;border-radius:99px;border:1px solid var(--line);padding:3px;display:flex;align-items:center;justify-content:${on ? "flex-end" : "flex-start"};background:${on ? "var(--accent)" : "var(--surface3)"}"><span style="width:22px;height:22px;border-radius:50%;background:${on ? "var(--accentInk)" : "var(--muted)"}"></span></button>
</div>`;
}
function wireNotify() {
  const b = $("#notify-toggle");
  if (!b) return;
  b.addEventListener("click", () => {
    const on = !notifyOn();
    store.set("sa-notify", on ? "on" : "off");
    if (on) askNotifyPermission();
    b.setAttribute("aria-pressed", String(on));
    b.style.justifyContent = on ? "flex-end" : "flex-start";
    b.style.background = on ? "var(--accent)" : "var(--surface3)";
    b.firstElementChild.style.background = on ? "var(--accentInk)" : "var(--muted)";
  });
}

/* ---------------------------------------------------------------- start */

async function boot() {
  const st = await api("/api/state");
  S.env = st.env; S.testMode = st.test_mode;
  const envEl = document.getElementById("env");
  if (st.env.name) {
    envEl.hidden = false;
    if (st.env.production) {           /* the live environment: a red PRODUCTION chip */
      envEl.style.borderColor = "var(--bad)"; envEl.style.color = "var(--bad)";
      document.getElementById("env-text").textContent = "PRODUCTION";
    } else {
      document.getElementById("env-text").textContent = String(st.env.name).toUpperCase() + " ";
    }
  }
  const banner = document.getElementById("banner");
  if (!st.env.allowed) {
    banner.hidden = false;
    banner.textContent = "This is the live Oracle environment. Making changes is switched off here.";
  }
  paintClaude(st.claude);
  if (!st.setup_complete && !location.hash.startsWith("#/setup")) location.hash = "#/setup";
  route();
  setInterval(async () => { paintClaude((await api("/api/state")).claude); }, 5000);
}

/* Claude sign-in: one button in the header, on every screen, while it is needed */
function paintClaude(c) {
  if (!c) return;
  const btn = document.getElementById("claude-signin");
  const wait = document.getElementById("claude-wait");
  btn.hidden = !c.installed || c.signed_in || c.signing_in;
  wait.hidden = !c.signing_in;
}
async function claudeSignin(jobId) {
  const r = await api("/api/claude/signin", jobId ? { job: jobId } : {});
  paintClaude({ installed: true, signed_in: false, signing_in: !!r.ok });
}
document.getElementById("claude-signin").addEventListener("click", () => claudeSignin());
window.addEventListener("hashchange", () => { S.ui = { open: null, filter: "All", q: "", closed: {} }; route(); });

function route() {
  clearTimers();
  const h = location.hash || "#/";
  if (h.startsWith("#/setup")) return renderSetup();
  if (h.startsWith("#/sheet/")) return renderPreview(h.slice(8));
  if (h.startsWith("#/job/")) return renderJob(h.slice(6));
  if (h.startsWith("#/summary/")) return renderSummary(h.slice(10));
  return renderUpload();
}

/* ---------------------------------------------------------------- setup checklist */

let setupStarted = false;
async function renderSetup() {
  setStage(null);
  if (!setupStarted) { setupStarted = true; api("/api/setup/start", {}); }
  const data = await api("/api/setup");
  const icon = (s) => s === "ok" ? '<span class="tick ok">✓</span>'
    : ["checking", "fixing", "signing"].includes(s) ? '<span class="tick busy"></span>'
    : s === "waiting" ? '<span class="tick wait">!</span>'
    : s === "failed" ? '<span class="tick bad">×</span>'
    : s === "skipped" ? '<span class="tick skip">–</span>' : '<span class="tick"></span>';
  const items = data.steps.map((s) => {
    let extra = "";
    // "Continue without automatic fixes": Claude's step never blocks setup
    const skip = s.skip ? `<button class="btn" data-step="${s.key}" data-skip="1">${esc(s.skip)}</button>` : "";
    if (s.state === "waiting") {
      extra = `${s.how ? `<div class="how">${esc(s.how)}</div>` : ""}
        <div class="actions"><button class="btn btnp" data-step="${s.key}"${s.retry ? ' data-retry="1"' : ""}>${esc(s.button || "Continue")}</button>${skip}</div>`;
    } else if (s.state === "failed" || s.state === "skipped") {
      extra = `<div class="actions"><button class="btn" data-step="${s.key}" data-retry="1">Try again</button></div>`;
    } else if (skip) {
      extra = `<div class="actions">${skip}</div>`;
    }
    return `<li>${icon(s.state)}<div><div class="t">${esc(s.title)}</div>
      <div class="s">${esc(s.state === "pending" ? "Not checked yet" : s.text)}</div>${extra}</div></li>`;
  }).join("");
  app.innerHTML = `<section class="card" style="display:flex;flex-direction:column;gap:14px">
    <div><h1>Let's set this up</h1><p class="lead" style="margin-top:6px">A few one-time steps on this computer. Most run by themselves; for the
    others you'll see a button and short instructions.</p></div>
    <ul class="steps">${items}</ul>
    ${data.complete ? `<div class="actions"><button class="btn btnp" id="go-home">Everything is ready - start</button></div>` : ""}
    </section>`;
  app.querySelectorAll("button[data-step]").forEach((b) => b.addEventListener("click", async () => {
    b.disabled = true;
    if (b.dataset.retry) await api("/api/setup/start", { from: b.dataset.step });
    else if (b.dataset.skip) await api("/api/setup/action", { step: b.dataset.step, skip: true });
    else await api("/api/setup/action", { step: b.dataset.step });
    renderSetup();
  }));
  const go = $("#go-home");
  if (go) go.addEventListener("click", () => { location.hash = "#/"; });
  if (data.complete) { later(() => { if (location.hash.startsWith("#/setup")) location.hash = "#/"; }, 2500); return; }
  later(renderSetup, 1500);
}

/* ---------------------------------------------------------------- stage 0: upload */

function step(n, t, s) {
  return `<div style="display:flex;gap:14px;align-items:flex-start"><div class="mono" style="width:30px;height:30px;border-radius:10px;background:var(--surface2);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--accent);flex:none">${n}</div><div><div style="font-weight:800">${t}</div><div style="font-size:13px;color:var(--muted);font-weight:600;line-height:1.5">${s}</div></div></div>`;
}

function renderUpload(message) {
  setStage(0);
  app.innerHTML = `<section style="display:flex;flex-wrap:wrap;gap:20px">
<div class="card" id="drop" style="flex:2 1 520px;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:16px;padding:56px 28px;border-style:dashed;border-width:2px;border-color:var(--accent);background:linear-gradient(180deg,var(--surface),var(--surface2))">
<div style="width:76px;height:76px;border-radius:24px;background:var(--glowA);display:flex;align-items:center;justify-content:center;color:var(--accent)">
<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4M7 9l5-5 5 5M4 20h16"/></svg>
</div>
<div style="font-size:24px;font-weight:800;letter-spacing:-.02em">Drop the setup workbook here</div>
<div style="font-size:14px;color:var(--muted);font-weight:600;max-width:440px;line-height:1.5">One Excel file with every module you need. Nothing is created until every check passes.</div>
<div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center">
<button class="btn btnp" id="choose">Choose workbook</button>
<a class="btn" href="/api/sheet/template" download="Upload sheet.xlsx" id="template">Get the blank template</a>
</div>
<input type="file" id="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" hidden aria-label="Setup workbook">
<div class="mono" style="font-size:12px;color:var(--muted)">.xlsx only</div>
${message ? `<div id="upload-state" role="alert" style="font-weight:800;font-size:14px;color:var(--bad);max-width:520px">${esc(message)}</div>` : ""}
</div>
<div class="card" style="flex:1 1 320px;min-width:0;display:flex;flex-direction:column;gap:18px">
<div class="label">How a run goes</div>
${step(1, "Upload", "The page reads every tab and finds each module.")}
${step(2, "Check", "Every row is checked against the sheet rules and Oracle. A red problem blocks the whole upload, with a suggestion to fix it.")}
${step(3, "Create", "If Oracle refuses a value, the run pauses for that item and asks you. Everything else keeps going.")}
${step(4, "Done", "One result card per item, plus a run summary.")}
</div>
</section>`;
  const drop = $("#drop"), input = $("#file");
  $("#choose").addEventListener("click", () => input.click());
  input.addEventListener("change", () => { if (input.files[0]) sendFile(input.files[0]); });
  ["dragenter", "dragover"].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.style.borderStyle = "solid"; }));
  ["dragleave", "drop"].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.style.borderStyle = "dashed"; }));
  drop.addEventListener("drop", (e) => { const f = e.dataTransfer.files[0]; if (f) sendFile(f); });
}

/* ---------------------------------------------------------------- module cards (stages 1-3) */

function moduleCard(m) {
  const open = S.ui.open === m.name;
  const c = KIND[m.kind];
  const bar = m.kind === "run" ? "var(--violet)" : (m.kind === "idle" ? "var(--muted)" : c[1]);
  const meta = MODS[m.name] || { mono: m.name.slice(0, 2).toUpperCase(), sub: "" };
  return `<button class="card modcard" style="padding:20px;display:block;cursor:pointer;${open ? "border-color:var(--accent)" : ""}" data-mod="${esc(m.name)}" aria-expanded="${open}">
<span style="display:flex;gap:14px;align-items:center">
<span class="mono" style="width:44px;height:44px;border-radius:12px;background:var(--surface2);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--accent);flex:none">${esc(meta.mono)}</span>
<span style="flex:1;min-width:0;display:block">
<span style="display:block;font-weight:800;font-size:17px">${esc(m.name)}</span>
<span style="display:block;font-size:12.5px;color:var(--muted);font-weight:600">${esc(meta.sub)}</span>
</span>
<span class="pill" style="${pillStyle(m.kind)}">${esc(m.pill)}</span>
</span>
<span style="display:block;height:8px;border-radius:99px;background:var(--surface3);overflow:hidden;margin-top:14px"><span class="${m.live ? "live" : ""}" style="display:block;height:100%;border-radius:99px;width:${m.prog}%;transition:width .5s;background-color:${bar}"></span></span>
<span style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;margin-top:12px"><span style="color:var(--muted)">${esc(m.line)}</span><span class="mono">${esc(m.count)}</span></span>
</button>`;
}

function modulesHtml(label, mods, extra) {
  const openMod = mods.find((m) => m.name === S.ui.open);
  return `<section style="display:flex;flex-direction:column;gap:12px" id="modules">
<div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px"><div class="label">${esc(label)}</div><div style="font-size:13px;color:var(--muted);font-weight:600">Open a module to see its items</div></div>
${extra || ""}
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(min(360px,100%),1fr));gap:16px">
${mods.map(moduleCard).join("")}
</div>
${openMod ? `<div class="card" style="display:flex;flex-direction:column;gap:12px">
<div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:17px;font-weight:800">${esc(openMod.name)}</div><button class="btn" style="min-height:36px" id="close-open">Close</button></div>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:10px">
${(openMod.items || []).map((it) => `<div style="background:var(--surface2);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;justify-content:space-between;gap:10px;align-items:center"><span style="font-weight:700">${esc(it.name)}</span><span class="pill" style="${pillStyle(it.kind)}">${esc(it.status)}</span></div>`).join("")}
</div>
${!(openMod.items || []).length ? `<div style="font-size:13px;color:var(--muted);font-weight:600">The items show here when the check is done.</div>` : ""}
${openMod.details || ""}
</div>` : ""}
</section>`;
}

function wireModules(rerender) {
  app.querySelectorAll("[data-mod]").forEach((b) => b.addEventListener("click", () => {
    S.ui.open = S.ui.open === b.dataset.mod ? null : b.dataset.mod;
    rerender();
  }));
  const c = $("#close-open");
  if (c) c.addEventListener("click", () => { S.ui.open = null; rerender(); });
}

function barHtml(o) {
  return `<div style="position:sticky;bottom:16px;z-index:5;margin-top:8px">
<div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding:14px 18px 14px 24px;border-radius:18px;background:var(--bar);border:1px solid var(--line);box-shadow:0 12px 40px rgba(0,0,0,.25);backdrop-filter:blur(10px)">
<div style="display:flex;gap:12px;align-items:center;flex:1 1 280px;min-width:0"><span class="dot" style="background:${o.dot};box-shadow:0 0 10px ${o.dot}"></span><div><div style="font-weight:800;font-size:15px">${esc(o.title)}</div><div style="font-size:12.5px;color:var(--muted);font-weight:600">${esc(o.sub)}</div></div></div>
<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
${o.secondary || ""}
${o.button}
</div>
</div>
</div>`;
}

/* ---------------------------------------------------------------- stage 1: check (while reading) */

async function sendFile(file) {
  if (!/\.xlsx$/i.test(file.name)) {
    renderUpload("This isn't an Excel workbook (.xlsx). In Excel, use File > Save As > Excel Workbook, then upload that file.");
    return;
  }
  setStage(1);
  let mods = [];
  try {        /* which kinds of setup the sheet has rows for (read on this PC, a moment) */
    mods = (await (await fetch("/api/sheet/peek", { method: "POST", body: file,
      headers: { "Content-Type": "application/octet-stream" } })).json()).modules || [];
  } catch (e) { mods = []; }
  const items = mods.reduce((s, m) => s + (m.count || 0), 0);
  const checking = () => {
    app.innerHTML = modulesHtml(`${file.name} · ${counted(mods.length, "module")} · ${counted(items, "item")}`,
      mods.map((m) => ({ name: m.name, pill: "Checking", kind: "run", prog: 70, live: true, line: "Reading rows…",
        count: counted(m.count, "item"), items: [] })));
    wireModules(checking);
  };
  checking();
  try {
    const r = await fetch("/api/sheet/upload", { method: "POST", body: file,
      headers: { "Content-Type": "application/octet-stream", "X-File-Name": file.name } });
    const res = await r.json();
    if (!res.id) { renderUpload((res.stops || ["The sheet couldn't be read."]).join(" ")); return; }
    S.previews[res.id] = res;
    location.hash = "#/sheet/" + res.id;
  } catch (e) {
    renderUpload("The page didn't answer. Check that it is still running, then try again.");
  }
}

/* ---------------------------------------------------------------- stage 1: check (the result) */

function groupsOf(p) {
  const recs = p.records || [];
  const names = (p.modules || []).filter((m) => m.count).map((m) => m.name);
  recs.forEach((r) => { if (r.group && !names.includes(r.group)) names.push(r.group); });
  return names;
}

/* the values a problem's own fix names ("Pick one of: a, b, c." / "for example 6"), shown read-only */
function suggestionsOf(x) {
  if (Array.isArray(x.suggestions) && x.suggestions.length) return x.suggestions.map(String);
  const fix = String(x.fix || "");
  let m = fix.match(/Pick one of: (.+?)\.?\s*$/);
  if (m) return m[1].replace(/\s*\.\.\.$/, "").split(/,\s+/).filter(Boolean);
  m = fix.match(/for example ([^\s,;]+?)[.,;]?(\s|$)/);
  return m ? [m[1]] : [];
}

function recordStatus(r) {
  if ((r.problems || []).length) return ["Problem", "bad"];
  if (r.skipped) return ["Already there", "idle"];
  if (r.held) return ["Held", "warn"];
  return ["Passed", "good"];
}

async function renderPreview(id) {
  setStage(1);
  const p = S.previews[id] || (S.previews[id] = await api("/api/sheet/" + id));
  if (p.error) { location.hash = "#/"; return; }
  if (p.signin === "waiting") {      // the sheet's checks with Oracle run once the user is signed in
    delete S.previews[id];
    later(() => { if (location.hash === "#/sheet/" + id) renderPreview(id); }, 3000);
  }
  if (p.job) { location.hash = "#/job/" + p.job; return; }      // already created from this upload
  S.last = () => renderPreview(id);
  const recs = p.records || [];
  const stops = p.stops || [];
  const oracleStops = p.oracle_stops || [];   // a check with Oracle that couldn't run: its real reason (2026-10-26)
  const problems = [...stops.map((s) => ({ where: oracleStops.includes(s) ? "Oracle" : "Sheet", title: s, why: "",
                                          suggestions: [] })),
    ...(p.problems || []).map((x) => ({
      where: [x.tab, x.row ? "row " + x.row : "", x.column].filter(Boolean).join(" · ") || "Sheet",
      title: x.text, why: x.fix || "", suggestions: suggestionsOf(x) }))];
  const unresolved = problems.length;
  const n = recs.length;
  const skips = recs.filter((r) => r.skipped).length;
  const waitingSignin = p.signin === "waiting" || p.signin === "failed";
  const ready = p.ok && n && !p.signin;
  let top = "";
  if (waitingSignin) {           /* the Oracle sign-in is renewed here, before Create */
    top = `<section class="card" style="border-color:var(--warn);display:flex;flex-direction:column;gap:12px">
<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><span class="pill" style="background:var(--warnBg);color:var(--warn);border:1px solid var(--warn)">${p.signin === "waiting" ? "Signing in" : "Sign-in needed"}</span><div style="font-size:18px;font-weight:800">${p.signin === "waiting" ? "Please sign in to Oracle" : "The Oracle sign-in didn't finish"}</div></div>
<div style="font-size:13px;color:var(--muted);font-weight:600;line-height:1.5">${p.signin === "waiting"
      ? `<span class="spinner tiny"></span> Your saved Oracle sign-in has expired. A sign-in window has opened: sign in there; it closes by itself. Then the sheet is checked with Oracle and Create becomes available. Nothing has been sent to Oracle.`
      : `The sheet can be created once you are signed in. Nothing has been sent to Oracle.`}</div>
${p.signin === "failed" ? `<div><button class="btn btnp" id="signin-again">Open the sign-in window again</button></div>` : ""}
</section>`;
  }
  if (unresolved) {
    top += `<section class="card" style="border-color:var(--bad);display:flex;flex-direction:column;gap:18px">
<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><span class="pill" style="background:var(--badBg);color:var(--bad)">${unresolved} problem${unresolved === 1 ? "" : "s"} left</span><div style="font-size:18px;font-weight:800">Fix these in the sheet, then upload it again.</div></div>
<div style="display:flex;flex-direction:column;gap:12px">
${problems.map((x) => `<div style="background:var(--surface2);border:1px solid var(--line);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:12px">
<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center"><span class="pill mono" style="background:var(--surface3);color:var(--text)">${esc(x.where)}</span><span style="font-weight:800">${esc(x.title)}</span></div>
${x.why ? `<div style="font-size:13px;color:var(--muted);font-weight:600">${esc(x.why)}</div>` : ""}
${x.suggestions.length ? `<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center" class="chips-ro"><span class="label">Suggested</span>
${x.suggestions.slice(0, 12).map((s) => `<span class="chip">${esc(s)}</span>`).join("")}</div>` : ""}
</div>`).join("")}
</div>
</section>`;
  } else if (ready) {
    top += `<section class="card" style="border-color:var(--accent);display:flex;gap:16px;align-items:center">
<div style="width:52px;height:52px;border-radius:16px;background:var(--glowA);color:var(--accent);display:flex;align-items:center;justify-content:center;flex:none"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
<div><div style="font-size:18px;font-weight:800">Every check passed</div><div style="font-size:13px;color:var(--muted);font-weight:600">${counted(n, "item")} ${n === 1 ? "is" : "are"} ready.${skips ? ` ${skips} already in Oracle ${skips === 1 ? "is" : "are"} skipped, nothing changed there.` : ""} Nothing has been created yet.</div></div>
</section>`;
  }
  /* module cards: one per module of the sheet, its records as the item list */
  const mods = groupsOf(p).map((g) => {
    const mine = recs.filter((r) => r.group === g);
    const bad = mine.filter((r) => (r.problems || []).length).length;
    const meta = (p.modules || []).find((m) => m.name === g) || {};
    return { name: g, pill: bad ? counted(bad, "problem") : "Ready", kind: bad ? "bad" : "good", prog: 100, live: false,
      line: bad ? "Fix this to continue" : "All rows passed", count: counted(meta.count || mine.length, "item"),
      items: mine.map((r) => { const st = recordStatus(r); return { name: r.name || r.title, status: st[0], kind: st[1] }; }),
      details: mine.length ? `<details class="more"><summary>What Oracle will get</summary>${mine.map((r) => detailHtml(r)).join("")}</details>` : "" };
  });
  const notes = [...(p.notes || []), ...(p.modules || []).filter((m) => m.text).map((m) => m.text)];
  const noteHtml = notes.length ? `<div style="font-size:13px;color:var(--muted);font-weight:600;line-height:1.5">${notes.map(esc).join("<br>")}</div>` : "";
  const testSwitch = ready && p.test_mode ? `<label class="label" style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="force"> Test: make this run fail once</label>` : "";
  const bar = barHtml({
    dot: unresolved || waitingSignin ? "var(--bad)" : "var(--accent)",
    title: unresolved ? `${unresolved} ${unresolved === 1 ? "problem blocks" : "problems block"} the upload`
      : waitingSignin ? "Waiting for the Oracle sign-in" : `All ${counted(n, "item")} are ready`.replace("All 1 item are", "1 item is"),
    sub: unresolved ? "Fix them in the sheet and upload it again. Nothing is created until all are fixed." : "Nothing has been created yet.",
    secondary: (unresolved ? `<a class="btn" href="#/" id="cancel">Upload the corrected sheet</a>` : "") + testSwitch,
    button: `<button class="btn btnp" id="create" style="min-width:200px"${ready ? "" : " disabled"}>Create ${counted(n, "item")}</button>`,
  });
  app.innerHTML = `${top}${modulesHtml(`${p.file} · ${counted(mods.length, "module")} · ${counted(n, "item")}`, mods, noteHtml)}${bar}`;
  wireModules(() => renderPreview(id));
  if ($("#signin-again")) $("#signin-again").addEventListener("click", async () => {
    await api("/api/sheet/" + id + "/signin", {}); delete S.previews[id]; renderPreview(id); });
  const btn = $("#create");
  if (btn && ready) btn.addEventListener("click", async () => {
    if (notifyOn()) askNotifyPermission();
    btn.disabled = true; btn.textContent = "Starting ...";
    const r = await api("/api/sheet/create", { upload: id, force_failure: !!($("#force") && $("#force").checked) });
    if (r.id) { p.job = r.id; location.hash = "#/job/" + r.id; }
    else if (r.signin) { delete S.previews[id]; renderPreview(id); }
    else { btn.disabled = false; btn.textContent = `Create ${counted(n, "item")}`;
      app.insertAdjacentHTML("afterbegin", `<div class="err-box">This can't be started right now.</div>`); }
  });
}

/* one record's detail: what the sheet says and what Oracle will get */
function detailHtml(r) {
  const n = (r.problems || []).length;
  return `<h3>${esc(r.title)} <span class="muted small">(${esc(r.tab)}, row ${r.row})</span></h3>
    ${n ? `<div class="small bad-t">${(r.problems || []).map((x) => esc(x.text)).join("<br>")}</div>` : ""}
    ${r.skipped ? `<div class="notes">${esc(r.skipped)}</div>` : ""}
    ${r.same_name ? `<div class="notes"><strong>Same name in Oracle:</strong> ${esc(r.same_name)}</div>` : ""}
    ${r.held ? `<div class="notes"><strong>Held:</strong> ${esc(r.held.replace(/^Held: /, ""))}</div>` : ""}
    ${r.oracle_summary ? `<div class="note-t"><strong>Oracle will get:</strong> ${esc(r.oracle_summary)}</div>` : ""}
    ${recordHtml(r)}`;
}

function cellHtml(c) {
  return `<td>${c.problem ? `<span class="bad-t">${esc(c.sheet ?? "empty")}</span>`
    : c.sheet == null ? `<span class="muted">${c.oracle && c.oracle !== "(left empty)" ? esc(c.oracle) : ""}</span>`
    : esc(c.sheet) + (c.oracle && c.oracle !== c.sheet && c.oracle !== "(only links the rows)" ? `<div class="note-t">Oracle gets: ${esc(c.oracle)}</div>` : "")}
    ${c.note && !c.problem ? `<div class="note-t">${esc(c.note)}</div>` : ""}</td>`;
}

function childTable(ch) {
  if (!(ch.rows || []).length) return ch.title ? `<h3>${esc(ch.title)}</h3><p class="muted small">None in the sheet for this one.</p>` : "";
  return `<h3>${esc(ch.title)}${ch.tab ? ` <span class="muted small">(${ch.count} on ${esc(ch.tab)})</span>` : ""}</h3>
    <div class="scroll"><table class="grid small-t"><thead><tr><th>Row</th>${ch.columns.map((c) => `<th>${esc(c.label)}</th>`).join("")}</tr></thead><tbody>
    ${ch.rows.map((k) => `<tr class="${k.cells.some((c) => c.problem) ? "bad" : ""}"><td>${k.row}</td>${k.cells.map(cellHtml).join("")}</tr>
    ${k.cells.filter((c) => c.problem).map((c) => `<tr class="bad"><td></td><td colspan="${ch.columns.length}">
      <span class="bad-t">${esc(c.problem)}</span> <span class="fix">${esc(c.fix || "")}</span></td></tr>`).join("")}`).join("")}
    </tbody></table></div>`;
}

function recordHtml(r) {
  let section = null;
  const rows = (r.fields || []).map((f) => {
    const sec = f.section !== section ? `<tr class="sec"><td colspan="3">${esc(f.section)}</td></tr>` : "";
    section = f.section;
    const oracle = f.problem ? `<span class="bad-t">${esc(f.problem)}</span><div class="fix">${esc(f.fix || "")}</div>`
      : `${f.default ? `<span class="muted">${esc(f.oracle)}</span>` : esc(f.oracle)}
         ${f.default && f.oracle !== "(left empty)" ? `<span class="tag">Oracle's default</span>` : ""}
         ${f.note ? `<div class="note-t">${esc(f.note)}</div>` : ""}`;
    return `${sec}<tr class="${f.problem ? "bad" : ""} ${f.required ? "req" : ""}">
      <th>${esc(f.label)}${f.required ? ' <span class="req-mark">Required</span>' : ""}</th>
      <td>${f.sheet == null ? '<span class="muted">empty</span>' : esc(f.sheet)}</td><td>${oracle}</td></tr>`;
  }).join("");
  const kids = r.child_tables ? r.child_tables.map(childTable).join("") : childTable(r.children || {});
  return `<div class="scroll"><table class="grid">
      <thead><tr><th>Field</th><th>What the sheet says</th><th>What Oracle will get</th></tr></thead>
      <tbody>${rows}</tbody></table></div>${kids}`;
}

/* ---------------------------------------------------------------- stages 2 and 3: the run */

async function renderJob(id) {
  const job = await api("/api/job/" + id);
  if (job.error) { location.hash = "#/"; return; }
  if (job.items) return renderBatch(id, job);
  return renderSingle(id, job);
}

const OPEN = ["open", "checking", "retrying"];
function itemStatus(it) {
  const q = it.question || {};
  if (it.state === "done") return it.skipped ? ["Already there", "idle"] : ["Created", "good"];
  if (it.state === "failed" && OPEN.includes(q.state)) return ["Needs you", "warn"];
  if (it.state === "failed" && q.state === "skipped") return ["Skipped", "warn"];
  if (it.state === "failed" && (it.saved === "yes" || it.saved === "maybe")) return ["Saved, not checked", "warn"];
  if (it.state === "failed") return ["Failed", "bad"];
  if (it.state === "running") return ["Creating", "run"];
  if (it.held) return ["Waiting", "idle"];
  return ["Queued", "idle"];
}

function decisionHtml(it) {
  const q = it.question, busy = q.state !== "open";
  const what = titleCase(it.what || "item");
  const sugg = q.suggestions || [];
  return `<div class="card question" data-n="${it.n}" style="flex:1 1 440px;min-width:0;border-color:var(--warn);display:flex;flex-direction:column;gap:16px;background:linear-gradient(180deg,var(--warnBg),var(--surface) 60%)">
<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="pill" style="background:var(--warnBg);color:var(--warn);border:1px solid var(--warn)">Needs your decision</span><span style="font-size:13px;color:var(--muted);font-weight:600">Everything else is on hold only for this item</span></div>
<div style="font-size:18px;font-weight:800;line-height:1.35">Oracle refused one value in ${esc(what)} "${esc(it.name)}"</div>
<div style="display:grid;grid-template-columns:auto 1fr;gap:8px 16px;font-size:14px">
<span class="label" style="align-self:center">Where</span><span style="font-weight:700">${esc([q.where, q.label].filter(Boolean).join(" · "))}${q.tab ? ` <span style="color:var(--muted);font-weight:600">(${esc(q.tab)}${q.row ? ", row " + q.row : ""})</span>` : ""}</span>
<span class="label" style="align-self:center">You sent</span><span class="mono" style="font-weight:700">${q.value == null || q.value === "" ? "(empty)" : esc(q.value)}</span>
<span class="label" style="align-self:center">Oracle said</span><span style="font-weight:600;color:var(--muted)">${esc(q.reason || "")}</span>
${q.proposed ? `<span class="label" style="align-self:center">Claude suggests</span><span style="font-weight:600">Change it to <span class="mono" style="font-weight:700">${esc(sugg[0] || "")}</span>: ${esc(q.proposed)} Nothing is changed until you choose.</span>` : ""}
</div>
${q.message ? `<div style="font-weight:800;font-size:14px;color:var(--bad)">${esc(q.message)}</div>` : ""}
${busy ? `<div style="display:flex;flex-direction:column;gap:8px"><div style="font-weight:800;font-size:14px;color:var(--violet)">${q.state === "checking" ? "Checking your answer against Oracle…" : "Trying it again with your answer…"}</div><div style="height:8px;border-radius:99px;background:var(--surface3);overflow:hidden"><div class="live" style="width:70%;height:100%;border-radius:99px;background-color:var(--violet)"></div></div></div>`
    : `<div style="display:flex;flex-direction:column;gap:10px">
${sugg.length ? `<span class="label">${q.proposed ? "Pick Claude's proposal" : "Pick a suggestion"}</span>
<div style="display:flex;flex-wrap:wrap;gap:8px">${sugg.map((s, i) => `<button class="btn q-pick" data-n="${it.n}" data-v="${esc(s)}"${i === 0 ? ' style="border-color:var(--accent);color:var(--accent)"' : ""}>${esc(s)}</button>`).join("")}</div>` : ""}
<label for="q-text-${it.n}" class="label" style="margin-top:6px">Or type your own</label>
<div style="display:flex;gap:8px;flex-wrap:wrap"><input id="q-text-${it.n}" class="field q-text" placeholder="Checked against Oracle before it is used" style="flex:1 1 220px"><button class="btn btnp q-use" data-n="${it.n}">Use it</button><button class="btn q-skip" data-n="${it.n}">Skip this item</button></div>
</div>`}
</div>`;
}

function jobModules(job, final) {
  const items = job.items;
  const names = [];
  items.forEach((it) => { const m = modOf(it.what); if (!names.includes(m)) names.push(m); });
  return names.map((name) => {
    const mine = items.filter((it) => modOf(it.what) === name), total = mine.length;
    const fin = mine.filter((it) => ["done", "failed"].includes(it.state) && !OPEN.includes((it.question || {}).state)).length;
    const asking = mine.some((it) => OPEN.includes((it.question || {}).state));
    const created = mine.filter((it) => it.state === "done").length;
    const skippedYou = mine.filter((it) => (it.question || {}).state === "skipped").length;
    const failed = mine.filter((it) => it.state === "failed").length - skippedYou;
    let pill, kind, prog, line, live = false, count = `${fin}/${total}`;
    if (final) {
      pill = failed ? `Done · ${failed} failed` : skippedYou ? `Done · ${skippedYou} skipped` : "All created";
      kind = failed ? "bad" : skippedYou ? "warn" : "good"; prog = 100; line = "Finished"; count = `${created}/${total}`;
    } else if (asking) { pill = "Needs you"; kind = "warn"; prog = fin / total * 100; line = "Waiting for your answer"; }
    else if (fin === total) { pill = failed ? `Done · ${failed} failed` : "Created"; kind = failed ? "bad" : "good"; prog = 100; line = "All created"; }
    else if (mine.some((it) => it.state === "running")) { pill = "Creating"; kind = "run"; prog = fin / total * 100; line = "Creating now"; live = true; }
    else { pill = "Queued"; kind = "idle"; prog = fin / total * 100; line = "Queued"; }
    return { name, pill, kind, prog, live, line, count,
      items: mine.map((it) => { const st = itemStatus(it); return { name: it.name, status: st[0], kind: st[1] }; }) };
  });
}

async function fileOf(job) {
  if (!job.upload) return null;
  const p = S.previews[job.upload] || (S.previews[job.upload] = await api("/api/sheet/" + job.upload));
  return p && !p.error ? p.file : null;
}

async function renderBatch(id, job) {
  const items = job.items, st = job.state;
  const asked = items.filter((it) => it.question && OPEN.includes(it.question.state));
  const final = ["done", "failed", "asking"].includes(st) && !asked.length;
  watchRun(id, job, final);
  setStage(final ? 3 : 2);
  const file = await fileOf(job);
  const total = items.length;
  const label = `${file ? file + " · " : ""}${counted(jobModules(job, final).length, "module")} · ${counted(total, "item")}`;
  if (!final) return renderRunning(id, job, asked, label);
  return renderDone(id, job, label);
}

function renderRunning(id, job, asked, label) {
  const items = job.items, total = items.length, st = job.state;
  const fin = items.filter((it) => ["done", "failed"].includes(it.state) && !OPEN.includes((it.question || {}).state)).length;
  const paused = asked.length > 0 && !["running", "queued", "repairing"].includes(st);
  const note = paused ? (asked.length === 1 ? "Paused for one answer. The rest continues right after." : `Paused for ${asked.length} answers. The rest continues right after.`)
    : st === "queued" ? (job.ahead ? "Waiting for the task before yours to finish" : "Starting")
    : job.repairing ? "A small problem came up and is being fixed; this can take a few minutes."
    : [job.text, job.sub_text].filter(Boolean).join(" · ") || "Running";
  const run = `<div class="card" style="flex:1 1 420px;min-width:0;display:flex;flex-direction:column;gap:18px">
<div style="display:flex;justify-content:space-between;align-items:baseline"><div style="font-size:18px;font-weight:800">Creating in Oracle</div><div class="mono" style="font-size:22px;font-weight:700;color:var(--accent)">${fin} / ${total}</div></div>
<div style="height:14px;border-radius:99px;background:var(--surface3);overflow:hidden"><div class="${paused ? "" : "live"}" style="height:100%;border-radius:99px;transition:width .4s;background-color:var(--accent);width:${total ? fin / total * 100 : 0}%"></div></div>
<div style="font-size:13px;color:var(--muted);font-weight:600">${esc(note)}</div>
${notifyRow()}
</div>`;
  const bar = barHtml({ dot: asked.length ? "var(--warn)" : "var(--accent)", title: `Creating: ${fin} of ${total} done`,
    sub: asked.length ? (asked.length === 1 ? "One item is waiting for your decision." : `${asked.length} items are waiting for your decision.`) : "Running. You can leave this page open.",
    button: `<button class="btn btnp" disabled style="min-width:200px">Run in progress</button>` });
  const typing = document.activeElement && document.activeElement.classList.contains("q-text");
  if (!typing) {
    app.innerHTML = `<section style="display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start">${run}${asked.map(decisionHtml).join("")}</section>
${modulesHtml(label, jobModules(job, false))}${bar}`;
    wireNotify();
    wireModules(() => renderJob(id));
    wireAnswers(id);
  }
  later(() => { if (location.hash === "#/job/" + id) renderJob(id); }, asked.length ? 3000 : 1500);
}

function wireAnswers(id) {
  const answer = async (n, body) => {
    app.querySelectorAll(`.question[data-n="${n}"] button`).forEach((b) => { b.disabled = true; });
    await api(`/api/job/${id}/answer`, Object.assign({ n: Number(n) }, body));
    renderJob(id);
  };
  app.querySelectorAll(".q-pick").forEach((b) => b.addEventListener("click", () => answer(b.dataset.n, { value: b.dataset.v })));
  app.querySelectorAll(".q-use").forEach((b) => b.addEventListener("click", () => {
    const v = $("#q-text-" + b.dataset.n).value;
    if (v.trim()) answer(b.dataset.n, { value: v });
  }));
  app.querySelectorAll(".q-text").forEach((t) => t.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && t.value.trim()) answer(t.id.replace("q-text-", ""), { value: t.value });
  }));
  app.querySelectorAll(".q-skip").forEach((b) => b.addEventListener("click", () => answer(b.dataset.n, { skip: true })));
}

function resultNote(it) {
  const st = itemStatus(it)[0];
  if (st === "Skipped") return (it.text ? it.text + " " : "") + "You skipped it. Nothing was saved for it.";
  if (st === "Saved, not checked") return it.text || (it.saved === "yes" ? "It is saved in Oracle, but not checked to the end." : "It may have been saved in Oracle.");
  return it.text || "";
}

function mmss(sec) { if (sec == null) return null; const m = Math.floor(sec / 60), s = Math.round(sec % 60); return `${m}:${String(s).padStart(2, "0")}`; }
function minSec(sec) { if (sec == null) return null; const m = Math.floor(sec / 60), s = Math.round(sec % 60); return m ? `${m} min ${s} s` : `${s} s`; }

function renderDone(id, job, label) {
  const items = job.items;
  const num = (job.summary || {}).numbers || {};
  const skippedYou = items.filter((it) => (it.question || {}).state === "skipped").length;
  const answered = items.filter((it) => ["answered", "retrying"].includes((it.question || {}).state)).length;
  const reps = num.repairs || [];
  const props = reps.filter((r) => r.kind === "proposal").length, fixes = reps.length - props;
  const cost = num.repair_cost_usd || 0;
  const claude = reps.length ? "Claude: " + [props ? counted(props, "proposal") : "", fixes ? counted(fixes, "repair") : ""].filter(Boolean).join(", ") + ", $" + cost.toFixed(2)
    : "Claude: not used";
  const results = items.map((it) => { const s = itemStatus(it); return { module: modOf(it.what), name: it.name, status: s[0], kind: s[1], note: resultNote(it) }; });
  const statuses = ["All", "Created", "Skipped", ...["Already there", "Saved, not checked", "Failed", "Waiting"].filter((s) => results.some((r) => r.status === s))];
  const failedNoSave = items.filter((it) => it.state === "failed" && it.saved === "no");
  const onlySkipped = failedNoSave.length && failedNoSave.every((it) => (it.question || {}).state === "skipped");
  const extra = [job.skipped ? `${job.skipped} already there` : "", results.some((r) => r.status === "Failed") ? `${results.filter((r) => r.status === "Failed").length} failed` : ""].filter(Boolean);
  const stats = `<section style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px">
<div class="card" style="padding:20px"><div class="label">Created</div><div class="mono" style="font-size:40px;font-weight:700;color:var(--accent);margin-top:6px">${job.created || 0}</div></div>
<div class="card" style="padding:20px"><div class="label">Skipped by you</div><div class="mono" style="font-size:40px;font-weight:700;color:var(--warn);margin-top:6px">${skippedYou}</div></div>
<div class="card" style="padding:20px"><div class="label">Answered during run</div><div class="mono" style="font-size:40px;font-weight:700;margin-top:6px">${answered}</div></div>
<div class="card" style="padding:20px"><div class="label">Run time</div><div class="mono" style="font-size:40px;font-weight:700;margin-top:6px">${mmss(num.seconds) || "–"}</div><div style="font-size:12.5px;color:var(--muted);font-weight:600;margin-top:2px">${esc(claude)}</div></div>
</section>`;
  const resultsCard = `<section class="card" style="display:flex;flex-direction:column;gap:18px">
<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
<div style="font-size:18px;font-weight:800">Result cards</div>
<button class="btn" id="toggle-all" aria-controls="results">Collapse all</button>
</div>
<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center">
<div style="flex:1 1 260px;position:relative">
<label for="q" style="position:absolute;left:-9999px">Search results</label>
<input id="q" class="field" value="${esc(S.ui.q)}" placeholder="Search by name or module" style="width:100%">
</div>
<div style="display:flex;gap:8px;flex-wrap:wrap" id="filters">
${statuses.map((f) => `<button class="btn" data-filter="${esc(f)}" style="${S.ui.filter === f ? "background:var(--accent);color:var(--accentInk);border-color:var(--accent)" : ""}" aria-pressed="${S.ui.filter === f}">${esc(f)}</button>`).join("")}
</div>
</div>
<div id="results" style="display:flex;flex-direction:column;gap:28px"></div>
</section>`;
  const bar = barHtml({ dot: "var(--accent)", title: num.seconds != null ? `Run finished in ${minSec(num.seconds)}` : "Run finished",
    sub: [`${job.created || 0} created`, `${skippedYou} skipped`, ...extra].join(" · "),
    secondary: job.failed_sheet ? `<a class="btn" id="failed-sheet" href="/api/job/${id}/failed.xlsx" download="${esc(job.failed_name || "Failed rows.xlsx")}">${onlySkipped ? "Skipped-only sheet" : "Failed-only sheet"}</a>` : "",
    button: `<a class="btn btnp" href="#/" id="new-run" style="min-width:200px">Start a new run</a>` });
  app.innerHTML = `${modulesHtml(label, jobModules(job, true))}${stats}${resultsCard}${summaryHtml(job.summary, job)}${bar}`;
  const paint = () => paintResults(results);
  paint();
  $("#q").addEventListener("input", (e) => { S.ui.q = e.target.value; paint(); });
  app.querySelectorAll("[data-filter]").forEach((b) => b.addEventListener("click", () => {
    S.ui.filter = b.dataset.filter;
    app.querySelectorAll("[data-filter]").forEach((x) => {
      const on = x.dataset.filter === S.ui.filter;
      x.setAttribute("aria-pressed", String(on));
      x.setAttribute("style", on ? "background:var(--accent);color:var(--accentInk);border-color:var(--accent)" : "");
    });
    paint();
  }));
  $("#toggle-all").addEventListener("click", () => {
    const names = [...new Set(results.map((r) => r.module))];
    const collapse = names.some((n) => !S.ui.closed[n]);
    names.forEach((n) => { S.ui.closed[n] = collapse; });
    paint();
  });
  wireModules(() => renderJob(id));
  if (job.state === "asking") later(() => { if (location.hash === "#/job/" + id) renderJob(id); }, 3000);
}

/* the result cards, one section per module (in the page's module order), each open or collapsed; search and the
   status filter apply live, a module without a matching card is left out. Inside a module: what needs attention
   first, then skipped, then created, each in its original order. */
const MOD_ORDER = ["Customers", "Order Types", "Payment Terms", "Lookup Types", "Business Units", "Price Lists"];
const STATUS_ORDER = ["Failed", "Needs you", "Saved, not checked", "Waiting", "Skipped", "Already there", "Created"];
const STATUS_RANK = { "Failed": 0, "Needs you": 0, "Saved, not checked": 0, "Waiting": 0, "Queued": 0, "Creating": 0,
  "Skipped": 1, "Already there": 1, "Created": 2 };
const KIND_OF = { "Failed": "bad", "Needs you": "warn", "Saved, not checked": "warn", "Waiting": "idle", "Skipped": "warn",
  "Already there": "idle", "Created": "good", "Queued": "idle", "Creating": "run" };
const monoOf = (name) => (MODS[name] || { mono: String(name || "?").slice(0, 2).toUpperCase() }).mono;
const byModuleOrder = (a, b) => (MOD_ORDER.indexOf(a) + 1 || 99) - (MOD_ORDER.indexOf(b) + 1 || 99);

function paintResults(results) {
  const box = $("#results");
  if (!box) return;
  const q = S.ui.q.toLowerCase();
  const shown = results.filter((r) => (S.ui.filter === "All" || r.status === S.ui.filter) && (!q || (r.module + " " + r.name).toLowerCase().includes(q)));
  const names = [...new Set(results.map((r) => r.module))].sort(byModuleOrder);
  const sections = names.map((name, gi) => {
    const all = results.filter((r) => r.module === name);
    const mine = shown.map((r, i) => [r, i]).filter(([r]) => r.module === name)
      .sort((a, b) => (STATUS_RANK[a[0].status] ?? 0) - (STATUS_RANK[b[0].status] ?? 0) || a[1] - b[1]).map(([r]) => r);
    if (!mine.length) return "";
    const open = !S.ui.closed[name];
    const counts = [...STATUS_ORDER, ...new Set(all.map((r) => r.status))].filter((st, i, a) => a.indexOf(st) === i)
      .map((st) => [st, all.filter((r) => r.status === st).length]).filter(([, n]) => n);
    return `<section class="rgroup" data-group="${esc(name)}">
<button class="rg-head" data-toggle="${esc(name)}" aria-expanded="${open}" aria-controls="rg-${gi}">
<span class="mono rg-mono" aria-hidden="true">${esc(monoOf(name))}</span>
<span class="rg-name"><span style="font-weight:800;font-size:17px">${esc(name)}</span><span class="mono" style="font-size:12.5px;color:var(--muted);font-weight:700">${counted(all.length, "item")}${mine.length !== all.length ? ` · ${mine.length} shown` : ""}</span></span>
<span class="rg-pills">${counts.map(([st, n]) => `<span class="pill" style="${pillStyle(KIND_OF[st] || "idle")}">${n} ${esc(st)}</span>`).join("")}</span>
<svg class="rg-chev" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
<span class="sr">${open ? "Collapse" : "Open"} ${esc(name)}</span>
</button>
<div class="rg-line" aria-hidden="true"></div>
<div class="rg-grid" id="rg-${gi}"${open ? "" : " hidden"}>
${mine.map((r) => `<div class="rcard">
<div style="display:flex;justify-content:space-between;gap:10px;align-items:center"><span class="mono rc-mono" aria-hidden="true">${esc(monoOf(name))}</span><span class="pill" style="${pillStyle(r.kind)}">${esc(r.status)}</span></div>
<div style="font-weight:800;font-size:16px;overflow-wrap:anywhere">${esc(r.name)}</div>
<div style="font-size:13px;color:var(--muted);font-weight:600;line-height:1.45;overflow-wrap:anywhere">${esc(r.note)}</div>
</div>`).join("")}
</div>
</section>`;
  }).join("");
  box.innerHTML = sections || `<div style="text-align:center;padding:28px;color:var(--muted);font-weight:600">No result matches that search.</div>`;
  box.querySelectorAll("[data-toggle]").forEach((b) => b.addEventListener("click", () => {
    const name = b.dataset.toggle;
    S.ui.closed[name] = !S.ui.closed[name];
    const grid = document.getElementById(b.getAttribute("aria-controls"));
    grid.hidden = !!S.ui.closed[name];
    b.setAttribute("aria-expanded", String(!S.ui.closed[name]));
    b.querySelector(".sr").textContent = (S.ui.closed[name] ? "Open " : "Collapse ") + name;
    toggleAllLabel(results);
  }));
  toggleAllLabel(results);
}

function toggleAllLabel(results) {
  const t = $("#toggle-all");
  if (!t) return;
  const names = [...new Set(results.map((r) => r.module))];
  t.textContent = names.some((n) => !S.ui.closed[n]) ? "Collapse all" : "Expand all";
}

/* one request run on its own (not from a sheet): the same steps, in the new frame */
async function renderSingle(id, job) {
  const st = job.state;
  const head = `<div><h1>${esc(job.title || "Your request")}</h1></div>`;
  if (["queued", "running", "repairing", "signing"].includes(st)) {
    setStage(2); watchRun(id, job, false);
    const text = st === "queued" ? (job.ahead ? "Waiting for the task before yours to finish" : "Starting") : job.text || "Working";
    const pct = Math.max(2, Math.min(99, job.percent || 0));
    app.innerHTML = `<section class="card">${head}
      <div class="step-now" style="margin-top:12px">${st === "signing" ? "" : '<span class="spinner"></span>&nbsp; '}${esc(text)}</div>
      <div class="bar"><span class="live" style="width:${pct}%"></span></div>
      <div class="pct">About ${pct}% done${st === "repairing" ? " - a small problem came up and is being fixed; this can take a few minutes" : ""}</div>
      ${(job.done_lines || []).length ? `<ul class="steps-done">${job.done_lines.map((s) => `<li>✓ ${esc(s)}</li>`).join("")}</ul>` : ""}
      ${st === "signing" ? `<p class="muted">The window closes by itself when you reach the Oracle home page. The task then continues where it stopped.</p>` : ""}
      </section>`;
    later(() => renderJob(id), 1000);
    return;
  }
  setStage(3); watchRun(id, job, true);
  if (st === "done") {
    const res = job.result || {};
    app.innerHTML = `<section class="card result">
      <div class="big ${res.partial ? "note" : "ok"}">${res.partial ? "!" : "✓"}</div>
      <h2>${res.partial ? "Done, with one note" : res.skipped ? "Already there" : "Done"}</h2>
      <p>${esc(res.text)}</p>
      ${(res.steps || []).length ? `<ul class="steps-done">${res.steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>` : ""}
      ${res.repaired ? `<p class="muted small">A small problem came up on the way and was fixed automatically.</p>` : ""}
      ${res.where ? `<div class="where"><strong>Where to look:</strong> ${esc(res.where)}</div>` : ""}
      ${createdHtml(res.created)}
      <div class="actions"><a class="btn btnp" href="#/">Start a new run</a></div></section>`;
    return;
  }
  const ask = job.ask || {};
  if (st === "needs_user" && ask.kind === "sign_in") {
    app.innerHTML = `<section class="card result"><div class="big ask">!</div>
      <h2>Please sign in to Oracle</h2><p>${esc(ask.text)}</p>
      <div class="actions"><button class="btn btnp" id="signin">Sign in to Oracle</button></div>
      <p class="muted small">A browser window opens; sign in there yourself. Nothing is created twice.</p></section>`;
    $("#signin").addEventListener("click", async () => { await api(`/api/job/${id}/signin`, {}); renderJob(id); });
    return;
  }
  if (st === "needs_user" && ask.kind === "value") {
    app.innerHTML = `<section class="card result"><div class="big ask">!</div>
      <h2>Please change a value in the sheet</h2><p>${esc(ask.text)}</p>
      ${(ask.problems || []).filter((p) => p.valid && p.valid.length).map((p) => `<div class="where"><strong>${esc(p.text)}</strong><br>You can pick: ${p.valid.slice(0, 60).map(esc).join(", ")}${p.valid.length > 60 ? " ..." : ""}</div>`).join("")}
      <p class="muted small">Nothing was created. Change the value in Excel, save, and upload the sheet again.</p>
      <div class="actions"><a class="btn" href="#/">Upload a corrected sheet</a></div></section>`;
    return;
  }
  if (ask.kind === "claude") {
    const c = (await api("/api/state")).claude || {};
    app.innerHTML = `<section class="card result"><div class="big ask">!</div>
      <h2>One more step to fix this</h2><p>${esc(ask.text)}</p>
      ${c.signing_in ? `<p><span class="spinner tiny"></span> Waiting for you to sign in to Claude. Claude's
        sign-in page is open in your browser; the fix starts by itself when you are signed in.</p>`
        : `<div class="actions"><button class="btn btnp" id="claude-fix">Sign in to Claude and fix it</button></div>
           <p class="muted small">Claude's sign-in page opens in your browser. Sign in with your own account;
           nothing else to press here.</p>`}
      <details class="more"><summary>Or do it yourself in Claude</summary>
        <textarea class="copybox" id="copy" readonly>${esc(ask.copy || "")}</textarea>
        <div class="actions"><button class="btn" id="copybtn">Copy the message</button></div></details></section>`;
    if ($("#claude-fix")) $("#claude-fix").addEventListener("click", async () => { await claudeSignin(id); renderJob(id); });
    if ($("#copybtn")) $("#copybtn").addEventListener("click", () => copyAsk(ask));
    later(() => renderJob(id), 3000);               // the fix starts by itself after the sign-in
    return;
  }
  app.innerHTML = `<section class="card result"><div class="big bad">×</div>
    <h2>This didn't work</h2><p>${esc(ask.text || (job.result || {}).text || "Something went wrong.")}</p>
    ${ask.todo ? `<p><strong>What to do:</strong> ${esc(ask.todo)}</p>` : ""}
    ${ask.copy ? `<textarea class="copybox" id="copy" readonly>${esc(ask.copy)}</textarea>
      <div class="actions"><button class="btn" id="copybtn">Copy the message</button></div>` : ""}
    <div class="actions"><a class="btn btnp" href="#/">Back to the upload</a></div></section>`;
  if ($("#copybtn")) $("#copybtn").addEventListener("click", () => copyAsk(ask));
}

/* the "Run summary" (page/run_summary.py): its numbers as cards (Overview, By module, Timeline, Claude and
   repairs, Decisions and problems), every fact of its sentences kept; the sentences themselves when there are no
   numbers (an older page). `job` (the run in memory, when there is one) adds what each question's answer was. */
const clockOf = (iso) => iso ? iso.slice(11, 16) : "?";
const secsOf = (iso) => iso ? Date.parse(iso.replace(" ", "T")) / 1000 : null;
function dur(sec) {
  if (sec == null) return null;
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), x = Math.floor(sec % 60);
  return [h ? h + " h" : "", m || h ? m + " min" : "", x + " s"].filter(Boolean).join(" ");
}
const money = (usd) => "$" + Number(usd || 0).toFixed(2);
const thousands = (n) => Number(n || 0).toLocaleString("en-US");

function tile(label, value, color, sub) {
  return `<div class="sum-tile"><div class="label">${esc(label)}</div><div class="mono" style="font-size:32px;font-weight:700;line-height:1.1;margin-top:6px;${color ? "color:" + color : ""}">${esc(value)}</div>${sub ? `<div style="font-size:12.5px;color:var(--muted);font-weight:600;margin-top:4px">${sub}</div>` : ""}</div>`;
}

function summaryHtml(sv, job) {
  if (!sv) return "";
  const s = sv.numbers;
  if (!s || !Array.isArray(s.records)) {          /* no numbers: the sentences as they come */
    return sv.sections ? `<section class="card run-summary"><div style="font-size:18px;font-weight:800">Run summary</div>
      ${sv.sections.map((sec) => `${sec.heading ? `<h3>${esc(sec.heading)}</h3>` : ""}
        <ul class="${sec.heading ? "" : "plain"}">${sec.lines.map((l) => `<li>${esc(l)}</li>`).join("")}</ul>`).join("")}</section>` : "";
  }
  const recs = s.records, qs = s.questions || [];
  const items = (job && job.items) || [];
  const itemOf = (n) => items.find((it) => it.n === n) || {};
  const qOf = (n) => qs.find((q) => q.n === n);
  const recName = (r) => r.name || `${titleCase(r.what || "customer")} ${r.n}`;
  const skippedYou = qs.filter((q) => q.state === "skipped").length;
  const notes = (sv.sections || []).filter((x) => !x.heading).flatMap((x) => x.lines);
  const fromFailed = notes.filter((l) => l.startsWith("This run was the upload"));
  const general = notes.filter((l) => !l.startsWith("This run was the upload"));
  const savedRecs = recs.filter((r) => r.state === "failed" && ["yes", "maybe"].includes(r.saved));

  /* 1. Overview */
  const overview = `<div class="card sum-card" style="grid-column:1/-1">
<div class="label">Overview</div>
<div class="sum-tiles">
${tile("Items", recs.length)}
${tile("Created", s.created, "var(--accent)")}
${s.skipped ? tile("Already in Oracle, skipped", s.skipped, "var(--muted)", "Nothing changed there") : ""}
${tile("Skipped by you", skippedYou, skippedYou ? "var(--warn)" : "")}
${tile("Failed", s.failed, s.failed ? "var(--bad)" : "", s.failed && skippedYou ? `Not created, including the ${skippedYou} skipped by you` : "Not created")}
${tile("Saved, not fully checked", s.saved_not_checked, s.saved_not_checked ? "var(--warn)" : "", savedRecs.map((r) => esc(recName(r)) + (r.registry_id ? ", Registry ID " + esc(r.registry_id) : "")).join("; "))}
${s.seconds != null ? tile("Run time", dur(s.seconds), "", `${esc(clockOf(s.started))} to ${esc(clockOf(s.ended))}`) : ""}
${s.check_seconds != null ? tile("Sheet check", dur(s.check_seconds), "", "Before Create") : ""}
</div>
${fromFailed.map((l) => `<div style="font-size:13px;color:var(--muted);font-weight:600">${esc(l)}</div>`).join("")}
</div>`;

  /* modules of the run, in the page's module order */
  const modNames = [...new Set(recs.map((r) => modOf(r.what || "customer")))].sort(byModuleOrder);
  const modRecs = (m) => recs.filter((r) => modOf(r.what || "customer") === m);
  const span = (rs) => {
    if (!rs.length || rs.some((r) => !r.started || !r.ended)) return null;
    const a = Math.min(...rs.map((r) => secsOf(r.started))), b = Math.max(...rs.map((r) => secsOf(r.ended)));
    return { start: rs.find((r) => secsOf(r.started) === a).started, end: rs.find((r) => secsOf(r.ended) === b).ended, sec: b - a };
  };
  const together = (rs) => rs.length > 1 && new Set(rs.map((r) => r.started + "|" + r.ended)).size === 1 && rs[0].started;

  /* 2. By module */
  const byModule = `<div class="card sum-card">
<div class="label">By module</div>
<div style="display:flex;flex-direction:column;gap:16px">
${modNames.map((m) => {
    const rs = modRecs(m), sp = span(rs);
    const created = rs.filter((r) => r.state === "created").length;
    const already = rs.filter((r) => r.state === "skipped").length;
    const you = rs.filter((r) => r.state === "failed" && (qOf(r.n) || {}).state === "skipped").length;
    const failed = rs.filter((r) => r.state === "failed").length - you;
    const notSent = rs.filter((r) => !r.started).length;
    const pills = [[created, "created", "good"], [already, "already there", "idle"], [you, "skipped", "warn"],
      [failed, "failed", "bad"], [notSent, "not sent", "idle"]].filter(([n]) => n)
      .map(([n, w, k]) => `<span class="pill" style="${pillStyle(k)}">${n} ${w}</span>`).join("");
    return `<div class="sum-mod">
<span class="mono rg-mono" aria-hidden="true">${esc(monoOf(m))}</span>
<div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:8px">
<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between"><div><span style="font-weight:800">${esc(m)}</span> <span class="mono" style="font-size:12.5px;color:var(--muted);font-weight:700">${counted(rs.length, "item")}</span></div>${sp ? `<span class="mono" style="font-size:13px;font-weight:700">${esc(dur(sp.sec))}</span>` : ""}</div>
<div style="display:flex;flex-wrap:wrap;gap:6px">${pills}${together(rs) ? `<span class="pill" style="${pillStyle("run")}">Created together in one go</span>` : ""}</div>
<div class="sum-bar" role="img" aria-label="${created} of ${rs.length} created"><span style="width:${rs.length ? created / rs.length * 100 : 0}%"></span></div>
</div>
</div>`;
  }).join("")}
</div>
</div>`;

  /* 3. Timeline */
  const row = (name, when, len, muted) => `<li class="sum-tl"><span class="sum-dot" aria-hidden="true"></span><span style="flex:1 1 150px;min-width:0;font-weight:${muted ? 600 : 700};${muted ? "color:var(--muted)" : ""};overflow-wrap:break-word">${esc(name)}</span><span style="display:flex;gap:12px;align-items:center;margin-left:auto"><span class="mono" style="font-size:12.5px;color:var(--muted);font-weight:700;white-space:nowrap">${esc(when)}</span>${len != null ? `<span class="mono" style="font-size:12.5px;font-weight:700;min-width:64px;text-align:right;white-space:nowrap">${esc(len)}</span>` : ""}</span></li>`;
  const timeline = `<div class="card sum-card">
<div class="label">Timeline</div>
<ul class="sum-list">
${s.started ? row("Run started", clockOf(s.started), null) : ""}
${s.ended ? row("Run finished", clockOf(s.ended), s.seconds != null ? dur(s.seconds) : null) : ""}
${s.check_seconds != null ? row("Checking the sheet before Create", "", dur(s.check_seconds), true) : ""}
</ul>
${modNames.map((m) => {
    const rs = modRecs(m), sp = span(rs);
    return `<div style="display:flex;flex-direction:column;gap:8px">
<div style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap"><div style="display:flex;gap:10px;align-items:center"><span class="mono rc-mono" aria-hidden="true">${esc(monoOf(m))}</span><span style="font-weight:800">${esc(m)}</span></div>${sp ? `<span class="mono" style="font-size:12.5px;font-weight:700">${esc(clockOf(sp.start))}–${esc(clockOf(sp.end))} · ${esc(dur(sp.sec))}</span>` : ""}</div>
${together(rs) ? `<div style="font-size:12.5px;color:var(--muted);font-weight:600">The ${rs.length} ${esc(rs[0].what)}s were created together in one go, so they share one time.</div>` : ""}
<ul class="sum-list">${rs.map((r) => r.seconds != null ? row(recName(r), `${clockOf(r.started)}–${clockOf(r.ended)}`, dur(r.seconds))
      : !r.started ? row(recName(r), "not sent (what it waited for wasn't ready)", null, true)
      : row(recName(r), `started ${clockOf(r.started)}, end not recorded`, null, true)).join("")}</ul>
</div>`;
  }).join("")}
</div>`;

  /* 4. Claude and repairs */
  const reps = s.repairs || [];
  const props = reps.filter((r) => r.kind === "proposal").length;
  const claude = `<div class="card sum-card">
<div class="label">Claude and repairs</div>
${reps.length ? `<div class="sum-tiles sum-tiles4">
${tile("Proposals", props, "var(--violet)")}
${tile("Repairs", reps.length - props)}
${tile("Tokens", s.repair_tokens != null ? thousands(s.repair_tokens) : "not recorded")}
${tile("Cost", money(s.repair_cost_usd), "var(--accent)")}
</div>
<ul class="sum-list">${reps.map((rp) => `<li class="sum-claude">
<span class="pill" style="${rp.kind === "proposal" ? "background:var(--glowB);color:var(--text);border:1px solid var(--violet)" : pillStyle("run")}">${rp.kind === "proposal" ? "Claude's proposal" : "Repair " + rp.attempt}</span>
<span style="flex:1 1 160px;min-width:0;font-weight:700;overflow-wrap:anywhere">for ${esc(rp.record || "the customer")}</span>
<span class="mono" style="font-size:12.5px;color:var(--muted);font-weight:700">${rp.tokens_total != null ? [`${thousands(rp.tokens_total)} tokens`, `${thousands(rp.tokens_new_input)} new`, `${thousands(rp.tokens_reread)} re-read`, `${thousands(rp.tokens_output)} written`].map((x) => `<span style="white-space:nowrap">${x}</span>`).join(" · ") : "tokens not recorded"}</span>
<span class="mono" style="font-size:13px;font-weight:700">${money(rp.cost_usd)}</span>
</li>`).join("")}</ul>
<div style="font-size:13px;font-weight:700">Total for repairs: ${s.repair_tokens != null ? thousands(s.repair_tokens) + " tokens, " : ""}${money(s.repair_cost_usd)}.</div>`
    : `<div style="font-size:14px;color:var(--muted);font-weight:600">Claude was not needed in this run (0 tokens, $0).</div>`}
${general.map((l) => `<div style="font-size:12.5px;color:var(--muted);font-weight:600;line-height:1.5">${esc(l)}</div>`).join("")}
</div>`;

  /* 5. Decisions and problems */
  const kv = (k, v, mono) => v == null || v === "" ? "" : `<span class="label" style="align-self:center">${esc(k)}</span><span class="${mono ? "mono" : ""}" style="font-weight:${mono ? 700 : 600};overflow-wrap:anywhere;${k === "Reason" ? "color:var(--muted)" : ""}">${esc(v)}</span>`;
  const decided = qs.map((q) => {
    const r = recs.find((x) => x.n === q.n) || {};
    const it = itemOf(q.n), sugg = (it.question || {}).suggestions || [];
    const outcome = q.state === "answered" ? (job ? (sugg.includes(q.answer) ? ["Suggestion used: " + q.answer, "good"] : ["Typed value: " + q.answer, "good"]) : ["Answered: " + q.answer, "good"])
      : q.state === "skipped" ? ["Skipped by you", "warn"]
      : q.state === "closed" ? ["Tried again, still not created" + (q.answer ? ` (last answer ${q.answer})` : ""), "bad"]
      : ["Waiting for your decision" + (q.answer ? ` (last answer ${q.answer})` : ""), "warn"];
    return { mod: modOf(r.what || it.what || "customer"), name: q.name, field: q.label || "a value", value: q.value, reason: q.reason || (it.question || {}).reason, outcome };
  });
  const problems = recs.filter((r) => r.state === "failed" && !qOf(r.n)).map((r) => {
    const it = itemOf(r.n);
    const saved = ["yes", "maybe"].includes(r.saved);
    return { mod: modOf(r.what || "customer"), name: recName(r), field: null, value: null,
      reason: it.text || (saved ? null : "Not created."), registry: r.registry_id,
      outcome: saved ? ["Saved, not fully checked", "warn"] : ["Not created", "bad"] };
  });
  const waiting = qs.filter((q) => ["open", "checking", "retrying"].includes(q.state)).length;
  const cards = [...decided, ...problems];
  const attention = `<div class="card sum-card">
<div class="label">Decisions and problems</div>
${cards.length ? `<div style="display:flex;flex-direction:column;gap:12px">${cards.map((c) => `<div class="sum-issue">
<div style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap"><div style="display:flex;gap:10px;align-items:center;min-width:0"><span class="mono rc-mono" aria-hidden="true">${esc(monoOf(c.mod))}</span><span style="font-weight:800;overflow-wrap:anywhere">${esc(c.name)}</span></div><span class="pill" style="${pillStyle(c.outcome[1])};white-space:normal">${esc(c.outcome[0])}</span></div>
<div class="sum-kv">${kv("Module", c.mod)}${kv("Field", c.field)}${kv("Value", c.value, true)}${kv("Registry ID", c.registry, true)}${kv("Reason", c.reason)}</div>
</div>`).join("")}</div>
${waiting ? `<div style="font-size:13px;font-weight:700;color:var(--warn)">Still waiting for a decision: ${waiting}. Everything else of this run is already done.</div>` : ""}`
    : `<div style="font-size:14px;color:var(--muted);font-weight:600">Nothing needed your attention</div>`}
</div>`;

  return `<section aria-label="Run summary" style="display:flex;flex-direction:column;gap:14px">
<div style="font-size:18px;font-weight:800">Run summary</div>
<div class="sum-grid">${overview}${byModule}${timeline}${claude}${attention}</div>
</section>`;
}

/* a run's summary on its own (also an older run, read from the logs): #/summary/<run> */
async function renderSummary(id) {
  setStage(3);
  const sv = await api("/api/summary/" + id);
  app.innerHTML = sv && sv.sections ? summaryHtml(sv) : `<section class="card">This run isn't in the page's records.</section>`;
}

function copyAsk(ask) {
  $("#copy").select(); navigator.clipboard.writeText(ask.copy).catch(() => document.execCommand("copy"));
  $("#copybtn").textContent = "Copied";
}

/* what Oracle shows now, as the folder's result lists it */
function createdHtml(created) {
  if (!created) return "";
  const nice = (k) => k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
  const flat = (v) => v === true ? "Yes" : v === false ? "No" : Array.isArray(v) ? v.map(flat).join("; ")
    : v && typeof v === "object" ? Object.entries(v).filter(([, x]) => x != null && x !== "").map(([k, x]) => `${nice(k)}: ${flat(x)}`).join(", ")
    : String(v);
  const rows = [];
  Object.entries(created).forEach(([k, v]) => {
    if (v == null || v === "") return;
    if (k === "values" && typeof v === "object") Object.entries(v).forEach(([a, b]) => rows.push([nice(a), flat(b)]));
    else rows.push([nice(k), flat(v)]);
  });
  if (!rows.length) return "";
  return `<details class="more"><summary>What Oracle shows now</summary><dl class="summary">
    ${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl></details>`;
}

boot();
