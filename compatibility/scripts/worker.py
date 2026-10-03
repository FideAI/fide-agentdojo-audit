"""Fresh-process native dispatch observation. No agent/tool execution."""
import sys, socket, json, hashlib, inspect, importlib, traceback
from pathlib import Path
REPO=Path(sys.argv[1]).resolve(); arm=sys.argv[2]
sys.dont_write_bytecode=True
attempts=[]
def gate(event,args):
    if event.startswith('socket.') or event in ('subprocess.Popen','os.system','os.posix_spawn'):
        attempts.append({'event':event,'stack':traceback.format_stack(limit=8)}); raise PermissionError('offline worker: '+event)
sys.addaudithook(gate)
try: socket.socket()
except PermissionError: pass
else: raise AssertionError('network block inactive')
control_attempts=list(attempts);attempts.clear()
sys.path.insert(0,str(REPO/'src'))
from agentdojo.task_suite import load_suites
if arm != 'default':
    importlib.import_module('agentdojo.default_suites.v1_1_2')
if arm == 'rebuilt': importlib.reload(load_suites)
def identity(task):
    cls=type(task); file=Path(inspect.getfile(cls)).resolve()
    result={'module':cls.__module__,'class':cls.__name__,'file':str(file.relative_to(REPO)),
        'file_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'class_sha256':hashlib.sha256(inspect.getsource(cls).encode()).hexdigest(),
        'ID':task.ID,'goal':getattr(task,'GOAL',None),'prompt':getattr(task,'PROMPT',None),'methods':{}}
    for method in ('security','utility','ground_truth','init_environment'):
        f=getattr(cls,method,None)
        if f:
            result['methods'][method]={'module':f.__module__,'sha256':hashlib.sha256(inspect.getsource(f).encode()).hexdigest()}
    return result
rows=[]
for version,suites in load_suites._SUITES.items():
    for name,suite in suites.items():
        for kind in ('user','injection'):
            registry=getattr(suite,'_'+kind+'_tasks'); selected=getattr(suite,kind+'_tasks')
            for tid,t in selected.items():
                variants=registry[tid]
                registered=[{'version':list(v),'module':type(x).__module__,'class':type(x).__name__} for v,x in variants.items()]
                getter=getattr(suite,'get_'+kind+'_task_by_id')(tid)
                rows.append({'version':version,'suite':name,'target':list(suite.benchmark_version),'kind':kind,'task_id':tid,
                    'selected':identity(t),'getter_agrees':type(getter) is type(t),'registered':registered})
print(json.dumps({'arm':arm,'python':sys.version,'network_gate_control':control_attempts,'unexpected_network_or_process_attempts':attempts,'rows':rows},indent=2))
