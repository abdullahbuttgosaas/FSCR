"""Claude's command-line tool (used only for automatic fixes): find it, check what this PC
allows, and install it for the current user WITHOUT administrator rights. Optional: setup
never depends on it. Standard library only. Never asks for or types a password, never
starts anything that shows an approval pop-up, prints no secret values, touches nothing in
Oracle.

  python common/claude_tool.py --find         # where it is and its version (one JSON line)
  python common/claude_tool.py --diagnose     # what this PC allows (JSON)
  python common/claude_tool.py --install      # try the routes in order until one works
  python common/claude_tool.py --install --simulate-blocked   # test: every route refused

Install routes, in this order (the first that works wins; nothing is done when the tool is
already there):
  existing    npm install -g, as before (works where npm's own folder is writable, e.g. a
              Windows PC with Node.js from the official installer, or any admin PC)
  standalone  Anthropic's own per-user installer, the same steps as claude.ai/install.ps1 /
              install.sh: version and checksum from downloads.claude.ai, then `claude install`
              (needs no Node.js; puts the tool in ~/.local/bin)
  portable    the official Node.js zip / tarball from nodejs.org (checksum checked), unpacked
              into the tools folder, then the tool installed through it with npm --prefix
  npm_prefix  the Node.js already on this PC, npm install -g --prefix <tools folder>
Tools folder: %LOCALAPPDATA%\\ConfigAutomation\\tools on Windows, ~/.local/share/ConfigAutomation/tools
elsewhere; page/_work/tools when that can't be written; CONFIG_AUTOMATION_TOOLS overrides it.
It is never added to the PATH of the system or the user: add_to_path() adds it to the PATH
of the calling process only (the page's own processes).
CONFIG_AUTOMATION_SIMULATE_BLOCKED=1 makes find() see nothing and every route refuse (tests).
"""
import argparse
import glob
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import ssl
import stat
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIN = sys.platform == "win32"
PACKAGE = "@anthropic-ai/claude-code"
CLAUDE_BASE = "https://downloads.claude.ai/claude-code-releases"
NODE_BASE = "https://nodejs.org/dist"
NPM_PING = "https://registry.npmjs.org/-/ping"
EXE_BLOCKED = {1260: "Windows blocks programs in your user folder (company policy)",
               4551: "Windows blocks programs in your user folder (application control policy)",
               5: "Windows refused to start a program from your user folder (access denied)",
               225: "the virus scanner blocked the program"}


def simulated():
    return os.environ.get("CONFIG_AUTOMATION_SIMULATE_BLOCKED") == "1"


# ---------------------------------------------------------------- folders

def _writable(d, create=True):
    """Can files be written in d? Without create, a missing d is judged by its nearest
    existing parent (nothing is left behind)."""
    try:
        d = Path(d)
        if create:
            d.mkdir(parents=True, exist_ok=True)
        else:
            while not d.exists() and d.parent != d:
                d = d.parent
        probe = d / f".write_probe_{os.getpid()}"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def tools_dir(create=False):
    """The per-user tools folder (see the module text)."""
    if os.environ.get("CONFIG_AUTOMATION_TOOLS"):
        cands = [Path(os.environ["CONFIG_AUTOMATION_TOOLS"])]
    elif WIN:
        cands = [Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "ConfigAutomation" / "tools"]
    else:
        cands = [Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "ConfigAutomation" / "tools"]
    cands.append(ROOT / "page" / "_work" / "tools")
    for c in cands:
        if c.exists() or (create and _writable(c)):
            return c
    return cands[0]


def _long(p):
    """A Windows path that may be longer than 260 characters (\\\\?\\ prefix)."""
    p = str(Path(p).resolve())
    return "\\\\?\\" + p if WIN and not p.startswith("\\\\") else p


def node_dir():
    return tools_dir() / "node"


def node_exe():
    """Node.js on the PATH, else the portable one in the tools folder."""
    found = shutil.which("node")
    if found:
        return found
    p = node_dir() / ("node.exe" if WIN else "bin/node")
    return str(p) if p.exists() else None


def prefix_dir():
    return tools_dir() / "npm"


def path_dirs():
    """Folders the page adds to its own PATH: the tools folder's Node.js and npm prefix, and
    where Anthropic's installer puts the tool."""
    t = tools_dir()
    if WIN:
        dirs = [t / "node", t / "npm", Path.home() / ".local" / "bin"]
    else:
        dirs = [t / "node" / "bin", t / "npm" / "bin", Path.home() / ".local" / "bin"]
    return [str(d) for d in dirs if d.exists()]


def add_to_path(environ=None):
    """Add path_dirs() to this process's PATH (or the given environment); returns it."""
    environ = os.environ if environ is None else environ
    parts = environ.get("PATH", "").split(os.pathsep)
    for d in reversed(path_dirs()):
        if d not in parts:
            parts.insert(0, d)
    environ["PATH"] = os.pathsep.join(p for p in parts if p)
    return environ


# ---------------------------------------------------------------- find and run

def candidates():
    t = tools_dir()
    home_bin = Path.home() / ".local" / "bin"
    out = []
    for name in ("claude", "claude.exe", "claude.cmd"):
        p = shutil.which(name)
        if p:
            out.append(p)
    if WIN:
        out += [Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd", home_bin / "claude.exe",
                t / "npm" / "claude.cmd", t / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"]
    else:
        out += [home_bin / "claude", t / "npm" / "bin" / "claude"]
    seen, res = set(), []
    for p in out:
        s = str(p)
        if s.lower() not in seen and Path(s).exists():
            seen.add(s.lower())
            res.append(s)
    return res


def find_path():
    """The first place the tool is found, or None."""
    if simulated():
        return None
    c = candidates()
    return c[0] if c else None


def command(cli):
    """How to run the tool. For an npm install (claude.cmd) the real program is called
    directly, so long arguments are not mangled by cmd.exe."""
    if cli.lower().endswith(".cmd"):
        base = Path(cli).parent / "node_modules" / "@anthropic-ai" / "claude-code"
        for exe in (base / "bin" / "claude.exe", base / "claude.exe"):
            if exe.exists():
                return [str(exe)]
        node = node_exe()
        for js in (base / "cli.js", base / "cli-wrapper.cjs"):
            if js.exists() and node:
                return [node, str(js)]
    return [cli]


def version(cli=None, timeout=60):
    """(version text or None, plain reason when it didn't start)."""
    cli = cli or find_path()
    if not cli:
        return None, "not installed"
    try:
        p = subprocess.run(command(cli) + ["--version"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=ROOT, env=add_to_path(dict(os.environ)),
                           stdin=subprocess.DEVNULL)
    except OSError as e:
        return None, _exec_reason(e)
    except subprocess.TimeoutExpired:
        return None, f"it didn't answer within {timeout} seconds"
    m = re.search(r"\d+\.\d+\.\d+\S*", p.stdout or "")
    if p.returncode == 0 and m:
        return p.stdout.strip().splitlines()[0], ""
    return None, f"it stopped with exit code {p.returncode}: {(p.stderr or p.stdout).strip()[-200:]}"


def find():
    """{"found", "path", "command", "version", "reason"}."""
    cli = find_path()
    if not cli:
        return {"found": False, "path": None, "version": None,
                "reason": "simulated: not found" if simulated() else "not installed"}
    v, why = version(cli)
    return {"found": bool(v), "path": cli, "command": command(cli), "version": v, "reason": why}


# ---------------------------------------------------------------- plain reasons

def _exec_reason(e):
    code = getattr(e, "winerror", None)
    if code in EXE_BLOCKED:
        return EXE_BLOCKED[code]
    if isinstance(e, PermissionError):
        return "this computer doesn't allow starting programs from that folder"
    return f"the program couldn't start ({type(e).__name__}: {e})"


def _net_reason(url, e):
    host = url.split("/")[2]
    r = getattr(e, "reason", e)
    if isinstance(e, urllib.error.HTTPError):
        if e.code == 407:
            return f"the company proxy wants a separate sign-in for {host} (HTTP 407)"
        if e.code in (401, 403, 451):
            return f"the network refused downloads from {host} (HTTP {e.code})"
        return f"{host} answered HTTP {e.code}"
    if isinstance(r, ssl.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in str(r):
        return f"the secure connection to {host} was refused (a company proxy may be checking downloads)"
    if isinstance(r, socket.gaierror):
        return f"{host} can't be found (no internet, or the company network blocks it)"
    if isinstance(r, (TimeoutError, socket.timeout)):
        return f"{host} didn't answer in time"
    if isinstance(r, ConnectionError):
        return f"the connection to {host} was cut off (the network may block it)"
    return f"{host} can't be reached ({type(r).__name__}: {r})"


class Refused(Exception):
    """A route can't be used here; the text is plain words."""


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "ConfigAutomation-setup"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
            return r.read()
    except (urllib.error.URLError, OSError) as e:
        raise Refused(_net_reason(url, e)) from e


def _download(url, dest, sha256, timeout=1800):
    """Stream url to dest and check its SHA-256; a wrong checksum deletes the file."""
    req = urllib.request.Request(url, headers={"User-Agent": "ConfigAutomation-setup"})
    h = hashlib.sha256()
    started = time.time()
    try:
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(req, timeout=120, context=ssl.create_default_context()) as r, \
                open(dest, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                h.update(chunk)
                if time.time() - started > timeout:
                    raise Refused(f"the download from {url.split('/')[2]} took longer than {timeout // 60} minutes")
    except Refused:
        Path(dest).unlink(missing_ok=True)
        raise
    except (urllib.error.URLError, OSError) as e:
        Path(dest).unlink(missing_ok=True)
        if getattr(e, "errno", None) == 28:
            raise Refused("the disk is full") from e
        if isinstance(e, PermissionError):
            raise Refused(f"the folder {Path(dest).parent} can't be written to") from e
        raise Refused(_net_reason(url, e)) from e
    if h.hexdigest().lower() != sha256.lower():
        Path(dest).unlink(missing_ok=True)
        raise Refused("the downloaded file didn't match its published checksum (it may have been changed "
                      "on the way, e.g. by a company proxy), so it was deleted")


def _npm_reason(out):
    t = out or ""
    if re.search(r"EACCES|EPERM", t):
        return "npm's own install folder needs administrator rights"
    if re.search(r"SELF_SIGNED|UNABLE_TO_GET_ISSUER|UNABLE_TO_VERIFY|CERT_", t):
        return "a company proxy blocks the npm download site (certificate check)"
    if re.search(r"ENOTFOUND|ETIMEDOUT|ECONNRESET|ECONNREFUSED|EAI_AGAIN", t):
        return "the npm download site (registry.npmjs.org) can't be reached"
    if re.search(r"E403|E401|407", t):
        return "the network refused the npm download site"
    if "ENOSPC" in t:
        return "the disk is full"
    if "ENAMETOOLONG" in t:
        return "a file path became too long for Windows"
    last = [l for l in t.strip().splitlines() if l.strip()][-1:] or ["no output"]
    return f"npm stopped: {last[0][:200]}"


def _run(cmd, timeout, env=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, cwd=ROOT, env=env, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        raise Refused(f"it didn't finish within {timeout // 60} minutes")
    except OSError as e:
        raise Refused(_exec_reason(e)) from e


# ---------------------------------------------------------------- routes

def _platform_key():
    m = platform.machine().lower()
    arch = "arm64" if m in ("arm64", "aarch64") or os.environ.get("PROCESSOR_ARCHITECTURE") == "ARM64" else "x64"
    if WIN:
        return f"win32-{arch}"
    if sys.platform == "darwin":
        return f"darwin-{arch}"
    musl = bool(glob.glob("/lib/ld-musl-*"))
    return f"linux-{arch}" + ("-musl" if musl else "")


def route_existing():
    """As before: npm install -g into npm's own folder."""
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        raise Refused("Node.js isn't installed on this computer")
    code, out = _run([npm, "install", "-g", PACKAGE], 900)
    if code != 0:
        raise Refused(_npm_reason(out))


def route_standalone():
    """Anthropic's own per-user installer (the steps of claude.ai/install.ps1 / install.sh)."""
    key = _platform_key()
    if WIN and not platform.machine().endswith("64"):
        raise Refused("Claude's tool needs 64-bit Windows")
    ver = _get(f"{CLAUDE_BASE}/latest").decode("utf-8", "replace").strip()
    if not re.match(r"^\d+\.\d+\.\d+", ver):
        raise Refused("downloads.claude.ai didn't give a version (the service may not be available "
                      "in this region or on this network)")
    manifest = json.loads(_get(f"{CLAUDE_BASE}/{ver}/manifest.json"))
    info = (manifest.get("platforms") or {}).get(key)
    if not info or not info.get("checksum"):
        raise Refused(f"there is no standalone version for this kind of computer ({key})")
    binary = info.get("binary") or ("claude.exe" if WIN else "claude")
    dest = tools_dir(create=True) / "downloads" / f"claude-{ver}-{key}{'.exe' if WIN else ''}"
    try:
        _download(f"{CLAUDE_BASE}/{ver}/{key}/{binary}", dest, info["checksum"])
        if not WIN:
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR)
        code, out = _run([str(dest), "install", "latest"], 900)
        if code != 0:
            raise Refused(f"Anthropic's installer stopped (exit code {code}): {out.strip()[-200:]}")
    finally:
        for _ in range(5):                  # the file may still be in use for a moment
            try:
                dest.unlink(missing_ok=True)
                break
            except OSError:
                time.sleep(1)


def _npm_prefix_install(node, npm_cli):
    """npm install -g --prefix <tools>/npm with the given Node.js; its folder goes on the PATH
    of the install (the package's own setup step runs node)."""
    prefix = prefix_dir()
    prefix.mkdir(parents=True, exist_ok=True)
    env = add_to_path(dict(os.environ))
    env["PATH"] = str(Path(node).parent) + os.pathsep + env["PATH"]
    cmd = ([node, str(npm_cli)] if npm_cli else [shutil.which("npm") or "npm"]) + \
        ["install", "-g", "--prefix", str(prefix), PACKAGE]
    code, out = _run(cmd, 900, env)
    if code != 0:
        raise Refused(_npm_reason(out))


def route_portable():
    """The official Node.js zip/tarball into the tools folder, then npm with a per-user prefix."""
    releases = json.loads(_get(f"{NODE_BASE}/index.json"))
    lts = next((r for r in releases if r.get("lts")), None)
    if not lts:
        raise Refused("nodejs.org didn't list a long-term-support version")
    v = lts["version"]
    arch = "arm64" if _platform_key().split("-")[1] == "arm64" else "x64"
    if WIN:
        name, kind = f"node-{v}-win-{arch}.zip", "zip"
    elif sys.platform == "darwin":
        name, kind = f"node-{v}-darwin-{arch}.tar.gz", "tar"
    else:
        name, kind = f"node-{v}-linux-{arch}.tar.gz", "tar"
    sums = _get(f"{NODE_BASE}/{v}/SHASUMS256.txt").decode("utf-8", "replace")
    m = re.search(r"^([0-9a-f]{64})\s+" + re.escape(name) + r"$", sums, re.M)
    if not m:
        raise Refused(f"nodejs.org has no {name} for this computer")
    tools = tools_dir(create=True)
    arc = tools / "downloads" / name
    _download(f"{NODE_BASE}/{v}/{name}", arc, m.group(1))
    tmp = tools / "node.unpacking"
    shutil.rmtree(_long(tmp), ignore_errors=True)
    try:
        if kind == "zip":
            with zipfile.ZipFile(arc) as z:
                z.extractall(_long(tmp))           # long-path safe on Windows
        else:
            with tarfile.open(arc) as t:
                t.extractall(tmp, filter="tar")    # keeps Node's own links and file modes
    except OSError as e:
        raise Refused("the disk is full" if getattr(e, "errno", None) == 28 else
                      f"Node.js couldn't be unpacked into {tools} ({type(e).__name__}: {e})") from e
    finally:
        arc.unlink(missing_ok=True)
    inner = next(tmp.iterdir())
    shutil.rmtree(_long(node_dir()), ignore_errors=True)
    os.replace(_long(inner), _long(node_dir()))
    shutil.rmtree(_long(tmp), ignore_errors=True)
    node = node_dir() / ("node.exe" if WIN else "bin/node")
    code, out = _run([str(node), "--version"], 60)
    if code != 0:
        raise Refused(f"the portable Node.js didn't start: {out.strip()[-200:]}")
    npm_cli = node_dir() / ("node_modules/npm/bin/npm-cli.js" if WIN else "lib/node_modules/npm/bin/npm-cli.js")
    _npm_prefix_install(str(node), npm_cli)


def route_npm_prefix():
    """The Node.js already on this PC, with a per-user npm prefix in the tools folder."""
    node = shutil.which("node")
    if not node or not (shutil.which("npm") or shutil.which("npm.cmd")):
        raise Refused("Node.js isn't installed on this computer")
    _npm_prefix_install(node, None)


ROUTES = [
    ("existing", "npm's usual install, as before", route_existing),
    ("standalone", "Anthropic's own installer for your user only (no Node.js needed)", route_standalone),
    ("portable", "a portable Node.js in your user folder, then npm for your user only", route_portable),
    ("npm_prefix", "the Node.js already on this computer, npm for your user only", route_npm_prefix),
]
SIMULATED = {"existing": "Node.js isn't installed on this computer (simulated)",
             "standalone": "the network refused downloads from downloads.claude.ai (HTTP 403) (simulated)",
             "portable": "Windows blocks programs in your user folder (company policy) (simulated)",
             "npm_prefix": "Node.js isn't installed on this computer (simulated)"}


def install(log=print, simulate_blocked=None):
    """Try the routes in order until the tool starts and prints its version.
    Returns {"ok", "route", "route_text", "path", "version", "routes": [...], "reason"}."""
    simulate_blocked = simulated() if simulate_blocked is None else simulate_blocked
    found = None if simulate_blocked else find()
    if found and found["found"]:
        return {"ok": True, "route": "already", "route_text": "already installed", "path": found["path"],
                "version": found["version"], "routes": [], "reason": ""}
    tried = []
    for key, text, fn in ROUTES:
        started = time.time()
        if simulate_blocked:
            tried.append({"route": key, "text": text, "ok": False, "reason": SIMULATED[key], "seconds": 0})
            log(f"claude tool route {key}: refused - {SIMULATED[key]}")
            continue
        log(f"claude tool route {key}: trying ({text})")
        try:
            fn()
            add_to_path()
            res = find()
            ok, reason = res["found"], ("" if res["found"] else f"installed, but it doesn't start: {res['reason']}")
        except Refused as e:
            ok, reason, res = False, str(e), None
        except Exception as e:  # noqa: BLE001 - every failure is a route result
            ok, reason, res = False, f"unexpected problem ({type(e).__name__}: {e})", None
        tried.append({"route": key, "text": text, "ok": ok, "reason": reason, "seconds": round(time.time() - started)})
        log(f"claude tool route {key}: {'worked' if ok else 'refused - ' + reason}")
        if ok:
            out = {"ok": True, "route": key, "route_text": text, "path": res["path"], "version": res["version"],
                   "routes": tried, "reason": ""}
            _save(out)
            return out
    out = {"ok": False, "route": None, "route_text": None, "path": None, "version": None, "routes": tried,
           "reason": "; ".join(f"{t['text']}: {t['reason']}" for t in tried)}
    _save(out)
    return out


def _save(result):
    """The last install result, for diagnosis (no secrets in it)."""
    try:
        d = tools_dir(create=True)
        (d / "last_install.json").write_text(json.dumps(dict(result, at=datetime.now(timezone.utc)
                                                             .isoformat(timespec="seconds")), indent=1), encoding="utf-8")
    except OSError:
        pass


# ---------------------------------------------------------------- diagnosis

def _can_run_from(d):
    """Can a program copied into folder d start? (Company policies often block user folders.)"""
    try:
        Path(d).mkdir(parents=True, exist_ok=True)
        if WIN:
            src = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "hostname.exe"
            probe = Path(d) / "run_probe.exe"
            shutil.copyfile(src, probe)
            cmd = [str(probe)]
        else:
            probe = Path(d) / "run_probe.sh"
            probe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            probe.chmod(0o755)
            cmd = [str(probe)]
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=30, stdin=subprocess.DEVNULL)
            return p.returncode == 0, "" if p.returncode == 0 else f"exit code {p.returncode}"
        except OSError as e:
            return False, _exec_reason(e)
        finally:
            probe.unlink(missing_ok=True)
    except OSError as e:
        return False, f"couldn't prepare the test ({type(e).__name__})"


def diagnose():
    out = {"platform": _platform_key(), "python": sys.version.split()[0]}
    node = shutil.which("node")
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    out["node"] = {"path": node, "version": _run([node, "--version"], 30)[1].strip() if node else None}
    out["npm"] = {"path": npm}
    if npm:
        try:
            code, txt = _run([npm, "--version"], 60)
            out["npm"]["version"] = txt.strip().splitlines()[-1] if code == 0 else None
            code, txt = _run([npm, "prefix", "-g"], 60)
            g = txt.strip().splitlines()[-1] if code == 0 else None
            out["npm"]["global_folder"] = g
            out["npm"]["global_folder_writable"] = _writable(g, create=False) if g else None
        except Refused as e:
            out["npm"]["error"] = str(e)
    out["claude"] = {"candidates": candidates(), **find()}
    home = Path.home()
    folders = {"tools folder": tools_dir(), "user home": home,
               "temp": Path(os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"),
               "project page/_work": ROOT / "page" / "_work", "~/.local/bin": home / ".local" / "bin"}
    if WIN:
        folders.update({"LOCALAPPDATA": Path(os.environ.get("LOCALAPPDATA", "")),
                        "APPDATA": Path(os.environ.get("APPDATA", ""))})
    out["writable"] = {k: {"path": str(v), "ok": _writable(v, create=False)} for k, v in folders.items()}
    ok, why = _can_run_from(tools_dir(create=True) / "probe")
    out["run_from_user_folder"] = {"ok": ok, "reason": why}
    dl = {}
    for url in (f"{CLAUDE_BASE}/latest", f"{NODE_BASE}/index.json", NPM_PING):
        try:
            _get(url, timeout=30)
            dl[url.split("/")[2]] = {"ok": True}
        except Refused as e:
            dl[url.split("/")[2]] = {"ok": False, "reason": str(e)}
    out["downloads"] = dl
    try:
        out["last_install"] = json.loads((tools_dir() / "last_install.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        out["last_install"] = None
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--find", action="store_true")
    g.add_argument("--diagnose", action="store_true")
    g.add_argument("--install", action="store_true")
    g.add_argument("--route", choices=["portable", "npm_prefix"],
                   help="test one per-user route into the tools folder (set CONFIG_AUTOMATION_TOOLS "
                        "to a scratch folder), then start the tool it installed")
    ap.add_argument("--simulate-blocked", action="store_true", help="test: every route refused")
    args = ap.parse_args()
    if args.route:
        started = time.time()
        try:
            dict((k, fn) for k, _, fn in ROUTES)[args.route]()
            cli = prefix_dir() / ("claude.cmd" if WIN else "bin/claude")
            v, why = version(str(cli))
            res = {"ok": bool(v), "route": args.route, "path": str(cli), "version": v, "reason": why}
        except Refused as e:
            res = {"ok": False, "route": args.route, "reason": str(e)}
        print(json.dumps(dict(res, seconds=round(time.time() - started))))
        sys.exit(0 if res["ok"] else 1)
    if args.simulate_blocked:
        os.environ["CONFIG_AUTOMATION_SIMULATE_BLOCKED"] = "1"
    if args.find:
        print(json.dumps(find()))
    elif args.diagnose:
        print(json.dumps(diagnose(), indent=1))
    else:
        res = install(log=lambda m: print(m, file=sys.stderr, flush=True))
        print(json.dumps(res, indent=1))
        sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
