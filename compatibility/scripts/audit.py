"""Independent static declaration oracle versus native default-suite selection."""
import ast,sys,json,hashlib,subprocess,datetime,collections,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT.parents[2]
REPO=Path(__import__('os').environ['AGENTDOJO_SOURCE'])
OUT=ROOT/'results'; PIN='089ed468cf3ed0322acc66b0211f26d9d90dbf60'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
assert subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==PIN
freeze=json.loads((ROOT/'protocol-freeze.json').read_text());assert sha(ROOT/'PROTOCOL.md')==freeze['sha256']
files=sorted((REPO/'src/agentdojo').rglob('*.py'))
input_manifest={str(p.relative_to(REPO)):sha(p) for p in files}
input_manifest['pyproject.toml']=sha(REPO/'pyproject.toml')
(ROOT/'sources/input-manifest.json').write_text(json.dumps({'pin':PIN,'acquired_from':'existing frozen clone; no fetch/mutation','files':input_manifest,'python_executable':sys.executable,'python':sys.version},indent=2)+'\n')
declarations=[]; unsupported=[]
for p in sorted((REPO/'src/agentdojo/default_suites').rglob('*.py')):
    tree=ast.parse(p.read_text()); constants={}
    for n in tree.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try: constants[n.targets[0].id]=ast.literal_eval(n.value)
            except (ValueError,TypeError):pass
    for n in tree.body:
        if not isinstance(n,ast.ClassDef):continue
        for dec in n.decorator_list:
            f=dec.func if isinstance(dec,ast.Call) else dec
            if not isinstance(f,ast.Attribute) or f.attr not in ('register_user_task','register_injection_task','update_user_task','update_injection_task'):continue
            try:
                suite=p.parent.name
                assert suite in ('workspace','travel','banking','slack')
                assert isinstance(f.value,ast.Name) and f.value.id=='task_suite'
                kind='user' if 'user' in f.attr else 'injection'
                prefix='UserTask' if kind=='user' else 'InjectionTask'
                num=int(n.name.removeprefix(prefix))
                version=(1,0,0)
                if f.attr.startswith('update'):
                    arg=dec.args[0]; version=constants[arg.id] if isinstance(arg,ast.Name) else ast.literal_eval(arg)
                assert len(version)==3
                declarations.append({'suite':suite,'kind':kind,'task_id':f'{kind}_task_{num}','version':list(version),'module':'.'.join(p.relative_to(REPO/'src').with_suffix('').parts),'class':n.name,'file':str(p.relative_to(REPO)),'line':n.lineno,'decorator':f.attr,'file_sha256':sha(p)})
            except Exception as e:unsupported.append({'file':str(p),'line':n.lineno,'error':repr(e)})
assert not unsupported,unsupported
loader=REPO/'src/agentdojo/task_suite/load_suites.py'; tree=ast.parse(loader.read_text()); maps={}; targets={}
for n in tree.body:
    if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and isinstance(n.value,ast.Dict) and n.target.id.endswith('_SUITES'):
        m={}
        for k,v in zip(n.value.keys,n.value.values):
            if isinstance(v,ast.Call): target=ast.literal_eval(v.args[0])
            else: assert isinstance(v,ast.Name); target=(1,0,0)
            m[ast.literal_eval(k)]=list(target)
        maps[n.target.id]=m
for n in ast.walk(tree):
    if isinstance(n,ast.Dict) and n.keys and all(isinstance(k,ast.Constant) and isinstance(k.value,str) and k.value.startswith('v1') for k in n.keys):
        targets={k.value:maps[v.id] for k,v in zip(n.keys,n.values)}
assert len(targets)==7
save('declarations.json',declarations);save('suite-targets.json',targets)
groups=collections.defaultdict(list)
for d in declarations:groups[(d['suite'],d['kind'],d['task_id'])].append(d)
expected=[]
for version,suites in targets.items():
    for suite,target in suites.items():
        for (s,kind,tid),ds in groups.items():
            if s!=suite:continue
            candidates=[d for d in ds if tuple(d['version'])<=tuple(target)]
            if not candidates:continue
            best=max(tuple(d['version']) for d in candidates)
            chosen=[d for d in candidates if tuple(d['version'])==best]
            expected.append({'version':version,'suite':suite,'kind':kind,'task_id':tid,'target':target,'expected':chosen,'ambiguous':len(chosen)!=1})
save('expected.json',expected)
# Freeze exact generated input inventory before any native observation.
(ROOT/'input-freeze.json').write_text(json.dumps({'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'declarations_sha256':sha(OUT/'declarations.json'),'expected_sha256':sha(OUT/'expected.json'),'worker_sha256':sha(ROOT/'scripts/worker.py'),'audit_sha256':sha(Path(__file__))},indent=2)+'\n')
def key(r):return (r['version'],r['suite'],r['kind'],r['task_id'])
def sig(x):return (x['module'],x['class'])
commands=[];arms={}
for arm in ('default','late','rebuilt'):
    cmd=[sys.executable,'-B',str(ROOT/'scripts/worker.py'),str(REPO),arm];commands.append(cmd)
    r=subprocess.run(cmd,text=True,capture_output=True,cwd=ROOT)
    (OUT/f'{arm}.stderr.log').write_text(r.stderr)
    (OUT/f'{arm}.json').write_text(r.stdout)
    assert r.returncode==0,(arm,r.returncode,r.stderr)
    arms[arm]={key(x):x for x in json.loads(r.stdout)['rows']}
save('commands.json',commands)
comparisons={};changes={};registered_violations=[]
for arm,rows in arms.items():
    comparisons[arm]={'mismatches':[],'ambiguous':[],'missing':[],'unexpected':[],'match_count':0}
    for e in expected:
        r=rows.get(key(e))
        if not r:comparisons[arm]['missing'].append(e);continue
        assert r['target']==e['target'];assert r['getter_agrees']
        eligible=[x for x in r['registered'] if tuple(x['version'])<=tuple(r['target'])]
        registered_best=max(eligible,key=lambda x:tuple(x['version']))
        if sig(registered_best)!=sig(r['selected']):registered_violations.append({'arm':arm,**r})
        if e['ambiguous']:comparisons[arm]['ambiguous'].append({'cell':key(e),'candidates':e['expected'],'actual':r['selected']});continue
        if sig(e['expected'][0])!=sig(r['selected']):comparisons[arm]['mismatches'].append({'cell':key(e),'expected':e['expected'][0],'actual':r['selected']})
        else:
            assert e['expected'][0]['file_sha256']==r['selected']['file_sha256']
            comparisons[arm]['match_count']+=1
    comparisons[arm]['unexpected']=[k for k in rows if k not in {key(e) for e in expected}]
    changes[arm]=[{'cell':k,'before':arms['default'][k]['selected'],'after':r['selected']} for k,r in rows.items() if k in arms['default'] and r['selected']!=arms['default'][k]['selected']]
# Authored bad expectations are independent of native results and do not alter observations.
control=next(e for e in expected if key(e)==('v1','workspace','injection','injection_task_0'))
actual=arms['default'][key(control)]['selected']
controls={'wrong_module_detected':sig({'module':'invalid.expected.module','class':'InjectionTask0'})!=sig(actual),
 'too_early_v112_detected':sig({'module':'agentdojo.default_suites.v1_1_2.workspace.injection_tasks','class':'InjectionTask0'})!=sig(actual),
 'registered_only_rule_violations':len(registered_violations),'all_id_sets_equal':len({tuple(sorted(a)) for a in arms.values()})==1}
assert all(controls[k] for k in ['wrong_module_detected','too_early_v112_detected','all_id_sets_equal'])
assert not registered_violations
save('comparisons.json',comparisons);save('changes.json',changes);save('controls.json',controls)
summary={'declarations':len(declarations),'cells':len(expected),'arms':{a:{'native_cells':len(arms[a]),'matches':c['match_count'],'mismatches':len(c['mismatches']),'ambiguous':len(c['ambiguous']),'missing':len(c['missing']),'unexpected':len(c['unexpected']),'changed_cells':len(changes[a])} for a,c in comparisons.items()},'controls':controls}
save('summary.json',summary)
assert input_manifest=={k:sha(REPO/k) for k in input_manifest},'input changed'
print(json.dumps(summary,indent=2))
