# Discovery-Linked Design Gate Template

Use this template when the agent routes a task to **Design**. The design must connect back to Discovery evidence and must be specific enough to enter Evidence without inventing missing assumptions.

## 1. Discovery Link

- Problem:
- Why it matters:
- Evidence map:
  - Papers:
  - Baselines:
  - Prior runs:
  - Missing evidence:
- Facts:
- Assumptions:
- Contradictions:
- Evidence confidence: high / medium / low
- Atomic fact verification:
  - Table present: yes / no
  - Non-true critical facts:
- Formal derivation verification:
  - Report present: yes / no
  - Invalid or unverifiable critical derivations:
- Evidence reviewer audit:
  - Verdict: pass / conditional-pass / fail / insufficient-evidence
  - Allowed conclusion strength:
  - Required evidence before proceeding:
- Core hypothesis:
- Support signal:
- Rejection signal:
- Minimum meaningful difference:
- Research record:

## 2. Problem Diagnosis

State the diagnosis before designing the solution. The design must address this diagnosis directly.

- Problem type: data / preprocessing / architecture / loss / optimization / inference / metric / artifact / baseline gap / invalid hypothesis / other
- Primary diagnosis:
- Competing diagnoses:
- Evidence supporting the diagnosis:
- Evidence still missing:
- Atomic fact verification status:
- Formal derivation verification status:
- Evidence audit status:
- Mechanistic analysis status:
- Falsifiable statement:
  - If this diagnosis is correct:
  - Then this design/action should change:
  - Verification signal:
- Chosen strategy: minimal intervention / controlled experimental variant / best-practice redesign / evidence gathering only
- Why this strategy:

## 2.1 Mechanistic Model Analysis

- Task mechanism:
- Required latent factors:
- Domain priors:
- Plausible shortcuts:
- Data signal:
- Architecture mechanism:
- Loss mechanism:
- Optimization dynamics:
- Code path consistency:
- Objective factual claims requiring Atomic Fact Verification:
- Formal/mechanism claims requiring Formal Derivation Verification:
- Candidate root causes:
- Evidence for / against each:
- Minimal discriminating test:
- Mechanistic verdict: pass / conditional-pass / fail / needs-probe / needs-runtime-check
- Confidence: high / medium / low

## 2.2 Branch Plan

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

## 2.3 Pre-Action Compliance Check

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

## 3. Candidate Solutions

Use brainstorming when the path is not obvious. Include candidates that address different problem types before selecting one.

| Candidate | Diagnosis Addressed | Mechanism | Verification Signal | Risk | Cost | Rollback |
|-----------|---------------------|-----------|---------------------|------|------|----------|
| S1 |  |  |  |  |  |  |
| S2 |  |  |  |  |  |  |
| S3 |  |  |  |  |  |  |

Selection:

- Selected candidate:
- Why this candidate first:
- Why alternatives are deferred:
- Gate required before implementation:
- Atomic Fact Verification required before implementation: yes / no
- Formal Derivation Verification required before implementation: yes / no

## 4. Algorithm Design

### Data Flow

- Input format:
- Target/label format:
- Preprocessing:
- Augmentation:
- Inference output:

### Network Topology

| Component | Design | Rationale | Expected Evidence |
|-----------|--------|-----------|-------------------|
| Backbone |  |  |  |
| Neck |  |  |  |
| Head |  |  |  |
| Auxiliary module |  |  |  |

### Loss and Optimization

```text
Total loss:
Primary loss:
Auxiliary loss:
Regularization:
Optimizer:
Learning-rate schedule:
Gradient clipping:
```

Mechanistic meaning:

- What behavior should the loss encourage?
- What failure mode should the design reduce?
- What signal would show the design is learning a shortcut?
- What gradient path should carry the learning signal?
- Which loss terms could compete or dominate?
- How does the objective align with the primary metric?
- Formal derivation verification:
  - Claim under review:
  - Verdict: valid / invalid / partially-valid / assumption-dependent / unverifiable
  - Corrected statement:

## 5. Experiment Protocol

- Dataset(s):
- Split strategy:
- Metrics:
- Primary metric:
- Secondary/safety metrics:
- Seeds:
- Compute assumptions:
- Environment snapshot method:
- Expected artifacts:
- Run-to-branch binding required: yes / no

## 6. Baselines and Controls

| ID | Method | Purpose | Required Artifact |
|----|--------|---------|-------------------|
| B0 | Minimal baseline | Lower-bound sanity |  |
| B1 | Strong baseline | Fair comparison |  |
| C1 | Control setting | Rule out confounder |  |

## 7. Ablation Matrix

| ID | Change | Hypothesis Tested | Expected Effect | Decision Rule |
|----|--------|-------------------|-----------------|---------------|
| E1 | Full design | Main hypothesis | Best or most balanced result |  |
| E2 | Remove module A | Module A contribution | Metric/probe degradation |  |
| E3 | Remove loss term B | Loss B contribution | Failure mode returns |  |
| E4 | Replace component C | Design specificity | Weaker or different behavior |  |

Ablation branch base:

- Full-model branch:
- Full-model commit:
- Branch rule: each ablation changes one factor unless an interaction ablation is explicitly approved.

## 8. Analysis Probes

- Feature maps:
- Attention or routing weights:
- CAM/saliency/equivalent:
- Gradient norms:
- Weight/output distributions:
- Error slices or subgroup analysis:
- Each probe must answer which mechanistic uncertainty:

## 9. Failure-Mode Forecast

| Failure Signal | Likely Cause | Diagnostic Check | Fallback |
|----------------|--------------|------------------|----------|
| Loss is NaN |  |  |  |
| Loss plateaus |  |  |  |
| Train improves but validation fails |  |  |  |
| Ablation contradicts hypothesis |  |  |  |
| Probe shows shortcut learning |  |  |  |

## 10. Resolution and Restart Plan

- Design status: approved / needs revision / blocked
- Reason:
- Evidence audit verdict:
- Mechanistic verdict:
- Formal derivation verdict:
- Pre-action compliance decision:
- Merge/archive decision:
- Evidence phase entry command or next smallest action:
- Research record:
- User confirmation needed before implementation: yes / no
- Success criterion:
- Resolution statuses:
  - Solved:
  - Partially solved:
  - Unresolved:
  - Needs more evidence:
- Restart point if unresolved: Problem / Evidence Pack / Diagnosis / Debate Brainstorming
