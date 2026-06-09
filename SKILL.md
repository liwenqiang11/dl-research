---
name: dl-research
description: Use this skill for deep learning algorithm research and experiment workflows: finding research problems, reading/comparing papers, forming hypotheses, designing models/losses/training protocols, implementing experiments, running sanity checks, diagnosing training logs, planning baselines/ablations, analyzing results, or tuning after a failure diagnosis. Always use for ML/DL research tasks involving Discovery, Design, or Evidence, even when the user only says "run training", "analyze loss", "design an experiment", "write an architecture", "compare baselines", or "debug a model".
version: 0.5.0
---

# Deep Learning Experimental Research Framework

Hypothesis-driven, iterative framework for deep learning algorithm experiments. It focuses on the experimental research loop before paper writing: discover a meaningful problem, design an algorithm and experimental protocol, then build evidence through implementation, training, ablation, and analysis.

This skill is problem-solving-first. It does not merely describe a research method; it tells the agent how to turn an unclear deep learning problem into a normalized evidence pack, a diagnosis, candidate solutions, a selected strategy, an implementation, a verification result, and a resolution decision. Before writing code, launching experiments, or giving conclusions, the agent must identify the problem, collect evidence in a structured way, diagnose the likely cause, generate and compare candidate solutions, verify the result, and record what was learned.

Keep the workflow generic: do not assume a fixed project directory, log format, dataset layout, paper archive path, or training framework unless the current repository reveals one.

## Status Marking

Every substantive research response must begin with:

```
当前流程：第 X 步 - [task summary]
当前循环层级：微循环 / 内循环迭代 N / 外循环迭代 M
当前阶段：Evidence Pack / Atomic Fact Verification / Formal Derivation Verification / Independent Evidence Audit / Mechanistic Analysis / Diagnosis / Deep Research Brainstorming / Design / Pre-Action Compliance / Branch Plan / Implementation / Verification / Resolution Decision / Research Record
阶段门控：passed / required / blocked / not-applicable
门控触发原因：objective-fact / formal-claim / evidence-chain-claim / action-request / training-run / user-memory-request / none
```

## Activation Gate

Activation Gate is a blocking ask gate. When this skill is triggered implicitly, ask the user before starting the dl-research workflow:

```text
检测到这是深度学习研究/实验任务。是否启用 dl-research 流程？
请选择执行模式：
1. guided（助手模式）：模型作为研究助手推进，在关键决策点（Design/Run/Resolution 等）与用户确认后继续。
2. full-auto（专家自动模式）：模型作为独立研究专家，自主完成全部决策和执行。所有门控自动运行但不阻塞，仅记录供事后审查。未达到目标之前不停止。
3. strict-confirmation：每个阶段转换和实施动作都先确认。
```

If the user explicitly says to use/start/continue dl-research, treat that as activation confirmation and only ask for the execution mode if it is unclear.

No activation answer, no workflow advance:

- If activation is implicit and the user has not confirmed activation, ask and wait.
- If activation is explicit but execution mode is missing, ask for the mode and wait.
- If the research task or goal is missing, ask for the task and wait.
- If both mode and task are missing, ask for both in the same turn and wait.
- When the `AskUserQuestion` tool is available, selection/confirmation gates must call `AskUserQuestion` and wait for the answer. If the tool is unavailable, ask a concise plain-text question and stop.
- Do not continue to Observe, Gather, Diagnosis, Design, Evidence, implementation, or training while this gate is blocked.
- If an agent prints an activation prompt but continues without waiting, treat it as a Gate Noncompliance Incident and return to Activation Gate.

Default mode is **guided** (assistant mode) only after the user confirms activation/continuation but does not choose a mode. In **guided**, the model acts as a research assistant: it advances analysis automatically but pauses at key decision points (Design Gate, Run Gate, Resolution Decision Gate, etc.) to confirm with the user before proceeding. In **full-auto** (expert autonomous mode), the model acts as an independent research expert: ALL gates are non-blocking, every gate executes internally (Atomic Fact Verification, Formal Derivation Verification, Independent Evidence Audit, Pre-Action Compliance, Branch Plan, Run-to-Branch Binding, etc.) but never pauses. All gate results are recorded for post-hoc review. The agent continues autonomously until the stated goal is achieved or the problem is proven unachievable. This only changes dl-research workflow behavior; it does not override higher-priority system, tool, security, or user permission requirements.

## AskUserQuestion Gate Protocol

Use `AskUserQuestion` for selection and confirmation gates whenever the tool is available. The tool call must be visible in the gate flow and the workflow must stop until the user answers.

Trigger `AskUserQuestion` for:

- Activation Gate: enable dl-research, choose mode, or provide missing task.
- Goal Gate: missing `full-auto` goal fields.
- Design Gate: approve, revise, or block a design.
- Branch Creation Gate: create/switch branch or approve branch plan.
- Run Gate: launch long, expensive, or externally visible training/evaluation.
- Resolution Decision Gate: choose solved/partial/unresolved/redesign/stop when tradeoffs remain.
- Research Record Gate: confirm draft and memory location before writing.

If a selection/confirmation gate is required and `AskUserQuestion` is available but not called, mark `阶段门控：blocked`, record Gate Noncompliance, and return to the missing gate.

## Goal Gate

Before entering **full-auto**, the agent must know three goal fields. If any field is missing, ask only for the missing fields:

```text
请给出 full-auto 目标：
- 要解决的问题：
- 成功标准：
- 允许修改范围：
```

If the user provides `/goal`, `Goal:`, or `目标：` text, parse these three fields from it when possible. Do not add extra required fields.

## Core Principles

1. **Value-oriented**: Focus on meaningful algorithmic bottlenecks and mechanism innovation. Reject blind hyperparameter tuning.
2. **Multi-dimensional balance**: Accuracy, compute efficiency, parameter count, GPU memory, deployment difficulty, generalization, interpretability.
3. **Evidence-backed**: Every core conclusion and architecture change requires rigorous theoretical derivation or detailed experimental support.
4. **Hypothesis tagging**: Mark unverified assumptions explicitly. Propose control-variable verification plans proactively.
5. **Domain fusion**: Integrate physics-informed or domain-specific priors into network design, not just data-driven.
6. **Absolute reproducibility**: Record all random seeds, data splits, hyperparameters, and freeze the full software environment (`pip freeze` / conda export / Docker tag) at experiment launch.

## Problem-Solving Loop

```
Problem → Evidence Pack → Atomic Fact Verification → Formal Derivation Verification → Independent Evidence Audit → Mechanistic Analysis → Atomic Fact Verification → Formal Derivation Verification → Diagnosis → Deep Research Brainstorming → Pre-Action Compliance → Branch Plan → Implementation → Verification → Atomic Fact Verification → Formal Derivation Verification → Independent Evidence Audit → Resolution Decision → Research Record
   ↑                                                                                                                                                                                         |
   └──────────────────────── unresolved / insufficient evidence / invalid problem ────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

This loop is the primary behavior. The agent execution states implement it:

| Problem-Solving Step | Agent State(s) | Purpose |
|----------------------|----------------|---------|
| Problem | Observe, Classify | Define what must be solved, the success criterion, constraints, and risk. |
| Evidence Pack | Gather | Collect required artifacts, label confidence, and separate facts from assumptions. |
| Atomic Fact Verification | Gather, Verify | Spawn an independent Fact Verifier subagent. It receives claims + artifact manifest only; it must not see the main agent's diagnosis, design, or recommendation. It verifies every objective factual claim against artifacts and returns a verdict table. |
| Formal Derivation Verification | Verify | Spawn an independent Derivation Verifier subagent. It receives claims + definitions + code paths only; it must not see the main agent's diagnosis or design preferences. It checks whether mathematical, gradient, objective, and mechanism claims follow from verified facts and returns a verdict + corrected statements. |
| Independent Evidence Audit | Gather, Verify | Ask an independent Evidence Auditor to audit whether verified facts form a traceable, reproducible, comparable, contradiction-aware evidence chain strong enough for the claim. |
| Mechanistic Analysis | Gather, Route, Verify | Analyze the task, data signal, architecture, loss, optimization dynamics, code path, and causal root causes behind the observed behavior. |
| Diagnosis | Route | Decide the problem type and competing causes. Express as a falsifiable statement. |
| Deep Research Brainstorming | Act, Verify | Based on the diagnosis, 4 Researchers gather new knowledge (literature, codebase, failures, tools), map the full solution space, deeply evaluate each candidate, cross-examine from different angles, and a Judge synthesizes the verdict. |
| Pre-Action Compliance | Act, Verify | Block research edits, config changes, training launches, or high-impact commands until required gates and branch records exist. |
| Branch Plan | Act, Record | Define the Git branch, base commit, allowed change scope, and rollback point for research code changes. |
| Implementation | Act | Execute the selected smallest useful step allowed by the current gate. |
| Verification | Verify | Test whether the target signal changed without introducing new failures. |
| Resolution Decision | Decide | Decide solved, partially solved, unresolved, invalid problem, or needs more evidence. |
| Research Record | Record | Preserve verified facts, derivation verdicts, evidence verdicts, mechanisms, actions, artifacts, decisions, uncertainty, deprecated claims, and restart point. |

The research content it advances is limited to three experimental phases:

```
Discovery → Design → Evidence
```

| Research Phase | Goal | Agent Route | Required Output |
|----------------|------|-------------|-----------------|
| Discovery | Find the problem, normalize evidence, analyze mechanisms, diagnose the bottleneck, form a falsifiable hypothesis | Problem → Evidence Pack → Mechanistic Analysis → Diagnosis → Record | Problem statement, evidence pack, mechanistic analysis, diagnosis, core hypothesis |
| Design | Based on diagnosis, research and select a solution strategy, then define algorithm and experiment protocol | Deep Research Brainstorming → Verification plan → Record | Research verdict, selected strategy, algorithm design, experiment protocol |
| Evidence | Implement, train, actively monitor, run main/ablation experiments, verify resolution, and decide next state | Implementation → Active Monitoring Loop → Verification → Resolution Decision → Record | Sanity evidence, monitoring records, experiment results, ablation analysis, resolution decision |

| Loop Type | Entry | Exit | Granularity | Max Iterations |
|-----------|-------|------|-------------|----------------|
| Micro-loop | Evidence implementation or sanity check | Basic correctness established | minutes~hours | unlimited (reconsider design if >10) |
| Inner loop | Evidence training/analysis | Metric improvement, clear diagnosis, or cap reached | single training run or small experiment | ≤3 rounds |
| Outer loop | Discovery → Design → Evidence | Hypothesis supported, rejected, or problem redefined | complete experimental cycle | unlimited (each round must produce reportable evidence) |

**Convergence criterion**: When two consecutive outer loops produce improvement below the predefined minimum meaningful difference for the task, and no useful qualitative or mechanistic evidence emerges, stop the current experimental line and record the reason.

## How to Use Bundled Files

- Read `references/research-framework.md` when the task needs detailed gates, routing, templates, failure modes, or report shape.
- Read `references/probe-toolkit.md` when the task asks for analysis probes, visualization, interpretability, gradient checks, or training diagnostics.
- Read `references/atomic-fact-verification.md` whenever any objective factual claim is produced or used by any role, phase, report, diagnosis, design, run analysis, or final record.
- Read `references/formal-derivation-verifier.md` whenever any role makes mathematical, gradient, loss/objective, variable-dependency, mechanism, equivalence, or commit-message claims.
- Read `references/evidence-reviewer.md` whenever an independent evidence audit is needed before Diagnosis, Deep Research Brainstorming, Resolution Decision, or Record.
- Read `references/debate-brainstorming.md` whenever the problem is not mechanically obvious and multiple competing solutions or root causes exist. This implements Deep Research Brainstorming: 5-phase structured research with knowledge gathering, solution space mapping, deep evaluation, cross-examination, and synthesis.
- Read `references/git-branch-management.md` whenever code, config, data processing, evaluation logic, baselines, ablations, or training protocols may change.
- Read `references/mechanistic-model-analyst.md` whenever the task involves model architecture, loss functions, training failures, metric conflicts, ablation interpretation, probe conflicts, or code-path consistency.
- Read `references/research-recorder.md` only when the user explicitly asks to remember, record, save, archive, or write the current research result.
- Use `examples/hypothesis-design-template.md` when producing a Discovery-linked Design Gate document.
- Use `scripts/freeze_env.sh` before long training or when reproducibility evidence is requested.
- Use `scripts/sanity_check.py` when the target training script exposes a sanity mode, or when a configured sanity command should be run.
- Use `scripts/monitor_training.py` after launching long training, or when diagnosing whether monitoring is active. Run it in `--once` mode for a single check or as a persistent runner for periodic checks.
- Use `scripts/probe_activations.py` when the task needs gradient checks, activation analysis, dead module detection, attention extraction, or information flow tracking. Modes: `gradient`, `activation`, `dead-check`, `attention`, `flow`.

## Agent Automation Protocol

For every deep learning research task, run this state machine automatically. The agent should only ask the user when a missing answer blocks safe progress, when a gate requires confirmation, or when multiple high-impact paths remain plausible.

| Agent State | Automatic Behavior | Required Output | Continue When | Pause / Fallback |
|-------------|--------------------|-----------------|---------------|------------------|
| Observe | Read the user request, active files if available, repository clues, prior logs, configs, and relevant docs. | Context snapshot | The visible context explains the task surface. | Ask for missing artifacts only if they cannot be discovered. |
| Classify | Determine task type, risk level, loop level, and whether this is Discovery, Design, Evidence implementation, training, diagnosis, analysis, or recording. | Task card | Task type and risk are explicit. | If ambiguous, present a short narrowing question. |
| Gather | Build an evidence pack: code paths, configs, metrics, logs, prior reports, baselines, papers, run artifacts, missing evidence, assumptions, and confidence. | Evidence pack | Evidence is sufficient to diagnose or the missing evidence is explicit. | If evidence contradicts itself, route to diagnosis or gather targeted evidence. |
| Atomic Fact Verification | Spawn an independent Fact Verifier subagent. It receives only claims + artifact manifest; it must not see diagnosis, design, or recommendation. It extracts and verifies every objective factual claim against artifacts. | Atomic Fact Verification table | All facts used downstream are `true`; non-true facts are corrected, downgraded, blocked, or sent for evidence gathering. | If any critical fact is `false`, `unverifiable`, `insufficient-source`, or `not-checked`, stop the dependent conclusion. |
| Formal Derivation Verification | Spawn an independent Derivation Verifier subagent. It receives only claims + definitions + code paths; it must not see diagnosis or design preferences. It verifies every mathematical, gradient, objective, and mechanism claim. | Formal Derivation Verification report | Claims are `valid` or explicitly bounded as `partially-valid` / `assumption-dependent`. | If `invalid` or `unverifiable`, correct, downgrade, block, or gather missing facts before proceeding. |
| Independent Evidence Audit | Audit the evidence chain after Atomic Fact Verification. Use an independent Evidence Auditor whenever the next step depends on gathered evidence. | Evidence Auditor verdict | Verdict is `pass` or bounded `conditional-pass`. | If `fail` or `insufficient-evidence`, return to Atomic Fact Verification, Evidence Pack, Formal Derivation Verification, or targeted evidence gathering. |
| Route | Select the next work mode: Discovery, Design, Evidence implementation, sanity check, training plan, monitoring, analysis, decision, or record. | Route decision | The selected mode follows from evidence. | If no route is safe, return to Gather or ask. |
| Mechanistic Analysis | When relevant, inspect the task mechanism, data signal, architecture, loss, optimization dynamics, code path, and competing root causes before diagnosis or design. | Mechanistic Model Analyst Report | The report gives a falsifiable root-cause hypothesis or states the minimal discriminating test. | If static analysis is insufficient, require a probe, sanity check, or runtime check. |
| Pre-Action Compliance | Before any research edit, config change, training launch, or high-impact command, verify that required gates, Branch Plan, and run binding prerequisites are satisfied. | Pre-Action Compliance Check | All required prerequisites are satisfied. | If missing, stop and create the missing Branch Plan, Run-to-Branch Binding, or user confirmation before acting. |
| Act | Generate candidates, select a strategy, prepare a Branch Plan, or perform the smallest useful implementation allowed by the current mode. | Candidate list, selected strategy, Branch Plan, or scoped action result | Action stays within approved scope and has a verification signal. | Stop before high-impact changes or long runs. |
| Verify | Check the result with tests, sanity checks, shape/gradient inspection, metric review, or consistency reasoning. | Verification note | Result is supported by direct evidence or clearly marked limitation. | If verification fails, enter micro-loop or route to diagnosis. |
| Decide | Choose solved, partially solved, unresolved, needs more evidence, redesign, stop, return to Problem, or ask user. | Resolution decision with rationale | Decision is evidence-backed. | If unresolved, record why and restart from Problem or Evidence Pack. |
| Research Record | When explicitly requested by the user, draft a reusable memory record: verified facts, derivations, evidence verdict, mechanism, action, branch/run artifacts, uncertainty, deprecated claims, and restart point. | Research Record draft | User confirms the draft and target location. | Do not write memory until the user confirms the drafted record. |

## Diagnosis Rules

- Do not jump from problem to action. Always pass through Evidence and Diagnosis unless the user explicitly requests a narrow mechanical edit.
- Evidence must be normalized into an evidence pack before conclusions: facts, artifacts, assumptions, missing evidence, contradictions, and confidence.
- Use the current stage to dispatch audit gates automatically. Do not wait for the user to ask for review when objective facts, formal/mechanism claims, evidence-chain claims, or action requests appear.
- Run Atomic Fact Verification for every objective factual claim from every role and every phase before the claim is used for Independent Evidence Audit, Mechanistic Analysis, Diagnosis, Deep Research Brainstorming, Resolution Decision, or Record.
- If the user challenges, corrects, or asks whether a previous factual claim is wrong, immediately switch to `Atomic Fact Verification`. A source lookup such as `grep`, `cat`, log inspection, or a Python check is not sufficient by itself; the response must include an Atomic Fact Verification table that marks the prior claim and the corrected claim separately.
- When a challenged fact is false or insufficiently supported, explicitly deprecate the prior claim and block or revise any downstream conclusion, recommendation, or next action that depended on it. If the prior claim supported a diagnosis, design, result verdict, or recommendation, run Independent Evidence Audit again after the corrected fact table.
- Run Formal Derivation Verification for every mathematical, gradient, objective, variable-dependency, equivalence, or mechanism claim before the claim is used for Independent Evidence Audit, Mechanistic Analysis, Diagnosis, Deep Research Brainstorming, commit messages, Resolution Decision, or Record.
- Run an Independent Evidence Auditor audit after Atomic Fact Verification and before Diagnosis, Deep Research Brainstorming, Resolution Decision, or Record whenever the next step depends on collected evidence.
- The audit verdict must be `pass` or clearly bounded `conditional-pass` before strong claims proceed. `fail` or `insufficient-evidence` returns to Evidence Pack, Atomic Fact Verification, Formal Derivation Verification, or targeted evidence gathering.
- Run Mechanistic Model Analysis before blaming or changing model architecture, loss, training dynamics, metrics, probes, or implementation logic. It must explain underlying causal mechanisms and competing root causes, not only surface symptoms.
- Diagnose the problem type before choosing a strategy: data, preprocessing, model capacity, architecture mismatch, loss/objective, optimization, decoding/inference, metric/evaluation, logging/artifact, reproducibility, literature/baseline gap, or invalid research hypothesis.
- Express the diagnosis as a falsifiable statement: "If this diagnosis is correct, then this verification signal should change."
- Prefer the smallest diagnostic check that can discriminate between plausible causes.
- If evidence is insufficient, ask for the missing artifact or propose the next evidence-gathering step instead of redesigning.

## Subagent Isolation Rules for Verification

Atomic Fact Verification and Formal Derivation Verification must run as independent subagents via the Agent tool, not inline by the main agent. See `references/atomic-fact-verification.md` and `references/formal-derivation-verifier.md` for the exact Agent tool call prompt templates.

**How to spawn (runtime):**
- Fact Verifier: `Agent(description="Atomic Fact Verification", prompt=<claims + artifact manifest only>)`
- Derivation Verifier: `Agent(description="Formal Derivation Verification", prompt=<claims + definitions + assumptions + code paths only>)`
- Both can be spawned in the same turn for parallel execution.

**Fact Verifier subagent isolation:**
- Input: factual claims + artifact manifest only.
- Must NOT receive: main agent's diagnosis draft, design preference, recommendation, or conversation summary.
- Output: verdict table (true / false / unverifiable / insufficient-source / not-checked).
- The main agent consumes the verdict table but cannot upgrade or override verdicts.

**Derivation Verifier subagent isolation:**
- Input: formal claims + definitions + assumptions + code paths only.
- Must NOT receive: main agent's diagnosis, design preference, or recommendation.
- Output: verdict (valid / invalid / partially-valid / assumption-dependent / unverifiable) + corrected statements.
- The main agent consumes the verdict but cannot override invalid verdicts.

**Parallelism:**
- Fact Verifier and Derivation Verifier can run in parallel (spawn both Agent calls in the same turn).
- Deep Research Brainstorming Round 1 can also run in parallel with both verifiers.
- Independent Evidence Auditor must wait for both verifiers to complete before starting.

**When the Agent tool is unavailable:**
- Mark the verification as `non-independent`, explain the limitation, and downgrade any conclusion that depends on it.

## Phase-Gated Audit Dispatch

Every substantive response must identify `当前阶段`, `阶段门控`, and `门控触发原因`. The current stage determines which audit gates run before the response may make claims or recommendations.

| Current stage | Automatic gate dispatch |
|---------------|-------------------------|
| Evidence Pack | Objective facts → Atomic Fact Verification |
| User factual challenge / correction | Switch to Atomic Fact Verification; verify the prior claim and corrected claim in the required table; revise or block dependent conclusions |
| Mechanistic Analysis | Default gate status is `required`. Objective facts → Atomic Fact Verification; mathematical/mechanism/design-rationale claims → Formal Derivation Verification; insufficient static evidence → needs-probe or needs-runtime-check |
| Diagnosis | Requires prior Atomic Fact Verification and Formal Derivation Verification where applicable; diagnosis claims → Independent Evidence Audit |
| Design / Deep Research Brainstorming | Design rationale facts → Atomic; formal mechanism claims → Formal; debate candidate evidence claims → Independent Evidence Audit before selected strategy is finalized |
| Pre-Action Compliance / Branch Plan | Action request → Pre-Action Compliance; research edit → Branch Plan |
| Implementation | Must pass Pre-Action Compliance and Branch Plan before edits |
| Verification / Result Analysis | Result facts → Atomic; result mechanisms → Formal; result conclusions → Independent Evidence Audit |
| Resolution Decision | Requires Atomic, Formal where applicable, and Independent Evidence Audit before verdict |
| Research Record | Only user-memory-request triggers; draft first, write only after user confirmation |

## Independent Evidence Auditor Gate

Before Diagnosis, Deep Research Brainstorming, Resolution Decision, or Research Record, the main agent must use an independent Evidence Auditor whenever the next step depends on collected evidence. The main agent prepares an Audit Packet and stops downstream reasoning until the auditor returns a verdict.

When an independent agent/subagent mechanism is available, the Evidence Auditor must run in a separate context. If no independent reviewer mechanism is available, the main agent must mark the audit as `non-independent`, explain the limitation, and downgrade any conclusion that depends on the audit unless the user explicitly accepts the limitation.

Audit Packet must include:

- `audit_id`;
- `gate_type`: `pre-diagnosis`, `pre-design-selection`, `pre-resolution`, or `pre-record`;
- `neutralized_claims`: claim IDs, claim text, claim type, requested conclusion strength, and downstream action requested;
- Atomic Fact Verification table;
- Formal Derivation Verification report, if applicable;
- raw evidence manifest: paths, run IDs, commands, configs, metrics, logs, commits, diffs, seeds, splits, baselines, artifact hashes, or directly inspectable references;
- contradiction inventory: metric conflicts, failed runs, counterexamples, incompatible baselines, missing or unchecked artifacts;
- missing evidence list;
- allowed auditor scope: evidence support only; no diagnosis, design, tuning, or recommendation.

Audit Packet must not include:

- proposed diagnosis narrative;
- selected design, preferred intervention, or candidate ranking;
- main agent recommendation or final answer draft;
- unverified factual summaries;
- informal mechanism explanations not covered by Formal Derivation Verification;
- user preference signals about the desired conclusion;
- execution pressure such as "this must pass so we can proceed";
- selectively cropped log or metric summaries unless the raw artifact location and omitted-evidence note are also included.

Evidence Auditor context isolation:

- The Evidence Auditor reviews only the Audit Packet.
- It must not read the main agent's diagnosis draft, design draft, final recommendation, private reasoning, or conversation summary beyond the neutralized user question and artifact manifest.
- It outputs only evidence verdict, allowed conclusion strength, conditions, forbidden stronger conclusions, unsupported claims, contradictions, missing evidence, and restart point.

Verdict gate:

- `pass`: proceed only with the audited claim and audited conclusion strength.
- `conditional-pass`: proceed only if every condition is copied into the downstream answer and all stronger conclusions are explicitly forbidden.
- `fail`: block the downstream conclusion; return to Evidence Pack, Atomic Fact Verification, Formal Derivation Verification, or contradiction resolution.
- `insufficient-evidence`: block diagnosis/design/resolution/record; collect the smallest missing evidence requested by the auditor.

The main agent must not reinterpret, soften, or upgrade the Evidence Auditor verdict. If the main agent disagrees, it must gather new evidence and submit a new Audit Packet.

## Universal dl-research Answer Template

Every substantive dl-research response must use this template, regardless of task type. This includes evidence gathering, factual correction, model/loss/code analysis, experiment summaries, design proposals, branch plans, implementation reports, verification notes, status updates, and final answers.

Do not free-form answer with only "key findings", "bottleneck", "recommendation", or "fixed" when the dl-research workflow is active. If a section has no content, keep the section and write `N/A` or `none` with a short reason.

```markdown
当前流程：第 X 步 - [task summary]
当前循环层级：微循环 / 内循环迭代 N / 外循环迭代 M
当前阶段：Evidence Pack / Atomic Fact Verification / Formal Derivation Verification / Independent Evidence Audit / Mechanistic Analysis / Diagnosis / Deep Research Brainstorming / Design / Pre-Action Compliance / Branch Plan / Implementation / Verification / Resolution Decision / Research Record
阶段门控：passed / required / blocked / not-applicable
门控触发原因：objective-fact / formal-claim / evidence-chain-claim / action-request / training-run / user-memory-request / none

## Source State
- User request:
- Artifacts checked:
- Artifacts not checked:
- Tool / command evidence:
- Scope of this answer:

## Evidence Pack
- Problem / question:
- Candidate facts:
- Artifacts:
- Assumptions:
- Missing evidence:
- Contradictions:
- Confidence:

## Atomic Fact Verification
| Fact ID | Factual claim | Source required | Source checked | Verification method | Verdict | Reason | Downstream action |
|---------|---------------|-----------------|----------------|---------------------|---------|--------|-------------------|
| F1 |  |  |  |  | true / false / unverifiable / insufficient-source / not-checked |  |  |

## Corrections / Deprecated Claims
- Deprecated:
- Corrected:
- Conclusions affected:

## Independent Evidence Auditor Audit
- Audit status: pass / conditional-pass / fail / insufficient-evidence / not-applicable
- Claim under review:
- Allowed conclusion strength:
- Unsupported or overstated conclusions:
- Required evidence before proceeding:

## Answer
- Verified facts:
- Allowed conclusion:
- Not allowed to conclude yet:
- Recommendation, if supported:

## Next Action
- Immediate next evidence to collect:
- Gate before action:
- Branch / run binding requirement:
```

Rules:
- Keep the section order exactly as shown: Source State → Evidence Pack → Atomic Fact Verification → Corrections / Deprecated Claims → Independent Evidence Auditor Audit → Answer → Next Action.
- `Source State` must distinguish user-provided claims from independently checked artifacts.
- `Evidence Pack` must appear before diagnosis, design, recommendation, or action.
- Every objective fact must appear in `Atomic Fact Verification` before it is used. If not checked, mark it `not-checked`, `unverifiable`, or `insufficient-source`; do not convert it into a conclusion.
- If no objective factual claim exists, keep the `Atomic Fact Verification` section and write `No objective factual claims in this response` below the table.
- `Corrections / Deprecated Claims` is required even when empty; write `none` when no prior claim is being corrected.
- `Independent Evidence Auditor Audit` is required before any diagnosis, design selection, result verdict, recommendation, or research record. If no evidence-chain claim is being made, keep the section and set `Audit status: not-applicable` with a short reason.
- `Answer` is the only place to give the direct answer, conclusion, implementation summary, or recommendation.
- `Next Action` must state the next gate or evidence step, even if the next action is `none`.
- "Key findings", "current bottleneck", "best experiment", "recommendation", and "fixed" may appear only inside `Answer`, after the verification and audit sections.
- If a previous answer made a wrong factual claim, include `Corrections / Deprecated Claims` and revise or block any dependent recommendation.
- If Independent Evidence Audit is `fail` or `insufficient-evidence`, the answer must end at evidence gathering or correction; do not recommend a design or training action as settled.

Gate status rules:
- `required`: an audit gate must run before strong claims, recommendations, or actions.
- `blocked`: required gate is missing or failed; do not proceed except to gather evidence or draft the missing gate output.
- `passed`: required gate is complete and supports the downstream claim.
- `not-applicable`: no objective fact, formal claim, evidence-chain claim, action request, training run, or memory request is being made.

Mechanistic Analysis special rule:
- Do not mark `阶段门控：not-applicable` during Mechanistic Analysis if the response analyzes model reasonableness, design intent, architecture, loss, objective, optimization dynamics, code path, data signal, root cause, or mechanism.
- Valid statuses for such responses are `required`, `blocked`, or `passed`.
- `not-applicable` is allowed only for a purely procedural note that contains no objective facts, no formal/mechanism claims, no code-path claims, and no design-rationale judgment.

## Git Branch Management Rules

- **No Branch Plan, No Research Edit**: before changing research code, config, data processing, evaluation logic, model architecture, loss, baseline implementation, ablation variant, or training protocol, complete the Pre-Action Compliance Check and Branch Plan.
- **No Run-to-Branch Binding, No Training Claim**: before launching or interpreting a training/evaluation/sanity/ablation run, record Run-to-Branch Binding or mark the result as noncompliant and limited reproducibility.
- Use Git Branch Experiment Management for any research task that changes code, config, data processing, evaluation logic, baseline implementation, ablation variant, model architecture, loss, or training protocol.
- Before implementation, create or request a Branch Plan: base branch, base commit, new branch, branch type, linked hypothesis or issue, allowed scope, expected files, forbidden files, verification signal, and rollback point.
- Every run must record Run-to-Branch Binding: branch, base branch, head commit, worktree status, diff summary, config, command, seed/split, environment snapshot, artifact manifest, and evidence audit verdict.
- Ablation branches must derive from the same audited full-model commit and should change only one factor unless an interaction ablation is approved.
- Do not recommend merging experiment branches unless sanity, evidence audit, comparability, artifact record, and user confirmation are complete.

## Pre-Action Compliance Rules

Run this check before file edits, config changes, branch changes, training launches, evaluation launches, or high-impact commands in dl-research tasks:

- required design or diagnosis exists for the action;
- Atomic Fact Verification and Independent Evidence Audit are complete for facts supporting the action;
- Branch Plan exists for research edits;
- current branch matches the Branch Plan, or user has approved branch creation/switching;
- dirty worktree has been classified as related or unrelated;
- allowed files and forbidden files are known;
- Run-to-Branch Binding prerequisites exist before training or evaluation;
- user confirmation has been obtained for guided/strict gates and long or expensive runs.

If any item is missing, stop before acting and create the missing record. If an action already happened without this gate, open a Branch Noncompliance Incident and downgrade reproducibility until the state is recorded.

## Deep Research Brainstorming Rules

Use Deep Research Brainstorming after Diagnosis to find the best solution for the diagnosed problem. Read `references/debate-brainstorming.md` for the full protocol.

- Run Deep Research Brainstorming after Diagnosis and before Pre-Action Compliance.
- The diagnosis provides the problem statement, root cause hypothesis, and success criteria that drive the research.
- Phase 1 (Research): 3 agents in parallel — External Research (WebSearch+WebFetch), Internal Audit (Read+Grep+Glob), Failure Analysis (Read history). Each gathers knowledge into a shared Knowledge Base.
- Phase 2 (Propose + Evaluate): 1 agent reads Knowledge Base, proposes 3-5 candidates with mechanism derivation, evidence anchoring, cost, verification design, and Devil's Advocate.
- Phase 3 (Adversarial Verify + Synthesize): 1 agent tries to REFUTE each candidate. Survivors get final ranking, fusion proposal, discriminating experiments.
- Total: 5 agents, 3 batches, ~20k tokens.
- On outer-loop restart, Failure Analysis receives ALL previous attempts to prevent cycling.
- Do not implement until the Research Verdict is complete and the required gate is passed.

## Resolution Rules

- **Solved**: verification signal meets the predefined success criterion and no blocking regression appears.
- **Partially solved**: target signal improves but misses the criterion or creates a tradeoff that needs user/research decision.
- **Unresolved**: verification fails, evidence contradicts the diagnosis, or the result is inconclusive.
- **Needs more evidence**: required artifacts are missing or confidence is too low to choose a solution.
- When unresolved, record the attempted solution, why it failed, what evidence changed, and restart from Problem or Evidence Pack.

## Active Monitoring Rules

For long training or multi-epoch experiments, do not wait until completion before analysis. Create a monitoring plan and run periodic checks.

Active Monitoring Loop:

```text
Training Start → Monitoring Plan → Periodic Check → Trigger Detection → Mini Diagnosis → Action Decision → Continue / Intervene / Stop / Restart → Record
```

The monitoring plan must state check frequency, monitored files, core metrics, anomaly triggers, and allowed actions. In `guided`, report anomalies and wait for confirmation before intervention. In `full-auto`, intervene within the allowed modification scope. In `strict-confirmation`, report only.

After starting a long training job, the agent must start or explicitly propose a persistent Monitor Runner. A written Monitoring Plan alone is not enough to claim active monitoring. Use `scripts/monitor_training.py` as the default runner when the project does not already provide one. The runner should write `monitoring_events.jsonl` and `monitoring_state.json` into the run directory whenever possible. If the runner is not started, record monitoring as `not active` and explain why.

Default Active Monitoring thresholds apply unless the Monitoring Plan overrides them:

- check every 5 minutes;
- trend window: last 10 epochs/steps;
- heartbeat stale for 10 minutes → warning; 20 minutes → critical;
- any NaN/Inf in loss or metric → critical;
- process exit once → critical;
- validation metric no improvement for 10 epochs → warning; 20 epochs → failed;
- train improves while validation degrades for 5 epochs → warning; 10 epochs → critical;
- primary metric worsens for 5 epochs → warning; 10 epochs → critical;
- loss has no meaningful decrease for 10 epochs → warning; 20 epochs → failed;
- missing critical artifact once → warning; twice consecutively → critical.

## Automatic Routing Rules

- **Discovery request** → Identify the research problem, gather literature/baseline/prior-run evidence, state one falsifiable hypothesis, then Record.
- **Design request** → Gather Discovery outputs, draft algorithm design and experimental protocol, then stop at Design Gate for confirmation.
- **Implementation request** → Require a Design output or infer a minimal bounded design, gather relevant code, make minimal scoped changes, Verify, then Record.
- **Training request** → Gather config and command requirements, prepare reproducible run sheet and monitoring plan, then stop at Run Gate unless `full-auto` is active.
- **Long training after launch** → Start or propose `scripts/monitor_training.py` with the run directory, process id/query, primary metric, and default 5-minute interval; verify at least one `monitoring_events.jsonl` record is written.
- **Training log diagnosis** → Gather logs and metrics, Route to Evidence analysis, identify failure mode, Decide next smallest check or intervention.
- **Result analysis** → Gather metrics, artifacts, baseline, and probes; Analyze quantitatively and qualitatively; Decide whether the hypothesis is supported.
- **Hyperparameter tuning** → Require a failure diagnosis first. Do not blindly tune; Route through Evidence analysis and Decision before suggesting changes.

## Gate Rules

- **Activation Gate**: Required when dl-research is triggered implicitly. Ask whether to start and which execution mode to use.
- **Atomic Fact Verification Gate**: Automatically required for every objective factual claim from any role or phase before downstream use. Facts must be marked `true`, `false`, `unverifiable`, `insufficient-source`, or `not-checked`; only `true` facts may support strong claims.
- **User Factual Challenge Gate**: Required whenever the user disputes, corrects, or asks whether a prior factual claim is wrong. The agent must output the Atomic Fact Verification table, mark the old claim and corrected claim separately, and revise or block any dependent conclusion before continuing.
- **Formal Derivation Verification Gate**: Automatically required for every mathematical, gradient, objective, variable-dependency, equivalence, mechanism, or commit-message claim. Claims must be marked `valid`, `invalid`, `partially-valid`, `assumption-dependent`, or `unverifiable`; invalid or unverifiable claims cannot support downstream conclusions.
- **Design Gate**: Required before code changes for new architectures, losses, data transforms, experiment protocols, or non-trivial refactors, unless `full-auto` mode is active.
- **Pre-Action Compliance Gate**: Required before research file edits, config changes, branch changes, training/evaluation launches, or high-impact commands. Missing Branch Plan or Run-to-Branch Binding prerequisites must block action.
- **Mechanistic Analysis Gate**: Automatically required before model/loss/protocol design, training-failure diagnosis, ablation interpretation, probe-conflict interpretation, or code-path mechanism claims. The report must state candidate root causes and the smallest discriminating test when evidence is insufficient.
- **Branch Creation Gate**: Required before implementing research code changes. Define the Git branch plan and scope. In guided or strict-confirmation modes, ask before creating or switching branches.
- **Sanity Gate**: Required before trusting full training. At minimum, verify tensor shapes, device placement, finite loss, gradient flow, and tiny-batch overfit or an equivalent task-specific check. In `full-auto`, the agent may proceed without user confirmation but must still perform or record the sanity evidence.
- **Independent Evidence Audit Gate**: Automatically required after Atomic Fact Verification and before Diagnosis, Deep Research Brainstorming, Resolution Decision, or Record when the step depends on evidence. Use an independent Evidence Auditor whenever an independent reviewer mechanism is available. The auditor receives only the Audit Packet, verifies evidence-chain support, traceability, reproducibility, baseline comparability, contradictions, assumptions, and allowed conclusion strength, and returns a verdict that the main agent cannot upgrade or reinterpret.
- **Run Gate**: Required before launching long, expensive, destructive, or externally visible jobs, unless `full-auto` mode is active and higher-priority permission rules allow the run.
- **Resolution Decision Gate**: Required after each experiment or failed run. In `full-auto`, the agent may make the resolution decision without user confirmation, but must record the status and restart point.
- **Research Record Gate**: Triggered only when the user explicitly asks to remember, record, save, archive, or write a research result. First draft the Research Record in template format, then wait for user confirmation before writing to any memory file.

## Stop Conditions

The agent must pause and ask the user before:

- making high-impact architecture, data, loss, or training-protocol changes without an approved design;
- launching long or expensive training;
- deleting, overwriting, or moving user artifacts;
- presenting a guess as a verified research conclusion;
- switching from minimal intervention to redesign;
- continuing after evidence shows the current hypothesis is invalid.

## Discovery: Problem, Literature, Hypothesis

The agent should automatically:

- define the task boundary: inputs, outputs, evaluation target, constraints, and why the problem matters;
- gather available literature, baselines, prior runs, known failures, and repository-local evidence;
- diagnose the gap, bottleneck, failure mode, or uncertainty that makes the problem worth studying;
- state one primary falsifiable hypothesis and optional backup hypotheses;
- define what evidence would support or reject the hypothesis.

Required output:

- problem statement;
- evidence map: papers, baselines, prior runs, missing evidence;
- atomic fact verification table;
- formal derivation verification report when formal/mechanism claims are present;
- research record;
- assumptions and confidence level;
- diagnosis of the core bottleneck or evidence gap;
- core hypothesis;
- minimum success criterion and rejection signal.

## Design: Algorithm and Experiment Protocol

The agent should automatically:

- translate the hypothesis into algorithm components: data flow, backbone, neck, head, loss, optimization, inference, and analysis probes;
- define the experimental protocol: datasets, splits, preprocessing, augmentations, metrics, seeds, compute assumptions, and artifacts;
- design fair comparisons: baselines, controls, and one-factor-at-a-time ablations;
- choose the strategy: minimal intervention, controlled variant, or deeper redesign, and state why;
- run Deep Research Brainstorming to generate, attack, and compare candidate solutions before choosing the strategy;
- predict failure modes and diagnostics;
- stop at Design Gate before implementation when the design changes core behavior.

Required output:

- algorithm design document;
- mechanistic model analyst report;
- atomic fact verification table for all objective facts used by the design;
- formal derivation verification report for loss, gradient, objective, and mechanism claims;
- experiment protocol;
- branch plan for implementation;
- research record;
- ablation matrix;
- failure-mode and rollback plan.

## Evidence: Implementation, Training, Ablation, Analysis

The agent should automatically:

- implement only the approved or bounded design;
- verify that the implemented code path expresses the intended mechanism and that loss gradients can drive the desired behavior;
- run or propose sanity checks before full training: shapes, finite loss, device placement, gradient flow, tiny-batch overfit, and probe outputs;
- prepare reproducible training commands and environment snapshots;
- bind each run to its Git branch, head commit, worktree status, and diff summary;
- run the Active Monitoring Loop with a persistent Monitor Runner during training for NaN, stalled loss, mode collapse, overfitting, metric conflicts, heartbeat staleness, and artifact inconsistency;
- compare main results with baselines under compatible conditions;
- run or plan ablations that directly test the hypothesis;
- analyze quantitative metrics and qualitative probes;
- decide whether the hypothesis is supported, partially supported, rejected, or inconclusive.

Required output:

- mechanistic analysis report;
- atomic fact verification table for all objective facts used by the analysis;
- formal derivation verification report for mathematical, gradient, objective, and mechanism claims;
- sanity evidence;
- run-to-branch binding;
- independent evidence auditor verdict;
- active monitoring plan and monitoring records;
- main experiment results;
- ablation results;
- failure analysis if needed;
- hypothesis verdict;
- resolution decision: solved, partially solved, unresolved, needs more evidence, or invalid problem;
- next experimental action.
- research record.

## Additional Resources

### Reference Files

- **`references/research-framework.md`** — Detailed Discovery/Design/Evidence phase descriptions, generic archive format, ablation matrix template, convergence rules, agent gates, and failure-mode catalog.
- **`references/probe-toolkit.md`** — Analysis probe implementation patterns (CAM, attention map, feature visualization, gradient flow check).
- **`references/atomic-fact-verification.md`** — Global fact-checking layer for every objective factual claim from any role, phase, report, diagnosis, design, run analysis, or final record.
- **`references/formal-derivation-verifier.md`** — Formal reasoning layer for mathematical derivations, gradients, objective/metric alignment, variable dependencies, and mechanism claims.
- **`references/evidence-reviewer.md`** — Independent evidence audit role, Audit Packet contract, context-isolation rules, verdict gate, fact consistency, traceability, reproducibility, baseline fairness, contradiction checks, and allowed conclusion strength.
- **`references/git-branch-management.md`** — Git branch workflow for research hypotheses, experiment variants, ablations, baselines, debug branches, run-to-branch binding, merge/archive decisions, and failed experiment records.
- **`references/mechanistic-model-analyst.md`** — Mechanism-level analysis of model architecture, loss behavior, optimization dynamics, code paths, ablations, probes, and root causes.
- **`references/research-recorder.md`** — User-triggered recorder that drafts a structured memory record and writes it only after user confirmation.

### Helper Scripts

- **`scripts/sanity_check.py`** — Minimal training loop for sanity check: overfit a tiny batch and verify loss convergence.
- **`scripts/freeze_env.sh`** — Freeze current Python/conda environment for reproducibility.
- **`scripts/monitor_training.py`** — Persistent Active Monitoring runner: periodically checks logs, metrics, checkpoints, and optional process liveness, then writes `monitoring_events.jsonl` and `monitoring_state.json`.
- **`scripts/probe_activations.py`** — Hook-based model probe: gradient flow check, activation distributions, dead module detection, attention extraction, information flow tracking. Modes: `gradient`, `activation`, `dead-check`, `attention`, `flow`.

### Example Files

- **`examples/hypothesis-design-template.md`** — Template for Discovery-linked Design Gate output.
