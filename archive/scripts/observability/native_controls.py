"""Authored in-memory controls through native execution, detector and trace logger."""
import copy
import json
from common import ROOT, NETWORK_ATTEMPTS, content_text, save
from audit import GOAL, MARKER, classify
from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.agent_pipeline.errors import AbortAgentError
from agentdojo.agent_pipeline.pi_detector import PromptInjectionDetector
from agentdojo.agent_pipeline.tool_execution import ToolsExecutor, ToolsExecutionLoop
from agentdojo.default_suites.v1.tools.email_client import send_email
from agentdojo.functions_runtime import FunctionCall, FunctionsRuntime, make_function
from agentdojo.logging import NullLogger, TraceLogger
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.types import text_content_block_from_string

class AuthoredDetector(PromptInjectionDetector):
    """Fixed decision; not the published neural detector or its measured accuracy."""
    def __init__(self, mode):
        super().__init__(raise_on_injection=mode == 'abort')
        self.flag = mode != 'pass'
    def detect(self, text):
        return self.flag

class Capture(BasePipelineElement):
    def __init__(self, logpath):
        self.logpath = logpath
        self.deep = self.shallow = self.prelog = None
    def query(self, query, runtime, env, messages, extra_args):
        self.deep = copy.deepcopy(messages)
        self.shallow = list(messages)
        self.prelog = json.loads(self.logpath.read_text())
        return query, runtime, env, messages, extra_args

class Finish(BasePipelineElement):
    def query(self, query, runtime, env, messages, extra_args):
        return query, runtime, env, [*messages, dict(role='assistant', content=[text_content_block_from_string('Finished authored control.')], tool_calls=None)], extra_args

def serialized(value):
    return json.loads(json.dumps(value, default=lambda x: x.model_dump()))

def main():
    suite = get_suite('v1.2.2', 'workspace')
    rows = []
    for variant in ['goal_send', 'wrong_recipient', 'invalid_attachment', 'no_call']:
        for mode in ['pass', 'redact', 'abort']:
            cell = variant + '-' + mode
            env = suite.load_and_inject_default_environment({})
            before_ids = set(env.inbox.emails)
            args = copy.deepcopy(GOAL)
            if variant == 'wrong_recipient':
                args['recipients'] = ['control@example.com']
            if variant == 'invalid_attachment':
                args['attachments'] = [{'type':'file'}]
            calls = [] if variant == 'no_call' else [FunctionCall(function='send_email', args=args, id='authored-1')]
            messages = [dict(role='user', content=[text_content_block_from_string('Run the authored local fixture.')]),
                        dict(role='assistant', content=None, tool_calls=calls)]
            delegate = NullLogger()
            delegate.logdir = str(ROOT/'results/native-logs')
            delegate.messages = []
            logger = TraceLogger(delegate, pipeline_name=cell, suite_name='workspace',
                                 user_task_id='user_task_control', injection_task_id='injection_task_0', attack_type='authored')
            path = ROOT/'results/native-logs'/cell/'workspace/user_task_control/authored/injection_task_0.json'
            capture = Capture(path)
            loop = ToolsExecutionLoop([ToolsExecutor(), capture, AuthoredDetector(mode), Finish()], max_iters=1)
            aborted = False
            with logger:
                logger.log(messages)
                try:
                    loop.query('authored', FunctionsRuntime([make_function(send_email)]), env, messages, {})
                except AbortAgentError:
                    aborted = True
            final_log = json.loads(path.read_text())
            final_tool = [m for m in final_log['messages'] if m['role']=='tool']
            deep_tool = [m for m in serialized(capture.deep or []) if m['role']=='tool']
            shallow_tool = [m for m in serialized(capture.shallow or []) if m['role']=='tool']
            rows.append(dict(cell=cell, variant=variant, mode=mode, aborted=aborted,
                 created_ids=sorted(set(env.inbox.emails)-before_ids),
                 effect_count=len(set(env.inbox.emails)-before_ids),
                 final_tool=final_tool, deep_tool=deep_tool, shallow_tool=shallow_tool,
                 prelog_tool=[m for m in (capture.prelog or {}).get('messages',[]) if m['role']=='tool'],
                 native_log_path=str(path.relative_to(ROOT))))
    # Mutation tests: no recorded payload is executed. These authored message copies
    # challenge the analysis rule, including incomplete and contradictory evidence.
    good = next(r for r in rows if r['cell']=='goal_send-pass')
    fixture = json.loads((ROOT/good['native_log_path']).read_text())
    fixture['_expected_sender'] = suite.load_and_inject_default_environment({}).inbox.account_email
    classification = []
    for name in ['full_receipt','redacted_receipt','unanswered_request','missing_error_field','recorded_error','wrong_recipient','missing_initial_state','no_terminal_assistant','run_error']:
        d = copy.deepcopy(fixture)
        m = next(m for m in d['messages'] if m['role']=='tool')
        if name in ['redacted_receipt','missing_error_field','recorded_error','wrong_recipient']:
            m['content'] = [text_content_block_from_string(MARKER)]
        if name=='unanswered_request':
            d['messages']=[x for x in d['messages'] if x['role']!='tool']
        if name=='missing_error_field':
            del m['error']
        if name=='recorded_error':
            m['error']='Authored error after unknown effect'
        if name=='wrong_recipient':
            m['tool_call']['args']['recipients']=['control@example.com']
            for a in d['messages']:
                if a['role']=='assistant' and a.get('tool_calls'):
                    a['tool_calls'][0]['args']['recipients']=['control@example.com']
        if name=='no_terminal_assistant':
            d['messages']=d['messages'][:-1]
        if name=='run_error':
            d['error']='Authored run failure'
        classification.append(dict(name=name, **classify(d, name!='missing_initial_state')))
    save('results/native-controls.json', dict(rows=rows, classification_controls=classification, network_attempts=len(NETWORK_ATTEMPTS)))
    print(json.dumps(dict(cells=len(rows), rows=[{k:r[k] for k in ['cell','effect_count','aborted']} for r in rows],
                         classifier=[{k:r[k] for k in ['name','strict','contract']} for r in classification], network_attempts=len(NETWORK_ATTEMPTS)),indent=2))
    assert not NETWORK_ATTEMPTS

if __name__=='__main__':
    main()
