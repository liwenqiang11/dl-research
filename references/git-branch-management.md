# Git Branch Experiment Management

Use this reference whenever a deep learning research task changes code, config, data processing, evaluation logic, model architecture, loss, training protocol, baseline implementation, or ablation variant. The goal is to prevent experiments from contaminating each other and to make every result traceable to a Git branch and commit.

## Core Rule

Every research code change must belong to a scoped Git branch before it is used for a run or a conclusion. If a run is executed from an untracked or dirty state, the result must be marked as limited reproducibility until the branch, commit, and diff are recorded.

Two hard rules apply:

- **No Branch Plan, No Research Edit**: do not change model code, loss code, training scripts, configs, data processing, evaluation logic, baseline code, or ablation variants until a Branch Plan exists.
- **No Run-to-Branch Binding, No Training Claim**: do not launch or interpret training/evaluation/sanity/ablation results as reproducible evidence until Run-to-Branch Binding exists.

If either rule is violated, open a Branch Noncompliance Incident before continuing.

## Branch Types

| Branch type | Purpose | Example |
|-------------|---------|---------|
| `research/<topic>` | Long-lived outer-loop research direction or hypothesis family | `research/anatomy-prior-dose` |
| `exp/<hypothesis>/<variant>` | One implementation variant for a bounded design | `exp/anatomy-posenc/v1` |
| `ablation/<group>/<factor>` | One-factor ablation derived from the full-model commit | `ablation/anatomy-posenc/no-posenc` |
| `baseline/<method>` | Baseline reproduction or project adaptation | `baseline/3d-unet` |
| `debug/<issue>` | Bug diagnosis or failed-run repair | `debug/nan-loss-dose-head` |
| `archive/<experiment-id>` | Preserved branch for a completed or rejected experiment | `archive/exp-20260519-anatomy-posenc-v1` |

Keep branch names lowercase, short, and stable. Use hyphens instead of spaces. Avoid metric values in branch names because metrics can change after audit.

## Branch Creation Gate

Before implementing non-trivial research changes, state:

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

Proceed only when the branch plan is compatible with the approved Design or diagnosis. In guided or strict-confirmation modes, ask before creating or switching branches if it changes the user's working context. If `AskUserQuestion` is available, call it for this branch creation/switch confirmation and wait for the answer.

## Pre-Action Compliance Check

Run this before research edits, config changes, branch switches, training launches, evaluation launches, or high-impact commands:

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

If `Branch Plan required` is yes and `Branch Plan present` is no, block the action. If `Run-to-Branch Binding required before command` is yes and the binding is missing, block the training/evaluation command or mark the result as noncompliant.

## Branch Scope Rules

- A branch should serve one hypothesis, variant, ablation factor, baseline, or bug diagnosis.
- Do not mix unrelated refactors, metric changes, data split changes, and model changes in one experiment branch.
- If a change must alter the metric, data split, or evaluation protocol, record that it breaks comparability unless a new comparison group is created.
- If user changes are already present, classify them as related or unrelated and do not overwrite them.

## Ablation Branch Rule

All ablation branches for one experiment group should be derived from the same audited full-model commit:

```text
exp/<hypothesis>/full@<commit>
  ├── ablation/<group>/no-module-a
  ├── ablation/<group>/no-loss-b
  └── ablation/<group>/replace-component-c
```

Each ablation branch should change one factor unless the Design explicitly approves an interaction ablation.

## Run-to-Branch Binding

Every training, evaluation, sanity check, or ablation run must record:

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

If `worktree status` is dirty, include a diff summary and downgrade reproducibility unless the dirty diff is archived with the run.

## Branch Noncompliance Incident

Use this when a research edit, config change, run, or high-impact command happened before the required branch gate or run binding.

```markdown
## Branch Noncompliance Incident
- Incident type: missing-branch-plan / missing-run-binding / dirty-unrecorded-run / wrong-branch-edit / scope-violation
- Discovered at:
- Action already taken:
- Current branch:
- Current head commit:
- Base branch if known:
- `git status --short` summary:
- Diff summary:
- Files changed:
- Untracked files:
- Related to intended task: yes / no / mixed / unknown
- Reproducibility impact: none / limited / broken
- Immediate containment:
- Required repair:
- Conclusion downgrade:
- User confirmation needed:
```

Containment options:

- create a compliant branch from the current state if the changes are useful and scoped;
- archive the diff with the run if a run already happened;
- mark the result as limited reproducibility;
- split unrelated changes before further research work;
- return to the stable branch and restart from a clean Branch Plan.

## Pre-Run Git Checklist

Before long or expensive runs:

- [ ] Current branch matches the Branch Plan.
- [ ] `git rev-parse HEAD` is recorded.
- [ ] `git status --short` is recorded.
- [ ] Diff is reviewed for out-of-scope files.
- [ ] Data split, metric, and evaluation changes are explicitly declared.
- [ ] Untracked files required by the run are listed.
- [ ] Run-to-Branch Binding is written to the run sheet or report.

## Merge Policy

Do not recommend merging an experiment branch into a stable branch unless:

- sanity checks passed;
- the Independent Evidence Audit is `pass` or bounded `conditional-pass`;
- metrics and baselines are comparable;
- temporary debug code is removed;
- run artifacts and decision record are complete;
- the target branch is named;
- user confirmation is obtained.

Possible merge outcomes:

- **merge**: accepted implementation, evidence sufficient, no blocking reproducibility issue;
- **keep as research branch**: useful but not stable enough;
- **archive**: completed, rejected, or superseded experiment kept for traceability;
- **discard after record**: only when user explicitly allows deletion or no useful artifact remains.

## Failed Experiment Policy

Failed branches are evidence. Do not silently delete them. Record:

```markdown
## Failed Branch Record
- Branch:
- Head commit:
- Run ID:
- Failure mode:
- Evidence:
- Last known good commit:
- Decision: debug / redesign / archive / discard with confirmation
- Restart point: Problem / Evidence Pack / Diagnosis / Design / Implementation
```

## Git Commands to Prefer

Use non-destructive commands for inspection:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff --name-only
git log --oneline --decorate -n 10
```

Avoid destructive commands such as `git reset --hard`, `git checkout -- <path>`, branch deletion, or forced updates unless the user explicitly requests them.
