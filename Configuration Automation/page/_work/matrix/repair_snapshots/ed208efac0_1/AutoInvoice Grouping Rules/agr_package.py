"""AutoInvoice grouping rules: Oracle's file layout read from the pod at run time, the import file built from it,
Oracle's log read, and the field-by-field read-back. No Oracle calls here (run.py makes them); everything is a
plain function of the files Oracle gave, so it is tested offline (page/matrix/test_matrix.py).

The one thing fixed in code is the three entity names (ENTITIES). The entity order, the member names, every CSV
header line, the field types and the metadata come from the pod's own template on every run; the import file is
the template's members in the template's own order, the metadata copied byte for byte (CLAUDE.md > File layout).
Copied from Receivables Payment Terms' rpt_package.py (isolation rule: no import across folders) and changed for
this task's three levels (rule > transaction class > characteristic) and its key (Name only).
"""
import csv
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, InvalidOperation

TASK = "AR_MANAGE_AUTOINVOICE_GROUPING_RULES"
METADATA = "ASM_SETUP_CSV_METADATA.xml"
ENTITIES = {"rule": "AR_AI_GROUPING_RULE", "class": "ORA_AR_AI_GRP_TXN_TYPE", "request": "ORA_AR_AI_GRP_TXN_REQUEST"}
PARENT = "AR_AI_GROUPING_RULE.Name"
CLASS_LINK = "ORA_AR_AI_GRP_TXN_TYPE.Class11"
AUDIT = ("LastUpdateDate", "LastUpdatedBy", "CreationDate", "CreatedBy", "LastUpdateLogin")
LAYOUT_TEXT = ("Oracle's file layout for AutoInvoice grouping rules isn't what this module knows. "
               "Nothing was created.")


class LayoutError(Exception):
    """The pod's files are not the layout this module knows: a plain stop, nothing is built (never a guess)."""

    def __init__(self, why):
        super().__init__(f"{LAYOUT_TEXT} ({why})")
        self.why = why


# ---------------------------------------------------------------- the layout

class Layout:
    """What the pod's template says: members in zip order, the metadata bytes, and per entity its member, header
    line (as written), header columns, field types, node path and position in the metadata."""

    def __init__(self):
        self.members, self.raw, self.metadata, self.entities = [], {}, b"", {}
        self.task = self.status = self.env = self.release = self.process_type = None
        self.newline, self.quote_all = "\n", True

    def order(self):
        """The entity names in the order the pod's metadata lists them."""
        return sorted(self.entities, key=lambda n: self.entities[n]["position"])


def _text(row, tag):
    el = row.find(tag)
    return (el.text or "").strip() if el is not None else ""


def read_layout(zip_bytes, need_completed=True):
    """The Layout of a template (or data) export. Raises LayoutError when the task, status, an entity, a member or a
    header doesn't fit; extra headers are allowed only as parent links (<ENTITY>.<Field>)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise LayoutError("the file Oracle gave is not a zip")
    lay = Layout()
    lay.members = z.namelist()
    lay.raw = {n: z.read(n) for n in lay.members}
    if METADATA not in lay.raw:
        raise LayoutError(f"no {METADATA}")
    lay.metadata = lay.raw[METADATA]
    try:
        root = ET.fromstring(lay.metadata)
    except ET.ParseError as e:
        raise LayoutError(f"{METADATA} can't be read: {e}")
    proc = root.find("MigrationProcessCSVMetadataVORow")
    if proc is None:
        raise LayoutError(f"{METADATA} has no process row")
    lay.task, lay.status = _text(proc, "ObjectShortName"), _text(proc, "ProcessStatus")
    lay.env, lay.release, lay.process_type = _text(proc, "ProcessEnv"), _text(proc, "ProcessRelease"), \
        _text(proc, "ProcessType")
    if lay.task != TASK:
        raise LayoutError(f"the file is for task {lay.task or '(none)'}, not {TASK}")
    if need_completed and lay.status != "COMPLETED":
        raise LayoutError(f"Oracle's process ended {lay.status or '(no status)'}")
    rows = proc.findall("MigrationProcessBusinessObjectCSVMetadata1/MigrationProcessBusinessObjectCSVMetadataVORow")
    for pos, row in enumerate(rows):
        name = _text(row, "BusinessObjectShortName")
        attrs = [a for a in _text(row, "XmlAttributeList").split(",") if a]
        types = [t for t in _text(row, "XmlAttributeTypeList").split(",") if t]
        if len(attrs) != len(types):
            raise LayoutError(f"{name}: {len(attrs)} fields but {len(types)} field types")
        lay.entities[name] = {"name": name, "position": pos, "attrs": attrs, "types": dict(zip(attrs, types)),
                              "node_path": _text(row, "XmlNodePath"), "node_sequence": _text(row, "NodeSequence")}
    missing = [e for e in ENTITIES.values() if e not in lay.entities]
    if missing:
        raise LayoutError(f"the file has no {', '.join(missing)}")
    for name, ent in lay.entities.items():
        member = f"{name}.csv"
        if member not in lay.raw:
            raise LayoutError(f"no {member} in the file")
        data = lay.raw[member]
        text = data.decode("utf-8-sig")
        first = text.split("\n", 1)[0]
        if first.endswith("\r"):
            lay.newline = "\r\n"
        header = next(csv.reader(io.StringIO(first)), [])
        if not header:
            raise LayoutError(f"{member} has no header line")
        extra = [h for h in header if h not in ent["attrs"]]
        bad = [h for h in extra if not re.fullmatch(r"[A-Z_]+\.\w+", h)]
        if bad:
            raise LayoutError(f"{member} has columns Oracle's metadata doesn't name: {', '.join(bad)}")
        absent = [a for a in ent["attrs"] if a not in header]
        if absent:
            raise LayoutError(f"{member} lacks the columns {', '.join(absent)}")
        lay.quote_all = first.startswith('"')
        end = data.find(b"\n")
        ent.update(member=member, header=header, head_bytes=data[:end + 1] if end >= 0 else data + b"\n")
    need = {ENTITIES["class"]: [PARENT], ENTITIES["request"]: [PARENT, CLASS_LINK]}
    for name, links in need.items():
        absent = [c for c in links + (["Class11"] if name == ENTITIES["class"] else ["FromColumnName"])
                  if c not in lay.entities[name]["header"]]
        if absent:
            raise LayoutError(f"{name}.csv lacks the columns {', '.join(absent)}")
    if "Name" not in lay.entities[ENTITIES["rule"]]["header"]:
        raise LayoutError(f"{ENTITIES['rule']}.csv lacks the column Name")
    return lay


def same_layout(a, b):
    """Differences between two layouts (template versus data export): entity order, headers, types."""
    out = []
    if a.order() != b.order():
        out.append(f"entity order {a.order()} versus {b.order()}")
    for n in ENTITIES.values():
        if a.entities[n]["header"] != b.entities[n]["header"]:
            out.append(f"{n} columns differ")
        if a.entities[n]["types"] != b.entities[n]["types"]:
            out.append(f"{n} field types differ")
    return out


# ---------------------------------------------------------------- rows of one rule

def iso(d):
    """A date as Oracle's import takes it: YYYY-MM-DD (an export's 2026/11/01 is turned round, never sent as is)."""
    if d in (None, ""):
        return ""
    if isinstance(d, date):
        return d.isoformat()
    s = str(d).strip().split(" ")[0].split("T")[0].replace("/", "-")
    return date.fromisoformat(s).isoformat()


def rule_rows(rule):
    """{entity: [row dicts]} for one checked rule (agr_rules.Rule), keyed by the pod's column names."""
    head = {"Name": rule.name, "Description": rule.description or "", "StartDate": iso(rule.from_date),
            "EndDate": iso(rule.to_date), "LineOrderingRuleName": "", "ConsBillingUseFlag": ""}
    classes, requests = [], []
    for code, chars in rule.classes.items():
        classes.append({PARENT: rule.name, "Class11": code})
        for ch in chars:
            requests.append({PARENT: rule.name, CLASS_LINK: code, "FromColumnName": ch})
    return {ENTITIES["rule"]: [head], ENTITIES["class"]: classes, ENTITIES["request"]: requests}


def build_zip(lay, rows):
    """The import file: every member of the template in the template's own order; the metadata byte for byte;
    each entity's CSV = its header line as Oracle wrote it plus our rows (columns by the header, a column we don't
    fill empty, audit columns always empty, date columns ISO). rows: {entity: [dict]}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for member in lay.members:
            ent = next((e for e in lay.entities.values() if e.get("member") == member), None)
            if ent is None:                      # the metadata (and anything else the pod adds): unchanged
                zo.writestr(member, lay.raw[member])
                continue
            out = io.StringIO()
            w = csv.writer(out, quoting=csv.QUOTE_ALL if lay.quote_all else csv.QUOTE_MINIMAL,
                           lineterminator=lay.newline)
            for r in rows.get(ent["name"], []):
                unknown = [c for c, v in r.items() if v not in (None, "") and c not in ent["header"]]
                if unknown:
                    raise LayoutError(f"{ent['member']} has no column {', '.join(unknown)}")
                vals = []
                for c in ent["header"]:
                    v = "" if c in AUDIT else str(r.get(c) if r.get(c) is not None else "")
                    if v and ent["types"].get(c) in ("date", "dateTime"):
                        v = iso(v)
                    vals.append(v)
                w.writerow(vals)
            zo.writestr(member, ent["head_bytes"] + out.getvalue().encode("utf-8"))
    return buf.getvalue()


# ---------------------------------------------------------------- an export's rows

def read_rows(zip_bytes):
    """{entity: [row dicts]} of a data export (its own layout)."""
    lay = read_layout(zip_bytes)
    out = {}
    for name, ent in lay.entities.items():
        rows = list(csv.reader(io.StringIO(lay.raw[ent["member"]].decode("utf-8-sig"))))
        out[name] = [dict(zip(rows[0], r)) for r in rows[1:] if any(r)]
    return lay, out


def key_of(row):
    """The rule Name of a rule row or a child row."""
    return row[PARENT] if PARENT in row else row.get("Name")


def rules_in(rows):
    """{Name: rule row} of an export."""
    return {key_of(r): r for r in rows.get(ENTITIES["rule"], [])}


def characteristics(rows):
    """The characteristic names Oracle's existing rules use (the only list Oracle gives: no public lookup exists,
    FSCR ora_reference_lookups.md:16)."""
    return sorted({r.get("FromColumnName") for r in rows.get(ENTITIES["request"], []) if r.get("FromColumnName")})


# ---------------------------------------------------------------- read-back

def same(a, b, kind):
    """Two values equal as Oracle means them: dates as dates (2026/11/01 = 2026-11-01), numbers as numbers."""
    a, b = (a or "").strip(), (b or "").strip()
    if a == b:
        return True
    if not a or not b:
        return False
    if kind in ("date", "dateTime"):
        try:
            return iso(a) == iso(b)
        except ValueError:
            return False
    if kind in ("decimal", "long", "integer", "number"):
        try:
            return Decimal(a) == Decimal(b)
        except InvalidOperation:
            return False
    return False


def compare_row(sent, got, types, where):
    out = []
    for c, v in sent.items():
        if c in AUDIT:
            continue
        if not same(v, got.get(c, ""), types.get(c, "string")):
            out.append(f"{where} {c}: Oracle has '{got.get(c, '')}', sent '{v}'")
    return out


def reconcile(lay, sent, before, after):
    """Every sent rule against a fresh export. sent: {Name: {entity: [rows]}}; before / after: an export's rows.
    Returns ({Name: {"saved", "diffs", "notes"}}, [names of other rules that changed])."""
    R, C, Q = (ENTITIES[r] for r in ("rule", "class", "request"))
    types = {n: e["types"] for n, e in lay.entities.items()}
    res = {}
    for key, rows in sent.items():
        heads = [r for r in after.get(R, []) if key_of(r) == key]
        if not heads:
            res[key] = {"saved": False, "diffs": [], "notes": []}
            continue
        diffs = []
        if len(heads) > 1:
            diffs.append(f"Oracle shows {len(heads)} rules named {key}")
        diffs += compare_row(rows[R][0], heads[0], types[R], "the rule's")
        got_c = {r.get("Class11"): r for r in after.get(C, []) if key_of(r) == key}
        for c in rows[C]:
            g = got_c.pop(c["Class11"], None)
            if g is None:
                diffs.append(f"transaction class {c['Class11']} isn't in Oracle")
            else:
                diffs += compare_row(c, g, types[C], f"class {c['Class11']}")
        diffs += [f"Oracle has a transaction class {k} that wasn't sent" for k in got_c]
        qkey = lambda r: (r.get(CLASS_LINK), r.get("FromColumnName"))
        got_q = {qkey(r): r for r in after.get(Q, []) if key_of(r) == key}
        for q in rows[Q]:
            g = got_q.pop(qkey(q), None)
            if g is None:
                diffs.append(f"characteristic {q['FromColumnName']} under class {q[CLASS_LINK]} isn't in Oracle")
            else:
                diffs += compare_row(q, g, types[Q], f"characteristic {q['FromColumnName']}")
        diffs += [f"Oracle has a characteristic {k[1]} under class {k[0]} that wasn't sent" for k in got_q]
        res[key] = {"saved": True, "diffs": diffs, "notes": []}
    changed = set()
    for name in (R, C, Q):
        def of(rows, k):
            return sorted(tuple(sorted(r.items())) for r in rows.get(name, []) if key_of(r) == k)
        keys = {key_of(r) for r in before.get(name, [])} | {key_of(r) for r in after.get(name, [])}
        changed |= {k for k in keys if k not in sent and of(before, k) != of(after, k)}
    return res, sorted(changed)


# ---------------------------------------------------------------- Oracle's log

# Oracle's attribute names -> (request key, sheet label, class row or not)
ATTRS = {"Name": ("name", "Name", False), "Description": ("description", "Item Description", False),
         "StartDate": ("from_date", "From Date", False), "EndDate": ("to_date", "To Date", False),
         "Class11": ("transaction_class", "Transaction Class", True),
         "FromColumnName": ("characteristic", "Characteristic", True),
         "ColumnId": ("characteristic", "Characteristic", True)}
# Oracle's messages (FSCR ora_error_handling.md:11-12, ora_input_validation.md:45) -> (request key, plain reason)
MESSAGES = {
    "AR_SU_DEFGR_DUPCLASS": ("transaction_class", "the same transaction class is given twice in this rule"),
    "AR_SU_DEFGR_DUPCOL": ("characteristic", "the same characteristic is given twice under one class"),
    "AR_CONS_BILL_TRAN_CLS_NOT_ALOW": ("transaction_class", "with consolidated billing only the Invoice class is "
                                                           "allowed"),
    "AR_CONS_BILL_GROUP_NOT_ALLOW_U": ("characteristic", "this characteristic needs consolidated billing"),
}


def unpack(data):
    if data[:2] == b"PK":
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            return [z.read(n).decode("utf-8", "replace") for n in z.namelist()]
        except zipfile.BadZipFile:
            return []
    return [data.decode("utf-8", "replace")]


def log_failures(texts, names):
    """The failed rows in Oracle's process log: [{"rule": a sent name the block quotes or None, "reasons", "field",
    "child", "raw"}]. How this task's log names a failed row is not proven yet, so a block is tied to a rule only
    when it quotes that rule's exact name; the read-back decides which rules were saved (CLAUDE.md > Gotchas)."""
    out = []
    for text in texts:
        flat = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", " ").replace("\\/", "/")
        for blk in flat.split("Row Identifier: ")[1:]:
            head, _, body = blk.partition("Message Text:")
            if "Status: Error" not in head:
                continue
            raw = " ".join(body.split("Total Objects", 1)[0].split())
            reasons, field, child = [], None, False
            for code, (key, plain) in MESSAGES.items():
                if code in raw:
                    reasons.append(f"{plain} ({code})")
                    field = field or key
                    child = child or key in ("transaction_class", "characteristic")
            for attr in re.findall(r"LOV_(\w+) with given set of values leads to no matching row", raw):
                key, label, kid = ATTRS.get(attr, (None, attr, False))
                field, child = field or key, child or kid
                reasons.append(f"Oracle has no matching value for {label}")
            for attr in re.findall(r"JBO-27040: Value .*? for field (\w+) exceeds the maximum length allowed", raw):
                key, label, kid = ATTRS.get(attr, (None, attr, False))
                field, child = field or key, child or kid
                reasons.append(f"{label} is longer than Oracle allows")
            for attr in re.findall(r"JBO-27014: Attribute (\w+) in \w+ is required", raw):
                if not reasons:
                    key, label, kid = ATTRS.get(attr, (None, attr, False))
                    field, child = field or key, child or kid
                    reasons.append(f"Oracle says {label} is required")
            if re.search(r"JBO-250(09|27)", raw) and not reasons:
                reasons.append("Oracle couldn't read a date (JBO-25009 / JBO-25027)")
            for code, msg in re.findall(r"(JBO-\d+|FND-\d+|AR-\d+): (.*?)(?=JBO-\d+|FND-\d+|AR-\d+|$)", raw):
                if code in ("JBO-25026", "JBO-25072", "JBO-27024", "JBO-27014", "JBO-27040", "JBO-25009", "JBO-25027"):
                    continue
                reasons.append(f"{msg.strip(' .')} ({code})")
            if not reasons:
                reasons = [raw[:300] or "Oracle gave no reason"]
            rule = next((n for n in sorted(names, key=len, reverse=True) if n and n in head + raw), None)
            out.append({"rule": rule, "reasons": list(dict.fromkeys(reasons)), "field": field, "child": child,
                        "raw": raw[:1500]})
    return out
