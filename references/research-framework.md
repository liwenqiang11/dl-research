# Research Framework — Detailed Reference

## Generic Research Archive Format

Archive baseline papers, prior runs, or important decisions in the repository's preferred research memory location. If the project has no established location, propose a lightweight repository-local file such as `research-memory.md`, `papers.md`, or `experiments/<experiment_id>/report.md` and ask before creating it.

```
Entry type: paper / baseline / experiment / decision / failure
Title:
Source:
Method or change summary:
Evidence:
Link or artifact path:
Decision impact:
---
```

Principles:
- Keep archives repository-local unless the user requests an external tracker.
- Record enough context for another researcher to reproduce the reasoning.
- Prefer stable artifact paths, commit hashes, configuration files, and exact commands over prose-only notes.

## Agent State Contract

Use this contract to make the agent's behavior predictable. Each state describes what the agent should do automatically, what it should output, and when it must pause.

| Agent State | Inputs | Automatic Actions | Outputs | Continue Condition | Pause / Fallback |
|-------------|--------|-------------------|---------|--------------------|------------------|
| Observe | User request, active files, repo clues | Read available context, identify referenced files, note visible constraints | Context snapshot | Task surface is understood | Ask only for unavailable blocking artifacts |
| Classify | Context snapshot | Identify task type, risk, research loop level, and likely work mode | Task card | Type and risk are explicit | Ask a focused narrowing question |
| Gather | Task card | Inspect minimal relevant code, configs, logs, metrics, papers, reports, baselines, assumptions, and contradictions | Evidence pack | Enough evidence to diagnose or missing evidence is explicit | Gather targeted evidence or mark uncertainty |
| Route | Evidence pack | Choose Discovery, Design, Evidence implementation, sanity, training plan, monitoring, analysis, resolution decision, or record | Route decision | Route follows from evidence | Return to Gather if route is unsafe |
| Act | Route decision | Brainstorm candidates, select a strategy, draft, patch, inspect, propose command, or analyze within the selected mode | Candidate list, selected strategy, or scoped action result | Action stays inside scope and has a verification signal | Stop before high-impact changes |
| Verify | Action result | Run tests/checks when feasible, or perform evidence-based consistency checks | Verification note | Result is supported or limitation is explicit | Enter micro-loop or route to diagnosis |
| Decide | Verification note | Select solved, partially solved, unresolved, needs more evidence, redesign, stop, return to Problem, or ask user | Resolution decision | Rationale is evidence-backed | Record failure and restart point |
| Record | Resolution decision | Preserve reusable lesson and next seed hypothesis | Archive-ready summary | Future agent can resume | Include record in response if no file write |

## Activation and Autonomy Modes

Use an Activation Gate when the skill is triggered implicitly. Activation Gate is a blocking ask gate. If the user explicitly requests `dl-research`, says to start/continue it, or selects a mode, do not ask whether to activate again; still ask and wait for any missing execution mode or research task before advancing.

Activation prompt:

```markdown
检测到这是深度学习研究/实验任务。是否启用 dl-research 流程？
执行模式：
- guided: 自动推进分析，但关键门控确认。
- full-auto: 全自动推进，允许绕过 dl-research 流程门控，但必须记录绕过项和风险。
- strict-confirmation: 每个阶段转换和实施动作都先确认。
```

Blocking rules:
- No activation answer, no workflow advance.
- If activation is implicit and the user has not confirmed activation, ask and wait.
- If execution mode is missing, ask for `guided`, `full-auto`, or `strict-confirmation` and wait.
- If the research task or goal is missing, ask for it and wait.
- If both mode and task are missing, ask for both in the same turn and wait.
- When the `AskUserQuestion` tool is available, selection/confirmation gates must call `AskUserQuestion` and wait. If unavailable, ask a concise plain-text question and stop.
- Default `guided` may be applied only after the user confirms activation/continuation but does not choose a mode.
- Printing an activation prompt without waiting is Gate Noncompliance; return to Activation Gate before continuing.

## AskUserQuestion Gate Protocol

Use `AskUserQuestion` for selection and confirmation gates whenever the tool is available. The call must be part of the visible gate flow, and the workflow must stop until the user answers.

Required uses:

| Gate | Use `AskUserQuestion` for |
|------|---------------------------|
| Activation Gate | Enable dl-research, choose mode, or provide missing task |
| Goal Gate | Missing `full-auto` goal fields |
| Design Gate | Approve, revise, or block a design |
| Branch Creation Gate | Create/switch branch or approve branch plan |
| Run Gate | Launch long/expensive/external training or evaluation |
| Resolution Decision Gate | Choose solved/partial/unresolved/redesign/stop when tradeoffs remain |
| Research Record Gate | Confirm record draft and memory location before writing |

If a gate requires user selection/confirmation and `AskUserQuestion` is available but not called, set `阶段门控：blocked`, record Gate Noncompliance, and return to the missing gate.

| Mode | Agent May Do Automatically | Must Confirm Before | Best For |
|------|----------------------------|---------------------|----------|
| guided | Observe, Classify, Gather, Evidence Pack, Diagnosis, candidate generation, low-risk analysis | Design changes, implementation, long runs, resolution decisions with tradeoffs | Default collaborative research |
| full-auto | All dl-research workflow steps, including candidate selection, implementation, runs, resolution decisions, and restarts | Only higher-priority system, tool, security, or explicit user permission requirements | User wants maximum automation |
| strict-confirmation | Read context and propose next step | Every phase transition, file edit, command, implementation, or run | Fragile projects or high uncertainty |

Full-auto gate bypass rules:
- dl-research workflow gates may be bypassed after the user selects `full-auto`;
- bypassed gates must be recorded in the final or archive note;
- the agent must still capture evidence, diagnosis, verification status, and unresolved restart point;
- the agent must not claim a conclusion is verified unless the evidence supports it;
- this mode does not override higher-priority system, tool, security, or explicit user permission requirements.

## Goal Gate

Before `full-auto` begins, require only these fields:

```markdown
请给出 full-auto 目标：
- 要解决的问题：
- 成功标准：
- 允许修改范围：
```

Parsing rules:
- If the user provides `/goal`, `Goal:`, or `目标：`, extract the three fields when possible.
- If only some fields are present, ask only for the missing fields.
- Do not require budget, stop conditions, or extra metadata unless the user adds them.
- The success criterion defines the default solved condition for the Resolution Decision.

## Problem-Solving Contract

Use this contract as the backbone of every Discovery, Design, or Evidence task.

| Step | Core Question | Required Output | Failure Mode |
|------|---------------|-----------------|--------------|
| Problem | What exactly must be solved? | Problem statement, success signal, constraints | Vague goal or moving target |
| Evidence Pack | What do we know, what is missing, and how confident are we? | Facts, artifacts, assumptions, contradictions, confidence | Guessing from memory |
| Atomic Fact Verification | Is every objective factual claim correct according to artifacts? | Atomic Fact Verification table | False or unverified facts contaminate reasoning |
| Formal Derivation Verification | Does the mathematical or mechanism conclusion follow? | Formal Derivation Verification report | Valid facts but invalid reasoning |
| Independent Evidence Audit | Do verified facts form an evidence chain that supports the claim? | Independent Evidence Auditor verdict with allowed conclusion strength | Unsupported or overstated conclusions |
| Mechanistic Analysis | What underlying mechanism or root cause explains the evidence? | Mechanistic Model Analyst Report with competing causes and discriminating test | Treating symptoms as causes |
| Diagnosis | What kind of problem is this? | Root-cause class and competing causes | Treating symptoms as causes |
| Debate Brainstorming | What possible solutions could address the diagnosis? Run multi-Advocate debate to find the best approach. | Debate verdict with convergence analysis, ranked candidates, fusion proposal, unresolved disputes | Single-solution fixation |
| Pre-Action Compliance | Is it safe and compliant to act now? | Pre-Action Compliance Check | Editing or running before required gates |
| Branch Plan | What Git branch isolates this research change? | Base branch, base commit, new branch, scope, expected files, rollback point | Experiments contaminate each other |
| Implementation | What is the smallest useful step? | Patch, design, command, analysis, or check | Overbroad redesign |
| Verification | Did the target signal change? | Test/sanity/metric/probe evidence | Unverified conclusion |
| Resolution Decision | Is the problem solved? | Solved, partially solved, unresolved, needs more evidence, or invalid problem | Endless tuning |
| Research Record / Restart | What should future agents know and where should the loop restart? | Research Record with artifacts, verdicts, deprecated claims, uncertainty, and restart point | Lost learning |

## Phase-Gated Audit Dispatcher

Every substantive research response must state:

```markdown
当前阶段：
阶段门控：passed / required / blocked / not-applicable
门控触发原因：objective-fact / formal-claim / evidence-chain-claim / action-request / training-run / user-memory-request / none
```

The current stage automatically dispatches required audit gates. Do not wait for the user to request review.

| Current stage | Trigger | Required gate |
|---------------|---------|---------------|
| Evidence Pack | Objective facts in collected evidence | Atomic Fact Verification |
| User factual challenge / correction | User disputes, corrects, or questions a prior factual claim | Atomic Fact Verification table for the prior claim and corrected claim; Independent Evidence Audit again if any dependent conclusion changes |
| Atomic Fact Verification | Non-true critical facts | Block dependent conclusions or gather evidence |
| Formal Derivation Verification | Invalid/unverifiable derivation | Block or correct mechanism/formal claim |
| Independent Evidence Audit | Evidence-chain claim | Atomic Fact Verification first; Formal Derivation Verification when formal claims exist |
| Mechanistic Analysis | Any model reasonableness, design intent, architecture, loss, objective, optimization, code-path, data-signal, root-cause, or mechanism analysis | Gate status cannot be `not-applicable`; dispatch Atomic and/or Formal as needed |
| Mechanistic Analysis | Objective fact | Atomic Fact Verification |
| Mechanistic Analysis | Mathematical, gradient, objective, mechanism, or design-rationale claim | Formal Derivation Verification |
| Diagnosis | Root-cause claim | Independent Evidence Audit after required fact/derivation checks |
| Design / Debate Brainstorming | Design rationale, debate verdict, or selected strategy | Atomic + Formal where applicable + Independent Evidence Audit |
| Pre-Action Compliance / Branch Plan | Edit/config/branch/train/evaluate action | Pre-Action Compliance and Branch Plan / Run-to-Branch prerequisites |
| Implementation | Research edit | Pre-Action Compliance must be passed |
| Verification / Result Analysis | Result metric/log/artifact fact | Atomic Fact Verification |
| Verification / Result Analysis | Result mechanism explanation | Formal Derivation Verification |
| Verification / Result Analysis | Result conclusion | Independent Evidence Audit |
| Resolution Decision | Verdict | Atomic + Formal where applicable + Independent Evidence Audit |
| Research Record | User memory request | Draft Research Record, wait for confirmation before writing |

Gate status meanings:
- `required`: run the gate before making a strong claim, recommendation, or action.
- `blocked`: the gate is missing or failed; only gather evidence, correct the claim, or draft the missing gate output.
- `passed`: the gate supports the downstream use.
- `not-applicable`: no gated claim or action is present.

Mechanistic Analysis special rule:
- During Mechanistic Analysis, `not-applicable` is valid only for a purely procedural note with no objective facts, no formal/mechanism claims, no code-path claims, and no design-rationale judgment.
- If the response analyzes model reasonableness or design intent, the gate status must be `required`, `blocked`, or `passed`.

## Evidence Pack Standard

Before diagnosis or solution selection, normalize evidence into this shape:

```markdown
## Evidence Pack
- Problem statement:
- Success criterion:
- Facts:
- Artifacts:
  - Code:
  - Config:
  - Logs:
  - Metrics:
  - Baselines/papers:
  - Run outputs:
- Assumptions:
- Missing evidence:
- Contradictions:
- Confidence: high / medium / low
- Next evidence to collect if blocked:
```

Rules:
- Facts must point to artifacts or direct observation.
- Assumptions must be labeled and must not be used as final conclusions.
- Contradictions must be resolved or carried into Diagnosis as competing causes.
- Confidence is low when key artifacts are missing, metrics are incompatible, or the run cannot be reproduced.

## Universal dl-research Answer Standard

Every substantive dl-research response must use this standard, regardless of task type. This includes evidence gathering, factual correction, model/loss/code analysis, experiment summaries, design proposals, branch plans, implementation reports, verification notes, status updates, and final answers.

If a section has no content, keep the section and write `N/A` or `none` with a short reason.

```markdown
当前流程：第 X 步 - [task summary]
当前循环层级：微循环 / 内循环迭代 N / 外循环迭代 M
当前阶段：Evidence Pack / Atomic Fact Verification / Formal Derivation Verification / Independent Evidence Audit / Debate Brainstorming / Mechanistic Analysis / Diagnosis / Design / Pre-Action Compliance / Branch Plan / Implementation / Verification / Resolution Decision / Research Record
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

## Independent Evidence Audit
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
- Keep the section order exactly as shown: Source State → Evidence Pack → Atomic Fact Verification → Corrections / Deprecated Claims → Independent Evidence Audit → Answer → Next Action.
- Do not put "key findings", "bottleneck", "best experiment", "fixed", or "recommended next step" before the Atomic Fact Verification table and Independent Evidence Audit.
- User-provided summaries are candidate evidence, not verified facts, until checked against artifacts.
- Every objective fact must either be verified in the table or explicitly marked `not-checked`, `unverifiable`, or `insufficient-source`.
- If no objective factual claim exists, keep the `Atomic Fact Verification` section and write `No objective factual claims in this response` below the table.
- If only part of the evidence is verified, conclusions must be limited to the verified subset and the answer must name what remains unchecked.
- `Independent Evidence Audit` is required before any diagnosis, debate brainstorming, result verdict, recommendation, or research record. If no evidence-chain claim is being made, keep the section and set `Audit status: not-applicable` with a short reason.
- `Answer` is the only place to give the direct answer, conclusion, implementation summary, or recommendation.
- `Next Action` must state the next gate or evidence step, even if the next action is `none`.
- If a previous wrong claim affected a recommendation, include it under `Corrections / Deprecated Claims` and rerun Independent Evidence Audit for the revised claim.

## Atomic Fact Verification Standard

Run Atomic Fact Verification for every objective factual claim from every role and every phase before downstream use. See `references/atomic-fact-verification.md` for the full contract.

```markdown
## Atomic Fact Verification
| Fact ID | Factual claim | Source required | Source checked | Verification method | Verdict | Reason | Downstream action |
|---------|---------------|-----------------|----------------|---------------------|---------|--------|-------------------|
| F1 |  |  |  |  | true / false / unverifiable / insufficient-source / not-checked |  | use / downgrade / block / gather evidence |
```

Rules:
- Objective facts from Evidence Pack, Independent Evidence Audit, Mechanistic Analysis, Diagnosis, Design, Branch Plan, Sanity, Training, Monitoring, Results, Resolution, and Record all require verification.
- User challenges or corrections of factual claims require a correction audit: verify the prior claim and corrected claim in the table, then deprecate, revise, or block dependent conclusions.
- Source inspection alone is not enough. A `grep`, CSV read, log read, or Python check must be reflected in the Atomic Fact Verification table before the corrected fact is used.
- If a new factual claim appears after a previous verification table, run Atomic Fact Verification again for the new claim.
- Only facts marked `true` may support strong claims.
- Facts marked `false`, `unverifiable`, `insufficient-source`, or `not-checked` must be corrected, downgraded, blocked, or sent for targeted evidence gathering.

## Evidence Audit Standard

Run an automatic Independent Evidence Audit after Atomic Fact Verification and Formal Derivation Verification whenever a diagnosis, debate brainstorming verdict, experiment verdict, or archived conclusion depends on collected evidence. See `references/evidence-reviewer.md` for the full role contract.

```markdown
## Independent Evidence Audit
- Verdict: pass / conditional-pass / fail / insufficient-evidence
- Claim under review:
- Allowed conclusion strength:
- Atomic fact verification table:
- Non-true facts used by claim:
- Formal derivation verification report:
- Invalid or unverifiable derivations used by claim:
- Traceability:
- Reproducibility:
- Baseline comparability:
- Statistical adequacy:
- Data and label validity:
- Probe validity:
- Contradictions:
- Assumptions incorrectly treated as facts:
- Unsupported or overstated conclusions:
- Required evidence before proceeding:
- Restart point if blocked: Evidence Pack / Diagnosis / Discovery / Design / Record
```

Rules:
- `pass` or explicitly bounded `conditional-pass` may proceed to Diagnosis, Debate Brainstorming, Resolution Decision, or Record.
- `fail` and `insufficient-evidence` must return to Atomic Fact Verification, Evidence Pack, or targeted evidence gathering.
- The reviewer checks whether verified facts are sufficient for the claim; it does not perform informal fact checking, propose new algorithms, or tune parameters.
- If evidence supports only a weak conclusion, downgrade the wording before proceeding.

## Formal Derivation Verification Standard

Run Formal Derivation Verification for every mathematical, gradient, objective, equivalence, variable-dependency, mechanism, or commit-message claim. See `references/formal-derivation-verifier.md` for the full contract.

```markdown
## Formal Derivation Verification
- Claim under review:
- Atomic facts used:
- Definitions:
- Assumptions:
- Derivation steps:
- Variable dependency:
- Gradient dependency:
- Scale or normalization analysis:
- Counterexample or edge case:
- Verdict: valid / invalid / partially-valid / assumption-dependent / unverifiable
- Corrected statement:
- Downstream action: use / downgrade / block / gather facts / run diagnostic
```

Rules:
- Formal claims must use facts already checked by Atomic Fact Verification.
- `invalid` and `unverifiable` derivations cannot support Diagnosis, Debate Brainstorming, commit messages, Resolution Decision, or Record.
- `partially-valid` claims must be rewritten to the supported part only.
- `assumption-dependent` claims must carry their assumptions wherever used.

## Research Recorder Standard

Use `references/research-recorder.md` only when the user explicitly asks to remember, record, save, archive, or write the current research result.

Workflow:

```text
User requests memory/record
→ Draft Research Record in template format
→ User confirms or edits
→ Write confirmed record to agreed location
```

```markdown
## Research Record
- Record type:
- Date/time:
- Phase: Discovery / Design / Evidence / Resolution / Record
- Loop level: micro / inner N / outer M
- Task or hypothesis:
- Branch and commit:
- Run ID / artifact paths:
- Atomic fact verification:
- Formal derivation verification:
- Evidence review:
- Mechanistic analysis:
- Action taken:
- Verification result:
- Decision:
- Deprecated or corrected prior claims:
- Remaining uncertainty:
- Next action:
- Restart point:
```

Rules:
- Do not write research memory automatically at phase boundaries or decision points.
- Draft first, then wait for user confirmation before writing.
- Do not strengthen conclusions beyond the Independent Evidence Audit verdict.
- Do not introduce new factual claims without Atomic Fact Verification.
- Do not introduce new formal/mechanism claims without Formal Derivation Verification.
- Every unresolved outcome must name a restart point.
- Wrong prior claims must be recorded as deprecated or corrected, not silently erased.

## Diagnosis Matrix

| Problem Type | Evidence to Gather | Diagnostic Question | Verification Signal |
|--------------|-------------------|---------------------|---------------------|
| Data or label issue | Samples, labels, split code, preprocessing outputs | Are inputs and targets aligned and representative? | Visual/sample audit passes; split leakage absent; label stats plausible |
| Preprocessing mismatch | Transform code, saved tensors, normalization stats | Does training/evaluation see the intended distribution? | Tensor ranges/shapes match protocol; train/val transforms compatible |
| Model architecture mismatch | Forward path, shapes, parameter counts, probes | Can the architecture express the hypothesis mechanism? | Shape checks pass; probes show intended module is used |
| Loss/objective issue | Loss terms, scales, gradients, target encoding | Does the objective optimize the desired behavior? | Loss components finite and balanced; gradients reach intended modules |
| Optimization issue | LR, optimizer, schedule, gradient norms, batch size | Is training numerically and dynamically stable? | Tiny overfit succeeds; gradients finite; loss decreases on controlled data |
| Inference/decoding issue | Validation code, thresholds, postprocess, metrics | Does evaluation use the same decision logic as training intent? | Controlled predictions decode as expected; metric implementation verified |
| Evaluation/metric issue | Metric code, baseline protocol, confidence intervals | Does the metric reflect the success criterion fairly? | Baseline comparison is compatible; metric aliases and directions are clear |
| Artifact/logging issue | Output paths, logs, checkpoints, configs | Can evidence be reproduced and audited? | Required artifacts exist and match the run command/config |
| Baseline/literature gap | Papers, prior runs, public baselines | Is the claimed gap real and fairly tested? | At least one comparison point or justified minimal baseline exists |
| Invalid hypothesis | Ablations, probes, subgroup errors | Did evidence reject the proposed mechanism? | Full model fails to beat controls or probes contradict mechanism |

## Strategy Selection

| Strategy | Use When | Advantage | Risk | Required Gate |
|----------|----------|-----------|------|---------------|
| Minimal intervention | Cause is local, evidence is thin, or user needs a quick fix | Low blast radius, fast verification | May leave structural debt | Verification Gate |
| Controlled experimental variant | Hypothesis is plausible but unproven | Stronger causal evidence | Requires careful controls | Design Gate |
| Best-practice redesign | Existing design blocks correctness or fair evaluation | Better long-term foundation | Higher breakage and migration risk | Design Gate and user confirmation |
| Evidence gathering only | Key artifacts are missing | Avoids blind action | No immediate fix | Record Gate |

## Git Branch Experiment Management

Use `references/git-branch-management.md` whenever a task changes code, config, data processing, evaluation logic, baseline implementation, ablation variant, model architecture, loss, or training protocol.

Hard rules:
- No Branch Plan, No Research Edit.
- No Run-to-Branch Binding, No Training Claim.

Before research edits, config changes, branch switches, training/evaluation launches, or high-impact commands, run a Pre-Action Compliance Check.

Required before implementation:

```markdown
## Branch Plan
- Base branch:
- Base commit:
- New branch:
- Branch type: research / exp / ablation / baseline / debug / archive
- Hypothesis or issue linked:
- Allowed change scope:
- Files expected to change:
- Files that must not change:
- Verification signal:
- Rollback branch or commit:
```

Required before action when relevant:

```markdown
## Pre-Action Compliance Check
- Intended action:
- Action type: edit / config-change / branch-change / train / evaluate / high-impact-command
- Required Design or diagnosis present: yes / no
- Atomic Fact Verification complete for action facts: yes / no
- Independent Evidence Audit complete for action rationale: yes / no
- Branch Plan required: yes / no
- Branch Plan present: yes / no
- Current branch:
- Current branch matches plan: yes / no
- Dirty worktree status:
- Dirty files classified as related/unrelated: yes / no
- Allowed files:
- Forbidden files:
- Run-to-Branch Binding required before command: yes / no
- User confirmation required: yes / no
- Decision: proceed / block / gather evidence / create branch plan / request confirmation
```

Required before trusting a run:

```markdown
## Run-to-Branch Binding
- Run ID:
- Output directory:
- Branch:
- Base branch:
- Head commit:
- Worktree status: clean / dirty
- Diff summary:
- Untracked files:
- Config:
- Command:
- Seed and split:
- Environment snapshot:
- Metric contract:
- Artifact manifest:
- Evidence audit verdict:
```

Rules:
- Each experiment branch should serve one hypothesis, variant, ablation factor, baseline, or bug diagnosis.
- Ablation branches for one group should derive from the same audited full-model commit.
- Dirty worktree runs must record the diff and be marked as limited reproducibility unless the dirty diff is archived.
- Merge recommendations require sanity evidence, evidence audit, comparable metrics/baselines, clean artifacts, and user confirmation.

## Mechanistic Model Analysis

Use `references/mechanistic-model-analyst.md` whenever the task involves model architecture, loss functions, training failures, metric conflicts, ablation interpretation, probe conflicts, or code-path consistency. The analyst must explain underlying mechanisms and competing root causes rather than only naming symptoms.

Required report:

```markdown
## Mechanistic Model Analyst Report
- Task mechanism:
- Data signal:
- Architecture mechanism:
- Loss mechanism:
- Optimization dynamics:
- Code path consistency:
- Candidate root causes:
- Evidence for / against each:
- Minimal discriminating test:
- Mechanistic verdict: pass / conditional-pass / fail / needs-probe / needs-runtime-check
- Confidence:
```

Rules:
- Do not blame the model before considering data, target definition, loss gradients, optimization dynamics, evaluation logic, and code execution path.
- Do not treat a plausible mechanism as verified without evidence.
- If multiple root causes remain plausible, recommend the smallest test that separates them.
- Treat "module exists" as insufficient; verify it is executed, receives gradients, and can affect outputs.
- Treat "metric improved" as insufficient; check whether ablation, probes, data splits, and baselines support the intended mechanism.

## Solution Generation Methods

Use Debate Brainstorming (see `references/debate-brainstorming.md`) as the primary method when the solution is not mechanically obvious. Single-agent methods below are fallbacks for trivial cases.

### Debate Brainstorming (primary)

Run a 3-round debate with 4 Advocates (data, model, loss, evaluation perspectives) and a Judge:

| Round | Activity | Parallelism |
|-------|----------|-------------|
| 1 — Independent Exploration | Each Advocate proposes their best solution through their lens | 4 parallel |
| 2 — Cross-Attack | Each Advocate attacks the other 3 proposals | 4 parallel |
| 3 — Revise | Each Advocate revises under attack, concedes valid points, absorbs good ideas | 4 parallel |
| Judge | Synthesize: convergence analysis, survivability ranking, fusion, unresolved disputes | 1 call |

Judge verdict types:
- **Convergent**: Multiple perspectives agree → high confidence, proceed to Mechanistic Analysis.
- **Fusable**: Perspectives are complementary → fuse best parts, verify each.
- **Divergent**: Fundamental disagreement → design minimal discriminating experiment, re-enter debate with new evidence.

On outer-loop restart, include previous debate conclusions and failed attempts as explicit evidence.

### Single-agent fallbacks

Use only when the fix is mechanically obvious (single clear path):

| Method | Use When | Output |
|--------|----------|--------|
| Root-cause brainstorming | Multiple plausible causes remain | Candidate fixes grouped by data/model/loss/optimization/evaluation |
| First-principles decomposition | The mechanism is unclear | Variables, assumptions, expected causal path |
| Baseline contrast | Proposed method underperforms or lacks novelty | Differences from baseline and targeted fixes |
| Ablation-driven ideation | A module fails to contribute | Candidate simplifications, replacements, or removals |
| Failure-case clustering | Errors concentrate in subgroups | Candidate data/probe/loss changes for each cluster |

Candidate solution format (for single-agent fallback):

```markdown
| Candidate | Diagnosis Addressed | Mechanism | Verification Signal | Risk | Cost | Rollback |
|-----------|---------------------|-----------|---------------------|------|------|----------|
```

Selection rule:
- Prefer the candidate that most directly tests the diagnosis with the lowest irreversible cost.
- If two candidates are plausible, choose the one with the clearer verification signal first.
- If all candidates depend on missing evidence, do not implement; return to Evidence Pack.

## Resolution Decision Standard

```markdown
## Resolution Decision
- Status: solved / partially solved / unresolved / needs more evidence / invalid problem
- Verification signal:
- Success criterion met: yes / no / partial
- Regressions or tradeoffs:
- What changed in the evidence pack:
- Next step:
- Restart point if unresolved: Problem / Evidence Pack / Diagnosis / Debate Brainstorming
```

Rules:
- "Solved" requires the predefined success criterion, not just subjective improvement.
- "Partially solved" must state the remaining gap.
- "Unresolved" must state what was tried and why it failed.
- Every unresolved outcome must restart the loop at a named point.

## Agent Routing Table

| User Intent | Default Route | Automatic First Moves | Required Stop |
|-------------|---------------|-----------------------|---------------|
| "Find a research direction/problem" | Observe → Classify → Gather → Route: Discovery | Inspect task context, prior failures, baselines, papers, and repository clues | Stop after core hypothesis is stated |
| "Read papers / compare methods" | Observe → Gather → Route: Discovery | Build method map, identify gaps, connect papers to possible hypotheses | Stop if literature evidence is too thin |
| "Design an experiment/model/loss" | Observe → Classify → Gather → Route: Design → Act: design draft | Review Discovery evidence, state falsifiable hypothesis, specify controls and probes | Stop at Design Gate |
| "Implement this research idea" | Observe → Classify → Gather → Route: Evidence implementation | Read relevant files, identify minimal diff, keep design scope visible | Stop if Design output is missing or change is high-impact |
| "Run training" | Observe → Classify → Gather → Route: Evidence training plan | Identify command, config, seed, output artifacts, environment snapshot, and monitoring plan | Stop at Run Gate for long/costly runs unless full-auto is active |
| "Analyze logs/results" | Observe → Gather → Route: Evidence analysis | Parse metrics, compare against baseline, identify anomalies and uncertainty | Stop at Resolution Decision Gate |
| "Tune hyperparameters" | Observe → Gather → Route: Evidence analysis first | Diagnose failure mode before proposing changes | Stop if no failure diagnosis exists |
| "Fix failed training" | Observe → Gather → Route: Evidence diagnosis | Check data, forward, loss, backward, optimizer, logs in order | Stop before broad redesign |

## Gate Checklist

### Activation Gate
- [ ] The skill was explicitly requested, or the user confirmed activation.
- [ ] If `AskUserQuestion` is available for missing activation/mode/task, it was called and the workflow waited for the answer.
- [ ] Execution mode is selected, or the user confirmed activation/continuation and accepted default `guided`.
- [ ] Research task or goal is known.
- [ ] If any activation answer, mode, or task is missing, the gate is `blocked` and the agent has asked and stopped.
- [ ] If `full-auto` is selected, gate bypass scope and remaining higher-priority limits are stated.
- [ ] If `full-auto` is selected, Goal Gate has `要解决的问题`, `成功标准`, and `允许修改范围`.
- [ ] If the user declines activation, answer without applying the full dl-research workflow.
- [ ] If an activation prompt was printed without waiting for required answers, record Gate Noncompliance and return to Activation Gate.

### Classification Gate
- [ ] Task type is identified: bug, build, feature, refactor, experiment, log diagnosis, architecture design, result analysis, training execution, or documentation.
- [ ] Risk level and constraints are stated.
- [ ] The current loop level is stated: micro-loop, inner-loop, or outer-loop.
- [ ] Unknowns that block safe progress are separated from unknowns that can be inferred.

### Design Gate
- [ ] Core hypothesis is falsifiable.
- [ ] Baseline or comparison point is named.
- [ ] Data flow, model topology, loss, optimizer, schedule, and probes are specified at the right level of detail.
- [ ] Ablation or control-variable plan exists.
- [ ] Failure signals and rollback or fallback path are listed.
- [ ] User confirmation is obtained before implementation when the change is high-impact.

### Pre-Action Compliance Gate
- [ ] The check was run before file edits, config changes, branch changes, training/evaluation launches, or high-impact commands.
- [ ] Required Design or diagnosis exists for the intended action.
- [ ] Atomic Fact Verification and Independent Evidence Audit are complete for facts and rationale supporting the action.
- [ ] Branch Plan exists before research edits.
- [ ] Current branch matches the Branch Plan or branch creation/switching is confirmed.
- [ ] Dirty worktree files are classified as related or unrelated.
- [ ] Allowed files and forbidden files are stated.
- [ ] Run-to-Branch Binding prerequisites exist before training or evaluation.
- [ ] Missing prerequisites block the action or create a Branch Noncompliance Incident.

### Atomic Fact Verification Gate
- [ ] Every objective factual claim from every role or phase is extracted.
- [ ] If the user challenged a prior fact, the old claim and corrected claim are both listed separately.
- [ ] Each fact has a source requirement and checked source.
- [ ] Verdict is one of `true`, `false`, `unverifiable`, `insufficient-source`, or `not-checked`.
- [ ] No downstream claim depends on a critical fact marked `false`, `unverifiable`, `insufficient-source`, or `not-checked`.
- [ ] New factual claims introduced after a prior check are verified before use.
- [ ] Source inspection commands are represented as table evidence; no correction is made only in prose.
- [ ] Any conclusion, recommendation, or next action that depended on a false claim is revised, blocked, or re-reviewed.

### Formal Derivation Verification Gate
- [ ] Every mathematical, gradient, objective, equivalence, variable-dependency, mechanism, or commit-message claim is extracted.
- [ ] Definitions, assumptions, derivation steps, dependencies, and edge cases are stated.
- [ ] Verdict is one of `valid`, `invalid`, `partially-valid`, `assumption-dependent`, or `unverifiable`.
- [ ] No downstream claim depends on a derivation marked `invalid` or `unverifiable`.
- [ ] Partially valid or assumption-dependent claims are rewritten or caveated before use.

### Mechanistic Analysis Gate
- [ ] Triggered before model/loss/protocol design, training-failure diagnosis, ablation interpretation, probe-conflict interpretation, or code-path mechanism claims.
- [ ] Task mechanism, data signal, architecture mechanism, loss mechanism, optimization dynamics, and code path consistency are considered.
- [ ] Competing root causes are listed with evidence for and against each.
- [ ] The report names the smallest discriminating test when static evidence is insufficient.
- [ ] The verdict is pass / conditional-pass / fail / needs-probe / needs-runtime-check.

### Branch Creation Gate
- [ ] A Branch Plan exists before research code/config/data/evaluation changes.
- [ ] Base branch and base commit are recorded.
- [ ] New branch name follows the branch type convention from `git-branch-management.md`.
- [ ] Allowed files and forbidden files are stated.
- [ ] Ablation branches derive from the same audited full-model commit when applicable.
- [ ] Rollback branch or commit is known.
- [ ] In guided or strict-confirmation modes, user approval is obtained before creating or switching branches.

### Evidence Audit Gate
- [ ] The audit was triggered after Atomic Fact Verification and before Diagnosis, Debate Brainstorming, Resolution Decision, or Record when claims depended on evidence.
- [ ] Every supporting fact appears in the Atomic Fact Verification table.
- [ ] Every formal/mechanism claim appears in the Formal Derivation Verification report when applicable.
- [ ] Assumptions are separated from facts.
- [ ] Reproducibility evidence is present or the claim is downgraded.
- [ ] Baseline comparisons use compatible data, preprocessing, metrics, budget, inference, and postprocessing, or the mismatch is stated.
- [ ] Contradictions and unsupported conclusions are listed.
- [ ] Verdict is `pass` or bounded `conditional-pass` before proceeding; otherwise restart from Evidence Pack or gather targeted evidence.

### Sanity Gate
- [ ] Input and label shapes match the design.
- [ ] Loss is finite on at least one forward pass.
- [ ] Gradients reach the intended trainable parameters.
- [ ] A tiny-batch overfit or task-equivalent sanity check is planned or completed.
- [ ] Probe outputs are generated or intentionally deferred with reason.

### Run Gate
- [ ] Environment snapshot method is chosen.
- [ ] Random seed and data split strategy are recorded.
- [ ] Run-to-Branch Binding is recorded: branch, base branch, head commit, worktree status, diff summary, config, command, seed/split, artifacts.
- [ ] Full command/config is captured.
- [ ] Expected artifacts and monitoring cadence are known.
- [ ] Active Monitoring Loop has files, metrics, triggers, and allowed actions.
- [ ] User approval is obtained for long or expensive runs.

### Resolution Decision Gate
- [ ] Best result is compared against baseline under compatible conditions.
- [ ] Failure or improvement is attributed to evidence, not guesswork.
- [ ] Status is one of: solved, partially solved, unresolved, needs more evidence, or invalid problem.
- [ ] If unresolved, the restart point is named: Problem, Evidence Pack, Diagnosis, or Debate Brainstorming.
- [ ] The reason for the decision is archived.

### Research Record Gate
- [ ] Triggered only because the user explicitly requested memory/record/archive/save/write.
- [ ] Research Recorder drafted the record in template format.
- [ ] Draft includes verified facts, derivation verdicts, evidence verdict, mechanism analysis, branch/run artifacts, action, result, decision, uncertainty, and restart point.
- [ ] Deprecated or corrected prior claims are named.
- [ ] Evidence and uncertainty are separated.
- [ ] Target memory location is proposed or user-provided.
- [ ] User confirmation is obtained before writing to any memory file.

## Pause Conditions

The agent must stop and ask the user before:

- launching a long, expensive, destructive, or externally visible action;
- changing task scope from a local fix to a redesign;
- implementing a new architecture, loss, data transform, or training protocol without a confirmed design;
- deleting, overwriting, or moving user artifacts;
- continuing when available evidence rejects the current hypothesis;
- claiming a result is validated without tests, metrics, logs, or an explicit limitation.

## Experimental Phase Contract

### Discovery: Problem, Literature, Hypothesis

Inputs:
- user goal, domain/task context, prior logs, known baselines, papers, datasets, and repository clues.

Automatic actions:
- define the task boundary and why the problem matters;
- map related methods into categories;
- diagnose the gap, bottleneck, failure mode, or uncertainty worth studying;
- formulate one primary falsifiable hypothesis;
- define what evidence would support or reject it.

Outputs:
- problem statement;
- evidence pack;
- diagnosis of the core bottleneck or evidence gap;
- baseline or comparison plan;
- core hypothesis;
- minimum success criterion and rejection signal.

Pass condition:
- the hypothesis is testable by a bounded Design/Evidence plan.

Fallback:
- gather more literature, narrow the task, or form a minimal baseline plan.

### Design: Algorithm and Experiment Protocol

Inputs:
- Discovery outputs, available code/data constraints, compute assumptions, and target metrics.

Automatic actions:
- design algorithm components: data flow, architecture, loss, optimizer, inference, and probes;
- define the experiment protocol: splits, preprocessing, augmentations, metrics, seeds, commands, and artifacts;
- design baselines, controls, and one-factor ablations;
- brainstorm candidate solutions and compare them;
- choose the strategy: minimal intervention, controlled variant, or redesign;
- predict failure modes and diagnostic checks.

Outputs:
- candidate solution table;
- algorithm design document;
- experiment protocol;
- ablation matrix;
- failure-mode and rollback plan.

Pass condition:
- the design can be implemented with scoped changes and evaluated fairly.

Fallback:
- revise the hypothesis, simplify the design, or return to Discovery if evidence is insufficient.

### Evidence: Implementation, Training, Main Experiment, Ablation, Analysis

Inputs:
- approved or bounded Design outputs, codebase, configs, logs, metrics, artifacts, and compute availability.

Automatic actions:
- implement the minimal verifiable version;
- run or propose sanity checks before full training;
- prepare reproducible training commands and environment snapshots;
- run the Active Monitoring Loop and detect failure modes during training;
- compare main experiment results to baselines;
- run or plan ablations that test the hypothesis;
- analyze metrics, probes, failures, and uncertainty;
- judge the hypothesis.

Outputs:
- sanity evidence;
- active monitoring plan and monitoring records;
- main experiment result;
- ablation result;
- failure analysis if needed;
- hypothesis verdict;
- resolution decision;
- next experimental action.

Pass condition:
- the verdict is supported by compatible evidence, or uncertainty is explicitly bounded.

Fallback:
- enter micro-loop for code/sanity failures, inner-loop for training detail failures, or outer-loop back to Discovery/Design for hypothesis/design failures.

## Active Monitoring Loop

Use this loop during long training jobs so the agent can catch anomalies before the final epoch.

```text
Training Start
→ Monitoring Plan
→ Periodic Check
→ Trigger Detection
→ Mini Diagnosis
→ Action Decision
→ Continue / Intervene / Stop / Restart
→ Record
```

The loop must be backed by a persistent Monitor Runner after training starts. A plan without a runner is only a monitoring design, not active monitoring. Prefer the bundled runner:

```bash
python /path/to/dl-research/scripts/monitor_training.py \
  --run-dir /path/to/experiment_log \
  --pid <training_pid> \
  --primary-metric <metric_column>
```

Use `--once` for a single diagnostic check. For continuous monitoring, run the command in a terminal, tmux/session manager, service supervisor, or detached process such as `setsid -f`. The runner writes `monitoring_events.jsonl` and `monitoring_state.json` in the run directory by default.

### Monitoring Plan

```markdown
## Monitoring Plan
- Check frequency: every 5 minutes by default, or every N minutes / every N epochs if overridden
- Monitored files:
  - train log:
  - metrics file:
  - tensorboard/events:
  - heartbeat/status file:
  - checkpoints:
- Core metrics:
  - train loss:
  - val loss:
  - primary metric:
  - learning rate:
  - gradient norm:
  - GPU/memory:
- Trigger rules:
  - NaN/Inf:
  - plateau:
  - overfitting:
  - metric regression:
  - stale heartbeat:
  - crash/missing artifact:
- Allowed actions:
  - guided:
  - full-auto:
  - strict-confirmation:
- Monitor Runner:
  - command:
  - output records:
  - active: yes / no
```

### Default Active Monitoring Thresholds

These defaults apply unless the Monitoring Plan overrides them.

| Trigger | Default Threshold | Status | Default Action |
|---------|-------------------|--------|----------------|
| Periodic check | Every 5 minutes | normal | Read logs/metrics and classify state |
| Trend window | Last 10 epochs/steps | normal | Use for trend checks |
| Heartbeat stale | 10 minutes without update | warning | Record and inspect process/log freshness |
| Heartbeat critical | 20 minutes without update | critical | Enter Mini Diagnosis |
| NaN/Inf in loss or metric | Once | critical | Enter Mini Diagnosis immediately |
| Training process exits unexpectedly | Once | critical | Inspect logs/checkpoints/artifacts |
| Critical artifact missing | Once | warning | Record missing artifact and recheck |
| Critical artifact missing | Two consecutive checks | critical | Treat artifact chain as broken |
| Validation metric no improvement | 10 epochs | warning | Flag plateau risk |
| Validation metric no improvement | 20 epochs | failed | Stop current candidate or enter Resolution Decision |
| Train improves while validation degrades | 5 epochs | warning | Flag overfitting risk |
| Train improves while validation degrades | 10 epochs | critical | Enter overfitting diagnosis |
| Primary metric worsens | 5 epochs | warning | Flag metric regression |
| Primary metric worsens | 10 epochs | critical | Enter metric regression diagnosis |
| Loss has no meaningful decrease | 10 epochs | warning | Flag stalled optimization |
| Loss has no meaningful decrease | 20 epochs | failed | Enter optimization/data/loss diagnosis |

Optional triggers such as GPU memory pressure, gradient-norm thresholds, or task-specific metric slices may be added in the Monitoring Plan when the project records those signals.

### Periodic Check

At each check:
- read the latest epoch/step;
- parse the last 10 metric points by default;
- compare train and validation trends;
- check NaN/Inf, crash text, stale heartbeat, and missing artifacts;
- classify status as `normal`, `warning`, or `critical`.

When using `scripts/monitor_training.py`, the runner performs these checks automatically from the run directory when possible:
- `train.log` as the default training log;
- `history.csv` as the default metrics file;
- `latest.pt` and `best.pt` as default checkpoint artifacts;
- optional `--pid` or `--process-query` for process liveness;
- optional `--heartbeat` for a project-specific heartbeat file;
- optional repeated `--checkpoint` arguments for custom artifacts.

### Trigger Detection

Default trigger examples:
- any NaN/Inf in loss or metric → `critical`;
- heartbeat stale for 10 minutes → `warning`; 20 minutes → `critical`;
- validation metric fails to improve for 10 epochs → `warning`; 20 epochs → `failed`;
- train improves while validation degrades for 5 epochs → `warning`; 10 epochs → `critical`;
- primary metric worsens for 5 epochs → `warning`; 10 epochs → `critical`;
- loss has no meaningful decrease for 10 epochs → `warning`; 20 epochs → `failed`;
- process exits unexpectedly or checkpoint/log stops updating → `critical`.

### Mini Diagnosis

```markdown
## Mini Diagnosis
- Status: normal / warning / critical
- Trigger:
- First observed at:
- Latest metrics:
- Likely causes:
- Missing evidence:
- Recommended action:
```

### Action Decision by Mode

| Mode | Monitoring Action |
|------|-------------------|
| guided | Report warning/critical status and wait before intervention |
| full-auto | Execute allowed intervention inside the Goal Gate modification scope and record the bypassed gate |
| strict-confirmation | Report only; do not intervene without confirmation |

### Monitoring Record

```markdown
## Monitoring Record
- Time:
- Epoch/step:
- Latest metrics:
- Status: normal / warning / critical
- Diagnosis:
- Action:
- Next check:
```

The persistent runner stores each monitoring record as one JSON object per line in `monitoring_events.jsonl`. The latest state, including missing-artifact counters and the last record, is stored in `monitoring_state.json`.

## Phase Transition Rules

- **Discovery → Design** only when the agent has a bounded problem, at least one comparison point or justified baseline gap, and a falsifiable hypothesis.
- **Design → Evidence** only when the candidate solution has been selected and the algorithm design, experiment protocol, metrics, baselines, ablations, and failure signals are explicit enough to implement.
- **Evidence → Design** when sanity checks pass but results reject a design mechanism, ablations show the proposed component is irrelevant, or probes expose shortcut behavior.
- **Evidence → Discovery** when the task definition, metric, data split, baseline assumption, or problem value is invalid.
- **Unresolved → Restart** at Problem, Evidence Pack, Diagnosis, or Debate Brainstorming, based on the first invalid or uncertain step.
- **Any phase → Research Record** only when the user explicitly asks to remember, record, archive, save, or write the result.

## Agent Output Contracts

### Discovery Output
```markdown
## Discovery
- Problem:
- Why it matters:
- Evidence map:
- Atomic fact verification:
- Formal derivation verification:
- Assumptions:
- Missing evidence:
- Confidence:
- Diagnosis:
- Baseline/comparison:
- Core hypothesis:
- Support signal:
- Rejection signal:
- Next phase: Design / gather more evidence / stop
- Research record:
```

### Design Output
```markdown
## Design
- Hypothesis link:
- Diagnosis link:
- Atomic fact verification:
- Formal derivation verification:
- Mechanistic analysis:
- Candidate solutions:
- Selected strategy:
- Branch plan:
- Algorithm change:
- Data flow:
- Loss/optimization:
- Experiment protocol:
- Baselines and controls:
- Ablation matrix:
- Failure modes:
- Gate decision: approved / needs revision / blocked
- Research record:
```

### Evidence Output
```markdown
## Evidence
- Implementation summary:
- Atomic fact verification:
- Formal derivation verification:
- Mechanistic analysis:
- Sanity evidence:
- Run-to-branch binding:
- Evidence reviewer audit:
- Main result:
- Ablation result:
- Failure analysis:
- Verification signal:
- Resolution decision: solved / partially solved / unresolved / needs more evidence / invalid problem
- Restart point if unresolved:
- Research record:
```

## Ablation Matrix Template

| Experiment ID | Module A | Module B | Module C | Expected Effect | Actual Effect |
|---------------|----------|----------|----------|-----------------|---------------|
| E1 (full)     | ✓        | ✓        | ✓        | best overall    |               |
| E2 (−A)       | ✗        | ✓        | ✓        | drop in X       |               |
| E3 (−B)       | ✓        | ✗        | ✓        | drop in Y       |               |
| E4 (−C)       | ✓        | ✓        | ✗        | drop in Z       |               |

Principles:
- Each experiment removes exactly one module (one-factor-at-a-time).
- If interactions are suspected, add pairwise removal experiments.
- Always include the full model as E1 for reference.

## Design Document Structure

```markdown
# Design: [Core hypothesis summary]

## Discovery Link
- Problem:
- Evidence gap:
- Core hypothesis:
- Support signal:
- Rejection signal:

## Literature / Baseline Contrast
- Difference from [paper or baseline A]:
- Difference from [paper or baseline B]:

## Data Flow and Augmentation
- Input format:
- Augmentation pipeline:
- Preprocessing:

## Network Topology
### Backbone
- Choice and rationale:
- Output features:

### Neck
- Structure:
- Feature fusion:

### Head
- Output format:
- Interface with loss:

## Loss Function
### Mathematical Form
$$
\mathcal{L} = \lambda_1 \mathcal{L}_1 + \lambda_2 \mathcal{L}_2
$$

### Mechanistic Meaning
- $\mathcal{L}_1$ measures:
- $\mathcal{L}_2$ measures:
- Expected gradient path:
- Possible shortcut incentives:
- Formal derivation verification:

## Mechanistic Model Analysis
- Task mechanism:
- Data signal:
- Architecture mechanism:
- Loss mechanism:
- Optimization dynamics:
- Code path consistency:
- Minimal discriminating test:

## Optimization
- Optimizer:
- LR schedule:
- Warmup:
- Weight decay:
- Gradient clipping:

## Analysis Probes
- [ ] Feature maps: layers and frequency
- [ ] Attention visualization
- [ ] CAM or equivalent explanation
- [ ] Gradient norm logging
- [ ] Weight distribution histogram

## Failure Mode Forecast
| Failure Signal | Possible Cause | Diagnostic Check |
|----------------|----------------|------------------|
| Loss plateau | ... | ... |
| Metric anomaly | ... | ... |

## Experiment Protocol
- Baselines:
- Main experiment:
- Ablation matrix:
- Expected metric delta:
- Minimum meaningful difference:
- Artifact plan:
```

## Failure Mode Catalog

Common failure modes and diagnostic approaches:

### Loss Plateau / No Decrease
1. Check learning rate — may be too low or too high
2. Verify data pipeline — labels may be incorrect or shuffled
3. Check gradient flow — may have vanishing/exploding gradients
4. Inspect loss function — may have numerical instability

### NaN Loss
1. Check for division by zero in loss computation
2. Verify log operations have proper epsilon guards
3. Check for overflow in attention/softmax (add temperature or clamp)
4. Inspect data for NaN/Inf values

### Mode Collapse
1. Check loss balance — one component may dominate
2. Verify data augmentation is not too aggressive
3. Look at output distribution — all predictions may converge to same value
4. Check for class imbalance issues

### Good Training but Poor Validation
1. Overfitting — add regularization, reduce model capacity
2. Data leak — verify train/val split is correct
3. Distribution shift — check if val set comes from different distribution
4. Augmentation mismatch — training augmentations may not generalize

### Missing or Inconsistent Artifacts
1. Missing metrics file — verify training command, output directory, and logger configuration
2. Missing checkpoint — check save interval, validation trigger, and permission errors
3. Metrics names changed — map aliases before comparing runs
4. Config not saved — reconstruct from command line only as a fallback and mark uncertainty

### Conflicting Metrics
1. Primary metric improves while safety/secondary metric regresses — use the predeclared success criteria
2. Validation improves but test degrades — suspect overfitting to validation or distribution mismatch
3. Qualitative probes contradict metrics — inspect data leakage, shortcut learning, or probe implementation
4. Ablation result is non-monotonic — check interactions and add pairwise ablations if justified

## Convergence Rules

1. **Inner loop max 3 rounds**: If hyperparameter tuning doesn't produce improvement after 3 rounds, stop inner loop and escalate to outer loop decision.
2. **Outer loop convergence**: When metric improvement across two consecutive outer loops < predefined minimum meaningful difference for the task, and no visible qualitative improvement, terminate iteration.
3. **Micro-loop sanity**: If sanity check (overfit tiny batch) fails after 10 attempts, the design is likely fundamentally flawed — escalate to Design revision.
4. **User override**: User may force advance or terminate at any decision point. Record user's decision rationale.

## Environment Reproducibility Checklist

Before starting any training run:

- [ ] Record `pip freeze > requirements_YYYYMMDD.txt` or `conda env export > env_YYYYMMDD.yml`
- [ ] Record PyTorch version and CUDA version
- [ ] Record GPU model and driver version (`nvidia-smi`)
- [ ] Record random seed (`torch.manual_seed()`, `np.random.seed()`, `random.seed()`)
- [ ] Record data split strategy and any random shuffling
- [ ] Record all hyperparameters in a config file (not just CLI args)
- [ ] Commit current code state (`git rev-parse HEAD`)

## Minimal Report Shape

Use this shape for lightweight research updates and archive entries:

```markdown
# Discovery / Design / Evidence Report

## Context
- Phase: Discovery / Design / Evidence
- Task:
- Hypothesis:
- Baseline:
- Primary metric:
- Success criterion:
- Branch:
- Commit:

## What Changed
- Code/config/data change:
- Branch plan or run-to-branch binding:
- Expected effect:
- Risk:

## Evidence
- Command or artifact path:
- Environment snapshot:
- Key metric table:
- Qualitative/probe observation:
- Evidence reviewer audit:
- Research record:

## Decision
- Verdict: supported / partially supported / rejected / inconclusive
- Next step: continue / adjust / redesign / stop / return to Discovery / record Evidence
- Rationale:
- Deprecated or corrected prior claims:
- Restart point:

## Open Questions
- [Unresolved uncertainty]
```
