"""Read-back check for a flexfield that had NO user context before the load (so the before-export
was empty and the after-export suddenly lists all its seeded contexts and segments).
GoSaaS helper, not official FSCR. Offline, standard library only. Never prints who columns.

python -I check_dff_rows.py --export-dir EXP2/unz --dff XLE_LE_INFO_DEV --date 2026/11/26 --prefix GAPFILL_XX_ \
    --expect-context GAPFILL_XX_CTX1 --expect-segment GAPFILL_XX_SEG1

For every CSV it counts the rows of --dff whose CreationDate or LastUpdateDate is on --date
(format as in the export, yyyy/mm/dd). PASS (exit 0) = the only rows created or updated on that date are
the expected context and segment (both present), and they start with --prefix. Any other row touched on
that date (for example the flexfield's parent row or a seeded context) gives FAIL.
"""
import argparse, csv, glob, os, sys

ap = argparse.ArgumentParser()
for x in ('--export-dir', '--dff', '--date', '--prefix', '--expect-context', '--expect-segment'):
    ap.add_argument(x, required=True)
a = ap.parse_args()
K = 'FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode'
bad, seen = [], set()
for f in sorted(glob.glob(os.path.join(a.export_dir, '*.csv'))):
    with open(f, encoding='utf-8-sig', newline='') as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get(K) or r.get('DescriptiveFlexfieldCode')) == a.dff]
    if not rows:
        continue
    hit = [r for r in rows if a.date in (r.get('CreationDate', '') + ' ' + r.get('LastUpdateDate', ''))]
    name = os.path.basename(f)
    print(f'{name}: {len(rows)} rows of {a.dff}; created/updated on {a.date}: {len(hit)}')
    for r in hit:
        code = r.get('SegmentCode') or r.get('ContextCode') or r.get('DescriptiveFlexfieldCode')
        if name == 'ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv' and code == a.expect_context:
            seen.add('context')
        elif name == 'ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv' and code == a.expect_segment:
            seen.add('segment')
        else:
            bad.append(f'{name}: {code}')
for x in (a.expect_context, a.expect_segment):
    if not x.startswith(a.prefix):
        bad.append(f'{x} does not start with {a.prefix}')
for b in bad:
    print('   unexpected: ' + b)
ok = not bad and seen == {'context', 'segment'}
if seen != {'context', 'segment'}:
    print('   missing: ' + ', '.join(sorted({'context', 'segment'} - seen)))
print('RESULT: PASS' if ok else 'RESULT: FAIL')
sys.exit(0 if ok else 1)
