"""Optional native fixtures or inert archive analysis, in new isolated output trees."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import project
from check_fixtures import check
from verify import verify

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['fixtures','full'],default='fixtures')
    p.add_argument('--classifier',choices=['original','amended'],default='original',help='Archive classifier; original preserves frozen reproduction')
    p.add_argument('--source',type=Path,default=ROOT/'.local/agentdojo')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    if sys.version_info[:2]!=(3,11): raise SystemExit('Use Python 3.11 for native reproduction')
    verify()
    source=args.source.resolve()
    if not (source/'.git').is_dir(): raise SystemExit('Run acquire.py first; source checkout is missing')
    # Exact frozen versions, never silently resolve substitute versions.
    installed={d.metadata['Name'].lower().replace('_','-'):d.version for d in importlib.metadata.distributions()}
    for row in (ROOT/'requirements.lock').read_text().splitlines():
        name,version=row.split('==')
        if installed.get(name.lower().replace('_','-'))!=version:
            raise SystemExit('Dependency mismatch: '+row)
    output=(args.output or ROOT/'runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8])).resolve()
    if output==ROOT or ROOT in output.parents and output.relative_to(ROOT).parts[0]!='runs':
        raise SystemExit('Outputs inside the package must be under runs/')
    output.mkdir(parents=True,exist_ok=False)
    (output/'logs').mkdir()
    # Only basic process variables are inherited; no provider tokens, proxies or tracing credentials.
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','SYSTEMROOT') if k in os.environ}
    env.update(PYTHONPATH=str(ROOT/'scripts'),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',
               COMPANION_RUN=str(output),COMPANION_SOURCE=str(source),LANGSMITH_TRACING='false',
               HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    sequence=['outcome/probe.py','outcome/registration_test.py','outcome/scope_controls.py','observability/native_controls.py','observability/check_amendment.py']
    if args.mode=='full': sequence+=['outcome/scan_records.py','outcome/adjudicate.py','outcome/compare_scores.py','observability/audit.py' if args.classifier=='original' else 'observability/run_amended_audit.py','observability/summarize.py']
    for script in sequence:
        with (output/'logs'/(script.replace('/','-')+'.log')).open('x') as log:
            result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts'/script)],cwd=output,env=env,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode: raise SystemExit('Failed '+script+'; inspect the isolated run log')
    amendment=json.loads((output/'observability/results/amendment-controls.json').read_text())
    assert amendment['passed'] and len(amendment['controls'])==13 and not amendment['network_attempts']
    report=dict(mode=args.mode,archive_classifier=args.classifier,amended_classifier_controls=13,python=platform.python_version(),platform=platform.platform(),
                upstream_commit=json.loads((ROOT/'source.json').read_text())['commit'],
                dependency_lock_sha256=hashlib.sha256((ROOT/'requirements.lock').read_bytes()).hexdigest(),
                fixtures=check(output),scope='Adapted scripts run by same assistant; not independent human review')
    if args.mode=='full':
        def read(path): return json.loads(path.read_text())
        checks=[('outcome/results/record-evidence.json','record-count-inputs.json',project.records),
                ('outcome/results/adjudication.json','adjudication-count-inputs.json',project.adjudications),
                ('outcome/results/comparison-evidence.json','comparison-count-inputs.json',project.comparison),
                ('observability/results/audit-evidence.json','observability-count-inputs.json',project.observability)]
        for generated,expected,fn in checks:
            if fn(read(output/generated))!=read(ROOT/'data'/expected): raise ValueError('Projected rows differ: '+generated)
        for component,name in [('outcome','outcome-cohort.json'),('observability','observability-cohort.json')]:
            if read(output/component/'sources/cohort-manifest.json')!=read(ROOT/'manifests'/name): raise ValueError('Raw record manifest differs: '+component)
        report['inert_archive_analysis']=dict(projected_tables_match=4,cohort_hashes_match=7400,selected_hashes_match=200,
                    note='Same copied analysis logic on acquired raw records; not independently implemented adjudication')
    if subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True):
        raise ValueError('Source changed during reproduction')
    report['source_clean_after']=True
    report['passed']=True
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
