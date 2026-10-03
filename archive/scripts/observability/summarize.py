"""Selection sensitivity on unchanged publisher labels; separate from rescoring."""
import csv
import json
from common import ROOT, save

rows=json.loads((ROOT/'results/audit-evidence.json').read_text())
excluded_tasks={r['user_task'] for r in rows if r['previously_excluded']}
table=[]
for arm in sorted({r['pipeline'] for r in rows}):
    selected=[r for r in rows if r['pipeline']==arm]
    matched=[r for r in selected if r['user_task'] not in excluded_tasks]
    assert len(selected)==40 and len(matched)==29
    counts={}
    for policy in ['strict','contract']:
        successes=sum(r[policy]=='success' for r in selected)
        unknown=sum(r[policy]=='unknown' for r in selected)
        counts[policy+'_lower']=successes
        counts[policy+'_upper']=successes+unknown
        counts[policy+'_unknown']=unknown
    table.append(dict(pipeline=arm, full_n=40, retained_n=29,
        full_publisher_successes=sum(r['publisher_security'] is True for r in selected),
        retained_publisher_successes=sum(r['publisher_security'] is True for r in matched),**counts))
save('results/selection-comparison.json',table)
with (ROOT/'results/selection-comparison.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(table[0]))
    writer.writeheader();writer.writerows(table)
print(json.dumps(table,indent=2))
