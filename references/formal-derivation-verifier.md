# Formal Derivation Verifier

Use the Formal Derivation Verifier for every mathematical, algorithmic, gradient, dependency, or mechanism claim in the dl-research workflow. This layer answers: "Does this conclusion follow from the stated definitions, assumptions, formulas, and code-level objective?"

It complements Atomic Fact Verification. Atomic Fact Verification checks whether facts are true; Formal Derivation Verification checks whether reasoning from those facts is valid.

## Core Rule

Every formal or mechanism claim must be derived or downgraded before it is used for diagnosis, design selection, commit messages, experiment interpretation, or final conclusions.

Formal claims include statements about:

- loss formulas, objectives, regularizers, constraints, and probability definitions;
- gradients, variable dependencies, optimization incentives, scale effects, and term interactions;
- whether a term optimizes quality, diversity, calibration, count, sparsity, smoothness, or another mechanism;
- whether a module, loss, or metric can causally explain an observed behavior;
- equivalence between two objectives or approximations;
- commit messages or reports that claim an algorithmic mechanism.

## Role Boundary

The verifier may:

- restate definitions and assumptions;
- derive equations step by step;
- check variable and gradient dependencies;
- test claims with counterexamples or edge cases;
- mark claims as valid, invalid, partially-valid, assumption-dependent, or unverifiable;
- provide a corrected statement with the weakest accurate wording.

The verifier must not:

- introduce unverified facts; send factual claims to Atomic Fact Verification first;
- use empirical metrics as proof of a mathematical claim;
- accept a mechanism claim because it is intuitively plausible;
- propose broad redesigns or hyperparameter tuning;
- skip assumptions such as positivity, normalization, matrix size, diagonal values, reductions, weights, or masks.

## Automatic Trigger

Trigger this layer automatically whenever the current stage contains a mathematical, gradient, objective, equivalence, dependency, or mechanism claim. Do not wait for the user to request review.

The phase-gated dispatcher must trigger Formal Derivation Verification whenever any role states or uses:

- "this loss optimizes/rewards/penalizes X";
- "this gradient is dominated by X";
- "this term encourages diversity/quality/count/sparsity/calibration";
- "this formula is equivalent to...";
- "this module causes the metric change";
- "this objective aligns with the metric";
- "the mechanism is supported by the equation";
- a commit message or report that makes an algorithmic mechanism claim.

If a new formal claim appears after a prior verification, run this verifier again for the new claim.

## Required Output

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

## Verdicts

- **valid**: The claim follows from the stated facts, definitions, and assumptions.
- **invalid**: The derivation contradicts the formula, dependency graph, gradient path, or a counterexample.
- **partially-valid**: Part of the claim follows, but another part is unsupported or overstated.
- **assumption-dependent**: The claim holds only under explicit assumptions that must be stated.
- **unverifiable**: Required definitions, code behavior, or facts are missing.

## Downstream Rules

- `valid`: May support mechanism claims within the stated assumptions.
- `partially-valid`: Must be rewritten to the supported part only.
- `assumption-dependent`: Must carry the assumptions wherever the claim is used.
- `invalid`: Must be removed or corrected. Any conclusion depending on it is blocked.
- `unverifiable`: Must not support diagnosis, design, commit messages, or resolution.

## Verification Checklist

- Are all symbols defined?
- Are matrix sizes, reductions, masks, weights, and normalizations stated?
- Does the derivation use diagonal or off-diagonal terms correctly?
- Does the claimed mechanism depend on variables that actually appear in the formula?
- Does the gradient path include the claimed variable or module?
- Are raw loss values, weighted loss values, and total loss distinguished?
- Does the metric measure the behavior the objective claims to optimize?
- Is there a simple counterexample that falsifies the claim?

## Example: Trace DPP Claim

Claim:

```text
trace(L_Y) = sum_i q_i^2 simultaneously rewards quality and diversity.
```

Definitions:

```text
L = diag(q) S diag(q)
L_ij = q_i S_ij q_j
trace(L_Y) = sum_{i in Y} L_ii
S_ii = 1
```

Derivation:

```text
trace(L_Y) = sum_{i in Y} q_i S_ii q_i
             = sum_{i in Y} q_i^2
```

Variable dependency:

```text
trace(L_Y) depends on q_i for i in Y.
Off-diagonal S_ij terms do not appear in the trace.
```

Verdict:

```text
invalid
```

Corrected statement:

```text
trace(L_Y) rewards quality of selected/GT items through q_i^2. It does not directly reward pairwise diversity because off-diagonal similarity terms vanish from the trace.
```
