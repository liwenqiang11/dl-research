# Research Recorder

Use the Research Recorder only when the user explicitly asks to remember, record, save, archive, or write the current research result. This role prepares a structured memory draft and writes it only after user confirmation.

## Core Rule

Do not write research memory automatically. The workflow is:

```text
User requests memory/record
→ Research Recorder drafts the record in the required template
→ User confirms or edits the draft
→ Research Recorder writes the confirmed record to the agreed location
```

## Trigger Gate

Trigger the Research Recorder only when the user explicitly requests memory, for example:

- "记忆上述结果"
- "记录这次实验"
- "保存到项目记忆"
- "归档这个结论"
- "写入 Research Record"
- "把这个失败原因记下来"

Do not trigger the recorder merely because a phase ended, a run failed, a conclusion changed, or a reusable lesson appeared. In those cases, include the information in the normal response, but do not write memory unless the user asks.

## Role Boundary

The Research Recorder may:

- summarize verified facts, derivation verdicts, evidence verdicts, mechanisms, actions, and decisions;
- preserve artifact paths, commands, branches, commits, configs, run IDs, metrics, and restart points;
- mark conclusions as active, provisional, rejected, superseded, or deprecated;
- prepare a draft record for user review;
- write the confirmed record to the agreed location after user approval;
- recommend where a future agent should resume.

The Research Recorder must not:

- introduce new factual claims without Atomic Fact Verification;
- introduce new formal/mechanism claims without Formal Derivation Verification;
- strengthen conclusions beyond the Independent Evidence Audit verdict;
- hide failed attempts, contradictions, or noncompliance incidents;
- write memory before the user confirms the drafted record;
- overwrite project memory without explicit user confirmation.

## Record Types

| Record type | When to use |
|-------------|-------------|
| `discovery` | Problem boundary, evidence map, hypothesis, missing evidence |
| `design` | Algorithm/protocol design, branch plan, expected verification |
| `implementation` | Code/config changes, branch, commit, diff summary |
| `sanity` | Shape/loss/gradient/tiny-overfit/probe checks |
| `run` | Training/evaluation command, run ID, metrics, artifacts |
| `analysis` | Mechanistic analysis, fact checks, derivation checks, evidence review |
| `decision` | Solved/partial/unresolved/invalid and restart point |
| `failure` | Failed experiment, failed branch, failed hypothesis, noncompliance |
| `deprecation` | Previously recorded conclusion is corrected or superseded |

## Required Record

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
  - table path or inline summary:
  - non-true critical facts:
- Formal derivation verification:
  - report path or inline summary:
  - invalid or assumption-dependent claims:
- Evidence review:
  - verdict:
  - allowed conclusion strength:
- Mechanistic analysis:
  - verdict:
  - root cause or mechanism:
- Action taken:
- Verification result:
- Decision:
- Deprecated or corrected prior claims:
- Remaining uncertainty:
- Next action:
- Restart point: Problem / Evidence Pack / Atomic Fact Verification / Formal Derivation Verification / Diagnosis / Design / Implementation / Verification / Resolution
```

## Confirmation Workflow

1. **Draft only**: When the user asks to remember a result, output a `Research Record` draft in the required template.
2. **Ask for confirmation**: If `AskUserQuestion` is available, call it to ask the user to confirm, edit, or choose the memory location. If unavailable, ask a concise plain-text question and stop.
3. **Write only after confirmation**: Do not write to `KnowledgeBase.md`, experiment reports, or any memory file until the user confirms the draft.
4. **Post-write note**: After writing, report the file path and whether the record was appended or newly created.

## Memory Location Policy

- If the repository has an established memory file or experiment report convention, use it.
- If no location is established, include the record in the response and propose a repository-local memory path before writing.
- For the Dose80 project, follow project-specific memory instructions when present, such as `KnowledgeBase.md`, `Papers/Zpaper.txt`, experiment report files, or training log rules.
- Never silently overwrite or delete previous records. Append or create a dated entry unless the user explicitly requests replacement.
- If the user asks for memory but does not specify a location, propose the most appropriate project-local target and wait for confirmation.

## Deprecation Rules

When a previous claim is found wrong:

```markdown
## Deprecated Claim
- Old claim:
- Where it appeared:
- Reason for deprecation:
- Atomic fact verdict or formal derivation verdict:
- Corrected statement:
- Impact on prior decisions:
- Required rerun or redesign:
```

Examples:

- A commit message claimed a loss rewards diversity, but Formal Derivation Verification marks it invalid.
- A mechanism analysis assumed a fixed GT count, but Atomic Fact Verification marks it false.
- A run was interpreted as reproducible, but Run-to-Branch Binding was missing.

## Recorder Decision Rules

- `pass` records may support future decisions.
- `conditional-pass` records must carry caveats.
- `fail`, `invalid`, `false`, or `unverifiable` records must name the blocked conclusion.
- Noncompliant branch/run records must downgrade reproducibility until repaired.
- Every unresolved outcome must name a restart point.
