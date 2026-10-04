# BioAgentLab Roadmap

BioAgentLab is being built as both a learning system and a research-grade framework for evidence-grounded AI agents in biology.

## v0.1 — Foundations
- Project architecture and packaging
- Book outline and first chapter
- Shared scientific data schemas
- Provider-agnostic LLM interface
- Generation, Reflection, Ranking, Evolution, Proximity and Meta-review agents
- Minimal Supervisor
- Runnable hypothesis-tournament example
- Smoke tests

## v0.2 — Knowledge and evidence
- Literature retrieval interfaces
- RAG and Agentic RAG
- Evidence provenance and evidence grading
- Citation-aware answer objects
- PubMed, NCBI, UniProt and KEGG adapters
- Persistent research memory

## v0.3 — Scientific reasoning
- Pairwise scientific debate
- Elo-style hypothesis ranking
- Multi-round hypothesis evolution
- Contradiction and redundancy detection
- Tool and action discovery
- Evidence self-verification
- Failure-mode logging

## v0.4 — Biology workflows
- Literature Agent
- Microbiome Agent
- Single-cell Agent
- Genomics Agent
- Multi-omics Agent
- Reproducible scientific-tool execution

## v0.5 — Benchmarking
- Biology-agent task suite
- Evidence-grounding metrics
- Tool-selection accuracy
- Reproducibility checks
- Unsupported-claim evaluation
- Cost and latency tracking

## v1.0 — BioDiscovery Agent
A full pipeline from research question to question decomposition, evidence retrieval, hypothesis generation, scientific debate, ranking, computational analysis, mechanistic interpretation, experimental design, meta-review and reproducible final report.

## Design principle

LLMs decide and reason; scientific software computes; databases provide evidence; agents cross-check one another; the supervisor coordinates the workflow.
