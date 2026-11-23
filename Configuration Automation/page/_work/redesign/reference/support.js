/* A small runtime for the approved mockup's component format (<x-dc>, {{holes}}, <sc-for>, <sc-if>, a DCLogic
   class), written only to render the reference mockup for comparison. Not part of the page. */
(function () {
  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(p) { Object.assign(this.state, typeof p === "function" ? p(this.state) : p); window.__dcRender && window.__dcRender(); }
  }
  window.DCLogic = DCLogic;
  const HOLE = /\{\{\s*([^}]+?)\s*\}\}/g;
  function get(scope, path) {
    path = path.trim();
    if (path === "true") return true;
    if (path === "false") return false;
    return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), scope);
  }
  function fill(text, scope) { return text.replace(HOLE, (_, p) => { const v = get(scope, p); return v == null ? "" : String(v); }); }
  function build(node, scope, out) {
    if (node.nodeType === 3) { out.appendChild(document.createTextNode(fill(node.nodeValue, scope))); return; }
    if (node.nodeType !== 1) return;
    const tag = node.tagName.toLowerCase();
    if (tag === "sc-for") {
      const m = /\{\{\s*(.+?)\s*\}\}/.exec(node.getAttribute("list") || "");
      const list = m ? get(scope, m[1]) || [] : [];
      const as = node.getAttribute("as");
      list.forEach((item) => { const s = Object.create(scope); s[as] = item; node.childNodes.forEach((c) => build(c, s, out)); });
      return;
    }
    if (tag === "sc-if") {
      const m = /\{\{\s*(.+?)\s*\}\}/.exec(node.getAttribute("value") || "");
      if (m && get(scope, m[1])) node.childNodes.forEach((c) => build(c, scope, out));
      return;
    }
    const el = node.namespaceURI === "http://www.w3.org/2000/svg"
      ? document.createElementNS(node.namespaceURI, node.tagName) : document.createElement(node.tagName);
    for (const a of node.attributes) {
      const name = a.name, raw = a.value;
      if (name.startsWith("hint-")) continue;
      const whole = /^\{\{\s*(.+?)\s*\}\}$/.exec(raw);
      if (/^on/i.test(name) && whole) {
        const fn = get(scope, whole[1]);
        const ev = name.slice(2).toLowerCase();
        if (typeof fn === "function") el.addEventListener(ev, fn);
        continue;
      }
      if (whole) {
        const v = get(scope, whole[1]);
        if (name === "disabled") { if (v) el.setAttribute("disabled", ""); continue; }
        if (name === "value") { el.value = v == null ? "" : v; el.setAttribute("value", v == null ? "" : v); continue; }
        el.setAttribute(name, v == null ? "" : String(v));
        continue;
      }
      el.setAttribute(name, fill(raw, scope));
    }
    node.childNodes.forEach((c) => build(c, scope, el));
    out.appendChild(el);
  }
  window.addEventListener("DOMContentLoaded", () => {
    const host = document.querySelector("x-dc");
    const script = document.querySelector("script[type='text/x-dc']");
    const tpl = new DOMParser().parseFromString("<body>" + host.innerHTML + "</body>", "text/html").body;
    const helmet = tpl.querySelector("helmet");
    if (helmet) { [...helmet.children].forEach((c) => document.head.appendChild(document.importNode(c, true))); helmet.remove(); }
    const props = {};
    const dp = JSON.parse(script.getAttribute("data-props") || "{}");
    Object.entries(dp).forEach(([k, v]) => { if (v && "default" in v) props[k] = v.default; });
    const q = new URLSearchParams(location.search);
    if (q.get("theme")) props.theme = q.get("theme");
    const Component = new Function("DCLogic", script.textContent + "\nreturn Component;")(DCLogic);
    const comp = new Component(props);
    host.innerHTML = "";
    const root = document.createElement("div");
    host.replaceWith(root);
    window.__dcRender = () => {
      const vals = comp.renderVals();
      const frag = document.createDocumentFragment();
      tpl.childNodes.forEach((c) => build(c, vals, frag));
      root.replaceChildren(frag);
    };
    window.__dcRender();
    if (comp.componentDidMount) comp.componentDidMount();
  });
})();
