/* Shared by index.html, story.html and technical.html.
   - Themes: night (default), dusk, light. Kept in this browser only (localStorage), on <html data-theme>.
   - Adds the moving background and the theme picker to the top bar.
   - Data helpers for story.html and technical.html: the same file as the dashboard
     (data/data.json when hosted, data/data.js = window.DASHBOARD_DATA when opened by double-click). */
(function(){
  "use strict";
  var THEMES = [
    {id:"night", name:"Night", sw:"linear-gradient(135deg,#0b1226 0%,#2f5bff 55%,#7a3cff 100%)"},
    {id:"dusk",  name:"Dusk",  sw:"linear-gradient(135deg,#1a0b22 0%,#ff3d7f 55%,#ff8a2b 100%)"},
    {id:"light", name:"Light", sw:"linear-gradient(135deg,#f6f5f2 0%,#cfe0ff 60%,#d9c8ff 100%)"}
  ];
  var root = document.documentElement;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function getTheme(){ var t = root.getAttribute("data-theme"); return (t === "dusk" || t === "light") ? t : "night"; }
  function setTheme(t){
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("fscr-theme", t); } catch (e) {}
    document.querySelectorAll(".thememenu button").forEach(function(b){ b.setAttribute("aria-checked", String(b.getAttribute("data-t") === t)); });
    var lbl = document.querySelector(".themepick .lbl"); if (lbl) lbl.textContent = THEMES.filter(function(x){ return x.id === t; })[0].name;
    try { window.dispatchEvent(new CustomEvent("fscr-theme", {detail:t})); } catch (e) {}
  }
  if (!root.getAttribute("data-theme")){
    var saved = null; try { saved = localStorage.getItem("fscr-theme"); } catch (e) {}
    root.setAttribute("data-theme", (saved === "dusk" || saved === "light") ? saved : "night");
  }

  function addBackground(){
    if (document.querySelector(".bg")) return;
    var bg = document.createElement("div");
    bg.className = "bg"; bg.setAttribute("aria-hidden", "true");
    bg.innerHTML = '<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div><div class="orb o4"></div><div class="grain"></div><canvas></canvas>';
    document.body.insertBefore(bg, document.body.firstChild);
    var cv = bg.querySelector("canvas"), cx = cv.getContext && cv.getContext("2d"); if (!cx) return;
    var COLS = {night:["143,192,255","183,155,255","92,240,190","255,198,77"],
                dusk:["255,150,190","255,180,110","201,168,255","255,214,140"],
                light:["42,120,214","123,79,224","27,175,122","217,119,63"]};
    var P = [], W = 0, H = 0, dpr = 1, lastDraw = 0;   // dots are tiny: normal resolution is enough
    function size(){ W = cv.clientWidth; H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr; cx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    size(); window.addEventListener("resize", size);
    var n = Math.round(Math.min(48, W * H / 26000));
    for (var i = 0; i < n; i++) P.push({x:Math.random()*W, y:Math.random()*H, r:Math.random()*1.6+.4, vx:(Math.random()-.5)*.18, vy:-(Math.random()*.25+.05), a:Math.random()*.5+.15, k:i % 4, ph:Math.random()*6});
    function draw(ts){
      if (!reduced){ requestAnimationFrame(draw); if (ts - lastDraw < 32) return; lastDraw = ts; }   // 30 frames a second
      var cols = COLS[getTheme()];
      cx.clearRect(0, 0, W, H);
      P.forEach(function(p){
        if (!reduced){ p.x += p.vx; p.y += p.vy; p.ph += .02; if (p.y < -5){ p.y = H + 5; p.x = Math.random()*W; } if (p.x < -5) p.x = W + 5; if (p.x > W + 5) p.x = -5; }
        cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, 6.283);
        cx.fillStyle = "rgba(" + cols[p.k] + "," + (p.a * (.7 + .3 * Math.sin(p.ph))).toFixed(3) + ")"; cx.fill();
      });
    }
    if (reduced) draw(0); else requestAnimationFrame(draw);
    if (reduced) window.addEventListener("fscr-theme", function(){ draw(0); });
  }

  function addPicker(){
    var ul = document.querySelector(".topnav ul"); if (!ul || ul.querySelector(".themeli")) return;
    var li = document.createElement("li"); li.className = "themeli";
    li.innerHTML = '<button class="themepick" type="button" aria-haspopup="true" aria-expanded="false" aria-label="Choose a colour theme">' +
      '<span class="dots3" aria-hidden="true"><i></i><i></i><i></i></span><span class="lbl"></span></button>' +
      '<div class="thememenu" role="menu" aria-label="Colour theme">' + THEMES.map(function(t){
        return '<button type="button" role="menuitemradio" data-t="' + t.id + '" aria-checked="false"><span class="sw3" style="background:' + t.sw + '"></span>' + t.name +
          '<svg class="tick" width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M2.5 7.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>';
      }).join("") + "</div>";
    ul.appendChild(li);
    var btn = li.querySelector(".themepick"), menu = li.querySelector(".thememenu");
    function open(on){ menu.classList.toggle("open", on); btn.setAttribute("aria-expanded", String(on)); }
    btn.addEventListener("click", function(e){ e.stopPropagation(); open(!menu.classList.contains("open")); if (menu.classList.contains("open")) menu.querySelector('[aria-checked="true"]').focus(); });
    menu.addEventListener("click", function(e){
      var b = e.target.closest("button[data-t]"); if (!b) return;
      e.stopPropagation(); setTheme(b.getAttribute("data-t")); open(false); btn.focus();
    });
    menu.addEventListener("keydown", function(e){
      var items = Array.prototype.slice.call(menu.querySelectorAll("button")), i = items.indexOf(document.activeElement);
      if (e.key === "ArrowDown"){ e.preventDefault(); e.stopPropagation(); items[(i + 1) % items.length].focus(); }
      if (e.key === "ArrowUp"){ e.preventDefault(); e.stopPropagation(); items[(i + items.length - 1) % items.length].focus(); }
      if (e.key === "Escape"){ e.stopPropagation(); open(false); btn.focus(); }
    });
    document.addEventListener("click", function(){ open(false); });
    setTheme(getTheme());
  }

  function fmt(n){ return (n == null) ? "–" : Number(n).toLocaleString("en-US"); }
  function pct(a, b){ return b ? Math.round(1000 * a / b) / 10 : 0; }
  function load(){
    if (location.protocol === "file:" && window.DASHBOARD_DATA) return Promise.resolve(window.DASHBOARD_DATA);
    return fetch("data/data.json", {cache:"no-store"})
      .then(function(r){ if (!r.ok) throw new Error("data"); return r.json(); })
      .catch(function(){ if (window.DASHBOARD_DATA) return window.DASHBOARD_DATA; throw new Error("no data"); });
  }
  function ease(t){ return 1 - Math.pow(1 - t, 3); }
  function countUp(el, from, to, ms){
    if (reduced || !ms){ el.textContent = fmt(to); return; }
    var t0 = null;
    function step(t){
      if (t0 === null) t0 = t;
      var p = Math.min(1, (t - t0) / ms);
      el.textContent = fmt(Math.round(from + (to - from) * ease(p)));
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = fmt(from);
    requestAnimationFrame(step);
  }
  function fill(rootEl, s){
    rootEl.querySelectorAll("[data-k]").forEach(function(el){
      var k = el.getAttribute("data-k");
      if (k in s) el.textContent = fmt(s[k]);
    });
  }
  function reveal(selector, cb, threshold){
    var els = Array.prototype.slice.call(document.querySelectorAll(selector));
    if (!("IntersectionObserver" in window)){ els.forEach(function(el){ el.classList.add("in"); if (cb) cb(el); }); return; }
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting && !e.target.classList.contains("in")){
          e.target.classList.add("in"); if (cb) cb(e.target); io.unobserve(e.target);
        }
      });
    }, {threshold: threshold == null ? 0.35 : threshold});
    els.forEach(function(el){ io.observe(el); });
  }
  function fail(){
    document.body.insertAdjacentHTML("beforeend",
      '<p style="position:fixed;bottom:12px;left:12px;right:12px;z-index:60;margin:0;padding:10px 14px;background:var(--card);border:1px solid var(--line);border-radius:10px;color:var(--err)">' +
      'Could not load the data. Run "python dashboard\\update.py" and keep the data folder next to this page.</p>');
  }
  window.FSCR = {reduced:reduced, fmt:fmt, pct:pct, load:load, countUp:countUp, fill:fill, reveal:reveal, fail:fail,
                 theme:getTheme, setTheme:setTheme};

  function boot(){ addBackground(); addPicker(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
