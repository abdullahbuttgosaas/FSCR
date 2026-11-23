"""The upload sheet: read an uploaded workbook, check it, build the folder requests, and
make the empty sheet. Plain code, no Claude; everything about tabs and columns comes from
page/sheet_definition.json and which folder runs them from page/sheet_registry.json (root
CLAUDE.md > The upload sheet).

  python page/workbook.py --template out.xlsx          # the empty sheet
  python page/workbook.py --check file.xlsx [--today YYYY-MM-DD]
                                                       # the preview, offline: lists from the
                                                       # definition only (the page also asks Oracle)

Used by page/server.py: make_template() for "Download the empty sheet", preview() for an
upload. preview() gets two helpers from the server: lists(folder, field, full) -> {"values":
[{"value", "label"}], "partial": bool, "failed": text or None} (the folder's --options; a
"partial" list holds only samples, full=True asks for the whole list), and Oracle's today.
Nothing here talks to Oracle or changes a configuration folder.
"""
import io
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFINITION = HERE / "sheet_definition.json"
REGISTRY = HERE / "sheet_registry.json"
LIST_TAB = "Lists"             # hidden tab of the empty sheet holding long drop-down lists
MAX_BYTES = 10 * 1024 * 1024

FILLS = {"section": ("1F3864", "2E75B6"), "required": "FFE699", "optional": "DDEBF7"}
TYPE_HINT = {"text": "Text", "long-text": "Long text", "digits": "Digits only", "date": "YYYY-MM-DD",
             "yes-no": "Yes / No", "pick": "Dropdown", "number": "Number"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------- the two files

def load_definition():
    """The sheet definition with every tab's columns written out ({"use": set} expanded,
    "@name" sections taken from the tab's "sections")."""
    d = json.loads(DEFINITION.read_text(encoding="utf-8"))
    for tab in d["tabs"]:
        cols = []
        for c in tab["columns"]:
            cols += [dict(x) for x in d["column_sets"][c["use"]]] if "use" in c else [dict(c)]
        for c in cols:
            c["section"] = tab.get("sections", {}).get(c.get("section"), c.get("section"))
            c.setdefault("required", False)
        tab["columns"] = cols
    return d


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def norm(s):
    return re.sub(r"\s+", " ", str(s or "").replace("*", "")).strip().lower()


def flat(t):
    """Text compared ignoring upper/lower case and extra spaces (also around commas)."""
    return re.sub(r"\s*,\s*", ",", " ".join(str(t or "").split())).lower()


def plain_day(d):
    return f"{d.day} {d.strftime('%B %Y')}"


# ---------------------------------------------------------------- the empty sheet

def hint_of(c):
    words = c.get("hint") or TYPE_HINT.get(c["type"], "Text")
    if not c.get("hint"):
        if c["type"] == "date":
            words += "; empty = today" if c.get("default") == "today" else "; empty = none"
        elif c["type"] == "yes-no" and c.get("default") is not None:
            words += f"; empty = {'Yes' if c['default'] else 'No'}"
        elif c.get("default") not in (None, ""):
            words = f"Empty = {c['default']}"
        if c.get("note"):
            words += f" ({c['note']})"
    return f"{'Required' if c['required'] else 'Optional'} · {words}"


def width_of(c):
    """Column width from the label: 6 wider than the label, at least 16, at most 30 (or the
    column's own "width", to copy a sheet the user designed)."""
    return c.get("width") or min(30, max(16, len(c["label"]) + 6))


def live_values(c, tab_name, lists):
    """A column's drop-down from Oracle's live list when the sheet is made ("values_live": the
    folder's --options field, whole list; 2026-10-26, Business Units: locations, sets). Without
    the lists helper, or when Oracle can't be read, the definition's own "values" (may be none)."""
    if not (c.get("values_live") and lists):
        return None
    folder = next((g["folder"] for g in load_registry()["groups"]
                   if norm(tab_name) in {norm(t) for t in list(g["record_tabs"]) + list(g["child_tabs"])}), None)
    try:
        got = lists(folder, c["values_live"], True) if folder else {}
    except Exception:  # noqa: BLE001 - the sheet is still made, without this list
        got = {}
    vals = [o["value"] for o in got.get("values") or [] if o.get("value") and o["value"].lower() != "none"]
    return vals or None


def make_template(lists=None):
    """The empty upload sheet as .xlsx bytes, made from the definition only (and, with the lists
    helper, Oracle's live lists for "values_live" columns)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    d = load_definition()
    lay = d["layout"]
    wb = Workbook()
    ws = wb.active
    ws.title = d["readme"]["tab"]
    for i, line in enumerate(d["readme"]["lines"], 1):
        ws.cell(i, 1, line or None).font = Font(bold=(i == 1), size=14 if i == 1 else 11)
    ws.column_dimensions["A"].width = 110
    lists_ws, list_row = None, 0
    last = lay["first_data_row"] + lay["template_rows"] - 1
    fill = lambda rgb: PatternFill("solid", fgColor=rgb)
    for tab in d["tabs"]:
        ws = wb.create_sheet(tab["name"])
        cols = tab["columns"]
        # row 1: sections, merged over their columns, two alternating colors
        start, shade = 1, 0
        for i in range(1, len(cols) + 1):
            if i == len(cols) or cols[i]["section"] != cols[start - 1]["section"]:
                cell = ws.cell(lay["section_row"], start, cols[start - 1]["section"])
                cell.fill, cell.font = fill(FILLS["section"][shade % 2]), Font(bold=True, color="FFFFFF")
                cell.alignment = Alignment(horizontal="center")
                if i > start:
                    ws.merge_cells(start_row=lay["section_row"], start_column=start,
                                   end_row=lay["section_row"], end_column=i)
                start, shade = i + 1, shade + 1
        for i, c in enumerate(cols, 1):
            letter = get_column_letter(i)
            head = ws.cell(lay["label_row"], i, c["label"] + (" *" if c["required"] else ""))
            head.fill = fill(FILLS["required" if c["required"] else "optional"])
            head.font, head.alignment = Font(bold=True), Alignment(wrap_text=True, vertical="center")
            hint = ws.cell(lay["hint_row"], i, hint_of(c))
            hint.font, hint.alignment = Font(italic=True, color="595959", size=9), Alignment(wrap_text=True, vertical="top")
            ws.column_dimensions[letter].width = width_of(c)
            values = ["Yes", "No"] if c["type"] == "yes-no" else \
                live_values(c, tab["name"], lists) or c.get("values") or []
            rng = f"{letter}{lay['first_data_row']}:{letter}{last}"
            if values:
                inline = '"' + ",".join(values) + '"'
                # Excel's limit for a list written in the rule; a value with a comma ("Yaqub, Younas")
                # would split there, so such a list goes on the hidden Lists tab too (2026-10-26)
                if len(inline) > 250 or any("," in v for v in values):
                    if lists_ws is None:
                        lists_ws = wb.create_sheet(LIST_TAB)
                        lists_ws.sheet_state = "hidden"
                    list_row += 1
                    for j, v in enumerate(values, 1):
                        lists_ws.cell(list_row, j, v)
                    inline = f"'{LIST_TAB}'!$A${list_row}:${get_column_letter(len(values))}${list_row}"
                dv = DataValidation(type="list", formula1=inline, allow_blank=True)
                dv.error, dv.errorTitle = "Please pick a value from the list.", c["label"]
                if c.get("dropdown_warn"):        # a value outside the list may be right (Price Lists' Business
                    dv.errorStyle = "warning"     # Unit: one on the Business Units tab), so Excel only warns
                    dv.error = ("This value isn't in Oracle's list. That's fine if it is on another tab of this "
                                "sheet (for example the Business Units tab); otherwise pick one from the list.")
                ws.add_data_validation(dv)
                dv.add(rng)
            if c["type"] != "yes-no" and c.get("format") != "general":   # dates and IDs stay text
                for r in range(lay["first_data_row"], last + 1):
                    ws.cell(r, i).number_format = "@"
        ws.row_dimensions[lay["label_row"]].height = 32
        ws.row_dimensions[lay["hint_row"]].height = 60
        ws.freeze_panes = ws.cell(lay["first_data_row"], 2)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------- reading an upload

def cell_text(v):
    """A cell as the text the sheet shows (dates as YYYY-MM-DD, whole numbers without .0)."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date().isoformat() if not (v.hour or v.minute or v.second) else v.isoformat(sep=" ")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    s = str(v).strip()
    return s or None


def read_tabs(data):
    """{tab name: {"headers": [(column number, text)], "rows": [(row number, {col: text})]}}"""
    from openpyxl import load_workbook
    lay = load_definition()["layout"]
    wb = load_workbook(io.BytesIO(data), data_only=True)
    tabs = {}
    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        headers = [(c.column, cell_text(c.value)) for c in ws[lay["label_row"]] if cell_text(c.value)] \
            if ws.max_row >= lay["label_row"] else []
        rows, raw = [], {}
        for r in ws.iter_rows(min_row=lay["first_data_row"], values_only=False):
            vals = {c.column: cell_text(c.value) for c in r if cell_text(c.value) is not None}
            if vals:
                rows.append((r[0].row, vals))
            for c in r:                # text with a space at the start or end, as typed ("keep_spaces")
                if isinstance(c.value, str) and c.value.strip() and c.value != c.value.strip():
                    raw[(c.row, c.column)] = c.value
        tabs[ws.title] = {"headers": headers, "rows": rows, "raw": raw}
    return tabs


# ---------------------------------------------------------------- one value

def clean(c, text):
    """(value for the request, problem, fix) for one non-empty cell (pick lists come later)."""
    t = c["type"]
    if t == "digits":
        if not re.fullmatch(r"\d+", text):
            return None, f"{c['label']} must be digits only; the sheet says '{text}'.", \
                "Write only the digits 0-9, for example 3010."
        return text, None, None
    if t == "date":
        try:
            if not DATE_RE.match(text):
                raise ValueError
            return date.fromisoformat(text).isoformat(), None, None
        except ValueError:
            return None, f"{c['label']} must be a date written as YYYY-MM-DD; the sheet says '{text}'.", \
                "Write it like 2026-11-01."
    if t == "number":            # a number with decimals (Payment Terms, 2026-10-25); ranges: the folder
        try:
            n = float(text.replace(",", ""))
        except ValueError:
            return None, f"{c['label']} must be a number; the sheet says '{text}'.", "Write a number, for example 30."
        return (int(n) if n.is_integer() else n), None, None
    if t == "yes-no":
        s = text.lower()
        if s in ("yes", "y", "true"):
            return True, None, None
        if s in ("no", "n", "false"):
            return False, None, None
        return None, f"{c['label']} must be Yes or No; the sheet says '{text}'.", "Write Yes or No."
    return text, None, None


def match(values, wanted):
    """Exact, else one unique case-insensitive match (value or label); never a guess."""
    hit = [o for o in values if wanted in (o["value"], o["label"])]
    if not hit:
        hit = [o for o in values if wanted.lower() in (o["value"].lower(), o["label"].lower())]
    return hit[0] if len(hit) == 1 else (None if not hit else "many")


def check_pick(c, text, folder, lists, cache):
    """(Oracle's spelling, problem, fix, note) for a pick-from-a-list column."""
    if c.get("check") is False:
        return text, None, None, "Not checked yet: Oracle's list is empty here."
    if c.get("check") == "folder":       # the folder checks it against Oracle's live list (Payment Terms --plan)
        return text, None, None, None
    fixed = [{"value": v, "label": v} for v in c.get("values") or []]
    source, partial, failed = fixed, False, None
    if c.get("live") and lists:
        key = (folder, c["live"], False)
        if key not in cache:
            cache[key] = lists(folder, c["live"], False)
        got = cache[key]
        if got.get("values"):
            source, partial = got["values"], got.get("partial", False)
        else:
            failed = got.get("failed") or "Oracle's list couldn't be read."
        hit = match(source, text) if source else None
        if hit is None and partial:                     # only samples so far: ask for the whole list
            key = (folder, c["live"], True)
            if key not in cache:
                cache[key] = lists(folder, c["live"], True)
            full = cache[key]
            if full.get("values"):
                source, partial = full["values"], False
            else:
                failed = full.get("failed") or "Oracle's full list couldn't be read."
    if not source:
        return text, None, None, (f"{failed} It is checked with Oracle when you press Create." if failed else None)
    hit = match(source, text)
    if hit == "many":
        return None, f"'{text}' matches more than one {c['label']}.", "Write it exactly as Oracle shows it.", None
    if hit is None:
        if partial or failed:
            return text, None, None, "Not one of the usual values; it is checked with Oracle when you press Create."
        shown = ", ".join(o["label"] for o in source[:40]) + (" ..." if len(source) > 40 else "")
        return None, f"Oracle has no {c['label']} called '{text}'.", f"Pick one of: {shown}", None
    return (hit["value"] if c.get("send") == "value" else hit["label"]), None, None, None


# ---------------------------------------------------------------- the preview

def default_text(c, today):
    dv = c.get("default")
    if c.get("default_text"):
        return c["default_text"]
    if dv == "today-1":           # sent as "today": the folder's rule, Oracle's today minus one day
        return (f"Oracle's today minus one day ({plain_day(today - timedelta(days=1))})" if today
                else "Oracle's today minus one day")
    if dv == "today":
        return f"Oracle's today ({plain_day(today)})" if today else "Oracle's today"
    if c["type"] == "yes-no" and dv is not None:
        return "Yes (ticked)" if dv else "No (not ticked)"
    return str(dv) if dv not in (None, "") else None


def shown_value(c, v):
    if v is None:
        return None
    if c["type"] == "yes-no":
        return "Yes (ticked)" if v else "No (not ticked)"
    return str(v)


class Upload:
    """One upload being checked: the preview for the page and the requests to run."""

    def __init__(self, today, lists):
        self.today = date.fromisoformat(today) if isinstance(today, str) else today
        self.lists, self.cache = lists, {}
        self.stops, self.notes, self.problems = [], [], []
        self.records, self.modules = [], []

    def problem(self, tab, row, col, text, fix):
        p = {"tab": tab, "row": row, "column": col, "text": text, "fix": fix}
        self.problems.append(p)
        return p

    def read_row(self, tab, folder, row, cells, colmap):
        """Every column of one row: checked values and the preview lines."""
        values, lines = {}, []
        for c in tab["columns"]:
            text = cells.get(colmap.get(norm(c["label"])))
            if c.get("keep_spaces") and text is not None:   # Business Units' Name: the folder refuses outer spaces
                text = getattr(self, "raw", {}).get((row, colmap.get(norm(c["label"]))), text)
            line = {"label": c["label"], "section": c["section"], "required": c["required"],
                    "sheet": text, "oracle": None, "problem": None, "fix": None, "note": None}
            if text is None:
                if c["required"]:
                    p = self.problem(tab["name"], row, c["label"], f"{c['label']} is missing.",
                                     f"Fill in {c['label']} on row {row}.")
                    line.update(problem=p["text"], fix=p["fix"])
                else:
                    line["oracle"] = default_text(c, self.today) or "(left empty)"
                    line["default"] = True
                lines.append(line)
                continue
            v, prob, fix = clean(c, text)
            note = None
            if not prob and c["type"] == "pick":
                v, prob, fix, note = check_pick(c, text, folder, self.lists, self.cache)
            if prob:
                self.problem(tab["name"], row, c["label"], prob, fix)
                line.update(problem=prob, fix=fix)
            else:
                values[c["label"]] = v
                line["oracle"] = shown_value(c, v)
                if c.get("oracle_checks") and not note:
                    note = "Oracle checks this while creating."
                line["note"] = note
            lines.append(line)
        return values, lines

    def dates(self, tab, row, cols, values, lines, parent=None):
        """Start / end pairs in one row, end dates after Oracle's today, and a child row's
        dates within its parent's (parent = (values, columns, rule))."""
        by = {c["label"]: c for c in cols}
        line_of = {l["label"]: l for l in lines}

        def day(label, vals, colset):
            v = vals.get(label)
            if v:
                return date.fromisoformat(v)
            c = colset.get(label)
            if c and c.get("default") == "today-1" and self.today:
                return self.today - timedelta(days=1)
            return self.today if c and c.get("default") == "today" else None

        def bad(label, text, fix):
            p = self.problem(tab, row, label, text, fix)
            line_of[label].update(problem=p["text"], fix=p["fix"])

        for c in cols:
            if c["type"] != "date" or not values.get(c["label"]):
                continue
            d = date.fromisoformat(values[c["label"]])
            if c.get("role") == "end":
                if self.today and d <= self.today:
                    bad(c["label"], f"{c['label']} ({plain_day(d)}) must be after Oracle's today "
                        f"({plain_day(self.today)}).", "Leave it empty for no end, or write a later date.")
                start = day(c.get("pair"), values, by) if c.get("pair") else None
                if start and d <= start:
                    bad(c["label"], f"{c['label']} ({plain_day(d)}) must be after {c['pair']} "
                        f"({plain_day(start)}).", f"Write a date after {start.isoformat()}.")
            elif c.get("role") == "start" and self.today and d > self.today:
                line_of[c["label"]]["note"] = f"Won't be active until {plain_day(d)} (after Oracle's today)."
        if parent:
            pvals, pcols, rule = parent
            pby = {c["label"]: c for c in pcols}
            what = rule["parent_what"]
            ps, pe = day(rule["parent_start"], pvals, pby), day(rule["parent_end"], pvals, pby)
            cs, ce = day(rule["start"], values, by), day(rule["end"], values, by)
            if ps and cs and cs < ps:
                bad(rule["start"], f"{rule['start']} ({plain_day(cs)}) is before the {what} starts "
                    f"({plain_day(ps)}).", f"Use {ps.isoformat()} or later, or change the {what}'s "
                    f"{rule['parent_start']}.")
            if pe and cs and cs >= pe:
                bad(rule["start"], f"{rule['start']} ({plain_day(cs)}) is not before the {what} ends "
                    f"({plain_day(pe)}).", f"Use a date before {pe.isoformat()}.")
            if pe and (ce is None or ce > pe):
                bad(rule["end"], f"{rule['end']} must be on or before the {what}'s {rule['parent_end']} "
                    f"({plain_day(pe)}); " + ("it is empty." if ce is None else f"it is {plain_day(ce)}."),
                    f"Write {pe.isoformat()} or earlier.")
        if not self.today:
            self.notes.append("Oracle's today couldn't be read, so dates left empty weren't compared.")

    def run(self, data):
        d, reg = load_definition(), load_registry()
        if len(data) > MAX_BYTES:
            self.stops.append("This file is too big (more than 10 MB). Please upload the sheet only.")
            return self.view()
        try:
            tabs = read_tabs(data)
        except Exception:  # noqa: BLE001 - any unreadable file gets the same plain answer
            self.stops.append("This file couldn't be read as an Excel workbook. Please upload the "
                              "sheet saved as .xlsx (Excel Workbook).")
            return self.view()
        defs = {norm(t["name"]): t for t in d["tabs"]}
        groups = {}
        for g in reg["groups"]:
            for name in list(g["record_tabs"]) + list(g["child_tabs"]):
                groups[norm(name)] = g
        ignore = {norm(t) for t in reg.get("ignore_tabs", [])} | {norm(d["readme"]["tab"])}
        known = {}
        for name, tab in tabs.items():
            if norm(name) in ignore:
                continue
            if norm(name) not in defs or norm(name) not in groups:
                self.notes.append(f"The tab '{name}' isn't set up yet, so it was left out."
                                  + (f" ({len(tab['rows'])} row{'s' if len(tab['rows']) != 1 else ''} in it.)"
                                     if tab["rows"] else ""))
                continue
            known[norm(name)] = (name, tab)
        if not known:
            self.stops.append("This workbook has none of the tabs the page knows. Please use the "
                              "empty sheet from \"Download the empty sheet\".")
            return self.view()
        for g in reg["groups"]:
            before = len(self.records)
            self.group(g, defs, known)
            self.module(g, known, len(self.records) - before)
        self.depends(reg)
        if not self.records and not self.stops:
            tabs_ = [name for g in reg["groups"] for name in g["record_tabs"]]
            self.stops.append("There is nothing to create: the sheet has no rows to create. Please fill in "
                              "at least one row on "
                              + (", ".join(tabs_[:-1]) + " or " + tabs_[-1] if len(tabs_) > 1 else tabs_[0]) + ".")
        return self.view()

    def depends(self, reg):
        """A group "depends_on" another (Price Lists on Business Units, 2026-10-26): a record whose column
        names a record of that group in this sheet (exactly, capitals and spaces count) is sent with the
        rule's key set (business_unit_pending), so the folder waits for it instead of refusing it; the
        line says so. The run itself creates the other group first (server.py)."""
        for g in reg["groups"]:
            dep = g.get("depends_on")
            if not dep:
                continue
            names = {r["values"].get(dep["match_column"]) for r in self.records if r["group"] == dep["group"]}
            for r in self.records:
                v = r["values"].get(dep["column"]) if r["group"] == g["name"] else None
                if v and v in names:
                    r["fixed"] = dict(r["fixed"], **{dep["key"]: True})
                    line = next((l for l in r["lines"] if l["label"] == dep["column"]), None)
                    if line and not line.get("problem"):
                        line["note"] = dep["note"].format(value=v)

    def module(self, g, known, count):
        """Each registry group is a module of the sheet (2026-10-25): Customers, Order Types, ...
        A module without rows is not an error: one plain line, and the other modules go on."""
        child_rows = sum(len(known[norm(t)][1]["rows"]) for t in g["child_tabs"] if norm(t) in known)
        text = None
        if not count:
            text = f"{g['name']}: there are no rows for this in the sheet, so nothing will be created."
            if child_rows:
                tabs_ = " / ".join(t for t in g["child_tabs"] if norm(t) in known)
                text += (f" ({tabs_} has {child_rows} row{'s' if child_rows != 1 else ''}, but there is no "
                         f"{g.get('record', 'record')} for {'them' if child_rows != 1 else 'it'}.)")
        self.modules.append({"name": g["name"], "record": g.get("record", "record"), "count": count,
                             "minutes_each": g.get("minutes_each", 3), "text": text,
                             **({"minutes_total": g["minutes_total"]} if g.get("minutes_total") else {})})

    def columns_of(self, tdef, sheet_name, tab):
        """{normalised label: column number}; a missing required column is a problem, an
        unknown column a note."""
        colmap = {norm(h): col for col, h in tab["headers"]}
        labels = {norm(c["label"]) for c in tdef["columns"]}
        for c in tdef["columns"]:
            if norm(c["label"]) not in colmap and c["required"]:
                self.problem(sheet_name, None, c["label"], f"The tab '{sheet_name}' has no column "
                             f"'{c['label']}'.", "Use the empty sheet from \"Download the empty sheet\".")
        for col, h in tab["headers"]:
            if norm(h) not in labels:
                self.notes.append(f"The column '{h}' on the tab '{sheet_name}' isn't known, so it was left out.")
        return colmap

    def too_many(self, g, known):
        """The group's record rows across its record tabs; more than max_records is a stop
        (Customers: at most 100 per upload since 2026-10-23, from both customer tabs)."""
        filled = [(name, [row for row, _ in known[norm(name)][1]["rows"]])
                  for name in g["record_tabs"] if norm(name) in known]
        filled = [(known[norm(name)][0], rows) for name, rows in filled if rows]
        total = sum(len(rows) for _, rows in filled)
        most = g.get("max_records")
        if not most or total <= most:
            return False
        what, one = g.get("record", "record"), "exactly one" if most == 1 else f"at most {most}"
        if most > 1:
            self.stops.append(f"The sheet has {total} {what}s. One upload holds {one} {what}s: split it "
                              f"into sheets of up to {most} {what}s and upload them one by one.")
            return True
        rows_of = lambda rows: f"row {rows[0]}" if len(rows) == 1 else             "rows " + ", ".join(map(str, rows[:-1])) + f" and {rows[-1]}"
        if len(filled) > 1:
            where = " and ".join(f"'{t}' {rows_of(rows)}" for t, rows in filled)
            self.stops.append(f"More than one {what} tab is filled: {where}. One upload holds {one} "
                              f"{what}: clear the rows on all but one tab, save, and upload again.")
        else:
            t, rows = filled[0]
            self.stops.append(f"The tab '{t}' has {total} filled rows ({rows_of(rows)}). One upload holds "
                              f"{one} {what}: keep one row, save, and upload again.")
        return True

    def group(self, g, defs, known):
        """The group's records and their child rows. A child tab with a "link" {"column"}
        joins each row to the record whose link name (the record tab's "link_name" columns
        joined with one space, e.g. Name, or First Name + Last Name) equals that column,
        ignoring case and extra spaces; two records with the same link name stop the sheet
        (works once several records are allowed). A child tab without a "link" belongs to the
        group's one record (max_records 1)."""
        folder = g["folder"]
        if self.too_many(g, known):
            return
        exact = any((r.get("link") or {}).get("exact") for r in g["child_tabs"].values())
        recs = []
        for tname, opts in g["record_tabs"].items():
            if norm(tname) not in known:
                continue
            sheet_name, tab = known[norm(tname)]
            tdef = defs[norm(tname)]
            colmap = self.columns_of(tdef, sheet_name, tab)
            self.raw = tab.get("raw") or {}
            for row, cells in tab["rows"]:
                values, lines = self.read_row(tdef, folder, row, cells, colmap)
                self.dates(sheet_name, row, tdef["columns"], values, lines)
                name = " ".join(values.get(k) for k in opts["name_from"] if values.get(k)) or "(no name)"
                link_name = " ".join(" ".join(str(values[k]).split()) for k in opts.get("link_name", opts["name_from"])
                                     if values.get(k))
                if exact:              # joined exactly as written (Payment Terms, 2026-10-25)
                    link_name = " ".join(str(values[k]) for k in opts.get("link_name", opts["name_from"]) if values.get(k))
                recs.append({"group": g["name"], "folder": folder, "tab": sheet_name, "row": row,
                             "link_name": link_name,
                             "what": opts["what"], "name": name, "fixed": opts.get("fixed", {}),
                             "values": values, "lines": lines, "tdef": tdef, "children": [],
                             "child_what": [r["what"] for r in g["child_tabs"].values()]})
        if any(r.get("link") for r in g["child_tabs"].values()) and not exact:   # exact: the folder says "twice"
            seen = {}
            for r in recs:
                if r["link_name"] and flat(r["link_name"]) in seen:
                    self.stops.append(f"Two {g.get('record', 'record')}s are named {seen[flat(r['link_name'])]['link_name']}. Give them "
                                      "different names or upload them separately.")
                    return
                seen[flat(r["link_name"])] = r
        for cname, rule in g["child_tabs"].items():
            if norm(cname) not in known:
                continue
            sheet_name, tab = known[norm(cname)]
            tdef = defs[norm(cname)]
            colmap = self.columns_of(tdef, sheet_name, tab)
            link = rule.get("link")
            rule["_unjoined"] = 0             # rows without their customer (already red)
            orphans = {}
            for row, cells in tab["rows"]:
                values, lines = self.read_row(tdef, folder, row, cells, colmap)
                if link:
                    key = values.get(link["column"])          # empty: already red (required)
                    hits = [r for r in recs if key and flat(r["link_name"]) == flat(key)]
                    if link.get("exact"):           # capitals and spaces count; a name twice is red already
                        hits = [r for r in recs if key and r["link_name"] == key][:1]
                    parent = hits[0] if len(hits) == 1 else None
                    if key and not parent and link.get("orphans"):    # e.g. codes for a type Oracle has
                        orphans.setdefault(key, []).append((row, values, lines))
                        continue
                    if key and not parent and recs:
                        rec_word = g.get("record", "record")
                        names = [r["link_name"] for r in recs]
                        text = (f"This {rule['what']} belongs to '{key}', but the {rec_word} in this sheet is "
                                f"'{names[0]}'." if len(names) == 1 else
                                f"This {rule['what']} belongs to '{key}', but no {rec_word} in this sheet has "
                                f"that name ({', '.join(names)}).")
                        p = self.problem(sheet_name, row, link["column"], text,
                                         f"Write the {rec_word}'s name in {link['column']}"
                                         + (f": '{names[0]}'." if len(names) == 1 else "."))
                        line = next((l for l in lines if l["label"] == link["column"]), None)
                        if line:
                            line.update(problem=p["text"], fix=p["fix"])
                else:
                    parent = recs[0] if len(recs) == 1 else None
                self.dates(sheet_name, row, tdef["columns"], values, lines,
                           (parent["values"], parent["tdef"]["columns"], rule["within_parent"])
                           if parent and rule.get("within_parent") else None)
                child = {"tab": sheet_name, "row": row, "values": values, "lines": lines, "rule": rule, "tdef": tdef}
                if parent:
                    parent["children"].append(child)
                else:
                    rule["_unjoined"] += 1
                    if len(recs) == 1:          # shown in red in the table, never sent to Oracle
                        recs[0].setdefault("unjoined", []).append(child)
            for key, rows_ in orphans.items():
                recs.append(self.orphan_record(g, link, rule, sheet_name, tdef, key, rows_, defs))
        if len(g["child_tabs"]) > 1:          # several child tabs: one table each in the preview
            order = list(g["child_tabs"].values())
            names = {id(r): known[norm(n)][0] if norm(n) in known else n for n, r in g["child_tabs"].items()}
            tdefs = {id(r): defs[norm(n)] for n, r in g["child_tabs"].items() if norm(n) in defs}
            for rec in recs:
                rec.update(child_rules=order, child_defs=tdefs, child_tabs_names=names, several_child_tabs=True)
        self.unique_records(recs, g.get("unique_records", []))
        self.reserved(recs, g.get("reserved", []))
        for rec in recs:
            self.child_rules(rec, g)
            for rule in g["child_tabs"].values():
                if rule.get("address_pick"):
                    self.address_pick(rec, [k for k in rec["children"] if k["rule"] is rule], rule["address_pick"],
                                      rows_missing=rule.get("_unjoined", 0))
        self.records += recs

    def address_pick(self, rec, kids, rule, rows_missing=0):
        """A child column Oracle fills from a list holding only the record's own address
        (Customers: Bill-to Site, offered on Ship to rows only). Empty = picked automatically;
        a typed value must equal the text built from the record's address columns (case and
        extra spaces ignored); on other rows a typed value is ignored with a note."""
        col = rule["column"]
        on = lambda k, cond: all(flat(k["values"].get(c) or "") == flat(v) for c, v in cond.items())
        text = ""
        for part in rule["text"]:
            v = rec["values"].get(part["column"])
            if v:
                v = str(v).upper() if part.get("upper") else str(v)
                text += (part.get("sep", "") if text else "") + v
        needed = [k for k in kids if on(k, rule["only_on"])]
        have, want = " / ".join(rule["only_on"].values()), " / ".join(rule["needs_row"].values())
        # (rows not joined to their customer are red already; their purpose may be the missing one)
        if needed and not rows_missing and not any(on(k, rule["needs_row"]) for k in kids):
            for k in needed:
                p = self.problem(k["tab"], k["row"], col, f"{rec['name']} has a {have} row but no {want} row. "
                                 f"Oracle needs a {want} purpose for a {have} purpose ({col} is the {want} "
                                 f"address).", f"Add a {want} row for {rec['name']}, or remove the {have} row.")
                line = next((l for l in k["lines"] if l["label"] == col), None)
                if line:
                    line.update(problem=p["text"], fix=p["fix"])
            return
        for k in kids:
            line = next((l for l in k["lines"] if l["label"] == col), None)
            typed = k["values"].get(col)
            if line is None:
                continue
            if not on(k, rule["only_on"]):
                if typed:
                    k["values"].pop(col)
                    line.update(oracle="(ignored)", note=f"Oracle only offers {col} on {have} rows, so "
                                                         "this value will be ignored.")
                continue
            if not typed:
                line.update(oracle=text or "(this customer's address)", note="Picked automatically",
                            default=False)
            elif flat(typed) != flat(text):
                p = self.problem(k["tab"], k["row"], col, f"{col} '{typed}' isn't this customer's address.",
                                 f"Use '{text}', or leave it empty to use this one.")
                line.update(problem=p["text"], fix=p["fix"])
            else:
                line.update(oracle=text, note=None)

    def orphan_record(self, g, link, rule, sheet_name, tdef, key, rows_, defs):
        """Child rows naming a record that isn't on the record tab, with a link "orphans" rule (Lookup
        Types, 2026-10-25: code rows for a lookup type that already exists in Oracle): one entry of
        their own, sent with the rule's "fixed" values (existing_only) so the folder checks that the
        type exists and may take codes. Shown as "<what> <name>" with one line for the name."""
        o = link["orphans"]
        kids = [{"tab": sheet_name, "row": row, "values": values, "lines": lines, "rule": rule, "tdef": tdef}
                for row, values, lines in rows_]
        rec_tab = next(iter(g["record_tabs"]))
        line = {"label": link["column"], "section": tdef["columns"][0]["section"], "required": True, "sheet": key,
                "oracle": key, "problem": None, "fix": None,
                "note": f"Not on the {rec_tab} tab: these codes are added to a {g.get('record', 'record')} that "
                        "already exists in Oracle (checked with Oracle)."}
        return {"group": g["name"], "folder": g["folder"], "tab": sheet_name, "row": kids[0]["row"],
                "link_name": key, "what": o["what"], "name": key, "fixed": dict(o.get("fixed", {}), **{o["key"]: key}),
                "values": {}, "lines": [line], "tdef": {"columns": []}, "children": kids,
                "child_what": [r["what"] for r in g["child_tabs"].values()], "label_tab": rec_tab,
                "orphan_rows": [k["row"] for k in kids]}

    def reserved(self, recs, rules):
        """A value a record (or its rows) may not have because another tab manages it (Lookup Types:
        the order type list belongs to the Order Types tab). Red on the record."""
        for rule in rules:
            for r in recs:
                v = r.get("link_name") or r["values"].get(rule["column"])
                if v in rule["values"]:
                    p = self.problem(r["tab"], r["row"], rule["column"], rule["text"].format(value=v),
                                     rule.get("fix") or "Remove these rows.")
                    line = next((l for l in r["lines"] if l["label"] == rule["column"]), None)
                    if line:
                        line.update(problem=p["text"], fix=p["fix"], note=None)

    def unique_records(self, recs, rules):
        """A column whose value may appear once per sheet in the group (Order Types: Lookup Code,
        case counts; Meaning, capitals ignored). Every row after the first is red."""
        for rule in rules:
            col, seen = rule["column"], {}
            for r in recs:
                v = r["values"].get(col)
                if v is None:
                    continue
                k = str(v).lower() if rule.get("ignore_case") else str(v)
                if k not in seen:
                    seen[k] = r
                    continue
                first = seen[k]
                p = self.problem(r["tab"], r["row"], col, f"{col} '{v}' is also on row {first['row']}"
                                 + (" (capitals ignored)" if rule.get("ignore_case") and v != first["values"][col] else "")
                                 + "; each one can be in the sheet only once.", "Keep one of the two rows, or change one.")
                line = next((l for l in r["lines"] if l["label"] == col), None)
                if line:
                    line.update(problem=p["text"], fix=p["fix"])

    def child_rules(self, rec, g):
        """Per customer: each purpose once, and one Yes per purpose in the flag column."""
        for cname, rule in g["child_tabs"].items():
            kids = [k for k in rec["children"] if k["rule"] is rule]
            for col in rule.get("unique", []):
                seen = {}
                for k in kids:
                    v = k["values"].get(col)
                    if v is None:
                        continue
                    if v.lower() in seen:
                        self.kid_problem(k, col, f"{col} '{v}' is listed twice for {rec['name']} "
                                         f"(rows {seen[v.lower()]} and {k['row']}).", "Keep one of the two rows.")
                    else:
                        seen[v.lower()] = k["row"]
            one = rule.get("one_yes_per")
            if one:
                marked = {}
                for k in kids:
                    if k["values"].get(one["flag"]) is True and k["values"].get(one["per"]):
                        marked.setdefault(k["values"][one["per"]].lower(), []).append(k)
                for ks in marked.values():
                    if len(ks) > 1:
                        rows = " and ".join(str(k["row"]) for k in ks)
                        for k in ks[1:]:
                            self.kid_problem(k, one["flag"], f"Only one {ks[0]['values'][one['per']]} row can be "
                                             f"{one['flag']}; rows {rows} both say Yes.",
                                             f"Set {one['flag']} to Yes on one of them only.")

    def kid_problem(self, kid, col, text, fix):
        p = self.problem(kid["tab"], kid["row"], col, text, fix)
        line = next((l for l in kid["lines"] if l["label"] == col), None)
        if line:
            line.update(problem=p["text"], fix=p["fix"])

    def request_of(self, rec):
        """The folder request for one record: fixed values, every filled column by its key,
        and the child rows (defaults are left to Oracle)."""
        req = dict(rec["fixed"])
        for c in rec["tdef"]["columns"]:
            if c.get("key") and c["label"] in rec["values"]:
                req[c["key"]] = rec["values"][c["label"]]
            elif c.get("key") and c.get("send_default"):
                # Order Types' Start Date: the date the preview showed (Oracle's today minus one
                # day), so Oracle gets what the user saw even when Oracle's date turns before the
                # run (seen 2026-10-25 at midnight UTC); "today" only when the date wasn't read.
                dv = c.get("default")
                if dv in ("today", "today-1"):
                    day = self.today and (self.today - timedelta(days=1 if dv == "today-1" else 0))
                    req[c["key"]] = day.isoformat() if day else "today"
                else:
                    req[c["key"]] = dv
        for k in rec["children"]:
            into = k["rule"]["into"]
            req.setdefault(into, []).append({c["key"]: k["values"][c["label"]] for c in k["tdef"]["columns"]
                                             if c.get("key") and c["label"] in k["values"]})
        return req

    def child_tables(self, rec):
        """A group with several child tabs (Payment Terms: lines and sets): one table per tab,
        each with its own columns, in tab order, empty ones included."""
        out = []
        for rule in rec["child_rules"]:
            kids = sorted([k for k in rec["children"] + rec.get("unjoined", []) if k["rule"] is rule],
                          key=lambda k: k["row"])
            cols = rec["child_defs"][id(rule)]["columns"] if id(rule) in rec["child_defs"] else []
            out.append({"title": rule["what"].capitalize() + "s", "tab": rec["child_tabs_names"][id(rule)],
                        "count": len(kids), "columns": [{"label": c["label"], "required": c["required"]} for c in cols],
                        "rows": [{"row": k["row"], "cells": k["lines"]} for k in kids]})
        return out

    def view(self):
        """Every record in sheet order with its own problems (its row and its child rows) and an
        "ok" flag; "ok" for the sheet = no stops and no problems at all (Create is for the whole
        sheet). "rows" says where the record and its child rows are (failed-only sheet)."""
        records, own = [], set()
        for rec in self.records:
            kids = sorted(rec["children"] + rec.get("unjoined", []), key=lambda k: k["row"])
            cols = kids[0]["tdef"]["columns"] if kids else []
            mine = {(rec["tab"], rec["row"])} | {(k["tab"], k["row"]) for k in kids}
            probs = [p for p in self.problems if (p["tab"], p["row"]) in mine]
            own |= {id(p) for p in probs}
            records.append({
                "group": rec["group"], "folder": rec["folder"], "tab": rec["tab"], "row": rec["row"],
                "name": rec["name"], "ok": not probs, "problems": probs,
                "rows": {"record": [rec["tab"], rec["row"]], "children": [[k["tab"], k["row"]] for k in kids
                                                                         if (k["tab"], k["row"]) != (rec["tab"], rec["row"])]},
                "title": f"{rec['what'][0].upper()}{rec['what'][1:]} {rec['name']}",
                "fields": rec["lines"],
                "children": {"title": " and ".join(w.capitalize() + "s" for w in rec["child_what"]) or None,
                             "columns": [{"label": c["label"], "required": c["required"]} for c in cols],
                             "rows": [{"row": k["row"], "cells": k["lines"]} for k in kids]},
                "request": self.request_of(rec),
                **({"label_tab": rec["label_tab"]} if rec.get("label_tab") else {}),
                **({"child_tables": self.child_tables(rec)} if len(set(id(k["rule"]) for k in kids)) > 1
                   or rec.get("several_child_tabs") else {})})
        order = {t: i for i, t in enumerate(dict.fromkeys(p["tab"] for p in self.problems))}
        self.problems.sort(key=lambda p: (order[p["tab"]], p["row"] or 0))
        ok = not self.stops and not self.problems and len(records) >= 1
        return {"ok": ok, "stops": self.stops, "notes": list(dict.fromkeys(self.notes)),
                "problems": self.problems, "records": records,
                "sheet_problems": [p for p in self.problems if id(p) not in own],
                "today": self.today.isoformat() if self.today else None,
                "modules": self.modules}


def preview(data, today=None, lists=None):
    return Upload(today, lists).run(data)


def subset_sheet(data, keep, lists=None, cells=None):
    """A new empty sheet (same tabs, headers, drop-downs) holding only the rows `keep` names
    from the uploaded workbook: {tab name: [row numbers]}, written from row 4 on in sheet
    order, each value under the column with the same label. Used for "Download a sheet with
    only the failed customers". cells (2026-10-26, Business Units' questions): {(tab, row, column
    label): {"value": a corrected value or None, "comment": text}} - the value replaces the
    sheet's, the comment goes on the cell (Oracle's reason and the suggested values)."""
    from openpyxl import load_workbook
    from openpyxl.comments import Comment
    lay = load_definition()["layout"]
    src = load_workbook(io.BytesIO(data), data_only=True)
    out = load_workbook(io.BytesIO(make_template(lists)))
    for name, rows in keep.items():
        sws = next((w for w in src.worksheets if norm(w.title) == norm(name)), None)
        ows = next((w for w in out.worksheets if norm(w.title) == norm(name)), None)
        if sws is None or ows is None:
            continue
        target = {norm(c.value): c.column for c in ows[lay["label_row"]] if c.value}
        cols = [(c.column, target.get(norm(c.value))) for c in sws[lay["label_row"]] if c.value]
        labels = {c.column: c.value for c in sws[lay["label_row"]] if c.value}
        for i, r in enumerate(sorted(rows)):
            for scol, ocol in cols:
                if ocol:
                    ows.cell(lay["first_data_row"] + i, ocol, cell_text(sws.cell(r, scol).value))
                    extra = (cells or {}).get((name, r, norm(labels.get(scol))))
                    if extra:
                        cell = ows.cell(lay["first_data_row"] + i, ocol)
                        if extra.get("value") is not None:
                            cell.value = extra["value"]
                        if extra.get("comment"):
                            cell.comment = Comment(extra["comment"], "Upload page")
    buf = io.BytesIO()
    out.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------- command line (testing)

def main():
    args = sys.argv[1:]
    if args[:1] == ["--template"] and len(args) > 1:
        Path(args[1]).write_bytes(make_template())
        print(f"wrote {args[1]}")
    elif args[:1] == ["--check"] and len(args) > 1:
        today = args[args.index("--today") + 1] if "--today" in args else None
        res = preview(Path(args[1]).read_bytes(), today)
        for r in res["records"]:
            r.pop("fields")
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
