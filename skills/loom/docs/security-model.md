# Security Model

## Threat Model

Loom mediates between AI models and local/remote filesystems. This is an inherently sensitive position. The primary threats are:

| Threat | Risk | Impact |
|--------|------|--------|
| **Unauthorized data access** | Remote model reads sensitive files or secrets | Data exfiltration, credential exposure |
| **Arbitrary code execution** | Model runs commands without user awareness | System compromise, data destruction |
| **Session hijacking** | Attacker reuses or forges session tokens | Unauthorized workspace access |
| **Policy bypass** | Model circumvents governance rules | Ungoverned actions on sensitive resources |
| **Audit tampering** | Attacker modifies event log | Loss of accountability, hidden malicious actions |
| **Prompt injection via files** | Malicious content in project files tricks the model | Unintended actions via the gateway |

## Defense by Topology

| Aspect | Local Topology | Remote Topology |
|--------|---------------|----------------|
| **Transport** | stdio (inherently trusted, same user) | HTTPS + TLS 1.3 only. No cleartext. |
| **Authentication** | None required (local user owns process) | API key (V0.3) or OAuth 2.0 + PKCE (V0.4+) |
| **Authorization** | Minimal: write token for write operations | Role-based: reader, writer, operator, admin |
| **Session leases** | Optional (local sessions are lightweight) | Mandatory. Default 30 min TTL. Auto-expire. No permanent sessions. |
| **Secrets** | Whitelist access via named aliases. OS keychain integration. | DENIED by default. Never exposed to remote clients. |
| **Shell execution** | Approval-gated (user confirms in CLI) | Denied by default. Requires explicit policy rule to unlock. |
| **Audit** | All events logged to events.jsonl | All events + source IP + client identity + request hash |
| **IP allowlisting** | N/A | Optional. Recommended for enterprise. |

## Policy Engine

Policies are YAML files in `.loom/policies/`:

```yaml
# .loom/policies/default.yaml
rules:
  - action: read_file
    default: allow
    conditions:
      - path_match: "*.env*"
        decision: deny
        reason: "Environment files may contain secrets"
      - path_match: ".git/**"
        decision: deny
        reason: "Git internals not exposed"

  - action: execute
    default: deny
    conditions:
      - command_match: "npm test"
        decision: allow
      - command_match: "cargo test"
        decision: allow
      - command_match: "*"
        decision: approve
        approval_timeout: 60

  - action: read_secret
    default: deny
    conditions:
      - alias_match: "database_url"
        decision: allow
```

## Action Classes

| Class | Examples | Risk Level | Local Default | Remote Default |
|-------|----------|:----------:|:------------:|:--------------:|
| **Read** | search_memory, list_files, get_context | Low | Allow | Allow |
| **Write** | write_memory, log_decision | Medium | Allow | Writer role required |
| **Read+** | read_file (sensitive paths) | Medium | Allow | Approve |
| **Write+** | write_file | High | Writer token required | Approve |
| **Execute** | Shell commands | Critical | Approve (user confirms) | Deny (default) |
| **Secret** | read_secret | Critical | Whitelist only | Deny (always) |

## Secret Management

Secrets are never passed in cleartext through the MCP tool surface. Instead:

- Secrets are defined in `.loom/policies/secrets.yaml` as named aliases
- Each alias maps to: an environment variable, an OS keychain entry, or a `.env` file key
- Models reference secrets by alias name, never by value
- For local topology: secret values are resolved and returned to the model
- For remote topology: secret access is DENIED by default, regardless of alias

## Audit Trail

Every action through the gateway is logged to `events.jsonl` with:

```json
{
  "event_type": "tool_call_executed",
  "timestamp": "2026-03-22T14:30:00Z",
  "session_id": "01HXY...",
  "actor": "claude-code",
  "client_ip": "127.0.0.1",
  "tool": "loom_read_file",
  "parameters": { "path": "src/auth/jwt.ts" },
  "policy_decision": "allow",
  "policy_rule_id": "read_file_default",
  "outcome": "success",
  "duration_ms": 12
}
```

Events are append-only. The file is never modified or truncated during normal operation. Tampering detection is planned for V1.0 (hash chain or Merkle tree over events).
