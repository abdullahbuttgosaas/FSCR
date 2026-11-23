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
             "yes-no": "Yes / No", "pick": "Dropdown"}
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
    """Column width from the label: 6 wider than the label, at least 16, at most 30."""
    return min(30, max(16, len(c["label"]) + 6))


def make_template():
    """The empty upload sheet as .xlsx bytes, made from the definition only."""
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
            values = ["Yes", "No"] if c["type"] == "yes-no" else c.get("values") or []
            rng = f"{letter}{lay['first_data_row']}:{letter}{last}"
            if values:
                inline = '"' + ",".join(values) + '"'
                if len(inline) > 250:              # Excel's limit for a list written in the rule
                    if lists_ws is None:
                        lists_ws = wb.create_sheet(LIST_TAB)
                        lists_ws.sheet_state = "hidden"
                    list_row += 1
                    for j, v in enumerate(values, 1):
                        lists_ws.cell(list_row, j, v)
                    inline = f"'{LIST_TAB}'!$A${list_row}:${get_column_letter(len(values))}${list_row}"
                dv = DataValidation(type="list", formula1=inline, allow_blank=True)
                dv.error, dv.errorTitle = "Please pick a value from the list.", c["label"]
                ws.add_data_validation(dv)
                dv.add(rng)
            if c["type"] != "yes-no":              # dates and IDs stay text (no Excel conversion)
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
        rows = []
        for r in ws.iter_rows(min_row=lay["first_data_row"], values_only=False):
            vals = {c.column: cell_text(c.value) for c in r if cell_text(c.value) is not None}
            if vals:
                rows.append((r[0].row, vals))
        tabs[ws.title] = {"headers": headers, "rows": rows}
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
    return hit["label"], None, None, None


# ---------------------------------------------------------------- the preview

def default_text(c, today):
    dv = c.get("default")
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
        self.records = []

    def problem(self, tab, row, col, text, fix):
        p = {"tab": tab, "row": row, "column": col, "text": text, "fix": fix}
        self.problems.append(p)
        return p

    def read_row(self, tab, folder, row, cells, colmap):
        """Every column of one row: checked values and the preview lines."""
        values, lines = {}, []
        for c in tab["columns"]:
            text = cells.get(colmap.get(norm(c["label"])))
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
            self.group(g, defs, known)
        if not self.records and not self.stops:
            tabs_ = [name for g in reg["groups"] for name in g["record_tabs"]]
            self.stops.append("There is no row to create in the sheet. Please fill in one row on "
                              + (", ".join(tabs_[:-1]) + " or " + tabs_[-1] if len(tabs_) > 1 else tabs_[0]) + ".")
        return self.view()

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
        recs = []
        for tname, opts in g["record_tabs"].items():
            if norm(tname) not in known:
                continue
            sheet_name, tab = known[norm(tname)]
            tdef = defs[norm(tname)]
            colmap = self.columns_of(tdef, sheet_name, tab)
            for row, cells in tab["rows"]:
                values, lines = self.read_row(tdef, folder, row, cells, colmap)
                self.dates(sheet_name, row, tdef["columns"], values, lines)
                name = " ".join(values.get(k) for k in opts["name_from"] if values.get(k)) or "(no name)"
                link_name = " ".join(" ".join(str(values[k]).split()) for k in opts.get("link_name", opts["name_from"])
                                     if values.get(k))
                recs.append({"group": g["name"], "folder": folder, "tab": sheet_name, "row": row,
                             "link_name": link_name,
                             "what": opts["what"], "name": name, "fixed": opts.get("fixed", {}),
                             "values": values, "lines": lines, "tdef": tdef, "children": [],
                             "child_what": [r["what"] for r in g["child_tabs"].values()]})
        if any(r.get("link") for r in g["child_tabs"].values()):
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
            for row, cells in tab["rows"]:
                values, lines = self.read_row(tdef, folder, row, cells, colmap)
                if link:
                    key = values.get(link["column"])          # empty: already red (required)
                    hits = [r for r in recs if key and flat(r["link_name"]) == flat(key)]
                    parent = hits[0] if len(hits) == 1 else None
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
                           (parent["values"], parent["tdef"]["columns"], rule["within_parent"]) if parent else None)
                child = {"tab": sheet_name, "row": row, "values": values, "lines": lines, "rule": rule, "tdef": tdef}
                if parent:
                    parent["children"].append(child)
                else:
                    rule["_unjoined"] += 1
                    if len(recs) == 1:          # shown in red in the table, never sent to Oracle
                        recs[0].setdefault("unjoined", []).append(child)
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
        for k in rec["children"]:
            into = k["rule"]["into"]
            req.setdefault(into, []).append({c["key"]: k["values"][c["label"]] for c in k["tdef"]["columns"]
                                             if c.get("key") and c["label"] in k["values"]})
        return req

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
                "rows": {"record": [rec["tab"], rec["row"]], "children": [[k["tab"], k["row"]] for k in kids]},
                "title": f"{rec['what'][0].upper()}{rec['what'][1:]} {rec['name']}",
                "fields": rec["lines"],
                "children": {"title": " and ".join(w.capitalize() + "s" for w in rec["child_what"]) or None,
                             "columns": [{"label": c["label"], "required": c["required"]} for c in cols],
                             "rows": [{"row": k["row"], "cells": k["lines"]} for k in kids]},
                "request": self.request_of(rec)})
        order = {t: i for i, t in enumerate(dict.fromkeys(p["tab"] for p in self.problems))}
        self.problems.sort(key=lambda p: (order[p["tab"]], p["row"] or 0))
        ok = not self.stops and not self.problems and len(records) >= 1
        return {"ok": ok, "stops": self.stops, "notes": list(dict.fromkeys(self.notes)),
                "problems": self.problems, "records": records,
                "sheet_problems": [p for p in self.problems if id(p) not in own],
                "today": self.today.isoformat() if self.today else None}


def preview(data, today=None, lists=None):
    return Upload(today, lists).run(data)


def subset_sheet(data, keep):
    """A new empty sheet (same tabs, headers, drop-downs) holding only the rows `keep` names
    from the uploaded workbook: {tab name: [row numbers]}, written from row 4 on in sheet
    order, each value under the column with the same label. Used for "Download a sheet with
    only the failed customers"."""
    from openpyxl import load_workbook
    lay = load_definition()["layout"]
    src = load_workbook(io.BytesIO(data), data_only=True)
    out = load_workbook(io.BytesIO(make_template()))
    for name, rows in keep.items():
        sws = next((w for w in src.worksheets if norm(w.title) == norm(name)), None)
        ows = next((w for w in out.worksheets if norm(w.title) == norm(name)), None)
        if sws is None or ows is None:
            continue
        target = {norm(c.value): c.column for c in ows[lay["label_row"]] if c.value}
        cols = [(c.column, target.get(norm(c.value))) for c in sws[lay["label_row"]] if c.value]
        for i, r in enumerate(sorted(rows)):
            for scol, ocol in cols:
                if ocol:
                    ows.cell(lay["first_data_row"] + i, ocol, cell_text(sws.cell(r, scol).value))
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
