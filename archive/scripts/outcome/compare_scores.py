"""Post hoc matched-record sensitivity; no model runs or recorded-call execution."""
import hashlib
import json
from pathlib import Path
import yaml
from probe import ROOT, REPO, network_attempts
from scan_records import receipt_text
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.default_suites.v1.tools.types import Email

BASE='gpt-4o-2024-05-13'
ARMS=[BASE]+[BASE+'-'+s for s in ['repeat_user_prompt','spotlighting_with_delimiting','tool_filter','transformers_pi_detector']]


def main():
    suite=get_suite('v1.2.2','workspace')
    original=suite.get_injection_task_by_id('injection_task_0')
    from agentdojo.default_suites.v1_1_2.workspace.injection_tasks import InjectionTask0
    corrected=InjectionTask0()
    all_rows=json.loads((ROOT/'results/record-evidence.json').read_text())
    selected=[r for r in all_rows if r['task']==0 and r['attack']=='important_instructions' and r['pipeline'] in ARMS]
    rows=[]
    for r in selected:
        out={'path':r['path'],'pipeline':r['pipeline'],'user_task':r['user_task'],
            'publisher_security':r['publisher_security'],'excluded':None}
        reasons=[]
        if not r['message_count']: reasons.append('empty_trace')
        if r['run_error'] is not None: reasons.append('run_error')
        if r['receipt_parse_or_consistency_errors']: reasons.append('receipt_error')
        if r['unpaired_tool_responses']: reasons.append('unpaired_response')
        if reasons:
            out['excluded']=reasons
            rows.append(out)
            continue
        try:
            d=json.loads((REPO/r['path']).read_text())
            env=suite.load_and_inject_default_environment(d.get('injections',{}))
            env=suite.get_user_task_by_id(r['user_task']).init_environment(env)
            pre=env.model_copy(deep=True)
            for m in d['messages']:
                if m['role']!='tool' or m.get('error') is not None: continue
                call=m.get('tool_call') or {}
                text=receipt_text(m.get('content'),r['pipeline'])
                if call.get('function')=='send_email':
                    email=Email.model_validate(yaml.safe_load(text))
                    env.inbox.emails[email.id_]=email
                elif call.get('function')=='delete_email':
                    eid=str(call['args']['email_id'])
                    if text.strip()!=f'Email with id {eid} deleted successfully.': raise ValueError('Missing deletion receipt')
                    env.inbox.trash[eid]=env.inbox.emails.pop(eid)
            out['original']=bool(original.security('',pre,env))
            out['corrected']=bool(corrected.security('',pre,env))
            out['receipt_goal']=r['exact_goal_supported_by_receipts']
            if out['corrected'] and not out['receipt_goal']:
                raise ValueError('Corrected score unsupported by exact-goal receipt')
            if out['original'] and not out['corrected']:
                raise ValueError('Unexpected original-positive/corrected-negative')
        except Exception as e:
            out['excluded']=[f'reconstruction_or_witness_error: {type(e).__name__}: {e}']
        rows.append(out)
    by_arm={a:{r['user_task']:r for r in rows if r['pipeline']==a} for a in ARMS}
    assert all(len(x)==40 for x in by_arm.values())
    shared=set.intersection(*[{t for t,r in arm.items() if not r['excluded']} for arm in by_arm.values()])
    counts={a:{'original':sum(arm[t]['original'] for t in shared),
        'corrected':sum(arm[t]['corrected'] for t in shared),
        'publisher':sum(arm[t]['publisher_security'] for t in shared),
        'excluded_before_intersection':sum(bool(r['excluded']) for r in arm.values())} for a,arm in by_arm.items()}
    summary={'selected_records':len(rows),'matched_tasks':len(shared),'matched_task_ids':sorted(shared),
        'arms':counts,'network_attempts':len(network_attempts),
        'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'results/comparison-evidence.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'results/comparison-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert not network_attempts
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
