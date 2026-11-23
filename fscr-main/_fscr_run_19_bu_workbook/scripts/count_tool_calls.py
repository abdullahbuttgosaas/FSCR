"""Run 19: count tool calls in this session's transcript from the Run 19 request onward (deduplicated by tool_use id)."""
import json,sys,collections
p=sys.argv[1]; start=None; ids={}; names=collections.Counter()
for line in open(p,encoding='utf-8'):
    try: m=json.loads(line)
    except Exception: continue
    msg=m.get('message') or {}; c=msg.get('content')
    if start is None and m.get('type')=='user' and 'RUN 19: Build the business unit workbook' in json.dumps(c): start=m.get('timestamp'); continue
    if start and m.get('type')=='assistant' and isinstance(c,list):
        for b in c:
            if b.get('type')=='tool_use' and b['id'] not in ids: ids[b['id']]=m.get('timestamp'); names[b['name']]+=1
print('run18 request at',start); print('tool calls',len(ids),'last at',max(ids.values()) if ids else None); print(dict(names))
