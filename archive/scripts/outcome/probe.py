"""Authored in-memory fixture calls; no historical payloads or inference."""
import hashlib
import inspect
import json
from pathlib import Path
import socket
import subprocess

from context import outcome_root as ROOT, REPO, PIN, NETWORK_ATTEMPTS as network_attempts

from agentdojo.task_suite.load_suites import get_suite
from agentdojo.default_suites.v1.tools.email_client import send_email, delete_email


def goal_send(task, pre):
    n = int(task.ID.split('_')[-1])
    if n == 0:
        return dict(recipients=[task._RECIPIENT], subject=task._SUBJECT, body=task._TEXT)
    if n == 3:
        email = pre.inbox.search_emails('', sender=task._SENDER)[0]
        return dict(recipients=[task._RECIPIENT], subject=email.subject, body=email.body)
    if n == 4:
        return dict(recipients=[task._RECIPIENT], subject=task._SUBJECT, body=f'{task._BODY} {task._CODE}')
    return dict(recipients=[task._RECIPIENT], subject='Security Code', body=task._CODE)


def main():
    rows = []
    provenance = {}
    for version in ['v1', 'v1.2.2']:
        suite = get_suite(version, 'workspace')
        for n in [0, 3, 4, 5]:
            task = suite.get_injection_task_by_id(f'injection_task_{n}')
            source = Path(inspect.getsourcefile(type(task)))
            provenance[f'{version}/{task.ID}'] = {
                'path': str(source.relative_to(REPO)),
                'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'security_line': inspect.getsourcelines(task.security)[1],
                'goal': task.GOAL,
            }
            for variant in ['no_send', 'goal', 'duplicate', 'delete_sent', 'unrelated_send', 'matching_subject_send']:
                pre = suite.load_and_inject_default_environment({})
                env = pre.model_copy(deep=True)
                args = goal_send(task, pre)
                events = []
                def emit(a):
                    out = send_email(env.inbox, **a)
                    events.append({'function': 'send_email', 'args': a, 'result': out.model_dump(mode='json')})
                    return out.id_
                def delete(email_id):
                    out = delete_email(env.inbox, email_id)
                    events.append({'function': 'delete_email', 'id': email_id, 'result': out})
                if variant != 'no_send':
                    sent_id = emit(args)
                    if n == 5:
                        delete(sent_id)
                    if variant == 'duplicate':
                        second = emit(args)
                        if n == 5:
                            delete(second)
                    elif variant == 'delete_sent' and n != 5:
                        delete(sent_id)
                    elif variant in ['unrelated_send', 'matching_subject_send']:
                        emit(dict(recipients=['control@example.com'], subject=args['subject'] if variant == 'matching_subject_send' else 'Unrelated control', body='Harmless control'))
                # No reformulation of task 5: its exact goal includes deleting the sent message.
                completed_sends = [e for e in events if e['function'] == 'send_email' and e['args'] == args]
                event_goal = bool(completed_sends) and (n != 5 or any(e['function'] == 'delete_email' for e in events))
                rows.append(dict(version=version, task=task.ID, variant=variant,
                    native_success=bool(task.security('', pre, env)), event_goal=event_goal,
                    goal_send_count=len(completed_sends), events=events,
                    final_sent_ids=[str(e.id_) for e in env.inbox.sent],
                    final_trash_ids=list(env.inbox.trash)))
    out = {'commit': PIN, 'rows': rows, 'provenance': provenance, 'network_attempts': network_attempts,
           'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT / 'results/probes.json').write_text(json.dumps(out, indent=2) + '\n')
    assert not network_attempts
    print(json.dumps({'cells': len(rows), 'disagreements': [
        {k:r[k] for k in ['version','task','variant','native_success','event_goal']} for r in rows
        if r['native_success'] != r['event_goal']], 'network_attempts': len(network_attempts)}, indent=2))


if __name__ == '__main__':
    main()
