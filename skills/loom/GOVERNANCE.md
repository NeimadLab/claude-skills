# Governance

## Decision Process

Loom uses a lightweight governance model appropriate for its current stage.

### Maintainer Authority
During V0.x, the project maintainer(s) have final authority on scope, architecture, and release decisions. This is intentional — early-stage projects need decisive leadership more than consensus processes.

### RFC Process
Significant changes require an RFC (Request for Comments):
1. Author creates `rfcs/NNN-title.md` using the template
2. PR opened for community review (7-day minimum comment period)
3. Maintainer(s) make final decision: accept, reject, or defer
4. Accepted RFCs are merged and tracked in the roadmap

### ADR Process
Architectural decisions are recorded in `adrs/`:
1. Author creates `adrs/NNN-title.md` using the template
2. ADRs document the context, decision, and consequences
3. ADRs are immutable once accepted — superseded by new ADRs if revisited

### Graduating to Open Governance
At V1.0, the project will adopt a more open governance model with:
- A core team with documented roles
- A public decision log
- Community input on roadmap priorities
