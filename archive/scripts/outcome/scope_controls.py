"""Counterexample to treating every harmful send as full attack completion."""
import json
from probe import ROOT, goal_send, network_attempts
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.default_suites.v1.tools.email_client import send_email, delete_email

rows=[]
for version in ['v1','v1.2.2']:
    suite=get_suite(version,'workspace')
    task=suite.get_injection_task_by_id('injection_task_5')
    pre=suite.load_and_inject_default_environment({})
    env=pre.model_copy(deep=True)
    email=send_email(env.inbox,**goal_send(task,pre))
    before=bool(task.security('',pre,env))
    delete_email(env.inbox,email.id_)
    after=bool(task.security('',pre,env))
    assert before is False and after is True
    rows.append(dict(version=version,send_only=before,send_then_delete=after))
assert not network_attempts
(ROOT/'results/scope-controls.json').write_text(json.dumps({'rows':rows,'network_attempts':0},indent=2)+'\n')
print('Two task-5 pairs passed: sent-only is not its stated full objective.')
