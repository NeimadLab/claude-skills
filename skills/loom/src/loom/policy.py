"""Policy engine — evaluate YAML rules on MCP tool calls.

Loads policy from .loom/policies/default.yaml and evaluates every
tool call against it. Returns allow/deny/approve with reasons.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from loom.constants import loom_dir
from loom.events import emit
from loom.models import Event

# Map MCP tool names to policy action classes
TOOL_ACTION_MAP = {
    "loom_search_memory": "read_memory",
    "loom_write_memory": "write_memory",
    "loom_log_decision": "write_memory",
    "loom_get_handoff_summary": "read_memory",
    "loom_get_context": "read_memory",
    "loom_get_state": "read_memory",
    "loom_open_session": "write_memory",
    "loom_close_session": "write_memory",
}


def load_policy(workspace: Path | None = None) -> dict | None:
    """Load policy from .loom/policies/default.yaml. Returns None if no policy."""
    root = workspace or Path.cwd()
    policy_path = loom_dir(root) / "policies" / "default.yaml"

    if not policy_path.exists():
        return None

    try:
        import yaml
    except ImportError:
        # PyYAML not installed — try parsing simple YAML manually
        return _parse_simple_yaml(policy_path)

    with open(policy_path) as f:
        return yaml.safe_load(f)


def _parse_simple_yaml(path: Path) -> dict:
    """Minimal YAML parser for policy files (no PyYAML dependency)."""

    text = path.read_text()
    rules = []
    current_rule = None
    current_conditions = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- action:"):
            if current_rule:
                if current_conditions:
                    current_rule["conditions"] = current_conditions
                rules.append(current_rule)
            current_rule = {"action": stripped.split(":", 1)[1].strip().strip('"')}
            current_conditions = None
        elif current_rule and stripped.startswith("default:"):
            current_rule["default"] = stripped.split(":", 1)[1].strip().strip('"')
        elif current_rule and stripped.startswith("requires:"):
            current_rule["requires"] = stripped.split(":", 1)[1].strip().strip('"')
        elif current_rule and stripped.startswith("approval_timeout:"):
            current_rule["approval_timeout"] = int(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("- path_match:") or stripped.startswith("- command_match:"):
            if current_conditions is None:
                current_conditions = []
            cond = {}
            key = stripped.split(":")[0].lstrip("- ").strip()
            cond[key] = stripped.split(":", 1)[1].strip().strip('"')
            current_conditions.append(cond)
        elif stripped.startswith("- alias_match:"):
            if current_conditions is None:
                current_conditions = []
            cond = {"alias_match": stripped.split(":", 1)[1].strip().strip('"')}
            current_conditions.append(cond)
        elif stripped.startswith("decision:") and current_conditions:
            current_conditions[-1]["decision"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("reason:") and current_conditions:
            current_conditions[-1]["reason"] = stripped.split(":", 1)[1].strip().strip('"')

    if current_rule:
        if current_conditions:
            current_rule["conditions"] = current_conditions
        rules.append(current_rule)

    return {"rules": rules}


def evaluate(
    tool_name: str,
    arguments: dict,
    workspace: Path | None = None,
    actor: str | None = None,
) -> dict:
    """Evaluate a tool call against the policy.

    Returns:
        {
            "decision": "allow" | "deny" | "approve",
            "reason": str,
            "rule_matched": str | None,
            "requires": str | None,
        }
    """
    root = workspace or Path.cwd()
    policy = load_policy(root)

    # No policy = allow everything
    if not policy or "rules" not in policy:
        return {"decision": "allow", "reason": "no policy configured", "rule_matched": None}

    action_class = TOOL_ACTION_MAP.get(tool_name, "unknown")
    rules = policy.get("rules", [])

    for rule in rules:
        if rule.get("action") != action_class:
            continue

        # Check conditions
        conditions = rule.get("conditions", [])
        for cond in conditions:
            if _condition_matches(cond, arguments):
                decision = cond.get("decision", rule.get("default", "allow"))
                result = {
                    "decision": decision,
                    "reason": cond.get("reason", f"Condition matched in {action_class} rule"),
                    "rule_matched": action_class,
                    "requires": rule.get("requires"),
                }
                _log_evaluation(tool_name, result, root, actor)
                return result

        # No condition matched — use default
        result = {
            "decision": rule.get("default", "allow"),
            "reason": f"Default for {action_class}",
            "rule_matched": action_class,
            "requires": rule.get("requires"),
        }
        _log_evaluation(tool_name, result, root, actor)
        return result

    # No matching rule at all
    return {"decision": "allow", "reason": "no matching rule", "rule_matched": None}


def _condition_matches(condition: dict, arguments: dict) -> bool:
    """Check if a condition matches the given arguments."""
    if "path_match" in condition:
        path_arg = arguments.get(
            "path", arguments.get("linked_files", [""])[0] if arguments.get("linked_files") else ""
        )
        return fnmatch.fnmatch(str(path_arg), condition["path_match"])

    if "command_match" in condition:
        cmd = arguments.get("command", "")
        return fnmatch.fnmatch(cmd, condition["command_match"])

    if "alias_match" in condition:
        content = arguments.get("content", "") + arguments.get("query", "")
        return condition["alias_match"].lower() in content.lower()

    return False


def _log_evaluation(tool_name: str, result: dict, workspace: Path, actor: str | None) -> None:
    """Log policy evaluation to the event log."""
    if result["decision"] != "allow":  # Only log non-trivial decisions
        emit(
            Event(
                event_type="policy_evaluated",
                actor=actor or "unknown",
                data={
                    "tool": tool_name,
                    "decision": result["decision"],
                    "reason": result["reason"],
                },
            ),
            workspace,
        )


def install_default_policy(workspace: Path | None = None) -> Path:
    """Install the default policy file into the workspace."""
    root = workspace or Path.cwd()
    policy_dir = loom_dir(root) / "policies"
    policy_dir.mkdir(parents=True, exist_ok=True)
    dest = policy_dir / "default.yaml"

    # Find the template
    template = Path(__file__).parent.parent.parent / "templates" / "policies" / "default.yaml"
    if template.exists():
        dest.write_text(template.read_text())
    else:
        # Fallback: minimal permissive policy
        dest.write_text(
            "# Loom Policy\nrules:\n"
            "  - action: read_memory\n    default: allow\n"
            "  - action: write_memory\n    default: allow\n"
        )

    return dest
