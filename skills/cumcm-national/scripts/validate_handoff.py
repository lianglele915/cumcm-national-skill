"""Validate CUMCM handoff files and evidence paths using the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys

STAGES = {"analysis", "preprocessing", "solving", "validation", "writing", "figures"}
STATUSES = {"completed", "partial", "failed", "not_applicable"}


def validate(data, root):
    errors = []
    if not isinstance(data, dict):
        return ["Root must be a JSON object"]
    root = Path(root).resolve()
    if not root.is_dir():
        return ["Project root must be an existing directory"]
    required = {"schema_version", "stage", "status", "mode", "inputs", "outputs",
                "decisions", "stage_data", "runs", "vscode_verification", "checks", "pending"}
    errors.extend(f"Missing field: {key}" for key in sorted(required - data.keys()))
    if data.get("schema_version") != "1.0":
        errors.append("Unsupported schema_version")
    for key, allowed in [("stage", STAGES), ("status", STATUSES),
                         ("mode", {"full", "stage", "review", "edit"})]:
        if not isinstance(data.get(key), str) or data[key] not in allowed:
            errors.append(f"Invalid {key}")
    for key in ["inputs", "outputs", "decisions", "runs", "checks", "pending"]:
        if not isinstance(data.get(key), list):
            errors.append(f"{key} must be a list")
    if not isinstance(data.get("stage_data"), dict):
        errors.append("stage_data must be an object")
    if errors:
        return errors

    def resolve_path(value, label, directory=False):
        if not isinstance(value, str) or not value or "\\" in value:
            errors.append(f"{label}: use a nonempty project-relative path with / separators")
            return None
        rel = Path(value)
        if rel.is_absolute() or PureWindowsPath(value).drive or PureWindowsPath(value).root:
            errors.append(f"{label}: absolute paths are not allowed")
            return None
        path = (root / rel).resolve()
        if not path.is_relative_to(root):
            errors.append(f"{label}: path escapes project root")
            return None
        if not (path.is_dir() if directory else path.is_file()):
            errors.append(f"{label}: path does not exist")
            return None
        return path

    output_paths = set()
    has_code = False
    for group in ["inputs", "outputs"]:
        for index, item in enumerate(data[group]):
            label = f"{group}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: expected object")
                continue
            path = resolve_path(item.get("path"), label)
            if not isinstance(item.get("role"), str) or not item["role"].strip():
                errors.append(f"{label}: role is required")
            expected = item.get("sha256")
            if not isinstance(expected, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", expected):
                errors.append(f"{label}: invalid sha256")
            elif path:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if expected.lower() != digest:
                    errors.append(f"{label}: sha256 mismatch")
            if group == "outputs" and path:
                output_paths.add(path)
                has_code |= path.suffix.lower() in {".py", ".m", ".jl", ".r", ".js", ".ipynb", ".ps1", ".sh", ".bat", ".cmd", ".c", ".cpp"}

    valid_vscode_logs = set()
    for index, run in enumerate(data["runs"]):
        label = f"runs[{index}]"
        if not isinstance(run, dict):
            errors.append(f"{label}: expected object")
            continue
        for key in ["command", "runtime"]:
            if not isinstance(run.get(key), str) or not run[key].strip():
                errors.append(f"{label}: {key} is required")
        resolve_path(run.get("cwd"), label + ".cwd", directory=True)
        log = resolve_path(run.get("log"), label + ".log")
        if log and log not in output_paths:
            errors.append(f"{label}: log must be a hashed output artifact")
        if type(run.get("exit_code")) is not int:
            errors.append(f"{label}: exit_code must be an integer")
        if not isinstance(run.get("runner"), str) or run["runner"] not in {"vscode-task", "vscode-terminal", "cli"}:
            errors.append(f"{label}: invalid runner")
        elif run["runner"].startswith("vscode-") and run.get("exit_code") == 0 and log:
            valid_vscode_logs.add(log)

    verification = data["vscode_verification"]
    if not isinstance(verification, dict) or not isinstance(verification.get("status"), str) or verification["status"] not in {
            "passed", "failed", "not_run", "cli_equivalent"}:
        errors.append("Invalid vscode_verification")
    else:
        evidence = verification.get("evidence")
        evidence_paths = set()
        if not isinstance(evidence, list):
            errors.append("vscode_verification.evidence must be a list")
        else:
            for value in evidence:
                path = resolve_path(value, "vscode evidence")
                if path:
                    evidence_paths.add(path)
                    if path not in output_paths:
                        errors.append("VS Code evidence must be a hashed output artifact")
        if verification["status"] == "passed" and not evidence_paths.intersection(valid_vscode_logs):
            errors.append("VS Code passed requires a successful editor run and matching evidence log")
        if has_code and data["status"] == "completed" and verification["status"] != "passed":
            errors.append("Completed code delivery requires VS Code passed; otherwise use partial")

    if data["status"] == "completed":
        if not data["outputs"]:
            errors.append("Completed stage requires output artifacts")
        if data["pending"]:
            errors.append("Completed stage cannot have pending items")
    if data["status"] in {"partial", "failed", "not_applicable"} and not data["pending"]:
        errors.append("Non-completed status requires a reason in pending")
    for item in data["checks"]:
        if not isinstance(item, dict) or not isinstance(item.get("status"), str) or item["status"] not in {
                "passed", "failed", "not_run", "not_applicable", "insufficient_evidence"}:
            errors.append("Invalid check entry/status")
    if data["status"] == "completed" and any(
            isinstance(item.get("status"), str) and item["status"] in {"failed", "not_run", "insufficient_evidence"}
            for item in data["checks"] if isinstance(item, dict)):
        errors.append("Completed stage has unresolved checks")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.handoff.read_text(encoding="utf-8-sig"))
        errors = validate(data, args.project_root)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
