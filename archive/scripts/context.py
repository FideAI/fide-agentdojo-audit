"""Shared context for explicit optional reproduction; no implicit sibling paths."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parents[1]
PIN = json.loads((PACKAGE/'source.json').read_text())['commit']
REPO = Path(os.environ['COMPANION_SOURCE']).resolve()
RUN = Path(os.environ['COMPANION_RUN']).resolve()
if not RUN.is_dir() or RUN == PACKAGE or PACKAGE in RUN.parents and 'runs' not in RUN.relative_to(PACKAGE).parts:
    raise RuntimeError('Runner must create a separate output directory')
if subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip() != PIN:
    raise RuntimeError('Wrong source commit')
if subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True):
    raise RuntimeError('Source checkout is not clean')
for name,digest in json.loads((PACKAGE/'manifests/upstream-code.json').read_text()).items():
    if hashlib.sha256((REPO/name).read_bytes()).hexdigest() != digest:
        raise RuntimeError('Source hash mismatch: '+name)
# No editable installation or unrelated installed AgentDojo can shadow this source.
sys.path.insert(0,str(REPO/'src'))
outcome_root = RUN/'outcome'
trace_root = RUN/'observability'
for root in (outcome_root,trace_root):
    for name in ('results','sources'): (root/name).mkdir(parents=True,exist_ok=True)
NETWORK_ATTEMPTS=[]
def deny(*args,**kwargs):
    NETWORK_ATTEMPTS.append('blocked')
    raise RuntimeError('Network disabled during reproduction')
for name in ('connect','connect_ex','sendto','sendmsg'):
    if hasattr(socket.socket,name): setattr(socket.socket,name,deny)
socket.create_connection=deny
socket.getaddrinfo=deny
socket.gethostbyname=deny
def audit(event,args):
    if event in ('socket.connect','socket.sendto','socket.getaddrinfo','subprocess.Popen','os.system','os.posix_spawn'):
        deny()
sys.addaudithook(audit)
