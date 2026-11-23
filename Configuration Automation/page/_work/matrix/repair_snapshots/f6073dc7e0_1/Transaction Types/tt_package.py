"""Transaction types (header only): Oracle's file layout read from the pod at run time, the import file built from it,
Oracle's log read, and the field-by-field read-back. No Oracle calls here (run.py makes them); everything is a plain
function of the files Oracle gave, so it is tested offline (page/matrix/test_matrix.py).

The one thing fixed in code is the two entity names (ENTITIES). Rows go only into AR_TRANSACTION_TYPE (the parent);
AR_REF_ACCT_TRX_TYPE (reference accounts per business unit: BU, ledger and account segments) is sent as its header line
only, because v1 leaves out every accounting field (user's rule 2026-11-02; FSCR: segments "may create a valid
combination"). Entity order, members, headers, types and metadata come from the pod's own template on every run
(CLAUDE.md > File layout). The shared parts are copied from Transaction Sources' ts_package.py (isolation rule: no
import across folders).
"""
import csv
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, InvalidOperation

TASK = "AR_MANAGE_TRANSACTION_TYPES"
TERMS_TASK = "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS"      # read only, for the payment term names and sets
TERMS_ENTITY = "AR_PAYMENT_TERM"
METADATA = "ASM_SETUP_CSV_METADATA.xml"
ENTITIES = {"type": "AR_TRANSACTION_TYPE", "accounts": "AR_REF_ACCT_TRX_TYPE"}
AUDIT = ("LastUpdateDate", "LastUpdatedBy", "CreationDate", "CreatedBy", "LastUpdateLogin")   # never sent (FSCR)
LAYOUT_TEXT = ("Oracle's file layout for transaction types isn't what this module knows. "
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
    absent = [c for c in ("Name", "SetCode") if c not in lay.entities[ENTITIES["type"]]["header"]]
    if absent:
        raise LayoutError(f"{ENTITIES['type']}.csv lacks the columns {', '.join(absent)}")
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


# ---------------------------------------------------------------- rows of one type

def iso(d):
    """A date as Oracle's import takes it: YYYY-MM-DD (an export's 2026/11/01 is turned round, never sent as is)."""
    if d in (None, ""):
        return ""
    if isinstance(d, date):
        return d.isoformat()
    s = str(d).strip().split(" ")[0].split("T")[0].replace("/", "-")
    return date.fromisoformat(s).isoformat()


def type_rows(t):
    """{entity: [row dicts]} for one checked type (tt_rules.TrxType): one parent row; no reference-account rows."""
    row = {"Name": t.name, "SetCode": t.set_code, "Description": t.description or "", "Type": t.trx_class,
           "Status": t.status, "StartDate": iso(t.from_date), "EndDate": iso(t.to_date), "CreationSign": t.sign,
           "DefaultStatus": t.trx_status, "DefaultPrintingOption": t.printing,
           "DefaultTermName": t.term or "", "DefaultTermSetCode": t.term_set or "", **t.flags}
    return {ENTITIES["type"]: [row], ENTITIES["accounts"]: []}


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
    """(Name, SetCode) of a type row, or of a reference-account row (its parent's)."""
    return (row.get("AR_TRANSACTION_TYPE.Name", row.get("Name")), row.get("AR_TRANSACTION_TYPE.SetCode",
                                                                          row.get("SetCode")))


def types_in(rows):
    """{(Name, SetCode): row} of an export's transaction types."""
    out = {}
    for r in rows.get(ENTITIES["type"], []):
        out.setdefault(key_of(r), r)
    return out


def term_keys(zip_bytes):
    """{(Name, SetCode)} of the Receivables payment terms in that task's data file (read only; its own layout is that
    module's business, so only the term CSV's Name and SetCode columns are read)."""
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    member = f"{TERMS_ENTITY}.csv"
    if member not in z.namelist():
        raise LayoutError(f"the payment terms file has no {member}")
    rows = list(csv.reader(io.StringIO(z.read(member).decode("utf-8-sig"))))
    if not rows or "Name" not in rows[0] or "SetCode" not in rows[0]:
        raise LayoutError("the payment terms file has no Name or SetCode column")
    i, j = rows[0].index("Name"), rows[0].index("SetCode")
    return {(r[i], r[j].strip()) for r in rows[1:] if len(r) > max(i, j) and r[i]}


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
    """Every sent type against a fresh export. sent: {(Name, SetCode): {entity: [rows]}}; before / after: an export's
    rows. A sent type is found in AR_TRANSACTION_TYPE; its sent non-empty values are compared; reference-account rows
    for it are noted (none were sent). Returns ({key: {"saved", "diffs", "notes", "entity"}}, [names of other types
    that changed])."""
    T, A = ENTITIES["type"], ENTITIES["accounts"]
    types = lay.entities[T]["types"]
    res = {}
    for key, rows in sent.items():
        hits = [r for r in after.get(T, []) if key_of(r) == key]
        if not hits:
            res[key] = {"saved": False, "diffs": [], "notes": [], "entity": None}
            continue
        diffs, notes = [], []
        if len(hits) > 1:
            diffs.append(f"Oracle shows the transaction type {key[0]} in set {key[1]} more than once")
        want = {c: v for c, v in rows[T][0].items() if v not in (None, "")}
        diffs += compare_row(want, hits[0], types, "the type's")
        accts = [r for r in after.get(A, []) if key_of(r) == key]
        if accts:
            notes.append(f"Oracle shows {len(accts)} reference account row(s) for it, though none were sent")
        res[key] = {"saved": True, "diffs": diffs, "notes": notes, "entity": T}
    changed = set()
    for name in ENTITIES.values():
        def of(rows, k):
            return sorted(tuple(sorted(r.items())) for r in rows.get(name, []) if key_of(r) == k)
        keys = {key_of(r) for r in before.get(name, [])} | {key_of(r) for r in after.get(name, [])}
        changed |= {k for k in keys if k not in sent and of(before, k) != of(after, k)}
    return res, sorted(f"{k[0]} ({k[1]})" for k in changed)


# ---------------------------------------------------------------- Oracle's log

# Oracle's attribute names -> (request key, sheet label, child row or not); FSCR lists no message ids for this task
ATTRS = {"Name": ("name", "Name", False), "SetCode": ("set_code", "Set Code", False),
         "Description": ("description", "Item Description", False), "Type": ("trx_class", "Class", False),
         "Status": ("status", "Status", False), "StartDate": ("from_date", "From Date", False),
         "EndDate": ("to_date", "To Date", False), "AccountingAffectFlag": ("open_receivable", "Open Receivable", False),
         "PostToGl": ("post_to_gl", "Post to GL", False), "AllowFreightFlag": ("allow_freight", "Allow Freight", False),
         "TaxCalculationFlag": ("tax_calculation", "Tax Calculation", False),
         "NaturalApplicationOnlyFlag": ("natural_application", "Natural Application Only", False),
         "AllowOverapplicationFlag": ("allow_overapplication", "Allow Overapplication", False),
         "CreationSign": ("creation_sign", "Creation Sign", False),
         "DefaultStatus": ("transaction_status", "Transaction Status", False),
         "DefaultPrintingOption": ("printing_option", "Printing Option", False),
         "DefaultTermName": ("payment_term", "Payment Term", False), "DefaultTermId": ("payment_term", "Payment Term", False),
         "DefaultTermSetCode": ("payment_term_set", "Payment Term Set", False)}
MESSAGES = {}


def unpack(data):
    if data[:2] == b"PK":
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            return [z.read(n).decode("utf-8", "replace") for n in z.namelist()]
        except zipfile.BadZipFile:
            return []
    return [data.decode("utf-8", "replace")]


def log_failures(texts, names):
    """The failed rows in Oracle's process log: [{"type": a sent name the block quotes or None, "reasons", "field",
    "child", "raw"}]. How this task's log names a failed row is not proven yet, so a block is tied to a type only
    when it quotes that type's exact name; the read-back decides which types were saved (CLAUDE.md > Gotchas)."""
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
            name = next((n for n in sorted(names, key=len, reverse=True) if n and n in head + raw), None)
            out.append({"type": name, "reasons": list(dict.fromkeys(reasons)), "field": field, "child": child,
                        "raw": raw[:1500]})
    return out
