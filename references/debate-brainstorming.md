# Debate Brainstorming

Use Debate Brainstorming after evidence is gathered and verified, before Diagnosis. Instead of a single agent generating solutions, multiple Advocates independently find solutions from different perspectives, attack each other's proposals, revise under pressure, and a Judge synthesizes the result.

## When to Trigger

Trigger Debate Brainstorming when:

- Diagnosis is not yet settled and multiple plausible paths exist;
- The problem has multiple competing root causes;
- The user requests brainstorming, solution exploration, or "find the best approach";
- After an outer-loop restart when previous solutions failed;
- When the task is non-trivial and a single-perspective solution risks fixation.

Skip Debate Brainstorming when:

- The problem is mechanically obvious (single clear fix);
- The user has already specified the exact solution;
- The task is purely evidence gathering with no design decision.

## Core Principle

Do not assign positions. Assign perspectives.

Each Advocate receives the same evidence pack and independently finds what they believe is the best solution, viewed through their assigned lens. Convergence across perspectives is a strong signal. Divergence identifies where experiments are needed.

## Perspective Lenses

| Advocate | Lens | Core Questions |
|----------|------|----------------|
| Data | Labels, distributions, splits, preprocessing, augmentation, leakage, sampling, noise | Are labels correct? Is the split clean? Could noise/imbalance/shift explain the behavior? |
| Model | Capacity, receptive field, normalization, feature fusion, inductive bias, expressivity | Can the architecture represent the mapping? Is the receptive field sufficient? Are there dead modules? |
| Loss | Objective alignment, gradient signal, term interaction, numerical stability, metric alignment | Does the objective produce the right gradients? Are terms competing? Is the optimized objective aligned with the metric? |
| Evaluation | Metric definition, decoding, postprocessing, baseline fairness, protocol reproducibility | Does the metric measure what we care about? Are baselines compared fairly? Could metric gaming explain the observation? |

## Debate Structure

### Round 1 — Independent Exploration (parallel)

Each Advocate analyzes the evidence pack through their lens and produces a complete proposal.

```markdown
## Advocate [Perspective] — Round 1 Proposal

### Problem Diagnosis (lens)
[Core problem from this perspective]

### Proposed Solution
[Concrete, actionable]

### Core Hypothesis
[One-sentence falsifiable claim]

### Evidence Support
- Supporting verified facts: [Fact IDs]
- Contradicting verified facts: [Fact IDs]
- Indeterminate facts: [Fact IDs]

### Mechanism
[Causal chain from proposed change to metric improvement]

### Implementation
- What to change:
- Minimum viable change:
- Cost:

### Verification Signal
- Success:
- Failure:
- Smallest test:

### Risks & Rollback
- Main risk:
- Rollback path:
```

### Round 2 — Cross-Attack (parallel)

Each Advocate reads the other Advocates' Round 1 proposals and attacks each one.

```markdown
## Advocate [Perspective] — Attacks

### On Advocate [Other]
- **Core weakness**: [single most damaging flaw]
- **Lens blind spot**: [what they missed by not using this perspective]
- **Fatal flaw under scrutiny**: [why their proposal fails from this angle]
- **Evidence gap**: [weak or unverifiable claims]
```

Rules:
- Attack the strongest part of the argument, not the weakest.
- Be precise. Cite specific evidence or logical flaws.
- Do not attack straw men.

### Round 3 — Revise (parallel)

Each Advocate reads attacks on their own proposal and produces a final revised version.

```markdown
## Advocate [Perspective] — Final Revised Proposal

### Attacks Received
- From [Other]: [summary]

### Concessions (attacks that stand)
[Valid criticisms and what was修正]

### Rebuttals (attacks that fail)
[Invalid criticisms and why]

### What I Learned
[Good ideas absorbed from other proposals]

### Final Proposal
[Revised solution incorporating valid criticisms and useful ideas]

### Remaining Weakness
[What is still uncertain or risky]
```

Rules:
- If an attack stands, concede. Do not defend for the sake of defending.
- Learn from others. If their idea is better, absorb it.
- Be honest about remaining weaknesses.

## Judge

After all 3 rounds, the Judge reads the complete debate record and synthesizes a verdict.

### Judge Input

- Full debate record (all 3 rounds, all Advocates)
- Original evidence pack
- Atomic Fact Verification table
- Formal Derivation Verification report (if applicable)

### Judge Analysis

```markdown
## Debate Verdict

### Convergence Analysis
- Convergent points: [what multiple Advocates independently agree on]
- Divergent points: [fundamental disagreements]
- Partial overlap: [partially shared ideas]

### Survivability Ranking
| Rank | Advocate | Perspective | Core Proposal | Attack Survivability | Evidence Support | Mechanism Strength |
|------|----------|-------------|---------------|---------------------|-----------------|-------------------|
| 1    |          |             |               |                     |                 |                   |
| 2    |          |             |               |                     |                 |                   |
| 3    |          |             |               |                     |                 |                   |
| 4    |          |             |               |                     |                 |                   |

### Fusion Proposal (if applicable)
- From Advocate [X]: [specific contribution]
- From Advocate [Y]: [specific contribution]
- Combined: [fused solution]

### Unresolved Disputes
[Disagreements that require experiments to resolve]
[Minimal discriminating experiment design for each]

### Final Recommendation
- Primary solution: [description]
- Fallback: [if primary fails]
- Restart point: [where to re-enter if this fails]
```

### Judge Evaluation Dimensions

| Dimension | Description |
|-----------|-------------|
| Evidence Anchoring | How many supporting facts are verified `true`? |
| Attack Survivability | Does the core argument hold after cross-examination? |
| Mechanism Strength | Is the causal chain complete and falsifiable? |
| Verifiability | Can a minimal discriminating experiment be designed? |
| Implementation Cost | Scope of change, training time, risk |
| Reversibility | Can we roll back if it fails? |
| Innovation Value | Does it bring new mechanistic understanding? |

### Convergence Handling

| Scenario | Interpretation | Action |
|----------|---------------|--------|
| Multiple perspectives converge on same solution | Strong signal — independent reasoning agrees | High confidence; proceed to Mechanistic Analysis |
| Perspectives diverge but solutions are complementary | Solutions address different aspects | Judge proposes fusion; verify each part |
| Perspectives fundamentally oppose each other | Core disagreement requires experiment | Design minimal discriminating experiment; run it; re-enter debate with new evidence |
| All perspectives agree on diagnosis but propose different fixes | Diagnosis is settled; fix strategy is not | Run fixes in order of evidence strength |

## Integration with Workflow

```
Evidence Pack
  → Atomic Fact Verification
  → Formal Derivation Verification
  → Independent Evidence Audit
  → Debate Brainstorming              ← replaces Solution Generation + Selection
    → Round 1: Independent Exploration (parallel)
    → Round 2: Cross-Attack (parallel)
    → Round 3: Revise (parallel)
    → Judge: Synthesize verdict
  → Mechanistic Analysis (on winning/fused solution)
  → Diagnosis (settled by debate + mechanism analysis)
  → Pre-Action Compliance
  → Branch Plan
  → Implementation
  → ...
```

## Agent Execution

Debate Brainstorming runs as parallel Agent calls:

```
Round 1: 4 Agent calls in parallel (one per Advocate)
Round 2: 4 Agent calls in parallel (each reads Round 1 results)
Round 3: 4 Agent calls in parallel (each reads Round 2 attacks)
Judge:   1 Agent call (reads all debate record)
Total:   13 Agent calls, 4 parallel batches
```

Each Advocate is an independent Agent with its own context. They do not share state except through the debate artifacts (proposals, attacks, revisions).

The Judge is a separate Agent that reads only the debate record and evidence pack. It does not participate in the debate.

## Outer-Loop Restart

When a previous solution fails and the workflow restarts from Problem or Evidence Pack:

- The debate is re-run with updated evidence (including what was learned from the failed attempt);
- Previous debate conclusions are included as additional evidence;
- Advocates are explicitly told: "Previous attempt X failed because Y. Do not repeat it.";
- This prevents cycling through the same solutions.
