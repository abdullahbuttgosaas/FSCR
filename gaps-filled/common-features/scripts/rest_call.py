"""Run FSCR's own fusion_rest_client.py (unchanged, in place) with readable errors.

Why: FSCR's client decodes HTTP error bodies as UTF-8 text, so Oracle's gzip-compressed
error messages (for example the reason a POST was refused) come out as garbage.
This wrapper swaps, at run time only, the client's request function for a copy that
un-gzips the error body and leaves the server address out of the message. No FSCR file
is changed. Same arguments as fusion_rest_client.py, plus the first argument FSCR root.

Usage:
  python -B rest_call.py <FSCR> <endpoint> [fusion_rest_client.py options...]
Never prints tokens or the server address.
"""
from __future__ import annotations

import gzip
import json
import sys
import urllib.error
import urllib.request
import zlib
from pathlib import Path


def _decode(raw: bytes) -> str:
    for fn in (gzip.decompress, lambda b: zlib.decompress(b, 47)):
        try:
            return fn(raw).decode("utf-8", errors="replace")
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    fscr = Path(sys.argv.pop(1)).resolve()
    scripts = fscr / "core" / "fusion-api" / "rest-api-client" / "scripts"
    sys.path.insert(0, str(scripts))
    import rest_client_common as rc  # FSCR module, used as is

    def request_bytes(props, url, *, method, access_token, headers, json_body, timeout):
        h = dict(headers)
        h["Authorization"] = f"Bearer {access_token}"
        h.setdefault("Accept", "application/json")
        body = None
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=body, headers=h, method=method)
        try:
            with rc.authorized_urlopen(props, req, timeout=timeout, access_token=access_token) as r:
                return r.read(), dict(r.headers.items()), r.status
        except urllib.error.HTTPError as exc:
            text = _decode(exc.read())
            # no server address in the message
            raise SystemExit(f"HTTP {exc.code}: {text.strip()[:2000]}")
        except urllib.error.URLError as exc:
            raise SystemExit(f"Network error: {exc.reason}")

    rc.request_bytes = request_bytes
    import fusion_rest_client  # FSCR entry point, used as is

    return fusion_rest_client.main()


if __name__ == "__main__":
    sys.exit(main())
