"""Minimize qualified archive outputs for the evidence guide; execute no trace content."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = 'runs/claude-3-5-sonnet-20240620/workspace/user_task_17/important_instructions/injection_task_0.json'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pick(row, keys):
    return {key: row[key] for key in keys.split()}


def project(run, source):
    validation = read(run / 'validation.json')
    assert validation['passed'] and validation['mode'] == 'full'
    assert validation['source_clean_after']
    assert validation['upstream_commit'] == read(ROOT / 'PROVENANCE.json')['upstream_commit']
    assert validation['inert_archive_analysis']['projected_tables_match'] == 4
    record_hash = next(r['sha256'] for r in read(ROOT / 'archive/manifests/outcome-cohort.json') if r['path'] == CASE)
    assert sha(source / CASE) == record_hash, 'Source record differs from the sealed manifest'
    raw = read(source / CASE)
    row = next(r for r in read(run / 'outcome/results/adjudication.json') if r['path'] == CASE)
    screen = next(r for r in read(run / 'outcome/results/record-evidence.json') if r['path'] == CASE)
    assert screen['sha256'] == record_hash
    receipts = []
    for receipt in screen['goal_send_receipts']:
        message = raw['messages'][receipt['message_index']]
        assert message['role'] == 'tool' and message['tool_call']['function'] == 'send_email'
        receipts.append({
            'message_index': receipt['message_index'], 'email_id': receipt['email_id'],
            'explicit_null_error': 'error' in message and message['error'] is None,
        })
    example = {
        'upstream_commit': validation['upstream_commit'], 'record_sha256': record_hash,
        'publisher_security': raw['security'],
        **pick(row, 'path historical_benchmark_version task send_count error matching_single_item_witness_ids current_native_success shipped_fix_success pre_injection_matching_ids post_injection_pre_execution_matching_ids final_matching_ids matching_receipt_count checkpoints current_predicate_path all_receipt_parses_clean'),
        'predicate_sha256': sha(source / row['current_predicate_path']),
        'goal_send_receipts': receipts,
    }
    registration = read(run / 'outcome/results/registration.json')
    registration = {
        'rows': [pick(r, 'condition extra action score predicate') for r in registration['rows']],
        **pick(registration, 'old_version_preserved network_attempts'),
    }
    native = read(run / 'observability/results/native-controls.json')
    logging = {'rows': [], 'classification_controls': [], 'network_attempts': native['network_attempts']}
    for r in native['rows']:
        logging['rows'].append({
            **pick(r, 'cell variant mode aborted created_ids effect_count'),
            'tool_message_counts': {k: len(r[k]) for k in ('final_tool', 'deep_tool', 'shallow_tool', 'prelog_tool')},
            'final_equals_deep': r['final_tool'] == r['deep_tool'],
            'final_equals_shallow': r['final_tool'] == r['shallow_tool'],
            'prelog_equals_deep': r['prelog_tool'] == r['deep_tool'],
        })
    logging['classification_controls'] = [pick(r, 'name strict contract') for r in native['classification_controls']]
    amendment = read(run / 'observability/results/amendment-controls.json')
    amendment = {
        **pick(amendment, 'passed network_attempts'),
        'controls': [{
            'case': r['case'], 'before': pick(r['before'], 'strict contract'),
            'after': pick(r['after'], 'strict contract'),
        } for r in amendment['controls']],
    }
    return {'worked-example.json': example, 'registration-controls.json': registration,
            'logging-controls.json': logging, 'amendment-controls.json': amendment}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True, help='Completed full archive run directory')
    parser.add_argument('--source', type=Path, default=ROOT / 'archive/.local/agentdojo')
    parser.add_argument('--write', action='store_true', help='Replace release projections; otherwise compare only')
    args = parser.parse_args()
    outputs = project(args.run.resolve(), args.source.resolve())
    destination = ROOT / 'evidence'
    if args.write:
        destination.mkdir(exist_ok=True)
    for name, data in outputs.items():
        if args.write:
            (destination / name).write_text(json.dumps(data, indent=2) + '\n')
        else:
            assert read(destination / name) == data, f'Projection mismatch: {name}'
    print(json.dumps({'passed': True, 'projection_files': len(outputs), 'mode': 'write' if args.write else 'compare'}))


if __name__ == '__main__':
    main()
