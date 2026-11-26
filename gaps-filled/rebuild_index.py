"""Rebuild gap_index.csv and gap_progress.tsv from the STATUS.md cards and screen-only.csv files.

GoSaaS tool, not official FSCR. Standard library only.
Run from the gaps-filled folder:  python rebuild_index.py

Reads:
  <module-folder>/<task-folder>/STATUS.md   one card per finished task (evidence folders are skipped)
  <module-folder>/screen-only.csv           columns task_code, task_name, reason
Writes (nothing else):
  gap_index.csv      status and fill columns updated by task_code (CRLF kept)
  gap_progress.tsv   one line per module plus a total line (CRLF)
Exit code 0 = no problems, 1 = problems printed (good cards are still applied).
"""
import csv
import io
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ROOT, 'gap_index.csv')
PROGRESS = os.path.join(ROOT, 'gap_progress.tsv')

MODULES = ['Common Features', 'Security', 'General Ledger', 'Payables', 'Receivables', 'Cash Management',
           'Fixed Assets', 'Expenses', 'Revenue Management', 'Project Financial Management', 'Purchasing',
           'Procurement', 'Sourcing and Supplier Management', 'Inventory Management', 'Order Management',
           'Manufacturing', 'Cost Management', 'Supply Planning', 'Maintenance']
SLUG = {m.lower().replace(' ', '-'): m for m in MODULES}          # folder name -> module name
KEYS = ['task_code', 'task_name', 'module', 'status', 'filled_by', 'date', 'minutes_to_write',
        'minutes_to_test', 'waiting_minutes', 'fresh_claude_pass', 'route', 'depends_on',
        'test_records', 'notes']
OPTIONAL = ['retest_after_wording_fix']
CARD_STATUS = {'tested', 'written', 'failed', 'screen-only', 'open'}  # screen-only card: a route was tried and proven not to work; open card: set back to open with its findings (verification run 2026-11-26)
SKIP_DIRS = {'evidence'}  # also skipped: names starting with '_' or '.' (work and shared folders)

problems = []
warnings = []


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, '/')


def read_card(path):
    """Return dict of keys, or None after recording a problem."""
    data, order, bad = {}, [], False
    with open(path, encoding='utf-8-sig') as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            if ':' not in line:
                problems.append(f'{rel(path)}: line {n} is not "key: value": {line[:60]}')
                bad = True
                continue
            k, v = line.split(':', 1)
            k, v = k.strip(), v.strip()
            if k in data:
                problems.append(f'{rel(path)}: key "{k}" appears twice')
                bad = True
            data[k] = v
            order.append(k)
    missing = [k for k in KEYS if k not in data or data[k] == '']
    if missing:
        problems.append(f'{rel(path)}: missing key(s) or empty value: {", ".join(missing)}')
        bad = True
    extra = [k for k in data if k not in KEYS + OPTIONAL]
    if extra:
        warnings.append(f'{rel(path)}: unknown key(s) ignored: {", ".join(extra)}')
    if not missing and [k for k in order if k in KEYS] != KEYS:
        warnings.append(f'{rel(path)}: keys are not in the standard order')
    if data.get('status') and data['status'] not in CARD_STATUS:
        problems.append(f'{rel(path)}: unknown status "{data["status"]}" (use tested, written, failed, screen-only or open)')
        bad = True
    if data.get('module') and data['module'] not in MODULES:
        problems.append(f'{rel(path)}: module "{data["module"]}" is not one of the 19 tracker modules')
        bad = True
    return None if bad else data


def find_cards():
    cards = []
    for top in sorted(os.listdir(ROOT)):
        top_path = os.path.join(ROOT, top)
        if not os.path.isdir(top_path) or top in SKIP_DIRS or top[0] in '_.':
            continue
        for dirpath, dirnames, filenames in os.walk(top_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and d[0] not in '_.')
            if 'STATUS.md' in filenames:
                cards.append((top, os.path.join(dirpath, 'STATUS.md')))
    return cards


def main():
    raw = open(INDEX, 'rb').read().decode('utf-8')
    rows = list(csv.reader(io.StringIO(raw, newline='')))
    header, body = rows[0], rows[1:]
    if 'screen_only' not in header:
        sys.exit('gap_index.csv has no screen_only column; nothing changed')
    col = {h: i for i, h in enumerate(header)}
    by_code = {}
    for r in body:
        if r[col['task_id']] in by_code:
            problems.append(f'gap_index.csv: task_code {r[col["task_id"]]} has two rows')
        by_code[r[col['task_id']]] = r
        if r[col['module']] not in MODULES:
            problems.append(f'gap_index.csv: {r[col["task_id"]]} has module "{r[col["module"]]}", not in the list')

    # ---- cards ----
    found = find_cards()
    per_code = defaultdict(list)
    for top, path in found:
        if top not in SLUG:
            problems.append(f'{rel(path)}: folder "{top}" is not a module folder of the 19 modules')
            continue
        card = read_card(path)
        if card is None:
            continue
        if card['module'] != SLUG[top]:
            problems.append(f'{rel(path)}: module "{card["module"]}" does not match its folder "{top}"')
            continue
        skill = os.path.join(os.path.dirname(path), 'SKILL.md')
        if card['status'] == 'tested' and not os.path.isfile(skill):
            problems.append(f'{rel(path)}: status tested but no SKILL.md beside it')
            continue
        if card['task_code'] not in by_code:
            problems.append(f'{rel(path)}: task_code {card["task_code"]} is not in gap_index.csv')
            continue
        card['_path'] = path
        card['_skill'] = rel(skill) if os.path.isfile(skill) else ''
        per_code[card['task_code']].append(card)

    applied = set()
    screen = set()  # screen-only rows (from cards and from screen-only.csv lists)
    for code, cards in per_code.items():
        if len(cards) > 1:
            problems.append(f'task_code {code} has {len(cards)} cards: '
                            + '; '.join(rel(c['_path']) for c in cards) + ' (none applied)')
            continue
        c, r = cards[0], by_code[code]
        if r[col['module']] != c['module']:
            problems.append(f'{rel(c["_path"])}: module "{c["module"]}" but gap_index.csv says "{r[col["module"]]}"')
            continue
        def put(name, value):
            if name == 'date':  # some colleague cards write dd/mm/yyyy; the index keeps yyyy-mm-dd
                d = value.split('/')
                if len(d) == 3 and len(d[2]) == 4 and d[0].isdigit() and d[1].isdigit():
                    value = f'{d[2]}-{int(d[1]):02d}-{int(d[0]):02d}'
            r[col[name]] = '' if value in ('unknown', 'none') else value
        put('status', c['status'])
        put('skill_path', c['_skill'])
        for k in ('filled_by', 'date', 'minutes_to_write', 'minutes_to_test', 'fresh_claude_pass', 'depends_on'):
            put(k, c[k])
        if c['status'] in ('tested', 'written'):
            r[col['screen_only']] = 'no'
        if c['status'] == 'screen-only':
            r[col['screen_only']] = 'yes'
            screen.add(code)
        applied.add(code)

    # ---- screen-only lists ----
    for slug, module in SLUG.items():
        path = os.path.join(ROOT, slug, 'screen-only.csv')
        if not os.path.isfile(path):
            continue
        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or 'task_code' not in reader.fieldnames:
                problems.append(f'{rel(path)}: no task_code column (need task_code, task_name, reason)')
                continue
            for n, s in enumerate(reader, 2):
                code = (s.get('task_code') or '').strip()
                if not code:
                    continue
                if code not in by_code:
                    problems.append(f'{rel(path)} line {n}: task_code {code} is not in gap_index.csv')
                    continue
                r = by_code[code]
                if r[col['module']] != module:
                    problems.append(f'{rel(path)} line {n}: {code} belongs to {r[col["module"]]}, not {module}')
                    continue
                if code in applied and r[col['status']] == 'screen-only':
                    continue  # the card says screen-only too
                if code in applied:
                    problems.append(f'{rel(path)} line {n}: {code} also has a STATUS.md card; card kept')
                    continue
                if not (s.get('reason') or '').strip():
                    warnings.append(f'{rel(path)} line {n}: {code} has no reason')
                r[col['status']] = 'screen-only'
                r[col['screen_only']] = 'yes'
                screen.add(code)

    # rows left marked screen-only that no list names any more go back to open
    for code, r in by_code.items():
        if r[col['status']] == 'screen-only' and code not in screen:
            r[col['status']] = 'open'
            r[col['screen_only']] = 'unknown'
            warnings.append(f'{code}: no longer in any screen-only.csv, set back to open')
        elif r[col['status']] in CARD_STATUS and code not in applied and code not in screen:
            warnings.append(f'{code}: gap_index.csv says {r[col["status"]]} but no STATUS.md card was applied (left as is)')

    # ---- write index (CRLF) ----
    buf = io.StringIO()
    csv.writer(buf, lineterminator='\r\n').writerows([header] + body)
    new = buf.getvalue()
    if new != raw:
        with open(INDEX, 'wb') as f:
            f.write(new.encode('utf-8'))

    # ---- progress ----
    stats = {m: Counter() for m in MODULES}
    last = {m: '' for m in MODULES}
    for r in body:
        m = r[col['module']]
        if m not in stats:
            continue
        st = r[col['status']]
        stats[m]['Missing'] += 1
        key = {'tested': 'Tested', 'written': 'Written', 'screen-only': 'Screen-only'}.get(st, 'Open')
        stats[m][key] += 1
        if r[col['date']] > last[m]:
            last[m] = r[col['date']]
    cols = ['Module', 'Missing', 'Tested', 'Written', 'Open', 'Screen-only', '% done', 'Last update']

    def line(name, s, upd):
        base = s['Missing'] - s['Screen-only']
        pct = round(100.0 * s['Tested'] / base, 1) if base > 0 else 0.0
        return [name] + [str(s[k]) for k in cols[1:6]] + [f'{pct}', upd or '-']
    out = [cols] + [line(m, stats[m], last[m]) for m in MODULES]
    total = sum(stats.values(), Counter())
    out.append(line('All 19 modules', total, max(last.values())))
    with open(PROGRESS, 'wb') as f:
        f.write(''.join('\t'.join(x) + '\r\n' for x in out).encode('utf-8'))

    # ---- report ----
    print(f'Cards found: {len(found)}; applied: {len(applied)}; screen-only rows: {len(screen)}')
    print(f'gap_index.csv: {"updated" if new != raw else "no change"}; gap_progress.tsv written')
    print()
    widths = [max(len(x[i]) for x in out) for i in range(len(cols))]
    for x in out:
        print('  '.join(v.ljust(widths[i]) for i, v in enumerate(x)))
    if warnings:
        print(f'\nWarnings ({len(warnings)}):')
        for w in warnings:
            print('  - ' + w)
    if problems:
        print(f'\nPROBLEMS ({len(problems)}):')
        for p in problems:
            print('  - ' + p)
        return 1
    print('\nNo problems.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
