"""Explicit public source download only; no installation or code execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
spec=json.loads((ROOT/'source.json').read_text())
def git(*args):
    return subprocess.check_output(['git','-c','core.hooksPath=/dev/null',*args],text=True)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination',type=Path,default=ROOT/'.local/agentdojo')
    args=p.parse_args(); dest=args.destination.resolve()
    if dest.exists(): raise SystemExit('Destination exists; refusing to overwrite it')
    dest.mkdir(parents=True)
    git('init',str(dest))
    git('-C',str(dest),'remote','add','origin',spec['repository'])
    git('-C',str(dest),'fetch','--depth','1','origin',spec['commit'])
    git('-C',str(dest),'checkout','--detach',spec['commit'])
    assert git('-C',str(dest),'rev-parse','HEAD').strip()==spec['commit']
    assert not git('-C',str(dest),'status','--porcelain')
    assert hashlib.sha256((dest/'LICENSE').read_bytes()).hexdigest()==spec['license_sha256']
    print(json.dumps(dict(acquired=True,commit=spec['commit'],source_clean=True)))
if __name__=='__main__': main()
