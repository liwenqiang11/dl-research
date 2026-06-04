# Atomic Fact Verification

Use Atomic Fact Verification for every objective factual statement produced or used by any role in the dl-research workflow. This layer answers only one question: "Is this factual statement correct according to the available artifacts?"

It is not limited to Evidence Pack or Mechanistic Model Analyst output. It applies to all facts from all agents, phases, summaries, diagnoses, designs, code analyses, training reports, user-provided reports, paper notes, metric interpretations, and final records.

## Core Rule

Every objective fact must be verified before it is used for diagnosis, mechanism analysis, design selection, implementation decisions, experiment verdicts, or archived conclusions.

Facts include statements about:

- code content, file paths, function names, line ranges, branches, commits, configs, and parameters;
- tensor shapes, matrix sizes, loss formulas, gradients, objective terms, and numerical scales;
- dataset counts, labels, splits, sample IDs, GT values, preprocessing, augmentation, and leakage checks;
- logs, metrics, epochs, checkpoints, best summaries, run IDs, output directories, and artifacts;
- baseline settings, paper claims, tables, figures, external reports, and user-provided summaries;
- causal or mechanistic claims that cite objective observations.

For experiment-summary answers, facts also include every entry in a comparison table: date/run ID, loss combination, metric value, epoch count, dataset identity, validation size, run status, "best" labels, and current/next-run recommendations that depend on those facts.

## Role Boundary

Atomic Fact Verification may:

- extract factual claims from any agent output;
- check each claim against artifacts or direct observations;
- mark the claim as true, false, unverifiable, insufficient-source, or not-checked;
- require source lookup or targeted evidence collection;
- block downstream use of unverified or false claims.

Atomic Fact Verification must not:

- propose mechanisms, designs, fixes, or hyperparameter changes;
- interpret whether a fact supports a hypothesis;
- repair a wrong claim by inventing missing context;
- use confidence language instead of a verdict;
- let a claim proceed because it "sounds plausible".

## Automatic Trigger

Trigger this layer automatically whenever the current stage contains any objective fact. Do not wait for the user to request review.

Also trigger this layer immediately when the user challenges, corrects, or questions a factual claim already made by any role. Examples include "isn't 225035 using the merged dataset?", "that number is wrong", "why did you say X?", "不是...", "你没有核验", or any contradiction between the user's statement and the agent's factual summary.

The phase-gated dispatcher must trigger Atomic Fact Verification whenever any objective fact appears before or inside:

- Evidence Pack;
- Independent Evidence Audit;
- Mechanistic Model Analyst Report;
- Diagnosis;
- Debate Brainstorming;
- Branch Plan or Run-to-Branch Binding;
- Sanity, training, monitoring, result, ablation, or probe reports;
- Resolution Decision;
- Record / research memory / final summary.

If a new factual claim is introduced after a previous audit, run Atomic Fact Verification again for the new claim.

## User Challenge Workflow

When the user challenges a factual claim, treat the challenge as a correction audit, not as ordinary clarification.

Required steps:

1. Restate the challenged prior claim as its own factual claim.
2. Restate the proposed or discovered corrected claim as a separate factual claim.
3. Check the required source for both claims.
4. Output the required Atomic Fact Verification table.
5. Mark the prior claim `false`, `insufficient-source`, or `unverifiable` when the source does not support it.
6. Mark the corrected claim `true` only when the checked source directly supports it.
7. Deprecate the prior claim in prose after the table.
8. If a diagnosis, design, result verdict, recommendation, training decision, or record depended on the wrong claim, block or revise it and trigger Independent Evidence Audit again.

Command output is evidence collection, not the audit itself. Running `grep`, reading a log, inspecting a CSV, or executing a Python snippet does not satisfy this gate unless the result is converted into the required Atomic Fact Verification table with verdicts and downstream actions.

Minimal challenge response shape:

```markdown
## Atomic Fact Verification
| Fact ID | Factual claim | Source required | Source checked | Verification method | Verdict | Reason | Downstream action |
|---------|---------------|-----------------|----------------|---------------------|---------|--------|-------------------|
| F1 | Prior claim: ... | ... | ... | ... | false | ... | deprecate / revise conclusion |
| F2 | Corrected claim: ... | ... | ... | ... | true | ... | use |

Correction:
- Deprecated prior claim: ...
- Corrected claim now allowed: ...
- Dependent conclusions revised or blocked: ...
```

## Fact Verdicts

Use exactly one verdict per factual claim:

- **true**: The source directly supports the claim.
- **false**: The source contradicts the claim.
- **unverifiable**: The available artifacts cannot verify the claim.
- **insufficient-source**: A source exists, but it is too indirect, incomplete, ambiguous, or summarized to support the claim.
- **not-checked**: The claim has not been checked yet. It must not be used downstream.

## Required Table

```markdown
## Atomic Fact Verification
| Fact ID | Factual claim | Source required | Source checked | Verification method | Verdict | Reason | Downstream action |
|---------|---------------|-----------------|----------------|---------------------|---------|--------|-------------------|
| F1 |  |  |  |  | true / false / unverifiable / insufficient-source / not-checked |  | use / downgrade / block / gather evidence |
```

## Source Standards

| Claim type | Acceptable source |
|------------|-------------------|
| Code content or line claim | File path plus inspected lines |
| Function behavior | Code path inspection, targeted runtime trace, or test output |
| Tensor shape or matrix size | Code-derived shape contract or runtime print/assertion |
| Metric value | Metrics file, log line, summary artifact, or reproducible command output |
| Loss scale or ratio | Metrics plus loss weights/config and calculation method |
| Dataset count or GT value | Dataset file, split file, label file, or inspected sample artifact |
| Best epoch/checkpoint | Summary file plus checkpoint/log consistency |
| Branch/commit state | Git command output or recorded run sheet |
| Paper claim | Paper title/link plus table, figure, method section, or exact local note |
| User-provided fact | User artifact or explicit statement, marked as user-provided until independently checked |

## Downstream Rules

- `true`: May be used, but only for claims it actually supports.
- `false`: Must be removed or corrected. Any conclusion depending on it is blocked.
- `unverifiable`: Must not support diagnosis, design, or resolution. Gather evidence or downgrade to hypothesis.
- `insufficient-source`: May support only weak exploratory notes if explicitly caveated; it cannot support strong claims.
- `not-checked`: Must not proceed to Independent Evidence Audit, Diagnosis, Debate Brainstorming, Resolution Decision, or Record.

## Claim Extraction Rules

When reviewing another agent's output, extract factual claims before judging conclusions. Examples:

- "kernel_gt is 5x5" -> verify matrix size from code and actual `gt_idx` length.
- "GT has 5 angles" -> verify label/split artifacts; do not infer from one sample.
- "L_dpp is 600x L_ot" -> verify raw metrics, weights, and calculation.
- "L_dpp occupies 89% of total_loss" -> verify whether terms are raw or weighted before computing ratio.
- "The module is unused" -> verify forward path or runtime execution, not just code presence.
- "225035 has just started and has no epoch result" -> verify run directory status, `train.log`, `history.csv`, or equivalent artifact before using it.
- "0522 uses the combined dataset" -> verify config paths in `train.log`, command/config file, or run sheet before using it.
- "0519 is the best experiment" -> verify all compared metric values and comparability before labeling it best.

## Interaction With Independent Evidence Audit

Independent Evidence Audit consumes the Atomic Fact Verification table. It does not replace it.

Independent Evidence Audit may judge whether verified facts support a conclusion, but it must not allow claims that depend on `false`, `unverifiable`, `insufficient-source`, or `not-checked` facts unless the conclusion is explicitly downgraded and the unsupported fact is not used as support.

## Subagent Execution Protocol

Atomic Fact Verification must run as an independent subagent via the Agent tool, not inline by the main agent.

### How to spawn the Fact Verifier

Use the Agent tool with the following prompt structure. The prompt must contain ONLY claims and artifact manifest — no diagnosis, no design, no recommendation.

```
Agent(
  description="Atomic Fact Verification",
  prompt="""
You are an independent Fact Verifier. Your ONLY job is to verify whether factual claims are correct according to the provided artifacts. You must NOT propose diagnoses, designs, fixes, or recommendations.

## Claims to Verify

<claims>
{claims_json}
</claims>

## Artifact Manifest

<artifacts>
{artifact_manifest}
</artifacts>

## Instructions

1. For each claim, inspect the referenced artifact (read the file, check the log, verify the config, etc.)
2. Output a verdict table with exactly this format:

| Fact ID | Factual claim | Source required | Source checked | Verification method | Verdict | Reason | Downstream action |
|---------|---------------|-----------------|----------------|---------------------|---------|--------|-------------------|

3. Verdict must be exactly one of: true / false / unverifiable / insufficient-source / not-checked
4. "true" only if the artifact directly supports the claim
5. Do NOT propose mechanisms, designs, fixes, or recommendations
6. Do NOT interpret whether a fact supports a hypothesis
7. If a claim references an artifact you cannot access, mark it "unverifiable"

Return ONLY the verdict table. No other output.
"""
)
```

### Claims format

```json
[
  {
    "id": "F1",
    "claim": "GT has 5 angles",
    "source_type": "dataset/label/split",
    "source_ref": "data/labels.json line 42"
  }
]
```

### Artifact manifest format

```json
[
  {
    "path": "data/labels.json",
    "description": "label file with angle annotations"
  }
]
```

### What the prompt MUST NOT contain

- Main agent's diagnosis draft or narrative
- Main agent's design preference or recommended solution
- Main agent's conversation summary or private reasoning
- User preference signals about the desired conclusion
- Execution pressure such as "this fact must be true so we can proceed"

### Context Isolation

- The Fact Verifier receives only claims + artifact manifest via the prompt.
- It must not read the main agent's diagnosis, design, recommendation, or conversation summary.
- It outputs only the verdict table.
- The main agent must not reinterpret, soften, or upgrade verdicts. If the main agent disagrees, it must gather new evidence and submit a new verification request.

### Parallelism

- Fact Verifier can run in parallel with Derivation Verifier (spawn both Agent calls in the same turn).
- Debate Brainstorming Round 1 can also run in parallel with both verifiers.
- Independent Evidence Auditor must wait for both verifiers to complete.

### Fallback

When the Agent tool is unavailable:
- Mark the verification as `non-independent`;
- Explain the limitation;
- Downgrade any conclusion that depends on the verification unless the user explicitly accepts the limitation.
