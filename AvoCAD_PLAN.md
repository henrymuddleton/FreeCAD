# AvoCAD (AI-Native FreeCAD) — Product + Technical Plan

## 1) Vision
AvoCAD is a branded FreeCAD-based CAD environment that adds a precise AI copilot capable of:
- creating geometry from natural language,
- editing existing parametric models safely,
- navigating and explaining the model tree/workbenches,
- performing multi-step workflows with explicit execution plans,
- using Elasticsearch for memory, retrieval, and context tracking.

AvoCAD keeps FreeCAD’s deterministic parametric model core and introduces AI as an auditable orchestration layer, not a black-box replacement.

---

## 2) User outcomes and core value
1. **Fast intent-to-model**: “Create a 120×80×5 mm plate with four M5 corner holes” should produce exact model operations.
2. **Safe edits**: “Change all fillets to 2 mm except around bearing seat” should be done with previews and rollback.
3. **Guided navigation**: “Show me where the pad thickness is defined” highlights relevant tree objects/properties.
4. **Reliable multi-step execution**: Complex requests become structured plans with checkpoints and verification.
5. **Contextual continuity**: AI remembers project conventions, previous decisions, and part constraints via Elasticsearch.

---

## 3) Product surfaces

## 3.1 UI additions
- **AvoCAD AI Panel** (dock widget)
  - Prompt input + attachments + mode selector (`Ask`, `Plan`, `Execute`)
  - Plan visualization (step list, status, dependencies)
  - Tool call trace and editable execution parameters
  - “Apply / Dry-run / Undo” actions
- **Context sidebar**
  - Active document summary
  - Retrieved memory snippets (from Elasticsearch)
  - Confidence + ambiguity warnings
- **Command palette integration**
  - Quick AI commands (`Explain selected`, `Find sketch driving this face`, `Generate TechDraw view`)

## 3.2 AI operating modes
- **Ask**: explanatory Q&A, no model mutation.
- **Plan**: produces machine-readable steps without executing.
- **Execute**: runs steps with transaction boundaries and checks.

## 3.3 Precision safeguards
- Default to **plan-first** on destructive operations.
- Require explicit user confirmation for:
  - topology-risky edits,
  - bulk edits,
  - external imports that alter assemblies.
- Always show generated FreeCAD command/script before execution.

---

## 4) System architecture

## 4.1 High-level components
1. **AvoCAD AI Orchestrator**
   - Converts user intent into a typed task graph.
   - Chooses tools/workbenches.
   - Performs step-by-step execution and validation.

2. **Tooling Runtime (deterministic adapters)**
   - FreeCAD-native tool adapters for:
     - document operations,
     - sketch/constraint manipulation,
     - Part/PartDesign operations,
     - TechDraw/CAM flows,
     - UI navigation tasks.

3. **Context Engine (Elasticsearch-backed)**
   - Indexes document metadata, object tree, parameters, chat turns, and executed actions.
   - Retrieves relevant historical and model context at prompt-time.

4. **Policy & Safety Layer**
   - Guards around scope, allowed tools, and operation risk categories.
   - Adds confirmation and rollback requirements.

5. **Execution Ledger**
   - Stores each plan step, tool inputs/outputs, checks, and resulting document diffs.

## 4.2 Data flow
1. User prompt enters AI panel.
2. Orchestrator requests context from Context Engine (Elasticsearch retrieval).
3. Planner emits step graph:
   - `analyze -> propose -> validate constraints -> execute -> verify`.
4. Executor runs steps using FreeCAD tool adapters under transactions.
5. Results + logs are indexed in Elasticsearch and shown in the panel.

---

## 5) FreeCAD integration strategy

## 5.1 Packaging strategy
- Start as an internal module/workbench: `src/Mod/AvoCAD`.
- Python-first for rapid iteration; use C++ only for performance-critical or deep GUI integration.
- Register as a full workbench + command set (`AvoCADWorkbench`, `AvoCAD_Plan`, `AvoCAD_Execute`, etc.).

## 5.2 Integration points
- **GUI dock integration** for AI panel and plan/status widgets.
- **Workbench and command registration** for discoverable actions.
- **Document/tree/property reading APIs** to build model context snapshots.
- **Transactional execution boundaries** to preserve undo/redo and safety.

## 5.3 Branding “FreeCAD” -> “AvoCAD”
- Introduce a branding config bundle:
  - app name, executable name, splash, about assets, vendor URLs, desktop file metadata.
- Keep compatibility mode for older FreeCAD configs/macros where feasible.

---

## 6) Elasticsearch design

## 6.1 Indices (suggested)
1. `avocad-project-context`
   - document id, object path, type, parameters, constraints, units, timestamp.
2. `avocad-conversation`
   - chat turns, user intent tags, resolved ambiguities, linked plan ids.
3. `avocad-execution-ledger`
   - plan steps, tool calls, validation results, errors, rollbacks.
4. `avocad-knowledge`
   - local docs, standards, templates, enterprise references.

## 6.2 Retrieval patterns
- Hybrid retrieval:
  - structured filters (document id, object types, version),
  - semantic retrieval for natural language context.
- Freshness weighting to prefer latest model state.
- Session-scoped context window with spillover to Elasticsearch.

## 6.3 Context retention policy
- Keep concise summaries per plan phase.
- Store full detail in ledger index.
- Redact secrets/credentials before indexing.

## 6.4 Security
- API key via secure settings store, never hardcoded.
- Optional on-prem Elasticsearch endpoint.
- Index-level RBAC for team/enterprise projects.

---

## 7) Multi-step reasoning/workflow engine

## 7.1 Planner schema
Each request compiles to:
- `goal`
- `assumptions`
- `required_inputs`
- `steps[]` with preconditions/postconditions
- `verification_checks[]`
- `rollback_strategy`

## 7.2 Execution model
- Execute one step at a time.
- Verify expected model conditions after each step.
- If verification fails:
  - auto-repair attempt,
  - fallback prompt with minimal clarification question,
  - rollback when needed.

## 7.3 Example complex workflow
Prompt: “Prepare this bracket for CNC and produce a 2D drawing package.”
- Analyze geometry + tolerances
- Validate manufacturability assumptions
- Generate CAM setup/operations
- Simulate toolpath
- Generate TechDraw sheets
- Export STEP, DXF/PDF, and NC code
- Produce summary report with unresolved risks

---

## 8) Precision and quality controls

## 8.1 Geometric precision safeguards
- Unit normalization before any math.
- Constraint-solver-aware edits (avoid over/under constrained states).
- Feature-level targeting via stable references where possible.
- Post-op checks: volume, bounding box, key dimensions, dependency graph sanity.

## 8.2 Reliability targets
- Step success rate target (e.g., >95% for predefined task suites).
- Deterministic replay support from ledger logs.
- Strict separation between “proposed change” and “committed change”.

## 8.3 Human-in-the-loop controls
- “Explain before apply” option on by default for first-time users.
- Inline diff preview of object/property changes.
- One-click revert to pre-plan transaction snapshot.

---

## 9) MVP scope (Phase 1)

## 9.1 Must-have capabilities
1. Branded shell name “AvoCAD” + icons/splash/about text.
2. AI panel with `Ask/Plan/Execute`.
3. Basic task coverage:
   - create/edit PartDesign primitives and sketches,
   - navigate model tree and properties,
   - explain constraints and dependencies.
4. Elasticsearch integration for chat + execution history.
5. Plan/step UI + execution trace + rollback.

## 9.2 Out of scope for MVP
- Fully autonomous assembly constraint solving for all edge cases.
- Advanced enterprise connectors beyond Elasticsearch.
- Multi-user real-time collaboration.

---

## 10) Roadmap

## Phase 0 (2–4 weeks): foundation
- Branding layer + module skeleton + AI panel UI scaffold.
- Elasticsearch connector, config page, health check command.
- Minimal planner schema and execution ledger.

## Phase 1 (4–8 weeks): functional MVP
- Implement core tool adapters (document/selection/sketch/PartDesign).
- Add plan + verify + rollback engine.
- Add retrieval-augmented context pipeline.
- Build initial acceptance task suite.

## Phase 2 (8–12 weeks): production hardening
- Expand workbench coverage (TechDraw, CAM, Assembly flows).
- Improve topological robustness heuristics.
- Add policy controls, audit exports, and enterprise auth options.

## Phase 3: advanced intelligence
- Domain templates (jig, enclosure, bracket, sheet-metal starter workflows).
- Automated standards checks.
- Proactive suggestions and optimization loops.

---

## 11) Technical implementation notes

## 11.1 Suggested module layout
`src/Mod/AvoCAD/`
- `Init.py`, `InitGui.py`
- `avocad_workbench.py`
- `ai_panel/` (dock UI)
- `planner/` (plan schema + orchestration)
- `executor/` (step runner + transaction hooks)
- `tools/` (FreeCAD deterministic adapters)
- `context/` (Elasticsearch indexing/retrieval)
- `safety/` (policy, confirmation, rollback)
- `tests/` (workflow and regression tests)

## 11.2 Telemetry and observability
- Structured logs per plan id / step id.
- Error taxonomy: parsing, ambiguity, tool failure, geometry failure, verification mismatch.
- Optional metrics dashboard for success rates and rollback frequency.

## 11.3 Testing strategy
- Golden-path scripted tasks for common CAD operations.
- Mutation tests for malformed/ambiguous prompts.
- Replay tests from execution ledger to ensure determinism.
- Non-regression suites for imports/exports and generated artifacts.

---

## 12) API and config requirements from you
To implement Elasticsearch integration, I will need:
1. Elasticsearch endpoint URL.
2. Authentication method (API key or username/password).
3. Preferred index naming prefix (e.g., `avocad-*`).
4. Deployment model: cloud or on-prem.
5. Any data retention/compliance rules.

If you share those, I can produce a concrete technical spec + first implementation patch plan (files, classes, commands, milestones) next.


---

## 13) Complete execution checklist (from current state to finished plan)

The items below are the exact implementation sequence required to complete this plan, with dependency order and done criteria.

### Stage A — Program setup and prerequisites (blockers first)
1. **Lock scope + success metrics**
   - Confirm MVP acceptance suite, latency targets, step success-rate target, and supported FreeCAD versions.
   - **Done when:** a signed-off MVP checklist exists in-repo.
2. **Collect Elasticsearch runtime inputs (hard blocker)**
   - Endpoint URL, auth method, index prefix, cloud/on-prem, retention/compliance constraints.
   - **Done when:** credentials/config are available through secure runtime config (not source code).
3. **Security baseline**
   - Define secrets handling, PII redaction policy, and index RBAC model.
   - **Done when:** threat model + secure-config doc is approved.

### Stage B — Core AvoCAD framework completion
4. **Stabilize module skeleton**
   - Finalize package layout (`ai_panel`, `planner`, `executor`, `tools`, `context`, `safety`, `tests`).
   - **Done when:** import graph is clean and module load passes in FreeCAD startup.
5. **Workbench command surface**
   - Add explicit commands for Ask/Plan/Execute, history view, context view, dry-run/apply/undo.
   - **Done when:** commands are visible in menu/toolbar and callable from Python console.
6. **Branding migration (FreeCAD -> AvoCAD shell assets)**
   - Name, splash, About, desktop metadata, app icons, compatibility notes.
   - **Done when:** branded binaries/UI labels are consistent across platforms.

### Stage C — AI interaction layer
7. **Upgrade panel from scaffold to full assistant UX**
   - Chat transcript, token streaming, plan timeline, step status, retry/cancel controls.
   - **Done when:** panel supports complete Ask/Plan/Execute loop with persisted session state.
8. **Context sidebar + trace surfaces**
   - Show retrieved context snippets, confidence, ambiguity flags, and tool-call trace.
   - **Done when:** each run displays “what context was used” + “why this action was chosen”.

### Stage D — Planner and execution engine
9. **Planner schema implementation**
   - Enforce structured plan object (`goal`, assumptions, required inputs, steps, checks, rollback).
   - **Done when:** every Execute request has a machine-validated plan object.
10. **Deterministic executor with transaction boundaries**
    - Step runner, pre/post checks, checkpointing, rollback hooks, idempotent retries.
    - **Done when:** failed steps rollback cleanly and do not corrupt model history.
11. **Clarification/ambiguity loop**
    - Automatic targeted questions when constraints/geometry references are underspecified.
    - **Done when:** ambiguous prompts never trigger destructive execution without confirmation.

### Stage E — FreeCAD tool adapters (capability depth)
12. **Document/selection adapters**
    - Read object tree, properties, selections, references, and unit context.
    - **Done when:** planner can reliably ground prompts to concrete model entities.
13. **Sketch + constraint adapters**
    - Create/edit constraints, dimension updates, diagnostics for over/under-constrained states.
    - **Done when:** constraint edits are safe, verified, and reversible.
14. **Part/PartDesign adapters**
    - Primitive creation, feature edits, patterns, boolean ops, fillets/chamfers with checks.
    - **Done when:** MVP geometry tasks are executable end-to-end.
15. **Navigation/explain adapters**
    - “Show where parameter lives”, highlight dependencies, surface driving sketches/features.
    - **Done when:** explain/navigation requests are accurate and clickable in UI.

### Stage F — Elasticsearch context engine
16. **Index and mapping setup**
    - Create `project-context`, `conversation`, `execution-ledger`, `knowledge` mappings + lifecycle policies.
    - **Done when:** mappings validated and write/read smoke tests pass.
17. **Ingestion pipeline**
    - Index document snapshots, action logs, plan steps, chat turns, and outcomes.
    - **Done when:** each interaction produces complete, queryable records.
18. **Retrieval pipeline**
    - Hybrid retrieval (structured filters + semantic), freshness ranking, session scoping.
    - **Done when:** planner receives ranked context payload with relevance diagnostics.
19. **Governance controls**
    - Redaction filters, retention enforcement, delete/export workflows.
    - **Done when:** compliance requirements are test-verified.

### Stage G — Safety and policy enforcement
20. **Risk classifier for operations**
    - Label actions by risk tier (read-only, reversible, topology-risky, destructive bulk).
    - **Done when:** high-risk operations always require explicit confirmation.
21. **Dry-run + diff preview**
    - Render property/object deltas before apply.
    - **Done when:** users can inspect exact pending mutations before commit.
22. **Global undo/revert checkpoints**
    - Snapshot before plan apply; one-click restore.
    - **Done when:** restore succeeds across supported MVP operations.

### Stage H — Output generation workflows
23. **TechDraw generation flow**
    - Drawing sheet creation, view placement, annotations, PDF/SVG/DXF export.
    - **Done when:** drawing package commands complete from prompt.
24. **CAM workflow starter**
    - Setup generation, operation scaffolding, simulation triggers, post-processing path.
    - **Done when:** defined MVP CAM scenario runs and outputs expected artifacts.
25. **Export orchestrations**
    - STEP/STL/DXF/PDF + report bundle outputs with deterministic naming.
    - **Done when:** multi-artifact export requests are reproducible.

### Stage I — Quality, test, and hardening
26. **Automated acceptance suite**
    - Golden CAD tasks for create/edit/navigate/explain/export.
    - **Done when:** pass-rate meets target and regressions are caught in CI.
27. **Replay determinism tests**
    - Re-execute ledger traces and compare outcomes.
    - **Done when:** replay variance is within agreed tolerance.
28. **Failure-mode test matrix**
    - Ambiguous prompts, topology drift, missing references, solver failures, ES outages.
    - **Done when:** fallback behavior is predictable and user-visible.
29. **Performance tuning**
    - Measure prompt-to-plan latency, per-step runtime, retrieval overhead.
    - **Done when:** MVP latency SLO is consistently met.

### Stage J — Release readiness and rollout
30. **Docs and in-app onboarding**
    - User guide, guardrail docs, operator runbook, troubleshooting.
    - **Done when:** first-time users can complete guided tasks without external help.
31. **Packaging and release pipeline**
    - Build profiles, versioning, changelog, signed artifacts, upgrade path.
    - **Done when:** reproducible release candidate is generated.
32. **Phased rollout**
    - Internal alpha -> design partner beta -> public preview with telemetry review gates.
    - **Done when:** exit criteria for each gate are achieved.

### Stage K — Post-MVP expansion (Phase 2/3 completion)
33. **Expanded workbench coverage**
    - Assembly, advanced TechDraw/CAM depth, domain templates.
34. **Enterprise controls**
    - SSO/auth options, audit export APIs, policy packs.
35. **Proactive intelligence**
    - Standards checks, design suggestions, optimization loops.

## 14) Immediate next actions required now
1. Provide Elasticsearch connection/auth/compliance inputs listed in Section 12.
2. Approve MVP acceptance criteria and risk policy defaults (confirmation thresholds).
3. Approve implementation order for Stages B->F as the first engineering sprint train.
