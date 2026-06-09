# Deep Research Brainstorming

Deep Research Brainstorming runs AFTER Diagnosis. Given a diagnosed problem, it finds the best solution through structured research, evaluation, and adversarial verification.

## When to Trigger

Trigger when:

- Diagnosis is complete and multiple solution paths exist;
- The problem has multiple competing root causes;
- The user requests brainstorming, solution exploration, or "find the best approach";
- After an outer-loop restart when previous solutions failed;
- When the task is non-trivial and a single-perspective solution risks fixation.

Skip when:

- The problem is mechanically obvious (single clear fix);
- The user has already specified the exact solution;
- The task is purely evidence gathering with no design decision.

## Core Principle

Research first, evaluate second, verify adversarially third. Every proposal must be grounded in knowledge gathered during this phase.

## Three Phases

```
Phase 1: Research (3 agents, parallel)
  ├─ External Research  → WebSearch + WebFetch
  ├─ Internal Audit     → Read + Grep + Glob
  └─ Failure Analysis   → Read history
  → 输出: 结构化知识库

Phase 2: Propose + Evaluate (1 agent)
  → 输出: 3-5 候选方案 + 深度评估 + 排序

Phase 3: Adversarial Verify + Synthesize (1 agent)
  → 输出: 最终方案 + 融合 + 判别实验
```

Total: 5 agents, 3 batches.

## Phase 1: Research

3 Researchers gather knowledge in parallel, each with a distinct strategy.

| Researcher | Strategy | What They Do | Tools |
|---|---|---|---|
| External Research | Find known solutions | Search papers, blogs, open-source, tools, frameworks. Extract methods, mechanisms, sources. | WebSearch, WebFetch |
| Internal Audit | Understand current code | Read core implementation. Find bottlenecks, hidden assumptions, code debt. Trace data flow. | Read, Grep, Glob |
| Failure Analysis | Learn from failures | Analyze all previous failed attempts. Extract lessons. Identify repeated patterns. | Read (logs, history, records) |

### External Research Prompt

```
Agent(
  description="Research Brainstorming: External Research",
  prompt="""
You are an External Researcher. Use WebSearch and WebFetch to find solutions for the diagnosed problem.

## Diagnosis
{diagnosis}

## Evidence Pack (already verified)
{evidence_pack}

## Instructions
1. Search for methods, papers, tools, and open-source implementations related to: {problem_keywords}
2. Use WebSearch to find relevant sources, then WebFetch to read the most promising ones.
3. For each finding, extract: method name, mechanism (how it works), source URL, confidence level.
4. Compare against the current baseline approach.
5. Do NOT propose solutions — just gather and organize knowledge.

## Output Format

### Findings
| # | Method | Mechanism | Source | Confidence | Relevance |
|---|--------|-----------|--------|------------|-----------|

### Summary
[2-3 sentence synthesis of the most important findings]

### Knowledge Gaps
[What you couldn't find or verify]
"""
)
```

### Internal Audit Prompt

```
Agent(
  description="Research Brainstorming: Internal Audit",
  prompt="""
You are an Internal Auditor. Read the codebase to understand the current implementation and find issues.

## Diagnosis
{diagnosis}

## Relevant Files
{relevant_files}

## Instructions
1. Read the core implementation files.
2. Identify: data flow, model architecture, loss computation, optimizer, evaluation logic.
3. Find: hardcoded assumptions, magic numbers, commented-out experiments, TODO comments.
4. Trace: how does a batch of data flow from input to loss to gradient?
5. Look for: potential bottlenecks, unused code, inconsistent implementations.

## Output Format

### Architecture Overview
[Brief description of the current implementation]

### Issues Found
| # | File | Line | Issue | Severity | Impact |
|---|------|------|-------|----------|--------|

### Hidden Assumptions
[List assumptions embedded in the code that may not hold]

### Data Flow
[Trace from input to loss to gradient]
"""
)
```

### Failure Analysis Prompt

```
Agent(
  description="Research Brainstorming: Failure Analysis",
  prompt="""
You are a Failure Analyst. Analyze all previous failed attempts to extract lessons.

## Diagnosis
{diagnosis}

## Experiment History
{experiment_dirs}

## Instructions
1. Review all previous experiment logs, history, and records.
2. For each failed attempt: what was tried, what happened, why did it fail?
3. Identify patterns: do failures cluster around a specific mechanism?
4. Extract lessons: what should NOT be tried again, and what might work with modification?

## Output Format

### Failed Attempts
| # | What Was Tried | What Happened | Why It Failed | Lesson |
|---|---------------|---------------|---------------|--------|

### Failure Patterns
[Common themes across failures]

### Avoid
[Directions that have been proven not to work]

### Retry Candidates
[Previous attempts that might work with modification]
"""
)
```

### Knowledge Base Assembly

After Phase 1, the main agent assembles the Knowledge Base:

```markdown
## Knowledge Base

### External Methods
[method table from External Research]

### Internal Issues
[issue table from Internal Audit]

### Failure Lessons
[lesson table from Failure Analysis]

### Avoid
[proven dead ends]

### Retry Candidates
[modification-worthy previous attempts]
```

## Phase 2: Propose + Evaluate

1 agent reads the Knowledge Base and produces evaluated candidates.

### Prompt

```
Agent(
  description="Research Brainstorming: Propose + Evaluate",
  prompt="""
You are a Solution Architect. Based on the diagnosis and knowledge base, propose and evaluate candidate solutions.

## Diagnosis
{diagnosis}

## Knowledge Base
{knowledge_base}

## Instructions
1. Propose 3-5 candidate directions that address the diagnosed root cause.
2. For each candidate:
   - Mechanism derivation: causal chain from change to improvement (not qualitative — derive it)
   - Evidence anchoring: what from the knowledge base supports this? What contradicts it?
   - Cost: implementation scope, training time, risk, dependencies
   - Verification design: smallest experiment to test it, success/failure signals
   - Devil's Advocate: why might this fail? What is the weakest link?
3. Rank by: evidence strength, mechanism clarity, cost, verifiability.

## Output Format

### Candidate A: [Name]
- **Core hypothesis**: [one-sentence falsifiable claim]
- **Source**: [where this comes from — paper/code/failure lesson]
- **Mechanism**: [causal derivation, not just description]
- **Evidence support**: [from knowledge base]
- **Evidence against**: [from knowledge base]
- **Cost**: [implementation effort, training time, risk]
- **Verification**: [smallest experiment, success signal, failure signal, estimated time]
- **Devil's Advocate**: [weakest link, most likely failure mode]
- **Type**: proven / adapted / exploratory

### Candidate B: [Name]
...

### Candidate C: [Name]
...

### Ranking
| Rank | Candidate | Evidence | Mechanism | Cost | Verifiability | Overall |
|------|-----------|----------|-----------|------|---------------|---------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

### Fusion Opportunities
[Can parts of different candidates be combined?]
"""
)
```

## Phase 3: Adversarial Verify + Synthesize

1 agent tries to REFUTE each candidate. Surviving candidates win.

### Prompt

```
Agent(
  description="Research Brainstorming: Verify + Synthesize",
  prompt="""
You are a Skeptical Judge. Your job is to try to REFUTE each candidate solution. If you cannot refute it, it survives.

## Top Candidates (from Phase 2)
{candidates}

## Knowledge Base
{knowledge_base}

## Diagnosis
{diagnosis}

## Instructions
1. For each candidate, try your BEST to REFUTE it:
   - Find the strongest counter-argument
   - Find contradicting evidence in the knowledge base
   - Identify conditions under which it would fail
   - Check: is the mechanism derivation valid? Are there hidden assumptions?
2. If your refutation succeeds → candidate is REFUTED
3. If your refutation fails → candidate SURVIVES
4. For surviving candidates:
   - Final ranking
   - Conditions for viability
   - Fusion opportunities
5. Design discriminating experiments to resolve remaining uncertainty.

## Output Format

### Candidate A: [Name]
- **Refutation attempt**: [your strongest argument against it]
- **Counter-evidence**: [from knowledge base]
- **Hidden assumptions**: [that might not hold]
- **Verdict**: REFUTED / SURVIVES
- **If refuted**: [why, and what would change my mind]
- **If survives**: [conditions, remaining risks]

### Candidate B: [Name]
...

### Candidate C: [Name]
...

### Final Recommendation
- **Primary**: [highest confidence surviving candidate]
- **Fallback**: [second choice if primary fails]
- **Fusion**: [if combining parts of candidates is better than either alone]

### Discriminating Experiments (priority-ordered)
| Priority | Experiment | Cost | Discriminates | Expected Result |
|----------|-----------|------|---------------|-----------------|
| 1 | | | | |
| 2 | | | | |

### Knowledge Gained (for Evidence Pack)
- New verified facts:
- New methods identified:
- Failure patterns confirmed:

### Unresolved Disputes
[What evidence would resolve each dispute]

### Restart Point
[Where to re-enter if all candidates fail]
"""
)
```

## Agent Execution Summary

```
Phase 1: 3 Agent calls in parallel (External + Internal + Failure)
Phase 2: 1 Agent call (reads Knowledge Base, proposes + evaluates)
Phase 3: 1 Agent call (adversarial verify + synthesize)

Total: 5 agents, 3 batches
Estimated tokens: ~20k-25k
```

## Outer-Loop Restart

When a previous solution fails:

- Phase 1 Failure Analysis receives ALL previous attempts as input
- Phase 2 proposals must explicitly reference failure lessons
- Phase 3 refutation checks against previous failures
- This prevents cycling through the same solutions

## Comparison with Previous Design

| Dimension | Previous (5-phase) | Current (3-phase) |
|---|---|---|
| Agent count | 17-19 | 5 |
| Batches | 5 | 3 |
| Token budget | ~60k | ~20k |
| External search | Not executed | Real WebSearch |
| Phase overlap | Phase 2/3 overlap | Merged |
| Cross-examination | 4 surface reviews | 1 deep refutation |
| Deliverable | Same | Same |
