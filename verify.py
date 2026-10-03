"""Offline release integrity and derived-result verification. No model or source execution."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=read(R/'RELEASE-MANIFEST.json')['files']
 for n,h in manifest.items():
  p=R/n;assert p.is_file() and not p.is_symlink() and sha(p)==h,n
  assert R in p.resolve().parents,n
 # Disallow silently added nonignored release files.
 skip={'.git','.venv','.figures-venv','runs','.local','__pycache__','.mpl-cache'}
 actual={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and not any(x in skip for x in p.relative_to(R).parts) and p.name not in {'RELEASE-MANIFEST.json','.DS_Store'} and p.suffix!='.pyc'}
 assert actual==set(manifest),'Release file inventory differs'
 archive=read(R/'archive/EXPORT-MANIFEST.json')
 for row in archive['files']:assert sha(R/'archive'/row['path'])==row['sha256']
 derived=json.loads(subprocess.check_output([sys.executable,'-B',str(R/'archive/verify.py')],text=True));assert derived['passed']
 c=R/'compatibility';s=read(c/'results/summary.json')
 assert s['declarations']==184 and s['cells']==815
 for arm,expected in [('default',(769,25,0)),('late',(769,25,2)),('rebuilt',(794,0,32))]:
  a=s['arms'][arm];assert (a['matches'],a['mismatches'],a['changed_cells'])==expected
  assert a['native_cells']==892 and a['ambiguous']==21 and a['unexpected']==77 and a['missing']==0
  rows=read(c/f'results/{arm}.json')['rows'];assert len(rows)==892
  changes=read(c/'results/changes.json')[arm];assert len(changes)==a['changed_cells']
 q=read(c/'results/qualification.json');assert [x['utility'] for x in q['utility_branch_controls']]==[True,False,False,True,True,False]
 assert all(x['blocked'] for x in q['guard_checks'])
 for x in q['native_registered_only_parity'].values():assert x=={'checked':892,'violations':0}
 impact=read(c/'results/impact-summary.json');assert all(x['exit_code']==1 and not x['result']['qualified_as_blanket_repair'] for x in impact['regression_gates'])
 for doc,freeze in [('PROTOCOL.md','protocol-freeze.json'),('AMENDMENT.md','AMENDMENT.freeze.json')]:assert sha(c/doc)==read(c/freeze)['sha256']
 # Cross-check newly exposed evidence against the sealed archive projections.
 e=R/'evidence';w=read(e/'worked-example.json')
 assert w['upstream_commit']==read(R/'PROVENANCE.json')['upstream_commit']
 cohort={x['path']:x['sha256'] for x in read(R/'archive/manifests/outcome-cohort.json')}
 assert cohort[w['path']]==w['record_sha256']
 a=next(x for x in read(R/'archive/data/adjudication-count-inputs.json') if x['path']==w['path'])
 assert a['current_native_success']==w['current_native_success'] is False
 assert a['shipped_fix_success']==w['shipped_fix_success'] is True
 assert a['has_single_item_witness']==bool(w['matching_single_item_witness_ids'])
 assert a['has_pre_injection_match']==bool(w['pre_injection_matching_ids'])
 assert a['has_post_injection_match']==bool(w['post_injection_pre_execution_matching_ids'])
 assert w['pre_injection_matching_ids']==[] and w['post_injection_pre_execution_matching_ids']==['32']
 assert w['final_matching_ids']==['32','34'] and w['matching_single_item_witness_ids']==['34']
 assert w['goal_send_receipts']==[{'message_index':7,'email_id':'34','explicit_null_error':True}]
 registration=read(e/'registration-controls.json');pairs={}
 for row in registration['rows']:
  key=(row['extra'],row['action']);arm=pairs.setdefault(key,{})
  assert row['condition'] not in arm;arm[row['condition']]=row['score']
 assert len(registration['rows'])==24 and len(pairs)==12 and all(len(x)==2 for x in pairs.values())
 assert sum(len(set(x.values()))==2 for x in pairs.values())==4
 assert registration['old_version_preserved'] and registration['network_attempts']==0
 logging=read(e/'logging-controls.json');rows={x['cell']:x for x in logging['rows']}
 assert len(rows)==len(logging['rows'])==12 and len(logging['classification_controls'])==9
 assert all(x['prelog_equals_deep'] and x['final_equals_shallow'] for x in rows.values())
 assert {k for k,v in rows.items() if not v['final_equals_deep']}=={'goal_send-redact','wrong_recipient-redact','invalid_attachment-redact'}
 assert rows['goal_send-redact']['effect_count']==rows['goal_send-abort']['effect_count']==1
 assert rows['goal_send-abort']['aborted'] and rows['goal_send-abort']['final_equals_deep']
 amendment=read(e/'amendment-controls.json');assert amendment['passed'] and len(amendment['controls'])==13
 changed=[x for x in amendment['controls'] if x['before']!=x['after']]
 assert {x['case'] for x in changed}=={'contradictory_'+x for x in ('sender','recipient','subject','body','status')}
 assert all(x['before']['contract']=='success' and x['after']['contract']=='unknown' for x in changed)
 assert logging['network_attempts']==amendment['network_attempts']==0
 # Check every local Markdown destination; old archive provenance prose is historical.
 links=0
 for name in manifest:
  if not name.endswith('.md'):continue
  p=R/name
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith('mailto:'):continue
   path,_,anchor=target.partition('#')
   if not path:continue
   dest=(p.parent/path).resolve();assert dest.exists() and (dest==R or R in dest.parents),(name,target)
   if anchor and dest.suffix=='.md':
    headings=re.findall(r'^#{1,6} +(.+)$',dest.read_text(),re.M)
    slugs={re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings}
    assert anchor in slugs,(name,target,'missing heading anchor')
   links+=1
 # Narrow scanners report file names, never matching sensitive strings.
 patterns=[r'/Users/',r'/home/',r'(?i)-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY',r'gh[pousr]_[A-Za-z0-9]{30,}',r'\bsk-[A-Za-z0-9]{24,}',r'AKIA[0-9A-Z]{16}']
 problems=[]
 for name in manifest:
  if name in ('verify.py',) or name.endswith(('.png','.pdf')):continue
  t=(R/name).read_text(errors='ignore')
  if any(re.search(x,t) for x in patterns):problems.append(name)
 assert not problems,('Sensitive-pattern matches in files',problems)
 print(json.dumps({'passed':True,'manifest_files':len(manifest),'archive_integrity':True,'compatibility_native_cells_per_arm':892,'local_link_destinations':links,'sensitive_pattern_scan':'no matches; not a guarantee of absence','scope':'Derived evidence and file integrity, not raw reproduction or human review.'},indent=2))
if __name__=='__main__':main()
