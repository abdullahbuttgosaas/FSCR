"""Page interface contract (root CLAUDE.md > Page interface): --spec, --options, --run.

A configuration folder's script calls page.main(SPEC, options_for, run_request) first
thing in main(). If the command line holds one of the three page commands, this
handles it and exits; otherwise it returns and the folder runs exactly as before.

Everything a page reads goes to stdout as JSON (one object for --spec / --options,
one JSON line per step for --run). The folder's normal prints go to stderr while a
page command runs, so stdout stays clean. Texts meant for the user are plain words:
plain_check() refuses the technical ones.
"""
import contextlib
import io
import json
import re
import sys
from datetime import date, datetime, timezone

CONTRACT = 1
TYPES = ("text", "number", "date", "yes-no", "pick", "rows")
SUB_TYPES = ("text", "number", "date", "yes-no", "pick")   # inside a rows field (no nesting)
MAIN, MORE = "main", "more options"

# Standard steps: key -> (percent, plain text)
STEPS = {
    "reading":   (5,   "Reading your request"),
    "checking":  (20,  "Checking the details with Oracle"),
    "creating":  (50,  "Creating it in Oracle"),
    "verifying": (85,  "Checking the result"),
    "done":      (100, "Done"),
}

# Error codes for the repair handoff -> plain text for the user
ERRORS = {
    "INVALID_REQUEST":    "Some details are missing or not valid.",
    "NOT_IN_ORACLE":      "Oracle doesn't have one of the values you chose.",
    "SIGN_IN_NEEDED":     "Your Oracle sign-in has expired. Please sign in again, then try once more.",
    "NO_PERMISSION":      "Your Oracle user isn't allowed to do this.",
    "PRODUCTION_REFUSED": "This project doesn't make changes in the live (production) Oracle.",
    "SETUP_NEEDED":       "This PC isn't set up for Oracle yet.",
    "TIMEOUT":            "Oracle took too long to answer.",
    "STEP_FAILED":        "Something went wrong on an Oracle screen.",
    "VERIFY_FAILED":      "It was saved, but Oracle doesn't show every value as requested.",
    "FAILED":             "Something went wrong.",
}

BANNED = re.compile(r"\b(REST|CSV|Playwright|exports?|exported|exporting|imports?|imported|"
                    r"importing|API|JSON)\b", re.I)


def plain_check(text, where):
    """Refuse technical words in text meant for the user (a folder bug, not user input)."""
    m = BANNED.search(text or "")
    if m:
        raise ValueError(f"page text for {where} uses the technical word '{m.group(0)}': {text!r}")
    return text


def _out(obj, stream):
    stream.write(json.dumps(obj, ensure_ascii=False) + "\n")
    stream.flush()


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class PageError(Exception):
    """Raise from a folder's run_request / options_for for a known, plain-language stop."""

    def __init__(self, code, text=None, detail=None):
        super().__init__(text or ERRORS.get(code, ERRORS["FAILED"]))
        self.code, self.text, self.detail = code, text or ERRORS.get(code, ERRORS["FAILED"]), detail


# ---------------------------------------------------------------- --spec

def _check_fields(fields, types, where):
    keys = set()
    for f in fields:
        name = f"{where}{f.get('key')!r}"
        if f.get("type") not in types:
            raise ValueError(f"spec field {name}: type must be one of {types}")
        need =("key", "label", "required", "type", "placeholder")
        if f.get("type") == "rows":
            need = ("key", "label", "required", "type", "fields", "min_rows", "add_label", "row_label")
        elif where == "":
            need += ("default",)
        for k in need:
            if k not in f:
                raise ValueError(f"spec field {name} has no {k!r}")
        if f["type"] not in types:
            raise ValueError(f"spec field {name}: type must be one of {types}")
        if f["key"] in keys:
            raise ValueError(f"spec field {name} appears twice")
        keys.add(f["key"])
        plain_check(f["label"], f"label of {name}")
        plain_check(f.get("help", ""), f"help of {name}")
        if f["type"] == "rows":
            plain_check(f["add_label"], f"add_label of {name}")
            plain_check(f["row_label"], f"row_label of {name}")
            if not isinstance(f["min_rows"], int) or f["min_rows"] < 0:
                raise ValueError(f"spec field {name}: min_rows must be a whole number >= 0")
            if f["required"] and f["min_rows"] < 1:
                raise ValueError(f"spec field {name}: a required rows field needs min_rows >= 1")
            if not f["fields"]:
                raise ValueError(f"spec field {name} has no sub-fields")
            _check_fields(f["fields"], SUB_TYPES, f"{f['key']}.")
    for f in fields:                          # optional "required_when" / "shown_when" keys
        for cond_key in ("required_when", "shown_when"):
            cond = f.get(cond_key)
            if cond is not None and (not isinstance(cond, dict) or not set(cond) <= keys):
                raise ValueError(f"spec field {where}{f['key']!r}: {cond_key} must name fields "
                                 f"of the same form, e.g. {{\"customer_type\": \"Person\"}}")


def check_spec(spec):
    """Make sure a folder's SPEC follows the contract (developer check)."""
    plain_check(spec["title"], "title")
    plain_check(spec["description"], "description")
    _check_fields(spec["fields"], TYPES, "")


def _spec_field(f, prefix=""):
    f = dict(f)
    f["required"] = bool(f["required"])
    f.setdefault("default", [] if f["type"] == "rows" else None)
    if f["type"] == "pick":
        f["options"] = f"--options {prefix}{f['key']}"
    if f["type"] == "rows":
        f["fields"] = [_spec_field(s, f"{f['key']}.") for s in f["fields"]]
    return f


def spec_json(spec):
    check_spec(spec)
    fields = []
    for f in spec["fields"]:
        f = _spec_field(f)
        # A field required only in some cases ("required_when") is shown up front too.
        f["group"] = MAIN if f["required"] or f.get("required_when") else MORE
        fields.append(f)
    return {"contract": CONTRACT, "title": spec["title"], "description": spec["description"],
            "groups": [MAIN, MORE], "fields": fields}


# ---------------------------------------------------------------- validation

def _field(spec, key):
    """A field by key; "rows_key.sub_key" finds a sub-field of a rows field."""
    top, _, sub = key.partition(".")
    f = next((f for f in spec["fields"] if f["key"] == top), None)
    if sub:
        if f is None or f["type"] != "rows":
            return None
        return next((s for s in f["fields"] if s["key"] == sub), None)
    return f


def _pick_keys(spec):
    keys = []
    for f in spec["fields"]:
        if f["type"] == "pick":
            keys.append(f["key"])
        elif f["type"] == "rows":
            keys += [f"{f['key']}.{s['key']}" for s in f["fields"] if s["type"] == "pick"]
    return keys


def _yes_no(v):
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return True if s in ("yes", "y", "true") else False if s in ("no", "n", "false") else None


def _empty(v):
    return v is None or (isinstance(v, str) and not v.strip())


def _value(f, v):
    """One filled-in value against its type. Returns (clean value, problem, plain text, valid)."""
    if f["type"] == "number":
        try:
            return (float(v) if "." in str(v) else int(v)), None, None, None
        except (TypeError, ValueError):
            return None, "not_a_number", f"{f['label']} must be a number, e.g. {f['placeholder']}.", None
    if f["type"] == "date":
        s = str(v).strip()
        if s.lower() != "today":
            try:
                date.fromisoformat(s)
            except ValueError:
                return None, "not_a_date", \
                    f"{f['label']} must be a date like {f['placeholder']}, or 'today'.", None
        return s, None, None, None
    if f["type"] == "yes-no":
        b = _yes_no(v)
        if b is None:
            return None, "not_yes_no", f"{f['label']} must be yes or no.", ["yes", "no"]
        return b, None, None, None
    return (v.strip() if isinstance(v, str) else v), None, None, None


def condition_holds(cond, given, fields):
    """Optional field keys "required_when" / "shown_when" (added 2026-10-21, e.g. Customers:
    {"customer_type": "Person"}): true when the request's value of that field - or the
    field's default when it is left out - equals the given value (case-insensitive)."""
    for k, want in (cond or {}).items():
        have = given.get(k)
        if _empty(have):
            have = next((x.get("default") for x in fields if x["key"] == k), None)
        if str(have).lower() != str(want).lower():
            return False
    return True


def condition_text(cond, fields):
    labels = {x["key"]: x["label"] for x in fields}
    return " and ".join(f"{labels.get(k, k)} is {v}" for k, v in cond.items())


def _check_fields_in(fields, given, prefix, where, problems, row=None):
    """Unknown keys, required and types for one form or one row; returns the clean dict."""
    clean = {}

    def problem(field, kind, text, valid=None):
        p = {"field": field, "problem": kind, "text": where + text}
        if row is not None:
            p["row"] = row
        if valid is not None:
            p["valid"] = valid
        problems.append(p)

    known = {f["key"] for f in fields}
    for key in given:
        if key not in known:
            problem(prefix + key, "unknown", f"'{key}' is not a field on this form.")
    for f in fields:
        v = given.get(f["key"])
        key = prefix + f["key"]
        if f["type"] == "rows":
            rows = [] if v is None else v
            if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                problem(key, "not_rows", f"{f['label']} must be a list of {f['row_label'].lower()} rows.")
                continue
            if len(rows) < f["min_rows"]:
                n = f["min_rows"]
                problem(key, "too_few_rows", f"Please add at least {n} "
                        f"{f['row_label'].lower()}{'' if n == 1 else 's'} ({f['add_label']}).")
            clean[f["key"]] = [
                _check_fields_in(f["fields"], r, f"{key}.", f"{f['row_label']} {i}: ", problems, i)
                for i, r in enumerate(rows, 1)]
            continue
        if f.get("shown_when") and not condition_holds(f["shown_when"], given, fields):
            if not _empty(v):                 # only for fields that use the optional key
                problem(key, "not_applicable", f"{f['label']} only applies when "
                        + condition_text(f["shown_when"], fields) + ".")
            continue
        required = f["required"] or bool(f.get("required_when")
                                         and condition_holds(f["required_when"], given, fields))
        if _empty(v) and f["required"] and f.get("type") == "pick" and f.get("default") not in (None, "", []):
            v = f["default"]      # a required list field with a default (Customers: the type); no other folder has one
        if _empty(v):
            if required:
                problem(key, "missing",
                        f"{f['label']} is missing." if row is not None else f"Please fill in {f['label']}.")
            continue
        value, kind, text, valid = _value(f, v)
        if kind:
            problem(key, kind, text, valid)
            continue
        clean[f["key"]] = value
    return clean


def check_request(spec, request):
    """Required, unknown and type checks (no Oracle needed). Returns (clean, problems).
    Problems inside a rows field name the row: "Installment 2: Days is missing."."""
    problems = []
    if not isinstance(request, dict):
        return {}, [{"field": None, "problem": "not_a_form",
                     "text": "The request must be the filled-in form."}]
    clean = _check_fields_in(spec["fields"], request, "", "", problems)
    return clean, problems


def _match(options_for, f, key, wanted, where, problems, row=None):
    """Exact match, or one unique case-insensitive match; never a guess."""
    values = options_for(key)
    wanted = str(wanted)
    hit = [o for o in values if wanted in (o["value"], o["label"])]
    if not hit:
        hit = [o for o in values if wanted.lower() in (o["value"].lower(), o["label"].lower())]
    if len(hit) == 1:
        return hit[0]["value"]
    p = {"field": key, "problem": "not_in_oracle" if not hit else "ambiguous",
         "text": where + (f"Oracle has no {f['label']} called '{wanted}'." if not hit else
                          f"'{wanted}' matches more than one {f['label']}; please pick one."),
         "valid": [o["label"] for o in values]}
    if row is not None:
        p["row"] = row
    problems.append(p)
    return None


def check_picks(spec, clean, options_for):
    """Pick-from-a-list fields (also inside rows) against the live list; each list is
    read once. Replaces each value with Oracle's spelling."""
    problems, cache = [], {}

    def opts(key):
        if key not in cache:
            cache[key] = options_for(key)
        return cache[key]

    for f in spec["fields"]:
        if f["type"] == "pick" and f["key"] in clean:
            v = _match(opts, f, f["key"], clean[f["key"]], "", problems)
            if v is not None:
                clean[f["key"]] = v
        elif f["type"] == "rows":
            for i, r in enumerate(clean.get(f["key"], []), 1):
                for s in f["fields"]:
                    if s["type"] == "pick" and s["key"] in r:
                        v = _match(opts, s, f"{f['key']}.{s['key']}", r[s["key"]],
                                   f"{f['row_label']} {i}: ", problems, i)
                        if v is not None:
                            r[s["key"]] = v
    return problems


# ---------------------------------------------------------------- --run

class Progress:
    """progress.step("creating") or progress.step("creating", text="Creating ZZ_1 (2 of 3)")."""

    def __init__(self, stream):
        self.stream = stream

    def step(self, key, percent=None, text=None):
        p, t = STEPS.get(key, (None, None))
        _out({"step": key, "percent": p if percent is None else percent,
              "text": plain_check(text or t, f"step {key}")}, self.stream)


def _classify(message):
    m = message or ""
    if re.search(r"sign-in.*expired|sign-in page|login_once", m, re.I):
        return "SIGN_IN_NEEDED"
    if re.search(r"Refusing to run|production", m, re.I):
        return "PRODUCTION_REFUSED"
    if re.search(r"ORACLE_ENV is not set|ORACLE_HOST is not set|\.env", m):
        return "SETUP_NEEDED"
    if re.search(r"\b403\b|not authori[sz]ed|insufficient privilege|permission", m, re.I):
        return "NO_PERMISSION"
    if re.search(r"Verification failed", m, re.I):
        return "VERIFY_FAILED"
    if re.search(r"Step '.+' failed", m):   # a screen step (often a changed screen: repairable)
        return "STEP_FAILED"
    if re.search(r"timed? ?out|Timeout", m, re.I):
        return "TIMEOUT"
    return "FAILED"


def _last_error(log):
    errs = [l[len("ERROR: "):] for l in log.splitlines() if l.startswith("ERROR: ")]
    return errs[-1] if errs else (log.strip().splitlines() or [""])[-1]


class _Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def run(spec, request_text, run_request, options_for=None, out=None):
    """Validate, then run the folder's flow. Returns the process exit code
    (0 done, 1 failed, 2 needs the user: missing/invalid values)."""
    out = out or sys.stdout
    progress = Progress(out)
    log = io.StringIO()
    err = _Tee(sys.stderr, log)
    current = {"step": "reading"}

    def final(ok, **kw):
        _out({"step": "result", "percent": 100, "ok": ok, **kw}, out)

    def stop(code, text=None, detail=None):
        final(False, text=plain_check(text or ERRORS[code], "error"),
              error={"code": code, "step": current["step"], "detail": detail})
        return 2 if code in ("INVALID_REQUEST", "NOT_IN_ORACLE") else 1

    orig_step = progress.step

    def tracked(key, percent=None, text=None):
        current["step"] = key
        orig_step(key, percent, text)
    progress.step = tracked

    with contextlib.redirect_stdout(err), contextlib.redirect_stderr(err):
        try:
            progress.step("reading")
            try:
                request = json.loads(request_text)
            except (TypeError, json.JSONDecodeError) as e:
                return stop("INVALID_REQUEST", "The request could not be read.", str(e))
            clean, problems = check_request(spec, request)
            if problems:
                return stop("INVALID_REQUEST", " ".join(p["text"] for p in problems), problems)
            progress.step("checking")
            if options_for:
                problems = check_picks(spec, clean, options_for)
                if problems:
                    code = "NOT_IN_ORACLE" if any(p["problem"] == "not_in_oracle" for p in problems) \
                        else "INVALID_REQUEST"
                    return stop(code, " ".join(p["text"] for p in problems), problems)
            result = run_request(clean, progress)
            if current["step"] != "done":
                progress.step("done")
            # Optional (added 2026-10-21): "partial" (done, with one note: an optional last
            # step didn't happen) and "steps" (plain lines, one per part, for the result card).
            more = {}
            if result.get("partial"):
                more["partial"] = True
            if result.get("steps"):
                more["steps"] = [plain_check(s, "steps") for s in result["steps"]]
            final(True, text=plain_check(result["text"], "result"),
                  created=result.get("created"), skipped=bool(result.get("skipped")),
                  where=plain_check(result.get("where", ""), "where"), **more)
            return 0
        except PageError as e:
            return stop(e.code, e.text, e.detail)
        except SystemExit as e:
            if e.code in (0, None):
                return stop("FAILED", detail="the folder's flow ended without a result")
            msg = _last_error(log.getvalue())
            return stop(_classify(msg), detail=msg)
        except Exception as e:  # noqa: BLE001 - every failure becomes one result line
            msg = f"{type(e).__name__}: {e}"
            return stop(_classify(msg), detail=msg)


# ---------------------------------------------------------------- entry point

def main(spec, options_for, run_request, argv=None):
    """Handle --spec / --options FIELD / --run 'JSON' and exit; return if none given."""
    argv = sys.argv[1:] if argv is None else argv
    out = sys.stdout
    if argv[:1] == ["--spec"]:
        _out(spec_json(spec), out)
        sys.exit(0)
    if argv[:1] == ["--options"]:
        key = argv[1] if len(argv) > 1 else ""
        f = _field(spec, key)
        if f is None or f["type"] != "pick":
            _out({"ok": False, "field": key, "text": f"'{key}' is not a pick-from-a-list field.",
                  "error": {"code": "NOT_A_LIST_FIELD", "detail": _pick_keys(spec)}}, out)
            sys.exit(2)
        log = io.StringIO()
        err = _Tee(sys.stderr, log)
        with contextlib.redirect_stdout(err), contextlib.redirect_stderr(err):
            try:
                values = options_for(key)
                code = 0
            except PageError as e:
                values, code, fail = None, 1, (e.code, e.text, e.detail)
            except SystemExit:
                msg = _last_error(log.getvalue())
                values, code, fail = None, 1, (_classify(msg), None, msg)
            except Exception as e:  # noqa: BLE001
                msg = f"{type(e).__name__}: {e}"
                values, code, fail = None, 1, (_classify(msg), None, msg)
        if code == 0:
            _out({"ok": True, "field": key, "label": f["label"], "values": values,
                  "read_at": _now()}, out)
        else:
            c, t, d = fail
            _out({"ok": False, "field": key, "text": t or ERRORS.get(c, ERRORS["FAILED"]),
                  "error": {"code": c, "detail": d}, "read_at": _now()}, out)
        sys.exit(code)
    if argv[:1] == ["--run"]:
        sys.exit(run(spec, argv[1] if len(argv) > 1 else "", run_request, options_for, out))


# ---------------------------------------------------------------- happy-path dates (the page)
# Added 2026-10-21 for page/server.py; nothing above calls these, so no folder changes
# behavior. The page offers only dates that keep a record usable:
#   - an end date is empty by default and must be after Oracle's today and after the start;
#   - a start date later than Oracle's today is allowed, with a plain note that the record
#     won't be active until then;
#   - "today" means Oracle's today minus one day (the project's rule), sent as that date;
#   - a date inside a repeating group may not start before its parent (Customers: a
#     purpose before its address, Oracle error HZ-120150, seen 2026-10-21).

ROW_DATE_PARENTS = {"purposes": "address_from_date"}   # rows key -> the start date it lies within


def date_role(key):
    """"start", "end" or None, from the field key (start_date, from_date, end_date, to_date,
    account_established_date, account_termination_date, ...)."""
    k = key.lower()
    if re.search(r"(^|_)(end|to|until|termination)(_|$)", k):
        return "end"
    if re.search(r"(^|_)(start|from|established|begin)(_|$)", k):
        return "start"
    return None


def date_pairs(fields):
    """{end key: start key} inside one list of fields (the form, or one rows field)."""
    keys = [f["key"] for f in fields if f.get("type") == "date"]
    starts = [k for k in keys if date_role(k) == "start"]
    pairs = {}
    for k in keys:
        if date_role(k) != "end":
            continue
        want = re.sub(r"(^|_)(end|to|until|termination)(_|$)",
                      lambda m: m.group(1) + {"end": "start", "to": "from", "until": "from",
                                              "termination": "established"}[m.group(2)] + m.group(3), k)
        pairs[k] = want if want in starts else (starts[0] if len(starts) == 1 else None)
    return pairs


def plain_day(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def happy_dates(spec, request, oracle_today):
    """Apply the page's date rules to one request. Returns (request with "today" written as
    Oracle's today minus one day, problems, notes). problems: [{"field", "row"?, "problem",
    "text"}] in the same form as check_request(); notes: plain sentences for the user."""
    from datetime import timedelta
    today = oracle_today if isinstance(oracle_today, date) else date.fromisoformat(str(oracle_today))
    yesterday = today - timedelta(days=1)
    req = json.loads(json.dumps(request))
    problems, notes = [], []

    def one(fields, values, prefix, row, where, parent_start, parent_label):
        pairs = date_pairs(fields)
        labels = {f["key"]: f["label"] for f in fields}
        seen = {}
        for f in fields:
            if f.get("type") != "date" or values.get(f["key"]) in (None, ""):
                continue
            k, v = f["key"], str(values[f["key"]]).strip()
            if v.lower() == "today":
                values[k] = v = yesterday.isoformat()
                notes.append(f"{where}{f['label']}: today means {plain_day(yesterday)} "
                             f"(Oracle's today minus one day).")
            try:
                seen[k] = date.fromisoformat(v)
            except ValueError:
                continue                                  # check_request reports bad dates
        for k, d in seen.items():
            role, label = date_role(k), labels[k]

            def bad(kind, text):
                p = {"field": prefix + k, "problem": kind, "text": where + text}
                if row is not None:
                    p["row"] = row
                problems.append(p)
            if role == "end":
                if d <= today:
                    bad("end_not_after_today", f"{label} must be after Oracle's today "
                        f"({plain_day(today)}), or left empty.")
                start = pairs.get(k)
                if start and start in seen and d <= seen[start]:
                    bad("end_not_after_start", f"{label} must be after {labels[start]} "
                        f"({plain_day(seen[start])}).")
            elif role == "start":
                if d > today:
                    notes.append(f"{where}{label} is {plain_day(d)}, after Oracle's today: it won't "
                                 f"be active until then.")
                if parent_start and d < parent_start:
                    bad("before_parent", f"{label} can't be before the {parent_label} "
                        f"({plain_day(parent_start)}).")

    one(spec["fields"], req, "", None, "", None, None)
    for f in spec["fields"]:
        if f.get("type") != "rows" or not isinstance(req.get(f["key"]), list):
            continue
        parent_key = ROW_DATE_PARENTS.get(f["key"])
        parent_start, parent_label = None, None
        if parent_key and any(x["key"] == parent_key for x in spec["fields"]):
            pv = req.get(parent_key)
            parent_start = date.fromisoformat(pv) if pv else today     # empty = Oracle's default, today
            parent_label = next(x["label"] for x in spec["fields"] if x["key"] == parent_key).lower()
        for i, r in enumerate(req[f["key"]], 1):
            if isinstance(r, dict):
                one(f["fields"], r, f"{f['key']}.", i, f"{f['row_label']} {i}: ", parent_start, parent_label)
    return req, problems, notes
