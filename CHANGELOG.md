# Changelog

All notable changes to dl-research will be documented in this file.

## [0.6.0] - 2026-06-04

### Added
- **Paper Close Reading**: Independent tool for extracting transferable design elements from local PDFs
  - New reference: `references/paper-close-reading.md`
  - 3-step protocol: Screening → Deep Read → Integration
  - Step 1: 1 agent screens papers by relevance to diagnosis
  - Step 2: N agents in parallel, one per paper, extracts design elements with mechanism derivation, formula, ablation evidence, applicability assessment
  - Step 3: 1 agent integrates all Paper Cards into unified Design Element Library
  - Output: `design-elements.md` consumed by Deep Research Brainstorming
  - Total: 5-7 agents, 3 batches, ~20-30k tokens
  - Triggered only when user provides local PDFs (not part of main loop)

## [0.5.0] - 2026-06-04

### Changed
- **Deep Research Brainstorming redesigned**: 5-phase → 3-phase, 17-19 agents → 5 agents
  - Phase 1 (Research): 3 parallel agents — External Research (WebSearch), Internal Audit (Read), Failure Analysis (Read history)
  - Phase 2 (Propose + Evaluate): 1 agent proposes 3-5 candidates with mechanism derivation, cost, verification design, Devil's Advocate
  - Phase 3 (Adversarial Verify + Synthesize): 1 agent tries to REFUTE each candidate, survivors get final ranking
  - Token budget: ~60k → ~20k
  - External search now actually executes via WebSearch/WebFetch

## [0.4.1] - 2026-06-04

### Changed
- **Workflow reorder**: Deep Research Brainstorming now runs AFTER Diagnosis, not before
  - Old: Evidence Pack → 核验 → Audit → Deep Research → Mechanistic Analysis → Diagnosis
  - New: Evidence Pack → 核验 → Audit → Mechanistic Analysis → Diagnosis → Deep Research
  - Rationale: should diagnose the problem first, then search for solutions based on the diagnosis
  - Updated: SKILL.md workflow diagram, step table, Status Marking, rules, research-framework.md

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
