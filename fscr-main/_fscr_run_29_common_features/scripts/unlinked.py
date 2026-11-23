# Run 29: find FSCR files that name an in-scope task code that Run 07 shows with no skill. Read-only.
import csv, os, re, collections, sys
base = sys.argv[1]
out = os.path.join(base, '_fscr_run_29_common_features')
r = list(csv.DictReader(open(os.path.join(out, 'common_features_tasks.csv'), encoding='utf-8')))
codes = {x['task_code'] for x in r if x['skill_or_guide'] == 'none'}
root = os.path.join(base, 'fscr-main')
skip = [os.path.join(root, 'knowledge', 'setup-task-catalog'), os.path.join(root, 'project')]
hits = collections.defaultdict(set)
pat = re.compile(r'\b(' + '|'.join(re.escape(c) for c in sorted(codes, key=len, reverse=True)) + r')\b')
for dp, dn, fn in os.walk(root):
    if any(dp.startswith(s) for s in skip):
        continue
    for f in fn:
        if not f.endswith(('.md', '.json', '.yaml', '.yml')):
            continue
        p = os.path.join(dp, f)
        try:
            s = open(p, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        for m in set(pat.findall(s)):
            hits[m].add(os.path.relpath(p, root).replace(os.sep, '/'))
with open(os.path.join(out, 'unlinked_mentions.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['task_code', 'task_name', 'files_naming_code'])
    for x in r:
        if x['task_code'] in hits:
            w.writerow([x['task_code'], x['task_name'], ' | '.join(sorted(hits[x['task_code']]))])
            print(x['task_code'], '|', x['task_name'], '|', sorted(hits[x['task_code']])[:3], len(hits[x['task_code']]))
print(len(hits), 'of', len(codes))
