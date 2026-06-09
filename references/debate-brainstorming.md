# Deep Research Brainstorming

Deep Research Brainstorming runs AFTER Diagnosis. Given a diagnosed problem, it finds the best solution through structured research: 4 Researchers gather new knowledge (literature, codebase, failures, tools), map the full solution space, deeply evaluate each candidate, cross-examine from different angles, and synthesize the best result.

## When to Trigger

Trigger Deep Research Brainstorming when:

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

Research first, decide second. Every proposal must be grounded in knowledge gathered during this phase, not just reasoning from existing evidence.

## Five Phases

```
Phase 1: Knowledge Gathering (4 Researchers, parallel)
  → Phase 2: Solution Space Mapping (4 Researchers, parallel, then dedup)
    → Phase 3: Deep Evaluation (parallel, one per candidate)
      → Phase 4: Cross-Examination (4 Researchers, parallel)
        → Phase 5: Synthesis (Judge, 1 call)
```

## Phase 1: Knowledge Gathering

4 Researchers, each with a distinct research strategy, gather new knowledge in parallel. Each uses the tools available to them (web search, code reading, log analysis, etc.).

| Researcher | Strategy | What They Do | Tools |
|---|---|---|---|
| Literature Survey | Find known solutions | Search papers, blogs, open-source projects. Compare baselines. Find SOTA. | WebSearch, WebFetch |
| Codebase Audit | Understand current implementation | Read core code. Find bottlenecks, hidden assumptions, code debt. Trace data flow. | Read, Grep, Glob |
| Failure Analysis | Learn from failures | Analyze all previous failed attempts. Extract lessons. Identify repeated patterns. | Read (logs, history, records) |
| Tool/Tech Landscape | Find available tools | Research relevant libraries, frameworks, techniques. Assess maturity and fit. | WebSearch, WebFetch |

### Researcher Prompt Template

```
Agent(
  description="Research Brainstorming: {strategy_name}",
  prompt="""
You are a Researcher in a Deep Research Brainstorming session. Your strategy is: {strategy_name}.

## Problem Statement
{problem_statement}

## Evidence Pack (already verified)
{evidence_pack}

## Your Task
{strategy_specific_instructions}

## Instructions
1. Actively gather NEW knowledge using the tools available to you.
2. For each finding, record: source, relevance, key insight, and confidence level.
3. Do NOT propose solutions yet — just gather and organize knowledge.
4. Be thorough but focused on the problem at hand.
5. Cite specific sources (paper titles, file paths, URLs, log lines).

## Output Format

### Findings
| # | Source | Finding | Relevance | Key Insight | Confidence |
|---|--------|---------|-----------|-------------|------------|

### Summary
[2-3 sentence synthesis of the most important findings]

### Knowledge Gaps
[What you couldn't find or verify that would be important]
"""
)
```

### Strategy-Specific Instructions

**Literature Survey:**
```
- Search for papers, blog posts, and open-source projects related to: {problem_keywords}
- For each relevant method: what problem does it solve, what mechanism does it use, what are its limitations?
- Compare against the current baseline approach.
- Look for: loss functions, architectures, training tricks, evaluation methods.
```

**Codebase Audit:**
```
- Read the core implementation files: {relevant_files}
- Identify: data flow, model architecture, loss computation, optimizer, evaluation logic.
- Find: hardcoded assumptions, magic numbers, commented-out experiments, TODO comments.
- Trace: how does a batch of data flow from input to loss to gradient?
- Look for: potential bottlenecks, unused code, inconsistent implementations.
```

**Failure Analysis:**
```
- Review all previous experiment logs, history, and records in: {experiment_dirs}
- For each failed attempt: what was tried, what happened, why did it fail?
- Identify patterns: do failures cluster around a specific mechanism?
- Extract lessons: what should NOT be tried again, and what might work with modification?
- Check: are there experiments that were started but never completed? Why?
```

**Tool/Tech Landscape:**
```
- Search for libraries and tools that could help with: {problem_description}
- For each tool: maturity, active maintenance, API quality, compatibility with current stack.
- Look for: existing implementations of proposed methods, pretrained models, benchmark results.
- Assess: would using this tool be faster than implementing from scratch?
```

## Phase 2: Solution Space Mapping

Each Researcher reads the Knowledge Base (all Phase 1 outputs) and maps out ALL viable directions from their perspective.

### Output Format

```markdown
## Solution Space Map

### Direction A: [Name]
- **Core hypothesis**: One-sentence falsifiable claim
- **Source**: Where this idea comes from (paper/code/failure lesson)
- **Mechanism**: Causal chain from change to improvement
- **Evidence**: What supports this
- **Cost**: Implementation effort, training time, risk
- **Type**: proven / adapted / exploratory

### Direction B: [Name]
...

### Direction C: [Name]
...
```

Each Researcher must propose **at least 2 directions**, not just one. The goal is breadth, not commitment to a single idea.

### Dedup and Merge

After Phase 2, a dedup step merges overlapping directions from different Researchers and keeps independent ones. Output: a unified Solution Space Map with unique candidate directions.

## Phase 3: Deep Evaluation

Each candidate direction is assigned to the most qualified Researcher for deep evaluation. This is not a surface-level description — it is a rigorous analysis.

### Output Format

```markdown
## Deep Evaluation: [Direction Name]

### Mechanism Derivation
[Complete causal chain from input to output. Not a qualitative description — a derivation.]

### Evidence Anchoring
| Claim | Source | Verified | Strength |
|-------|--------|----------|----------|
| [claim] | [paper/code/experiment] | true/false/unverifiable | strong/moderate/weak |

### Cost Estimation
- **Implementation**: [scope, file count, estimated effort]
- **Training**: [GPU hours, memory, data requirements]
- **Risk**: [probability of failure, rollback difficulty]
- **Dependencies**: [external libraries, data, compute]

### Verification Design
- **Smallest discriminating experiment**: [specific steps]
- **Success signal**: [metric threshold or behavior]
- **Failure signal**: [metric threshold or behavior]
- **Estimated time to verify**: [hours/days]

### Devil's Advocate
[Why might this fail? What is the weakest link? What assumption is most likely wrong?]
```

## Phase 4: Cross-Examination

Each Researcher reviews the other Researchers' top candidates from their professional perspective.

### Output Format

```markdown
## Cross-Examination

### On [Direction X] (evaluated by Researcher Y)
- **From Literature perspective**: [What do papers say about this approach's limitations?]
- **From Codebase perspective**: [Can the current code support this? What needs to change?]
- **From Failure perspective**: [How is this different from previous failed attempts?]
- **From Tool perspective**: [Is there a ready-made implementation? Is it better to build or buy?]

### Verdict on [Direction X]
- Strengths that survive scrutiny:
- Weaknesses exposed:
- Conditions for viability:
```

## Phase 5: Synthesis

The Judge reads all research artifacts and produces the final verdict.

### Judge Input

- Phase 1 Knowledge Base (all 4 Researchers' findings)
- Phase 2 Solution Space Map (deduped)
- Phase 3 Deep Evaluations
- Phase 4 Cross-Examination results
- Original Evidence Pack
- Atomic Fact Verification table
- Formal Derivation Verification report

### Output Format

```markdown
## Research Verdict

### Solution Space Overview
- Total directions explored: N
- Literature-backed: X
- Adapted from prior work: Y
- Purely exploratory: Z
- Previously failed (with modification): W

### Top-3 Candidates
| Rank | Direction | Evidence | Mechanism | Cost | Survivability | Verification Time |
|------|-----------|----------|-----------|------|---------------|-------------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

### Fusion Proposal (if applicable)
- From [Direction X]: [specific contribution]
- From [Direction Y]: [specific contribution]
- Combined: [fused solution]
- Why fusion is better than either alone:

### Knowledge Gained (for Evidence Pack)
- New verified facts:
- New methods identified:
- New tools available:
- Failure patterns confirmed:

### Discriminating Experiments (priority-ordered)
| Priority | Experiment | Cost | Discriminates | Expected Result |
|----------|-----------|------|---------------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### Unresolved Disputes
[What evidence would resolve each dispute]

### Final Recommendation
- **Primary**: [direction with highest confidence]
- **Fallback**: [direction if primary fails]
- **Restart point**: [where to re-enter if both fail]
```

## Agent Execution

Deep Research Brainstorming runs as parallel Agent calls:

```
Phase 1: 4 Agent calls in parallel (one per Researcher strategy)
Phase 2: 4 Agent calls in parallel (each reads all Phase 1 outputs)
Phase 3: 4-6 Agent calls in parallel (one per candidate direction)
Phase 4: 4 Agent calls in parallel (each reviews others' evaluations)
Phase 5: 1 Agent call (Judge reads everything)
Total: 17-19 Agent calls, 5 parallel batches
```

Each Researcher is an independent Agent with its own context. They share knowledge only through the Knowledge Base artifact (Phase 1 outputs).

The Judge is a separate Agent that reads all research artifacts. It does not participate in the research.

## Outer-Loop Restart

When a previous solution fails and the workflow restarts:

- Phase 1 Failure Analysis Researcher receives ALL previous attempts as input:
  - What was tried
  - What happened
  - Why it failed
  - What evidence was generated
- This prevents cycling through the same solutions
- Other Researchers also receive the failure summary to avoid repeating known dead ends

## Token Budget Control

Each Researcher's output should be bounded:
- Phase 1: ≤ 3000 tokens per Researcher
- Phase 2: ≤ 2000 tokens per Researcher (max 5 directions)
- Phase 3: ≤ 2000 tokens per evaluation
- Phase 4: ≤ 1500 tokens per Researcher
- Phase 5: ≤ 3000 tokens for Judge

Total estimated: ~50k-70k tokens per brainstorming session.

## Comparison with Old Debate

| Dimension | Old Debate | Deep Research |
|---|---|---|
| Starting point | Existing Evidence Pack | Problem + active knowledge gathering |
| Knowledge sources | Only existing facts | Literature + code + failures + tools |
| Output per agent | 1 proposal | Full solution space map |
| Depth | Fixed 3 rounds | Iterative, deep evaluation |
| Evidence | Qualitative references | Structured evidence anchoring |
| Cross-validation | Surface-level attacks | Professional cross-examination |
| Deliverable | Ranked proposals | Ranked proposals + knowledge base + experiment plan |
