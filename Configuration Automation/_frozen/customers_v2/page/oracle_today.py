"""Print Oracle's today as one JSON line: {"today": "YYYY-MM-DD"} or {"today": null, "error": ...}.

Oracle's today is the date of a read-only REST response from Oracle (the `Date` header,
common.oracle.server_date), never this PC's clock (root CLAUDE.md > Dates). Used by the
page for its date rules. Prints no secret values.
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    try:
        from common import oracle
        r, err = oracle.try_call("GET", f"{oracle.API_BASE}/standardLookups",
                                 params={"finder": "LookupTypeFinder;LookupType=YES_NO",
                                         "onlyData": "true", "limit": 1}, timeout=60)
        if r is None:
            raise RuntimeError((err or "no answer").splitlines()[-1][:200])
        print(json.dumps({"today": oracle.server_date(r).isoformat()}))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"today": None, "error": f"{type(e).__name__}: {str(e)[:200]}"}))


if __name__ == "__main__":
    main()
