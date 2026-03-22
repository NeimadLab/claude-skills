"""Project templates — pre-built memory entries for common project types.
Each template seeds the workspace with relevant decisions, conventions,
goals, and risks so the AI tool has useful context from minute one.
"""

from __future__ import annotations

from pathlib import Path

from loom.memory import MemoryStore
from loom.models import MemoryEntry, MemoryStatus, MemoryType

TEMPLATES: dict[str, dict] = {
    "web-backend": {
        "description": "Web backend API (FastAPI, Express, Rails, etc.)",
        "entries": [
            {
                "type": "observation",
                "content": "This is a web backend project. Prioritize API design, data modeling, auth, and error handling.",
            },
            {
                "type": "observation",
                "content": "Prefer explicit error types and HTTP status codes over generic 500 responses.",
            },
            {
                "type": "observation",
                "content": "All API endpoints must have input validation and rate limiting.",
            },
            {
                "type": "goal",
                "content": "Maintain comprehensive API documentation (OpenAPI/Swagger).",
            },
            {
                "type": "risk",
                "content": "Authentication and authorization must be verified on every protected endpoint.",
            },
            {
                "type": "risk",
                "content": "Database migrations must be reversible and tested before deployment.",
            },
            {
                "type": "observation",
                "content": "Follow REST conventions: plural nouns for resources, proper HTTP verbs, consistent pagination.",
            },
        ],
    },
    "web-frontend": {
        "description": "Web frontend (React, Vue, Next.js, etc.)",
        "entries": [
            {
                "type": "observation",
                "content": "This is a web frontend project. Prioritize component design, state management, accessibility, and performance.",
            },
            {
                "type": "observation",
                "content": "All interactive elements must be keyboard-accessible (WCAG 2.1 AA).",
            },
            {
                "type": "observation",
                "content": "Prefer composition over inheritance for components. Keep components small and focused.",
            },
            {
                "type": "goal",
                "content": "Core Web Vitals targets: LCP <2.5s, FID <100ms, CLS <0.1.",
            },
            {
                "type": "risk",
                "content": "Bundle size must be monitored. No dependency added without checking its impact.",
            },
            {"type": "observation", "content": "Use semantic HTML elements. Avoid div soup."},
        ],
    },
    "mobile-app": {
        "description": "Mobile application (React Native, Flutter, Swift, Kotlin)",
        "entries": [
            {
                "type": "observation",
                "content": "This is a mobile app project. Prioritize offline-first, performance, and platform conventions.",
            },
            {
                "type": "observation",
                "content": "All network requests must handle offline state gracefully with retry and caching.",
            },
            {"type": "goal", "content": "App startup time under 2 seconds on mid-range devices."},
            {
                "type": "risk",
                "content": "Deep linking and push notification configuration must be tested on both platforms.",
            },
            {
                "type": "observation",
                "content": "Follow platform-specific design guidelines (Material Design / Human Interface Guidelines).",
            },
        ],
    },
    "data-pipeline": {
        "description": "Data pipeline / ETL / analytics",
        "entries": [
            {
                "type": "observation",
                "content": "This is a data pipeline project. Prioritize idempotency, data quality, and observability.",
            },
            {
                "type": "observation",
                "content": "All transformations must be idempotent — re-running a pipeline must produce the same result.",
            },
            {
                "type": "observation",
                "content": "Schema validation at pipeline boundaries. Fail fast on unexpected data shapes.",
            },
            {
                "type": "goal",
                "content": "Every pipeline step must emit metrics: input count, output count, error count, duration.",
            },
            {
                "type": "risk",
                "content": "PII data must be identified and handled according to retention policy. No PII in logs.",
            },
            {
                "type": "risk",
                "content": "Large dataset processing must be chunked to avoid memory exhaustion.",
            },
        ],
    },
    "cli-tool": {
        "description": "Command-line tool / developer utility",
        "entries": [
            {
                "type": "observation",
                "content": "This is a CLI tool project. Prioritize UX, error messages, and composability.",
            },
            {
                "type": "observation",
                "content": "Exit codes must be meaningful: 0 success, 1 general error, 2 usage error.",
            },
            {
                "type": "observation",
                "content": "All output meant for machines goes to stdout. Human messages go to stderr.",
            },
            {
                "type": "observation",
                "content": "Support --json flag on all data commands for scripting and piping.",
            },
            {
                "type": "goal",
                "content": "Help text must be self-sufficient. A user should never need to open docs for basic usage.",
            },
            {
                "type": "risk",
                "content": "Avoid breaking changes to CLI flags and output format in minor versions.",
            },
        ],
    },
    "infra-devops": {
        "description": "Infrastructure / DevOps / platform engineering",
        "entries": [
            {
                "type": "observation",
                "content": "This is an infrastructure project. Prioritize reproducibility, security, and documentation.",
            },
            {
                "type": "observation",
                "content": "All infrastructure must be defined as code. No manual changes to production.",
            },
            {
                "type": "observation",
                "content": "Secrets are never stored in code or config files. Use secret managers.",
            },
            {"type": "goal", "content": "Zero-downtime deployments for all services."},
            {
                "type": "risk",
                "content": "IAM permissions must follow least-privilege principle. Audit quarterly.",
            },
            {"type": "risk", "content": "Disaster recovery must be tested, not just documented."},
        ],
    },
    "library": {
        "description": "Reusable library / SDK / package",
        "entries": [
            {
                "type": "observation",
                "content": "This is a library project. Prioritize API design, backward compatibility, and documentation.",
            },
            {
                "type": "observation",
                "content": "Public API surface must be minimal. Prefer explicit over implicit. No magic.",
            },
            {
                "type": "observation",
                "content": "All public functions and types must have docstrings with examples.",
            },
            {
                "type": "observation",
                "content": "Follow semantic versioning strictly. Breaking changes only in major versions.",
            },
            {"type": "goal", "content": "100% of public API covered by tests and documentation."},
            {
                "type": "risk",
                "content": "Minimize dependencies. Each dependency is a supply chain risk.",
            },
        ],
    },
}


def list_templates() -> list[dict]:
    """List available templates with descriptions."""
    return [
        {"name": name, "description": t["description"], "entries": len(t["entries"])}
        for name, t in TEMPLATES.items()
    ]


def apply_template(
    template_name: str,
    workspace: Path | None = None,
) -> dict:
    """Apply a template to a workspace. Seeds memory with domain-specific entries."""

    root = workspace or Path.cwd()

    if template_name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        return {"error": f"Unknown template: {template_name}. Available: {available}"}

    template = TEMPLATES[template_name]
    store = MemoryStore(root)
    imported = 0

    for entry_data in template["entries"]:
        entry = MemoryEntry(
            type=MemoryType(entry_data["type"]),
            content=entry_data["content"],
            status=MemoryStatus.VALIDATED,
            actor=f"template:{template_name}",
            tags=[template_name],
        )
        store.write(entry)
        imported += 1

    store.close()

    from loom.events import emit
    from loom.models import Event

    emit(
        Event(
            event_type="template_applied",
            data={"template": template_name, "entries": imported},
        ),
        root,
    )

    return {
        "template": template_name,
        "description": template["description"],
        "entries_added": imported,
    }
