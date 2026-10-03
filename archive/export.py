"""Copy only the explicit allowlist to a new PRIVATE directory; no publication."""
import argparse
import json
from pathlib import Path
import shutil
from verify import ROOT, verify

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('destination',type=Path); args=p.parse_args()
    verify()
    destination=args.destination.resolve()
    if destination==ROOT or ROOT in destination.parents: raise SystemExit('Choose a directory outside the package')
    destination.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'EXPORT-MANIFEST.json').read_text())
    for name in [r['path'] for r in manifest['files']]+['EXPORT-MANIFEST.json']:
        target=destination/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target)
    print('Created private allowlisted copy; publication is not approved.')
if __name__=='__main__': main()
