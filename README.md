# BioAgentLab

**An evidence-grounded AI agent framework and learning resource for biology, bioinformatics, and biomedical discovery.**

BioAgentLab is both a hands-on learning project for mastering AI agents from first principles and a research-oriented framework for building reliable scientific agents for biology.

中文主线教材：**《AI Agent for Biology：从 LLM、Tool Use、RAG 到自主生物医学科研智能体》**

## Why BioAgentLab?

A useful scientific agent should not simply chain prompts. It should be able to:

- decompose a research question;
- discover and select appropriate tools;
- retrieve and grade evidence;
- generate falsifiable hypotheses;
- criticize its own assumptions;
- compare competing hypotheses;
- execute reproducible computational analyses;
- recover from failed actions;
- record provenance and decisions;
- propose the next experiment.

The central principle is:

**LLMs reason and decide; specialist scientific software computes; databases provide evidence; agents cross-check one another; the supervisor coordinates the workflow.**

## Scientific-agent loop

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
Proximity
      |
      v
Meta-review
      |
      v
Evidence Verification
      |
      v
Supervisor
      |
      v
Next Action / Final Report
~~~

## Repository map

~~~text
BioAgentLab/
├── book/                 Chinese AI Agent for Biology textbook
├── bioagent/             Reusable scientific-agent framework
├── workflows/            Biology-specific workflows
├── examples/             Runnable examples
├── benchmark/            Evaluation suite
├── docs/                 Architecture notes
├── tests/                Tests
├── ROADMAP.md
└── pyproject.toml
~~~

## Current status — v0.1

The first scaffold now includes:

- provider-agnostic LLM interface;
- evidence and hypothesis schemas;
- Generation Agent;
- Reflection Agent;
- Ranking Agent;
- Evolution Agent;
- Proximity Agent;
- Meta-review Agent;
- minimal Scientific Supervisor;
- offline hypothesis-tournament example;
- smoke tests;
- book outline and Chapter 1.

Retrieval, real biology tools, scientific debate, evidence verification, persistent memory and domain workflows will be added step by step.

## Quick start

~~~bash
git clone https://github.com/zbyloveyj/BioAgentLab.git
cd BioAgentLab
python -m pip install -e .
python examples/01_hypothesis_tournament.py
~~~

For development:

~~~bash
python -m pip install -e ".[dev]"
pytest
~~~

## Learning path

1. Book overview: book/README.md
2. Chapter 1: book/part01_foundations/01_from_llm_to_agent.md
3. Architecture: docs/architecture.md
4. Runnable example: examples/01_hypothesis_tournament.py
5. Roadmap: ROADMAP.md

## Planned biology agents

- Literature Agent
- Genomics Agent
- Single-cell Agent
- Microbiome Agent
- Multi-omics Agent
- BioDiscovery Agent

## Long-term goal

The capstone system will take a biological research question and progressively produce an evidence-grounded, reproducible and experimentally testable research report.

The ambition is not an autonomous chatbot that merely sounds scientific.

The ambition is a **scientific decision-and-orchestration system** that knows when to reason, when to search, when to compute, when to doubt itself and when evidence is still insufficient.

## License

A license has not yet been selected. The repository is currently under active early development.
