"""Run ONE check of common/check_setup.py and print its outcome as one JSON line.

  python page/setup_check.py packages | browser | login_file | connection | session | look

Used by page/server.py for the setup checklist. It reuses the checks of the first-run
setup unchanged (common/check_setup.py) and only captures what they print, so no
value from the login file is ever shown: the checks print key names, never values.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    buf = io.StringIO()
    ok, extra = False, {}
    try:
        with contextlib.redirect_stdout(buf):
            from common import check_setup as cs
            if name == "packages":
                ok = cs.check_packages()
            elif name == "browser":
                ok = cs.check_browser_launch()
            elif name == "login_file":
                env = cs.check_env_file()
                ok = env is not None and all(cs.results)
                extra = {"exists": (ROOT / ".env").exists(), "production": bool(env and env["prod"])}
            elif name == "connection":
                from common import oracle  # noqa: F401  (loads the login file into the environment)
                ok = cs.check_rest()
            elif name == "session":
                ok = cs.check_session()
            elif name == "look":
                from common import oracle  # noqa: F401
                ok = cs.check_screen_look()
            else:
                print(f"[FAIL] unknown check {name!r}")
    except Exception as e:  # noqa: BLE001 - report every failure as a result
        buf.write(f"[FAIL] {name} - {type(e).__name__}: {str(e).splitlines()[0][:200] if str(e) else ''}\n")
        ok = False
    lines = [l for l in buf.getvalue().splitlines() if l.strip()]
    print(json.dumps({"check": name, "ok": bool(ok), "lines": lines, **extra}))


if __name__ == "__main__":
    main()
