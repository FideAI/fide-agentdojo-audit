"""Recheck review clarifications by reading pinned records/source; execute no trace code."""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = "089ed468cf3ed0322acc66b0211f26d9d90dbf60"
MARKER = "<Data omitted because a prompt injection was detected>"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(source):
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    assert actual == PIN, "Wrong upstream commit"
    manifest = {r["path"]: r["sha256"] for r in read(ROOT / "archive/manifests/outcome-cohort.json")}

    def record(path):
        target = source / path
        assert sha(target) == manifest[path], f"Record hash mismatch: {path}"
        return read(target)

    cases = [r for r in read(ROOT / "archive/data/adjudication-count-inputs.json")
             if r["current_native_success"] is False and r["shipped_fix_success"] is True]
    versions = [{"path": r["path"], "sha256": manifest[r["path"]],
                 "benchmark_version": record(r["path"]).get("benchmark_version")} for r in cases]
    selected = [r for r in read(ROOT / "archive/data/comparison-count-inputs.json")
                if r["excluded"] and r["pipeline"] == "gpt-4o-2024-05-13-transformers_pi_detector"]
    redactions = []
    for r in selected:
        messages = record(r["path"])["messages"]
        indices = []
        for i, m in enumerate(messages):
            if m.get("role") != "tool" or (m.get("tool_call") or {}).get("function") != "send_email":
                continue
            content = m.get("content")
            text = content if isinstance(content, str) else "".join(
                block.get("text", "") for block in (content or []) if isinstance(block, dict))
            if text.strip() == MARKER:
                indices.append(i)
        redactions.append({"path": r["path"], "sha256": manifest[r["path"]],
                           "publisher_security": r["publisher_security"],
                           "redacted_send_response_message_indices": indices})
    names = ["src/agentdojo/task_suite/load_suites.py", "src/agentdojo/task_suite/task_suite.py",
             "src/agentdojo/agent_pipeline/pi_detector.py"]
    declarations = []
    for path in sorted((source / "src/agentdojo/default_suites/v1_1_2").rglob("*.py")):
        names.append(str(path.relative_to(source)))
        for node in ast.parse(path.read_text()).body:
            if not isinstance(node, ast.ClassDef):
                continue
            for decorator in node.decorator_list:
                expression = ast.unparse(decorator)
                if "task_suite." in expression:
                    declarations.append({"file": str(path.relative_to(source)), "class": node.name,
                                         "line": decorator.lineno, "registration": expression})
    source_hashes = {}
    for name in names:
        # HEAD alone is insufficient: also reject modified inspected source files.
        committed = subprocess.check_output(["git", "-C", str(source), "show", f"{PIN}:{name}"])
        assert (source / name).read_bytes() == committed, f"Modified source: {name}"
        source_hashes[name] = sha(source / name)
    return {"source_pin": PIN,
            "scope": "Read-only metadata/marker projection of existing selected records and static registrations. No historical execution attribution or new model trials.",
            "selection": "All retained original-fail/corrected-pass cases; all excluded records in the selected detector configuration. No new records selected.",
            "version_counts": dict(Counter(r["benchmark_version"] or "absent_or_null" for r in versions)),
            "case_versions": versions,
            "excluded_detector_count": len(redactions),
            "excluded_detector_with_redacted_send": sum(bool(r["redacted_send_response_message_indices"]) for r in redactions),
            "excluded_detector_saved_successes": sum(r["publisher_security"] for r in redactions),
            "excluded_detector_records": redactions,
            "v1_1_2_declarations": declarations, "source_hashes": source_hashes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--write", action="store_true", help="Deliberately replace the reviewed projection")
    args = parser.parse_args()
    result = project(args.source.resolve())
    destination = ROOT / "evidence/review-mechanisms.json"
    if args.write:
        destination.write_text(json.dumps(result, indent=2) + "\n")
    else:
        assert result == read(destination), "Projection differs from retained result"
    print(json.dumps({k: result[k] for k in ["version_counts", "excluded_detector_count",
                     "excluded_detector_with_redacted_send", "excluded_detector_saved_successes"]}))
