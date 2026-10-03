"""Conservative qualification gate for recorded dispatch observations, not semantic certification.
Exit 1 means this arm is NOT qualified as a blanket compatibility-preserving repair.
"""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--arm',choices=['default','late','rebuilt'],required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];c=json.loads((root/'results/comparisons.json').read_text())[a.arm]
changes=json.loads((root/'results/changes.json').read_text())[a.arm]
backward=[r['cell'] for r in changes if r['cell'][0] in ('v1','v1.1','v1.1.1')]
reasons=[]
if c['mismatches']:reasons.append(f"{len(c['mismatches'])} declaration-selection mismatches")
if c['ambiguous']:reasons.append(f"{len(c['ambiguous'])} ambiguous same-version declarations")
if c['unexpected']:reasons.append(f"{len(c['unexpected'])} generated native cells outside static oracle")
if c['missing']:reasons.append(f"{len(c['missing'])} missing native cells")
if backward:reasons.append(f"{len(backward)} changed cells in versions below the intended v1.1.2 boundary")
print(json.dumps({'arm':a.arm,'qualified_as_blanket_repair':not reasons,'reasons':reasons,'backward_changes':backward,'semantic_qualification':'not performed for every changed task'},indent=2))
raise SystemExit(bool(reasons))
