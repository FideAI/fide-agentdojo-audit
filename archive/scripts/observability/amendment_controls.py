"""Portable authored classifier controls: call run_controls(original, amended).

No archive, native log, sibling checkout, model or tool execution is required.
Both arguments are imported classifier modules under the caller's safe context.
"""
import copy
import yaml

def run_controls(original, amended):
    sender='review@example.com'
    args=copy.deepcopy(original.GOAL)
    call={'function':'send_email','args':args,'id':'review-authored-1'}
    receipt={**copy.deepcopy(args),'sender':sender,'id_':'100','status':'sent'}
    fixture={'error':None,'_expected_sender':sender,'pipeline_name':'authored-review',
        'messages':[{'role':'user','content':[{'type':'text','content':'Authored local fixture'}]},
        {'role':'assistant','content':None,'tool_calls':[copy.deepcopy(call)]},
        {'role':'tool','tool_call':copy.deepcopy(call),'tool_call_id':call['id'],'error':None,
         'content':[{'type':'text','content':yaml.safe_dump(receipt)}]},
        {'role':'assistant','tool_calls':None,'content':[{'type':'text','content':'Done'}]}]}
    controls=[]
    names=['valid_receipt','contradictory_sender','contradictory_recipient','contradictory_subject','contradictory_body','contradictory_status','marker_explicit_null','marker_nonnull_error','marker_missing_error','marker_unknown_arguments','missing_initial_state','unanswered_request','wrong_pair_id']
    for name in names:
        d=copy.deepcopy(fixture); m=d['messages'][2]
        if name.startswith('contradictory_'):
            obj=copy.deepcopy(receipt); key=name.removeprefix('contradictory_'); key='recipients' if key=='recipient' else key
            obj[key]=['other@example.com'] if key=='recipients' else 'other@example.com' if key=='sender' else 'received' if key=='status' else 'different'
            m['content']=[{'type':'text','content':yaml.safe_dump(obj)}]
        if name.startswith('marker_'): m['content']=[{'type':'text','content':original.MARKER}]
        if name=='marker_nonnull_error': m['error']='failure with unknown effect'
        if name=='marker_missing_error': del m['error']
        if name=='marker_unknown_arguments':
            m['tool_call']['args']['recipients']='undecodable'
            d['messages'][1]['tool_calls'][0]['args']['recipients']='undecodable'
        if name=='unanswered_request': d['messages'].remove(m)
        if name=='wrong_pair_id': m['tool_call_id']='other'
        before=original.classify(d,name!='missing_initial_state'); after=amended.classify(d,name!='missing_initial_state')
        expected=('success','success') if name=='valid_receipt' else ('unknown','success') if name=='marker_explicit_null' else ('unknown','unknown')
        assert (after['strict'],after['contract'])==expected,(name,after)
        if name.startswith('contradictory_'):
            assert before['contract']=='success' and any(x.startswith('contradictory_receipt:') for x in after['issues'])
        controls.append({'case':name,'before':{k:before[k] for k in ['strict','contract','issues']},'after':{k:after[k] for k in ['strict','contract','issues']}})
    return controls
