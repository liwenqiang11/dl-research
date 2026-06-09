# Paper Close Reading

Systematic extraction of transferable design elements from local PDF papers for scientific transfer learning. This is an independent tool, not part of the main dl-research loop. Trigger only when the user provides local PDFs.

## When to Trigger

Trigger when:

- The user provides local PDF files and wants to extract useful design elements;
- The user says "精读论文", "extract from paper", "read this paper for transferable methods";
- The user wants to do scientific transfer learning from specific papers.

Skip when:

- No local PDFs are provided;
- The user only wants a general summary (use normal reading instead);
- The task is purely evidence gathering with no design decision.

## Core Principle

Extract TRANSFERABLE DESIGN ELEMENTS, not summaries. For each element, answer:
1. What is it?
2. WHY does it work? (mechanism, not just description)
3. How to implement it? (formula, code, hyperparameters)
4. Does the ablation prove it works? (evidence)
5. Can we use it? (applicability + adaptation)

## Three Steps

```
Step 1: Screening (1 agent)
  → 读摘要+引言+结论, 判断相关度, 排序

Step 2: Deep Read (N agents 并行, 每 agent 1 篇)
  → 逐节精读, 提取设计元素, 输出 Paper Card

Step 3: Integration (1 agent)
  → 交叉对比 + 冲突检测 + 适配建议
  → 输出: design-elements.md
```

Total: 5-7 agents, 3 batches.

## Step 1: Screening

Quickly assess which papers are relevant and prioritize reading order.

### Prompt

```
Agent(
  description="Paper Close Reading: Screening",
  prompt="""
You are a Paper Screener. Quickly assess which papers are relevant to the diagnosed problem.

## Diagnosis
{diagnosis}

## Papers to Screen
{pdf_paths}

## Instructions
For each paper, read ONLY: abstract, introduction (first 2 paragraphs), conclusion, and results tables.
Do NOT read the full method section yet.

For each paper, answer:
1. What problem does it solve?
2. How similar is it to our diagnosed problem?
3. What type of contribution is it? (loss / architecture / training trick / evaluation / data)
4. Does it have ablation experiments?
5. Does it provide code?

## Output Format

| # | Title | Problem | Similarity | Contribution Type | Has Ablation | Has Code | Priority |
|---|-------|---------|------------|-------------------|-------------|----------|----------|

Priority: high / medium / low
Similarity: high / medium / low

### Recommended Reading Order
[Which papers to read first, and why]
"""
)
```

## Step 2: Deep Read

Extract transferable design elements from each paper. One agent per paper, run in parallel.

### Prompt

```
Agent(
  description="Paper Close Reading: Deep Read - {paper_title}",
  prompt="""
You are a Paper Analyst performing deep reading for scientific transfer learning.
Your goal is NOT to summarize the paper — it is to extract TRANSFERABLE DESIGN ELEMENTS
that can be applied to the diagnosed problem.

## Diagnosis
{diagnosis}

## Paper
{pdf_path_or_content}

## Screening Notes
{screening_result_for_this_paper}

## Extraction Protocol

Read the paper section by section and extract:

### 1. Problem Statement
- What exact problem does this paper solve?
- What is their claimed contribution?
- What gap does it fill?

### 2. Design Elements Extraction

For EACH distinct design element (loss term, architecture component, training strategy, data processing, evaluation method), extract:

#### Element: [Name]

**What it is:**
[One-sentence description]

**Why it works (mechanism):**
[NOT just "it improves X". Derive the causal chain:
 - What does this element do to the input/signal/gradient?
 - Why does that lead to the claimed improvement?
 - What is the mathematical or intuitive justification?
 This is the KEY step that separates deep reading from superficial reading.]

**Concrete implementation:**
- Formula: [exact mathematical formula]
- Pseudocode: [if formula alone is unclear]
- Hyperparameters: [name, recommended value, sensitivity if reported]
- Initialization: [how to initialize, if applicable]
- Key code snippet: [if code is available, the core implementation]

**Ablation evidence:**
[What does the paper's ablation experiment show about this specific element?
 - How much does it contribute to the final metric?
 - Is it essential or optional?
 - Cite the specific table/figure number]

**Applicability to our problem:**
- Direct transfer possible? [yes / no / with adaptation]
- What needs to change? [specific adaptation steps]
- What could go wrong? [risks of transfer]
- Confidence: [high / medium / low — based on problem similarity and evidence strength]

**Code reference:**
[If the paper provides code, point to the exact file/line implementing this element]

### 3. Training Protocol
- Optimizer: [Adam/SGD/... + specific settings]
- Learning rate: [value + schedule]
- Batch size: [value]
- Epochs: [value]
- Data augmentation: [what specifically]
- Regularization: [dropout/weight decay/... + values]
- Any non-standard training tricks?

### 4. Evaluation Protocol
- Metrics used: [list]
- Baselines compared: [list]
- Statistical significance: [reported? how?]
- Fairness of comparison: [same data splits? same compute budget?]

### 5. Limitations (stated and unstated)
- Paper states: [their acknowledged limitations]
- I observe: [limitations they don't mention]

### 6. Key Takeaways for Our Problem
- Most valuable element: [which one element is most transferable]
- Quick win: [what could we adopt with minimal effort]
- Long-term investment: [what would require more work but has higher payoff]

## Rules
- Every claim must cite: section, table, figure, or equation number from the paper.
- Be specific, not vague. "The loss uses a focal weighting term with gamma=2.0 (Eq. 5, Table 3 ablation shows +2.1 mAP)" is good. "The loss is better" is bad.
- Focus on elements that are transferable to the diagnosed problem.
- If the paper's problem is very different from ours, still extract the mechanism — it might be adaptable.
"""
)
```

## Step 3: Integrate

Synthesize all Paper Cards into a unified Design Element Library.

### Prompt

```
Agent(
  description="Paper Close Reading: Integration",
  prompt="""
You are a Research Integrator. Synthesize multiple Paper Cards into a unified Design Element Library
that can be consumed by the Deep Research Brainstorming phase.

## Diagnosis
{diagnosis}

## Paper Cards
{all_paper_cards}

## Instructions

### 1. Element Inventory
List ALL design elements extracted from all papers. Group by type:
- Loss functions
- Architecture components
- Training strategies
- Data processing
- Evaluation methods

### 2. Cross-Paper Comparison
For elements of the same type across different papers:
| Element | Paper A | Paper B | Paper C | Conflict? | Best Version |
Compare: do different papers agree or contradict each other?

### 3. Conflict Resolution
If Paper A says "X works" and Paper B says "X doesn't work":
- Analyze: different problem domains? different data? different baselines?
- Judge: which context is more similar to ours?
- Recommend: should we try X or avoid it?

### 4. Transferability Ranking
Rank all elements by:
- Evidence strength (ablation results, multiple papers confirming)
- Problem similarity (how close is their problem to ours)
- Implementation cost (how hard to adapt)
- Risk (what could go wrong)

### 5. Recommended Adoption Plan
| Priority | Element | Source | Adaptation Needed | Effort | Expected Impact |
Which elements should we adopt first?

### 6. Design Element Library
For each recommended element, write a self-contained description:
- **Name**: [element name]
- **Type**: loss / architecture / training / data / evaluation
- **Source**: [paper title + section/figure/table reference]
- **Mechanism**: [why it works — from Paper Card]
- **Implementation**: [formula + code reference]
- **Evidence**: [ablation results with specific numbers]
- **Adaptation plan**: [how to apply to our problem]
- **Risks**: [what could go wrong]
- **Confidence**: high / medium / low

### 7. Quick Wins vs Long-term Investments
- Quick wins: [elements that can be adopted with minimal effort]
- Long-term: [elements that require more work but have higher payoff]
- Experimental: [elements with weak evidence but interesting potential]

## Output Format

Write the complete Design Element Library in markdown.
This file will be consumed by dl-research Deep Research Brainstorming Phase 1 (External Research).
"""
)
```

## Output File

The integration step produces `design-elements.md` in the project root:

```markdown
# Design Element Library
Generated from: [list of papers]
For problem: [diagnosis summary]
Date: [date]

## Quick Wins
| Element | Source | Mechanism | Effort | Expected Impact |

## Design Elements

### Loss Functions
#### Element: [Name]
- **Source**: [paper, section, table]
- **Mechanism**: [why it works]
- **Implementation**: [formula]
- **Evidence**: [ablation results]
- **Adaptation**: [for our problem]
- **Risks**: [what could go wrong]
- **Confidence**: [high/medium/low]

### Architecture Components
...

### Training Strategies
...

## Cross-Paper Conflicts
| Topic | Paper A says | Paper B says | Resolution |

## Adoption Plan
| Priority | Element | Adaptation | Effort | Impact |
```

## Integration with dl-research

When `design-elements.md` exists in the project:

1. Deep Research Brainstorming Phase 1 (External Research) reads it as input
2. Phase 1 Internal Audit checks if our code can support the extracted designs
3. Phase 2 Propose uses elements as candidate building blocks
4. Elements are cited in the final Research Verdict

To invoke: user provides PDFs and requests paper close reading. The protocol runs independently and writes `design-elements.md`. Then the user can start dl-research which will consume it.

## Agent Execution Summary

```
Step 1: 1 Agent (screening, reads abstracts only)
Step 2: N Agents in parallel (one per paper, typically 3-5)
Step 3: 1 Agent (integration, reads all Paper Cards)

Total: 5-7 agents, 3 batches
```

## Token Budget

- Step 1: ~2k tokens (abstracts only)
- Step 2: ~5k tokens per paper × N papers
- Step 3: ~5k tokens (synthesis)
- Total: ~20k-30k tokens for 3-5 papers
