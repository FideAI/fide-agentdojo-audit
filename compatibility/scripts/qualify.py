import sys,ast,socket,traceback,json,hashlib,collections,importlib,subprocess
from types import SimpleNamespace as NS
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=Path(__import__('os').environ['AGENTDOJO_SOURCE'])
sys.dont_write_bytecode=True
# Allocate unconnected sockets before the gate; no bind/connect/send.
socks=[socket.socket() for _ in range(2)]
attempts=[]
tree=ast.parse((ROOT/'scripts/worker.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='gate')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'exact-worker-gate','exec'))
sys.addaudithook(gate)
checks=[]
for name,fn in [('connect',lambda:socks[0].connect(('127.0.0.1',9))),('connect_ex',lambda:socks[1].connect_ex(('127.0.0.1',9))),('create_connection',lambda:socket.create_connection(('127.0.0.1',9))),('process',lambda:subprocess.run([sys.executable,'-c','raise SystemExit(99)']))]:
    before=len(attempts)
    try:fn()
    except PermissionError:checks.append({'operation':name,'blocked':True,'events':[x['event'] for x in attempts[before:]]})
    else:raise AssertionError('Gate failed: '+name)
for s in socks:s.close()
attempts.clear();sys.path.insert(0,str(REPO/'src'))
from agentdojo.task_suite import load_suites
old=load_suites.get_suite('v1','workspace').get_user_task_by_id('user_task_13')
importlib.import_module('agentdojo.default_suites.v1_1_2')
# The public cached getter may retain the object if called before import; the properties show current registry selection.
new=load_suites.get_suite('v1','workspace').user_tasks['user_task_13']
rows=[]
for t,label in [(old,'before_import'),(new,'after_late_import')]:
    m=sys.modules[type(t).__module__]
    saved={name:getattr(m,name) for name in ['check_added_to_file','check_new_email']}
    try:
        for name in saved:setattr(m,name,lambda *a,**k:True)
        for case,recipient in [('lowercase',t._SENDER),('uppercase',t._SENDER.upper()),('wrong','different@example.test')]:
            email=NS(subject=t._EMAIL_2_SUBJECT,recipients=[recipient],body=' '.join(t._NAMES+t._SCORES))
            pre=NS(inbox=NS(_get_next_id=lambda:'new'));post=NS(inbox=NS(emails={'new':email}))
            rows.append({'arm':label,'case':case,'module':type(t).__module__,'utility':bool(t.utility('',pre,post))})
    finally:
        for name,f in saved.items():setattr(m,name,f)
assert [x['utility'] for x in rows]==[True,False,False,True,True,False]
# Full native registered-only parity independent of the static-declaration inventory.
parity={}; socket_events={}
for arm in ['default','late','rebuilt']:
    data=json.loads((ROOT/f'results/{arm}.json').read_text());bad=[]
    for r in data['rows']:
        compatible=[v for v in r['registered'] if tuple(v['version'])<=tuple(r['target'])]
        top=sorted(compatible,key=lambda v:v['version'])[-1]
        if (top['module'],top['class'])!=(r['selected']['module'],r['selected']['class']):bad.append(r)
    parity[arm]={'checked':len(data['rows']),'violations':len(bad)};assert not bad
    socket_events[arm]=dict(collections.Counter(x['event'] for x in data['unexpected_network_or_process_attempts']))
result={'guard_worker_sha256':hashlib.sha256((ROOT/'scripts/worker.py').read_bytes()).hexdigest(),'guard_checks':checks,'utility_branch_controls':rows,'qualification_import_blocked_events':[x['event'] for x in attempts],'native_registered_only_parity':parity,'worker_blocked_events_excluding_selftest':socket_events,'scope':'Utility helpers check_added_to_file and check_new_email held true; no complete-task or live-tool claim. Guard is Python-level, not OS sandbox.'}
(ROOT/'results/qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
