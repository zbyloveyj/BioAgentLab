# BioAgentLab Architecture

## Core idea

BioAgentLab separates reasoning, evidence, tools, state and supervision.

~~~text
                 Supervisor
                     |
      +--------------+--------------+
      |              |              |
  Reasoning       Evidence        Tools
    Agents          Layer          Layer
      |              |              |
      +--------------+--------------+
                     |
                 State / Trace
~~~

## Scientific reasoning layer

~~~text
Research Question
      |
      v
Generation
      |
      v
Reflection
      |
      v
Scientific Debate
      |
      v
Ranking
      |
      v
Evolution
      |
      v
Proximity / Deduplication
      |
      v
Meta-review
      |
      v
Evidence Verification
      |
      v
Supervisor decision
~~~

## Reliability boundary

LLMs should interpret scientific goals, decompose tasks, select tools, compare hypotheses, explain outputs and identify missing evidence.

Specialist tools should perform statistical tests, align sequences, quantify abundance, call variants, cluster cells, fit numerical models, calculate enrichment and execute reproducible pipelines.

## Planned biology tool layer

- Literature: PubMed-style adapters
- Molecular knowledge: NCBI, UniProt, KEGG
- Microbiome: MetaPhlAn, HUMAnN, MAG and strain workflows
- Single-cell: Scanpy and scverse-compatible tools
- Genomics: CLI and workflow-tool adapters
- Multi-omics: modular statistical and modeling adapters

## Traceability

Mature workflows should record decision context, selected tool, tool arguments, software version, result summary, evidence source, confidence, critique, retry information and failure information.
