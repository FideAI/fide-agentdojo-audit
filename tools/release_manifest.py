"""Refresh reviewed content inventory. Inspect changes before committing this manifest."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
SKIP={'.git','.venv','.figures-venv','runs','.local','__pycache__','.mpl-cache'}
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and not any(x in SKIP for x in p.relative_to(R).parts) and p.name not in {'RELEASE-MANIFEST.json','.DS_Store'} and p.suffix!='.pyc'}
(R/'RELEASE-MANIFEST.json').write_text(json.dumps({'files':files,'scope':'Explicit prepared release contents. Hash integrity is not human review or authenticity.'},indent=2)+'\n')
print(f'Manifest: {len(files)} files')
