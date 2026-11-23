/* The page: setup checklist, then one thing: upload a filled-in sheet, check it, preview it,
   create it in Oracle, show progress and the result. Plain JavaScript, no outside libraries.
   Talks only to the local server. */
"use strict";

const app = document.getElementById("app");
const S = { env: null, testMode: false, timers: [], previews: {} };

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

/* ---------------------------------------------------------------- start */

async function boot() {
  const st = await api("/api/state");
  S.env = st.env; S.testMode = st.test_mode;
  const envEl = document.getElementById("env");
  if (st.env.name) {
    envEl.hidden = false;
    envEl.textContent = st.env.name;
    envEl.classList.toggle("prod", st.env.production);
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
window.addEventListener("hashchange", route);
document.getElementById("home-link").addEventListener("click", (e) => { e.preventDefault(); location.hash = "#/"; });

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
    const skip = s.skip ? `<button class="btn ghost" data-step="${s.key}" data-skip="1">${esc(s.skip)}</button>` : "";
    if (s.state === "waiting") {
      extra = `${s.how ? `<div class="how">${esc(s.how)}</div>` : ""}
        <div class="actions" style="margin-top:10px"><button class="btn" data-step="${s.key}"${s.retry ? ' data-retry="1"' : ""}>${esc(s.button || "Continue")}</button>${skip}</div>`;
    } else if (s.state === "failed" || s.state === "skipped") {
      extra = `<div class="actions" style="margin-top:10px"><button class="btn ghost" data-step="${s.key}" data-retry="1">Try again</button></div>`;
    } else if (skip) {
      extra = `<div class="actions" style="margin-top:10px">${skip}</div>`;
    }
    return `<li>${icon(s.state)}<div><div class="t">${esc(s.title)}</div>
      <div class="s">${esc(s.state === "pending" ? "Not checked yet" : s.text)}</div>${extra}</div></li>`;
  }).join("");
  app.innerHTML = `<h1>Let's set this up</h1>
    <p class="lead">A few one-time steps on this computer. Most run by themselves; for the
    others you'll see a button and short instructions.</p>
    <div class="panel"><ul class="steps">${items}</ul>
    ${data.complete ? `<div class="actions"><button class="btn" id="go-home">Everything is ready - start</button></div>` : ""}
    </div>`;
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

/* ---------------------------------------------------------------- upload */

function renderUpload(message) {
  app.innerHTML = `<h1>Upload your sheet</h1>
    <p class="lead">Fill in the sheet in Excel, save it and drop it here. The page reads it, checks it
    and shows you what Oracle will get. Nothing is sent to Oracle until you press Create.</p>
    <div class="panel">
      <label class="drop" id="drop" tabindex="0">
        <input type="file" id="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" hidden>
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
          stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <path d="M17 8l-5-5-5 5M12 3v12"/></svg>
        <div class="drop-t">Drop the filled-in sheet here</div>
        <div class="muted small">or <span class="linklike">choose a file</span> (Excel workbook, .xlsx)</div>
      </label>
      <div id="upload-state">${message ? `<div class="err-box">${esc(message)}</div>` : ""}</div>
      <div class="template-row">
        <div><strong>Need the sheet?</strong> <span class="muted">It has a tab for each kind of setup,
          with the required columns in yellow.</span></div>
        <a class="btn ghost" href="/api/sheet/template" download="Upload sheet.xlsx" id="template">Download the empty sheet</a>
      </div>
    </div>`;
  const drop = $("#drop"), input = $("#file");
  input.addEventListener("change", () => { if (input.files[0]) sendFile(input.files[0]); });
  drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
  ["dragenter", "dragover"].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add("on"); }));
  ["dragleave", "drop"].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove("on"); }));
  drop.addEventListener("drop", (e) => { const f = e.dataTransfer.files[0]; if (f) sendFile(f); });
}

async function sendFile(file) {
  if (!/\.xlsx$/i.test(file.name)) {
    $("#upload-state").innerHTML = `<div class="err-box">This isn't an Excel workbook (.xlsx). In Excel, use
      File &gt; Save As &gt; Excel Workbook, then upload that file.</div>`;
    return;
  }
  $("#drop").classList.add("busy");
  $("#upload-state").innerHTML = `<p class="checking"><span class="spinner"></span>&nbsp; Reading <strong>${esc(file.name)}</strong>
    and checking it with Oracle: its lists, the address places, and whether Oracle already has a customer
    with the same name. This takes about a minute. Nothing is created.</p>`;
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

/* ---------------------------------------------------------------- preview */

async function renderPreview(id) {
  const p = S.previews[id] || (S.previews[id] = await api("/api/sheet/" + id));
  if (p.error) { location.hash = "#/"; return; }
  if (p.signin === "waiting") {      // the sheet's checks with Oracle run once the user is signed in
    delete S.previews[id];
    later(() => { if (location.hash === "#/sheet/" + id) renderPreview(id); }, 3000);
  }
  if (p.job) { location.hash = "#/job/" + p.job; return; }      // already created from this upload
  const recs = p.records || [];
  const rec = recs[0];
  const what = recs.length === 1 ? "customer" : "customers";
  const bad = recs.filter((r) => !r.ok);
  const head = `<a class="back" href="#/">&larr; Upload another sheet</a>
    <h1>${recs.length > 1 ? `Your sheet: ${recs.length} customers` : esc(p.ok && rec ? rec.title : "Your sheet")}</h1>
    <p class="lead">${esc(p.file)}</p>`;
  /* the summary: how many, how many with problems, about 3 minutes per customer */
  const summary = recs.length ? `<div class="panel summary-panel"><div class="sum-row">
      <div><div class="sum-n">${recs.length}</div><div class="muted small">${what} in the sheet</div></div>
      <div><div class="sum-n ${bad.length ? "bad-t" : "ok-t"}">${bad.length}</div><div class="muted small">with problems</div></div>
      <div><div class="sum-n">~${recs.length * 3} min</div><div class="muted small">to create (about 3 minutes each)</div></div>
    </div></div>` : "";
  const stops = (p.stops || []).length ? `<div class="panel stop"><h2>This sheet can't be created yet</h2>
      <ul>${p.stops.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : "";
  const loose = p.sheet_problems || (recs.length ? [] : p.problems || []);
  const problems = loose.length ? `<div class="panel stop"><h2>${loose.length} thing${loose.length === 1 ? "" : "s"} to fix in the sheet</h2>
      ${fixList(loose)}<p class="muted small">Change these in Excel, save, and upload the sheet again.</p></div>` : "";
  const notes = (p.notes || []).length ? `<div class="notes">${p.notes.map((n) => `<div>${esc(n)}</div>`).join("")}</div>` : "";
  const ready = p.ok && rec && !p.signin;
  /* the Oracle sign-in is renewed here, before Create, so a run never stops to ask for it */
  const signin = p.signin === "waiting" ? `<div class="panel stop"><h2>Please sign in to Oracle</h2>
      <p><span class="spinner tiny"></span> Your saved Oracle sign-in has expired. A sign-in window has opened:
      sign in there; it closes by itself. Then the sheet is checked with Oracle and <strong>Create in Oracle</strong>
      becomes available. Nothing has been sent to Oracle.</p></div>`
    : p.signin === "failed" ? `<div class="panel stop"><h2>The Oracle sign-in didn't finish</h2>
      <p>The sheet can be created once you are signed in. Nothing has been sent to Oracle.</p>
      <div class="actions"><button class="btn" id="signin-again">Open the sign-in window again</button></div></div>` : "";
  /* the customers: those with problems first (open), then the others, each in sheet order */
  const order = [...bad, ...recs.filter((r) => r.ok)];
  const list = order.map((r) => customerHtml(r, !r.ok || recs.length === 1)).join("");
  app.innerHTML = `${head}${signin}${summary}${stops}${problems}${notes}${list}
    <div class="panel actions-panel">
      ${ready ? `<p style="margin:0 0 4px">Everything is checked. Press <strong>Create in Oracle</strong> to create
        ${recs.length > 1 ? `these ${recs.length} customers, one after another` : esc(rec.title.charAt(0).toLowerCase() + rec.title.slice(1))}.
        Nothing has been sent to Oracle yet.</p>`
        : `<p style="margin:0 0 4px">Nothing was sent to Oracle.${bad.length ? " Create is available once every customer is OK." : ""}</p>`}
      ${ready && p.test_mode ? `<label class="testswitch"><input type="checkbox" id="force"> Test: make this run fail once</label>` : ""}
      <div class="actions" style="margin-top:16px">
        ${ready ? `<button class="btn" id="create">Create in Oracle</button>` : ""}
        <button class="btn ghost" id="cancel">${ready ? "Cancel" : "Upload a corrected sheet"}</button>
      </div></div>`;
  $("#cancel").addEventListener("click", () => { location.hash = "#/"; });
  if ($("#signin-again")) $("#signin-again").addEventListener("click", async () => {
    await api("/api/sheet/" + id + "/signin", {}); delete S.previews[id]; renderPreview(id); });
  const btn = $("#create");
  if (btn) btn.addEventListener("click", async () => {
    btn.disabled = true; btn.textContent = "Starting ...";
    const r = await api("/api/sheet/create", { upload: id, force_failure: !!($("#force") && $("#force").checked) });
    if (r.id) { p.job = r.id; location.hash = "#/job/" + r.id; }
    else if (r.signin) { delete S.previews[id]; renderPreview(id); }
    else { btn.disabled = false; btn.textContent = "Create in Oracle";
      app.insertAdjacentHTML("beforeend", `<div class="err-box">This can't be started right now.</div>`); }
  });
}

function fixList(list) {
  return `<ul class="fixlist">${list.map((x) => `<li><span class="where-cell">${esc(x.tab)}${x.row ? `, row ${x.row}` : ""}${x.column ? `, ${esc(x.column)}` : ""}</span>
    ${esc(x.text)} <span class="fix">${esc(x.fix || "")}</span></li>`).join("")}</ul>`;
}

/* one customer of the sheet: name, OK / problems badge, and (opened) the full table */
function customerHtml(r, open) {
  const n = (r.problems || []).length;
  return `<details class="cust" ${open ? "open" : ""}><summary>
      <span class="cust-name">${esc(r.title)}</span>
      <span class="badge ${n ? "bad" : "ok"}">${n ? `${n} problem${n === 1 ? "" : "s"}` : "OK"}</span>
      <span class="muted small">${esc(r.tab)}, row ${r.row}</span></summary>
    ${n ? `<div class="cust-fix">${fixList(r.problems)}</div>` : ""}
    ${r.same_name ? `<div class="notes same-name"><strong>Same name in Oracle:</strong> ${esc(r.same_name)}</div>` : ""}
    ${recordHtml(r, false)}</details>`;
}

function recordHtml(r, many) {
  let section = null;
  const rows = r.fields.map((f) => {
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
  const ch = r.children || {};
  const kids = (ch.rows || []).length ? `<h3>${esc(ch.title)}</h3>
    <div class="scroll"><table class="grid small-t"><thead><tr><th>Row</th>${ch.columns.map((c) =>
      `<th class="${c.required ? "req" : ""}">${esc(c.label)}</th>`).join("")}</tr></thead><tbody>
    ${ch.rows.map((k) => `<tr class="${k.cells.some((c) => c.problem) ? "bad" : ""}"><td>${k.row}</td>${k.cells.map((c) => {
      const changed = !c.problem && c.oracle && c.sheet != null && c.oracle !== c.sheet && c.oracle !== "(only links the rows)";
      return `<td>${c.problem ? `<span class="bad-t">${esc(c.sheet ?? "empty")}</span>`
        : c.sheet == null ? `<span class="muted">${esc(c.oracle)}</span>`
        : esc(c.sheet) + (changed ? `<div class="muted small">Oracle gets: ${esc(c.oracle)}</div>` : "")}
        ${c.note && !c.problem ? `<div class="note-t">${esc(c.note)}</div>` : ""}</td>`;
    }).join("")}</tr>
    ${k.cells.filter((c) => c.problem).map((c) => `<tr class="bad fixrow"><td></td><td colspan="${ch.columns.length}">
      <span class="bad-t">${esc(c.problem)}</span> <span class="fix">${esc(c.fix || "")}</span></td></tr>`).join("")}`).join("")}
    </tbody></table></div>` : ch.title ? `<h3>${esc(ch.title)}</h3><p class="muted small">None in the sheet for this one.</p>` : "";
  return `<div class="panel preview">
    ${many ? `<h2 style="margin-top:0">${esc(r.title)} <span class="muted small">(${esc(r.tab)}, row ${r.row})</span></h2>` : ""}
    <div class="scroll"><table class="grid">
      <thead><tr><th>Field</th><th>What the sheet says</th><th>What Oracle will get</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
    ${kids}</div>`;
}

/* ---------------------------------------------------------------- progress and result */

async function renderJob(id) {
  const job = await api("/api/job/" + id);
  if (job.error) { location.hash = "#/"; return; }
  const head = `<a class="back" href="#/">&larr; Upload another sheet</a><h1>${esc(job.title || "Your request")}</h1>`;
  const back = job.upload ? `<a class="btn ghost" href="#/" style="text-decoration:none">Upload a corrected sheet</a>` : "";
  const st = job.state;
  if (job.items) return renderBatch(id, job, head);
  if (["queued", "running", "repairing", "signing"].includes(st)) {
    const text = st === "queued" ? (job.ahead ? "Waiting for the task before yours to finish" : "Starting")
      : job.text || "Working";
    const pct = Math.max(2, Math.min(99, job.percent || 0));
    app.innerHTML = `${head}<div class="panel">
      <div class="step-now">${st === "signing" ? "" : '<span class="spinner"></span>&nbsp; '}${esc(text)}</div>
      <div class="bar"><span style="width:${pct}%"></span></div>
      <div class="pct">About ${pct}% done${st === "repairing" ? " - a small problem came up and is being fixed; this can take a few minutes" : ""}</div>
      ${(job.done_lines || []).length ? `<ul class="steps-done">${job.done_lines.map((s) => `<li>✓ ${esc(s)}</li>`).join("")}</ul>` : ""}
      ${st === "signing" ? `<p class="muted">The window closes by itself when you reach the Oracle home page. The task then continues where it stopped.</p>` : ""}
      </div>`;
    later(() => renderJob(id), 1000);
    return;
  }
  if (st === "done") {
    const res = job.result || {};
    app.innerHTML = `${head}<div class="panel result">
      <div class="big ${res.partial ? "note" : "ok"}">${res.partial ? "!" : "✓"}</div>
      <h2 style="margin-top:0">${res.partial ? "Done, with one note" : res.skipped ? "Already there" : "Done"}</h2>
      <p>${esc(res.text)}</p>
      ${(res.steps || []).length ? `<ul class="steps-done">${res.steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>` : ""}
      ${res.repaired ? `<p class="muted small">A small problem came up on the way and was fixed automatically.</p>` : ""}
      ${res.where ? `<div class="where"><strong>Where to look:</strong> ${esc(res.where)}</div>` : ""}
      ${createdHtml(res.created)}
      <div class="actions"><a class="btn" href="#/" style="text-decoration:none">Upload another sheet</a></div></div>`;
    return;
  }
  const ask = job.ask || {};
  if (st === "needs_user" && ask.kind === "sign_in") {
    app.innerHTML = `${head}<div class="panel result"><div class="big ask">!</div>
      <h2 style="margin-top:0">Please sign in to Oracle</h2><p>${esc(ask.text)}</p>
      <div class="actions"><button class="btn" id="signin">Sign in to Oracle</button></div>
      <p class="muted small">A browser window opens; sign in there yourself. Nothing is created twice.</p></div>`;
    $("#signin").addEventListener("click", async () => { await api(`/api/job/${id}/signin`, {}); renderJob(id); });
    return;
  }
  if (st === "needs_user" && ask.kind === "value") {
    app.innerHTML = `${head}<div class="panel result"><div class="big ask">!</div>
      <h2 style="margin-top:0">Please change a value in the sheet</h2><p>${esc(ask.text)}</p>
      ${(ask.problems || []).filter((p) => p.valid && p.valid.length).map((p) => `<div class="valid"><strong>${esc(p.text)}</strong><br>You can pick: ${p.valid.slice(0, 60).map(esc).join(", ")}${p.valid.length > 60 ? " ..." : ""}</div>`).join("")}
      <p class="muted small">Nothing was created. Change the value in Excel, save, and upload the sheet again.</p>
      <div class="actions">${back || `<a class="btn ghost" href="#/" style="text-decoration:none">Upload a corrected sheet</a>`}</div></div>`;
    return;
  }
  if (ask.kind === "claude") {
    const c = (await api("/api/state")).claude || {};
    app.innerHTML = `${head}<div class="panel result"><div class="big ask">!</div>
      <h2 style="margin-top:0">One more step to fix this</h2><p>${esc(ask.text)}</p>
      ${c.signing_in ? `<p><span class="spinner tiny"></span> Waiting for you to sign in to Claude. Claude's
        sign-in page is open in your browser; the fix starts by itself when you are signed in.</p>`
        : `<div class="actions"><button class="btn" id="claude-fix">Sign in to Claude and fix it</button></div>
           <p class="muted small">Claude's sign-in page opens in your browser. Sign in with your own account;
           nothing else to press here.</p>`}
      <details class="more"><summary>Or do it yourself in Claude</summary>
        <textarea class="copybox" id="copy" readonly>${esc(ask.copy || "")}</textarea>
        <div class="actions"><button class="btn ghost" id="copybtn">Copy the message</button></div></details></div>`;
    if ($("#claude-fix")) $("#claude-fix").addEventListener("click", async () => { await claudeSignin(id); renderJob(id); });
    if ($("#copybtn")) $("#copybtn").addEventListener("click", () => copyAsk(ask));
    later(() => renderJob(id), 3000);               // the fix starts by itself after the sign-in
    return;
  }
  app.innerHTML = `${head}<div class="panel result"><div class="big bad">×</div>
    <h2 style="margin-top:0">This didn't work</h2><p>${esc(ask.text || (job.result || {}).text || "Something went wrong.")}</p>
    ${ask.todo ? `<p><strong>What to do:</strong> ${esc(ask.todo)}</p>` : ""}
    ${ask.copy ? `<textarea class="copybox" id="copy" readonly>${esc(ask.copy)}</textarea>
      <div class="actions"><button class="btn ghost" id="copybtn">Copy the message</button></div>` : ""}
    <div class="actions"><a class="btn" href="#/" style="text-decoration:none">Back to the upload</a></div></div>`;
  if ($("#copybtn")) $("#copybtn").addEventListener("click", () => copyAsk(ask));
}

/* a sheet run: its customers one after another, then one card per customer */
function renderBatch(id, job, head) {
  const items = job.items, st = job.state;
  const badge = (it) => it.state === "done" ? `<span class="badge ok">Created</span>`
    : it.state === "failed" ? `<span class="badge bad">Failed</span>`
    : it.state === "running" ? `<span class="badge wait">Working</span>` : `<span class="muted small">Waiting</span>`;
  if (["queued", "running"].includes(st)) {
    const pct = Math.max(2, Math.min(99, job.percent || 0));
    const text = st === "queued" ? (job.ahead ? "Waiting for the task before yours to finish" : "Starting") : job.text || "Working";
    app.innerHTML = `${head}<div class="panel">
      <div class="step-now"><span class="spinner"></span>&nbsp; ${esc(text)}</div>
      ${job.sub_text ? `<div class="muted" style="margin-top:6px">${esc(job.sub_text)}</div>` : ""}
      <div class="bar"><span style="width:${pct}%"></span></div>
      <div class="pct">About ${pct}% done${job.repairing ? " - a small problem came up and is being fixed; this can take a few minutes" : ""}</div>
      <ul class="steps-done">${items.map((it) => `<li>${badge(it)} ${esc(it.name)}</li>`).join("")}</ul></div>`;
    later(() => renderJob(id), 1500);
    return;
  }
  const failed = items.filter((it) => it.state === "failed");
  const savedFailed = failed.filter((it) => it.saved !== "no");
  const card = (it) => {
    if (it.state === "done") {
      const rid = (it.created || {}).registry_id;
      return `<details class="cust" open><summary><span class="cust-name">${esc(it.name)}</span>${badge(it)}
        ${rid ? `<span class="muted small">Registry ID ${esc(rid)}</span>` : ""}</summary><div class="cust-result">
        <p>${esc(it.text || "")}</p>${it.repaired ? `<p class="muted small">A small problem came up on the way and was fixed automatically.</p>` : ""}
        ${it.where ? `<div class="where"><strong>Where to look:</strong> ${esc(it.where)}</div>` : ""}${createdHtml(it.created)}</div></details>`;
    }
    const saved = it.saved === "yes" ? `Saved in Oracle with Registry ID ${esc(it.registry_id || "?")}, but not checked to the end.`
      : it.saved === "maybe" ? `It may have been saved in Oracle${it.registry_id ? ` (Registry ID ${esc(it.registry_id)} if it was)` : ""}.`
      : "Nothing was saved in Oracle.";
    return `<details class="cust" open><summary><span class="cust-name">${esc(it.name)}</span>${badge(it)}</summary>
      <div class="cust-result"><p>${esc(it.text || "It didn't work.")}</p>
      ${(it.text || "").includes(saved) ? "" : `<p><strong>${saved}</strong></p>`}
      ${it.todo ? `<p><strong>What to do:</strong> ${esc(it.todo)}</p>` : ""}</div></details>`;
  };
  app.innerHTML = `${head}<div class="panel summary-panel"><div class="sum-row">
      <div><div class="sum-n ${failed.length ? "" : "ok-t"}">${job.created} of ${job.total}</div><div class="muted small">created</div></div>
      ${failed.length ? `<div><div class="sum-n bad-t">${failed.length}</div><div class="muted small">failed</div></div>` : ""}</div>
      ${job.failed_sheet ? `<div class="actions" style="margin-top:14px"><a class="btn" href="/api/job/${id}/failed.xlsx" download="Failed customers.xlsx"
        style="text-decoration:none">Download a sheet with only the failed customers</a></div>
        <p class="muted small">It holds the failed customers that saved nothing, with their purposes. Fix them in Excel and upload that sheet.</p>` : ""}
      ${savedFailed.length ? `<div class="notes"><strong>Saved but not checked to the end (not in that sheet):</strong>
        ${savedFailed.map((it) => `${esc(it.name)}${it.registry_id ? ` (Registry ID ${esc(it.registry_id)})` : ""}`).join(", ")}.
        Uploading the same rows again (same values, within 12 hours, on this PC) checks them without creating them twice.</div>` : ""}</div>
    ${[...failed, ...items.filter((it) => it.state !== "failed")].map(card).join("")}
    ${summaryHtml(job.summary)}
    <div class="actions" style="margin-top:20px"><a class="btn ghost" href="#/" style="text-decoration:none">Upload another sheet</a></div>`;
}

/* the "Run summary": plain sentences the server builds from what the page logged (run_summary.py) */
function summaryHtml(sv) {
  if (!sv || !sv.sections) return "";
  return `<div class="panel run-summary"><h2 style="margin-top:0">Run summary</h2>
    ${sv.sections.map((sec) => `${sec.heading ? `<h3>${esc(sec.heading)}</h3>` : ""}
      <ul class="${sec.heading ? "" : "plain"}">${sec.lines.map((l) => `<li>${esc(l)}</li>`).join("")}</ul>`).join("")}</div>`;
}

/* a run's summary on its own (also an older run, read from the logs): #/summary/<run> */
async function renderSummary(id) {
  const sv = await api("/api/summary/" + id);
  app.innerHTML = `<a class="back" href="#/">&larr; Upload another sheet</a><h1>Run summary</h1>
    ${sv && sv.sections ? summaryHtml(sv) : `<div class="panel">This run isn't in the page's records.</div>`}`;
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
