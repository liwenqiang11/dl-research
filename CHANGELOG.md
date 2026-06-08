# Changelog

All notable changes to dl-research will be documented in this file.

## [0.4.0] - 2026-06-04

### Changed
- **Deep Research Brainstorming** replaces shallow Debate Brainstorming
  - 5-phase protocol: Knowledge Gathering → Solution Space Mapping → Deep Evaluation → Cross-Examination → Synthesis
  - Phase 1: 4 Researchers (Literature Survey, Codebase Audit, Failure Analysis, Tool/Tech Landscape) actively gather NEW knowledge
  - Phase 2: Each Researcher maps full solution space (≥2 directions), not just one proposal
  - Phase 3: Deep evaluation per candidate — mechanism derivation, evidence anchoring, cost estimation, devil's advocate
  - Phase 4: Professional cross-examination from each perspective
  - Phase 5: Judge synthesizes — top-3 ranking, fusion, knowledge gained, discriminating experiments
  - Total: 17-19 Agent calls, 5 parallel batches (vs old 13 calls, 4 batches)
  - On outer-loop restart, Failure Analysis Researcher receives ALL previous attempts
- All references unified from "Debate Brainstorming" to "Deep Research Brainstorming"

## [0.3.0] - 2026-06-04

### Added
- **Debate Brainstorming**: Multi-Advocate adversarial debate protocol (4 perspectives × 3 rounds + Judge synthesis)
  - New reference: `references/debate-brainstorming.md`
  - Perspectives: data, model, loss, evaluation
  - Rounds: Independent Exploration → Cross-Attack → Revise
  - Judge: convergence analysis, survivability ranking, fusion proposal
- **Subagent isolation for verification**: Atomic Fact Verification and Formal Derivation Verification now run as independent subagents via Agent tool
  - Context isolation: verifiers cannot see diagnosis, design, or recommendation
  - Input/output contracts defined with Agent tool call prompt templates
  - Parallel execution supported (both verifiers + Debate Round 1 can run concurrently)
- **probe_activations.py**: Hook-based model probe tool
  - Modes: `gradient`, `activation`, `dead-check`, `attention`, `flow`
  - Supports `--layers` filter and `--json` output
- Subagent Isolation Rules section in SKILL.md

### Changed
- **full-auto mode**: Redefined as "expert autonomous mode" — all gates non-blocking, never stops until goal achieved
- **guided mode**: Redefined as "assistant mode" — confirms at key decision points
- Solution Generation + Selection replaced by Debate Brainstorming in workflow
- All "Evidence Review" references unified to "Independent Evidence Audit"
- All "Design Selection" references unified to "Debate Brainstorming"
- Status Marking `当前阶段` list updated to include Debate Brainstorming
- research-framework.md Solution Generation Methods: Debate Brainstorming as primary method, single-agent methods as fallbacks

### Fixed
- Terminology consistency across all files (SKILL.md, 8 reference files, 1 example file, 1 template)

## [0.2.23] - 2026-05-20

### Initial version
- Core workflow: Problem → Evidence Pack → Verification → Diagnosis → Solution → Implementation → Verification → Resolution
- Roles: Atomic Fact Verification, Formal Derivation Verification, Evidence Reviewer, Mechanistic Model Analyst, Git Branch Management, Research Recorder, Active Monitoring
- Scripts: sanity_check.py, freeze_env.sh, monitor_training.py
- References: research-framework.md, probe-toolkit.md, atomic-fact-verification.md, formal-derivation-verifier.md, evidence-reviewer.md, git-branch-management.md, mechanistic-model-analyst.md, research-recorder.md
