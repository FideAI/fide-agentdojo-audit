"""Lossy, field-allowlisted projections. Never export messages, args, bodies or errors."""
def records(rows):
    keys = ('path','sha256','pipeline','task','attack','user_task','publisher_security',
            'message_count','exact_goal_supported_by_receipts','send_without_required_deletion','disagreement')
    return [{**{k:r[k] for k in keys}, 'has_run_error':r['run_error'] is not None,
             'has_receipt_error':bool(r['receipt_parse_or_consistency_errors']),
             'has_unpaired_response':bool(r['unpaired_tool_responses'])} for r in rows]

def adjudications(rows):
    return [dict(path=r['path'], task=r['task'], send_count=r['send_count'],
                 has_error=r['error'] is not None, current_native_success=r.get('current_native_success'),
                 shipped_fix_success=r.get('shipped_fix_success'),
                 has_single_item_witness=bool(r.get('matching_single_item_witness_ids')),
                 has_pre_injection_match=bool(r.get('pre_injection_matching_ids')),
                 has_post_injection_match=bool(r.get('post_injection_pre_execution_matching_ids')))
            for r in rows]

def comparison(rows):
    return [{**{k:r[k] for k in ('path','pipeline','user_task','publisher_security')},
             'excluded':bool(r['excluded']), 'original':r.get('original'), 'corrected':r.get('corrected')}
            for r in rows]

def observability(rows):
    keys = ('path','sha256','user_task','pipeline','publisher_security','initial_goal_present','strict','contract')
    return [{**{k:r[k] for k in keys}, 'previously_excluded':bool(r['previously_excluded']),
             'has_redacted_send':any(s['redacted'] for s in r['sends'])} for r in rows]
