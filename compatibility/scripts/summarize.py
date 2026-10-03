import json,collections,subprocess,sys,hashlib,ast,difflib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'results';repo=Path(__import__('os').environ['AGENTDOJO_SOURCE'])
cs=json.loads((O/'changes.json').read_text());comp=json.loads((O/'comparisons.json').read_text());out={}
for a,rs in cs.items():
    out[a]={'changed_cells':len(rs),'unique_changed_tasks':sorted({tuple(r['cell'][1:]) for r in rs}),'per_nominal_version':dict(collections.Counter(r['cell'][0] for r in rs)),
      'goals_unchanged':all(r['before']['goal']==r['after']['goal'] for r in rs),'prompts_unchanged':all(r['before']['prompt']==r['after']['prompt'] for r in rs),
      'ground_truth_source_unchanged':all(r['before']['methods']['ground_truth']['sha256']==r['after']['methods']['ground_truth']['sha256'] for r in rs)}
out['ambiguous_tasks']=sorted({tuple(r['cell'][1:]) for r in comp['default']['ambiguous']})
out['static_exclusions']={'cells':len(comp['default']['unexpected']),'tasks':sorted({tuple(r[1:]) for r in comp['default']['unexpected']}),'reason':'create_user_task_with_output/combinator-created tasks, not top-level decorated classes; native identity impact and registered-only parity still cover them','source_locators':['src/agentdojo/default_suites/v1/workspace/user_tasks.py:1523-1564','src/agentdojo/default_suites/v1/slack/user_tasks.py:687-711']}
for v in ['v1','v1_1_2']:
 f=repo/f'src/agentdojo/default_suites/{v}/workspace/user_tasks.py';tree=ast.parse(f.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='UserTask13');s=ast.get_source_segment(f.read_text(),cls);(O/f'user-task-13-{v}.txt').write_text(s+'\n')
(O/'user-task-13.diff').write_text(''.join(difflib.unified_diff((O/'user-task-13-v1.txt').read_text().splitlines(True),(O/'user-task-13-v1_1_2.txt').read_text().splitlines(True),fromfile='v1/UserTask13',tofile='v1_1_2/UserTask13')))
gates=[]
for arm in ['default','late','rebuilt']:
 cmd=[sys.executable,'-B',str(R/'scripts/regression_gate.py'),'--arm',arm];p=subprocess.run(cmd,text=True,capture_output=True);assert p.returncode==1
 gates.append({'command':cmd,'exit_code':p.returncode,'result':json.loads(p.stdout),'stderr':p.stderr})
out['regression_gates']=gates
(O/'impact-summary.json').write_text(json.dumps(out,indent=2)+'\n')
manifest=json.loads((R/'sources/input-manifest.json').read_text());assert all(hashlib.sha256((repo/f).read_bytes()).hexdigest()==s for f,s in manifest['files'].items())
print(json.dumps(out,indent=2))
