"""Verify actual suite registration before/after loading the existing correction."""
import importlib
import inspect
import json
from pathlib import Path
from probe import ROOT, REPO, goal_send, network_attempts
from agentdojo.task_suite import load_suites
from agentdojo.default_suites.v1.tools.email_client import send_email


def sample(label):
    suite = load_suites.get_suite('v1.2.2','workspace')
    task = suite.get_injection_task_by_id('injection_task_0')
    rows=[]
    for extra in ['none','same_subject_mention','unrelated_mention']:
        pre=suite.load_and_inject_default_environment({})
        # Authored neutral fixture text, not an attack payload.
        if extra != 'none':
            first = next(iter(pre.inbox.emails.values()))
            first.body += '\nReference note: ' + (task._SUBJECT if extra == 'same_subject_mention' else 'ordinary unrelated text')
        for action in ['no_send','send_once','send_twice','wrong_recipient']:
            env=pre.model_copy(deep=True)
            args=goal_send(task,pre)
            if action == 'wrong_recipient':
                args['recipients']=['control@example.com']
            if action != 'no_send':
                send_email(env.inbox,**args)
            if action == 'send_twice':
                send_email(env.inbox,**args)
            direct=bool(task.security('',pre,env))
            native=bool(suite._check_injection_task_security(task,[],pre,env,[]))
            assert direct == native
            rows.append(dict(condition=label,extra=extra,action=action,score=native,
                predicate=str(Path(inspect.getsourcefile(type(task))).relative_to(REPO))))
    return rows


rows=sample('default_loader')
before=load_suites.get_suite('v1.2.2','workspace').get_injection_task_by_id('injection_task_0')
importlib.import_module('agentdojo.default_suites.v1_1_2')
# This intervention rebuilds the version snapshots after registering the shipped
# module. A late import alone does not update already-created suite copies.
importlib.reload(load_suites)
rows += sample('register_shipped_module_and_rebuild')
after=load_suites.get_suite('v1.2.2','workspace').get_injection_task_by_id('injection_task_0')
old=load_suites.get_suite('v1','workspace').get_injection_task_by_id('injection_task_0')
assert type(before) is type(old)
assert type(before) is not type(after)
for r in rows:
    if r['action'] in ['no_send','wrong_recipient']:
        assert not r['score']
    elif r['condition']=='register_shipped_module_and_rebuild':
        assert r['score']
assert not network_attempts
(ROOT/'results/registration.json').write_text(json.dumps({'rows':rows,
    'old_version_preserved':True,'network_attempts':len(network_attempts)},indent=2)+'\n')
print(json.dumps({'cells':len(rows),'changed_verdicts':sum(a['score'] != b['score'] for a,b in zip(rows[:12],rows[12:])),
    'old_version_preserved':True,'network_attempts':len(network_attempts)},indent=2))
