"""Reconstruct inbox bookkeeping from receipts as data; never execute logged calls.

This uses current pinned fixtures, NOT an asserted reconstruction of historical code.
"""
import collections
import hashlib
import inspect
import json
from pathlib import Path
import yaml

from probe import ROOT, REPO, PIN, network_attempts
from scan_records import receipt_text
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.default_suites.v1.tools.types import Email


def main():
    evidence = json.loads((ROOT/'results/record-evidence.json').read_text())
    suite = get_suite('v1.2.2','workspace')
    # Existing source fix, not Fide's invented predicate. The already-created
    # suite snapshot remains unchanged by this late import.
    from agentdojo.default_suites.v1_1_2.workspace.injection_tasks import InjectionTask0 as ShippedFix
    fixed_task0 = ShippedFix()
    rows = []
    for r in evidence:
        if not r['disagreement']:
            continue
        data = json.loads((REPO/r['path']).read_text())
        task = suite.get_injection_task_by_id(f"injection_task_{r['task']}")
        row = {'path':r['path'], 'historical_benchmark_version':data.get('benchmark_version'),
               'task':r['task'], 'send_count':len(r['goal_send_receipts']), 'error':None}
        try:
            env = suite.load_and_inject_default_environment(data.get('injections',{}))
            env = suite.get_user_task_by_id(r['user_task']).init_environment(env)
            pre = env.model_copy(deep=True)
            checkpoints = []
            for i,m in enumerate(data['messages']):
                if m['role'] != 'tool' or m.get('error') is not None:
                    continue
                call = m.get('tool_call') or {}
                text = receipt_text(m.get('content'),r['pipeline'])
                if call.get('function') == 'send_email':
                    obj = yaml.safe_load(text)
                    if not isinstance(obj,dict) or obj.get('status') != 'sent':
                        raise ValueError(f'Unusable send response {i}')
                    email = Email.model_validate(obj)
                    env.inbox.emails[email.id_] = email
                elif call.get('function') == 'delete_email':
                    eid = str(call['args']['email_id'])
                    if text.strip() != f'Email with id {eid} deleted successfully.':
                        raise ValueError(f'Unusable deletion response {i}')
                    env.inbox.trash[eid] = env.inbox.emails.pop(eid)
                else:
                    continue
                checkpoints.append({'message_index':i, 'native_success':bool(task.security('',pre,env))})
            # Tight existing predicate on each matching item, evaluated against a one-item view.
            # This isolates cardinality interference without relaxing payload requirements.
            candidates = list(env.inbox.emails.values())
            if r['task'] != 5:
                witness_ids = []
                for email in candidates:
                    one = env.model_copy(deep=True)
                    one.inbox.emails = {email.id_:email}
                    if task.security('',pre,one):
                        witness_ids.append(email.id_)
                row['matching_single_item_witness_ids'] = witness_ids
            row['current_native_success'] = bool(task.security('',pre,env))
            if r['task'] == 0:
                row['shipped_fix_success'] = bool(fixed_task0.security('',pre,env))
                baseline = suite.load_and_inject_default_environment({})
                baseline = suite.get_user_task_by_id(r['user_task']).init_environment(baseline)
                pre_matches = pre.inbox.search_emails(task._SUBJECT)
                baseline_matches = baseline.inbox.search_emails(task._SUBJECT)
                row['pre_injection_matching_ids'] = [e.id_ for e in baseline_matches]
                row['post_injection_pre_execution_matching_ids'] = [e.id_ for e in pre_matches]
                row['final_matching_ids'] = [e.id_ for e in env.inbox.search_emails(task._SUBJECT)]
                row['matching_receipt_count'] = len(r['goal_send_receipts'])
            row['checkpoints'] = checkpoints
            row['current_predicate_path'] = str(Path(inspect.getsourcefile(type(task))).relative_to(REPO))
            row['all_receipt_parses_clean'] = not r['receipt_parse_or_consistency_errors']
        except Exception as e:
            row['error'] = f'{type(e).__name__}: {e}'
        rows.append(row)
    summary = {'candidate_records':len(rows),
        'current_false_single_item_true':sum(r.get('current_native_success') is False and bool(r.get('matching_single_item_witness_ids')) for r in rows),
        'current_true_historical_false':sum(r.get('current_native_success') is True for r in rows),
        'shipped_fix_resolves_current_false':sum(r.get('current_native_success') is False and r.get('shipped_fix_success') is True for r in rows),
        'current_false_with_match_introduced_by_injection':sum(bool(r.get('current_native_success') is False and r.get('post_injection_pre_execution_matching_ids') and not r.get('pre_injection_matching_ids')) for r in rows),
        'reconstruction_errors':sum(r['error'] is not None for r in rows),
        'by_task': {str(n):dict(collections.Counter(
            'reconstruction_error' if r['error'] else 'current_true' if r['current_native_success']
            else 'cardinality_interference' if r.get('matching_single_item_witness_ids')
            else 'unresolved' for r in rows if r['task']==n)) for n in [0,3,4,5]},
        'network_attempts':len(network_attempts),
        'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'results/adjudication.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'results/adjudication-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    assert not network_attempts


if __name__=='__main__':
    main()
