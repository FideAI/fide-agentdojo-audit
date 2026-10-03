"""Pinned, offline-only execution context for this private follow-up."""
from pathlib import Path
import hashlib
import json
import socket
import subprocess

from context import trace_root as ROOT, outcome_root as PRIOR, REPO, PIN, NETWORK_ATTEMPTS

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + '\n')

def content_text(content):
    if isinstance(content, str):
        return content
    return '\n'.join(x.get('content', x.get('text', '')) for x in content or [] if isinstance(x, dict))
