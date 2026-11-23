"""Secret scanner. Looks for tokens, passwords, sign-in names, e-mail addresses, machine paths and links to
folders that only exist on someone else's computer. Run it on your evidence folder before you upload it.

Usage:
  python secret_scan.py evidence/Procurement
  python secret_scan.py evidence/Procurement --names "First Last,flast"     (also flag these words)
  python secret_scan.py <folder> --ignore-paths knowledge/ pillars/            (skip parts of a tree)

What is flagged (the matched text is shown masked, never in full):
  token        JWT-style tokens (eyJ...), "Bearer ..." values, access/refresh/id tokens, client secrets, API keys,
               private key blocks, Authorization headers
  password     a password, pwd or passwd setting that has a value
  username     username= / user_name / "PerformerUsername" style fields with a value, and any --names word
  email        e-mail addresses (except example.com / oracle.com documentation addresses)
  machine_path paths into a personal folder on a computer: a drive letter + Users folder, or a Mac/Linux home folder
  run_folder   references to folders that exist only on the kit authors' computer (old run, gap-fill and
               evidence-pack folders)
  oracle_host  Oracle pod host names (*.oraclecloud.com) - your environment's address should not be shared
Images (PNG/JPG) cannot be read as text: they are listed so you can look at them yourself.
Exit code 1 when anything is found, 0 when clean.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXT_EXT = {".md", ".txt", ".csv", ".json", ".py", ".html", ".htm", ".xml", ".yaml", ".yml", ".properties", ".log",
            ".ini", ".cfg", ".toml", ".js", ".ts", ".sh", ".ps1", ".bat", ".sql", ".dat", ".err", ""}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

PATTERNS = [
    ("token", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{16,}")),
    ("token", re.compile(r"(?i)[\"']?(access_token|refresh_token|id_token|client_secret|api[_-]?key|secret[_-]?key)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9._~+/=-]{8,}")),
    ("token", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token", re.compile(r"(?i)authorization\s*:\s*(basic|bearer)\s+[A-Za-z0-9._~+/=-]{8,}")),
    ("password", re.compile(r"(?i)[\"']?(password|passwd|pwd)[\"']?\s*[:=]\s*[\"']?(?!\s*$)(?![\"']?\s*(<|\{|\$|\*\*\*|none|null|\"\"|''))[^\s\"',;]{3,}")),
    ("username", re.compile(r"(?i)[\"']?(user_?name|performer_?user_?name|login_?name|signin_?name)[\"']?\s*[:=]\s*[\"']?(?!<|\{|\$)[A-Za-z0-9._@-]{3,}")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(com|org)|oracle\.com|noreply)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("machine_path", re.compile(r"(?i)\b[A-Z]:\\(?:Users|Documents and Settings|GoSaaS|Projects|Work)\\[^\s\"'<>|]*")),
    ("machine_path", re.compile(r"(?i)\b[A-Z]:/(?:Users|GoSaaS)/[^\s\"'<>|]*")),
    ("machine_path", re.compile(r"(?<![\w.])/(?:Users|home)/[A-Za-z0-9._-]+/")),
    # built from pieces so this line does not flag itself
    ("run_folder", re.compile("_fscr" + r"_run_\d|_gap" + "_fills|_fscr" + "_evidence_pack|fscr" + r"-work\d*\b")),
    ("oracle_host", re.compile(r"(?i)\b[a-z0-9-]+\.(?:fa\.)?[a-z0-9-]*\.?oraclecloud\.com\b")),
]


def mask(s: str) -> str:
    s = s.strip()
    return s if len(s) <= 6 else s[:3] + "*" * min(len(s) - 5, 12) + s[-2:]


def scan_text(text: str, names: list[str]) -> list[tuple[int, str, str]]:
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for kind, rx in PATTERNS:
            for m in rx.finditer(line):
                hits.append((n, kind, mask(m.group(0))))
        low = line.lower()
        for nm in names:
            if nm and re.search(r"(?<![a-z0-9])" + re.escape(nm.lower()) + r"(?![a-z0-9])", low):
                hits.append((n, "username", mask(nm)))
    return hits


def scan(paths: list[Path], names: list[str], ignore: list[str]) -> tuple[list[tuple[str, int, str, str]], list[str], int]:
    found, images, files = [], [], 0
    for root in paths:
        items = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for p in items:
            rel = p.relative_to(root).as_posix() if root.is_dir() else p.name
            if any(rel.startswith(i) for i in ignore) or "/.git/" in f"/{rel}":
                continue
            files += 1
            ext = p.suffix.lower()
            if ext in IMAGE_EXT:
                images.append(rel)
                continue
            if ext not in TEXT_EXT:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for n, kind, m in scan_text(text, names):
                found.append((rel, n, kind, m))
            for kind, rx in PATTERNS:  # file names too
                if rx.search(rel):
                    found.append((rel, 0, kind + " (file name)", mask(rel)))
    return found, images, files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--names", default="", help="comma-separated extra words to flag (your name, your sign-in name)")
    ap.add_argument("--ignore-paths", nargs="*", default=[], help="relative path prefixes to skip")
    ap.add_argument("--max", type=int, default=200, help="most findings to print (default 200)")
    a = ap.parse_args()
    names = [x.strip() for x in a.names.split(",") if x.strip()]
    found, images, files = scan(a.paths, names, a.ignore_paths)
    for rel, n, kind, m in found[: a.max]:
        print(f"{kind:13} {rel}:{n}  {m}")
    if len(found) > a.max:
        print(f"... and {len(found) - a.max} more")
    print(f"Scanned {files} files: {len(found)} finding(s); {len(images)} image(s) to check by eye")
    for i in images:
        print(f"  look at: {i}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
