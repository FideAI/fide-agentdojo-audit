"""Reproduce compatibility observations in a fresh directory; never overwrite released results."""
import argparse,hashlib,importlib.metadata,json,os,platform,shutil,subprocess,sys,uuid
from pathlib import Path
from project import project
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
NAMES=['summary','comparisons','changes','controls','declarations','expected','suite-targets','default','late','rebuilt','impact-summary','qualification']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=REPO/'archive/.local/agentdojo');p.add_argument('--output',type=Path);a=p.parse_args()
 if sys.version_info[:2]!=(3,11):raise SystemExit('Use Python 3.11')
 installed={d.metadata['Name'].lower().replace('_','-'):d.version for d in importlib.metadata.distributions()}
 for row in (REPO/'requirements.lock').read_text().splitlines():
  name,version=row.split('==')
  if installed.get(name.lower().replace('_','-'))!=version:raise SystemExit('Dependency mismatch: '+row)
 source=a.source.resolve();spec=json.loads((ROOT/'source-files.json').read_text())
 def clean():
  assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==spec['pin']
  assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
  assert all(sha(source/f)==h for f,h in spec['files'].items())
 clean()
 for doc,freeze in [('PROTOCOL.md','protocol-freeze.json'),('AMENDMENT.md','AMENDMENT.freeze.json')]:
  assert sha(ROOT/doc)==json.loads((ROOT/freeze).read_text())['sha256']
 out=(a.output or REPO/'runs'/('compatibility-'+uuid.uuid4().hex[:12])).resolve()
 if REPO==out or REPO in out.parents and out.relative_to(REPO).parts[0]!='runs':raise SystemExit('In-repository outputs must be under runs/')
 out.mkdir(parents=True,exist_ok=False)
 for d in ['results','sources','logs']:(out/d).mkdir()
 shutil.copytree(ROOT/'scripts',out/'scripts')
 for n in ['PROTOCOL.md','AMENDMENT.md','protocol-freeze.json','AMENDMENT.freeze.json']:shutil.copyfile(ROOT/n,out/n)
 env={k:os.environ[k] for k in ['PATH','HOME','TMPDIR','SYSTEMROOT'] if k in os.environ}
 env.update(AGENTDOJO_SOURCE=str(source),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',LANGSMITH_TRACING='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
 for n in ['audit.py','qualify.py','summarize.py']:
  with (out/'logs'/f'{n}.log').open('x') as log:r=subprocess.run([sys.executable,'-B',str(out/'scripts'/n)],cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode:raise SystemExit(f'Failed {n}; inspect {out}/logs')
 for n in NAMES:
  actual=project(json.loads((out/'results'/f'{n}.json').read_text()));expected=json.loads((ROOT/'results'/f'{n}.json').read_text())
  if actual!=expected:raise SystemExit('Projected observations differ: '+n)
 assert (out/'results/user-task-13.diff').read_bytes()==(ROOT/'results/user-task-13.diff').read_bytes()
 clean()
 report={'passed':True,'projected_result_files_match':len(NAMES),'source_files_unchanged':len(spec['files']),'upstream_commit':spec['pin'],'python':platform.python_version(),'platform':platform.platform(),'native_cells_per_arm':892,'arms':3,'utility_branch_controls':6,'expected_blanket_repair_gate_exit':1,'scope':'Portable adapted-script computational rerun; not independent human review or new model outcomes.'}
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
