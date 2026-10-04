# Contributing to BioAgentLab

BioAgentLab is currently in an early research and teaching phase.

## Design principles
1. Evidence before eloquence.
2. Reliable scientific software should perform numerical computation.
3. Every agent decision should be inspectable.
4. Biological claims should carry provenance whenever possible.
5. Reproducibility is a first-class feature.
6. Multi-agent systems should reduce error, not merely multiply prompts.

## Development workflow
- Keep changes small and testable.
- Add or update tests when behavior changes.
- Prefer provider-agnostic interfaces.
- Never hard-code secrets or API keys.
- Put domain workflows under workflows/.
- Put reusable primitives under bioagent/.
- Put learning material under book/.

## Coding style
- Python 3.10+
- Type hints for public APIs
- Clear docstrings
- Minimal hidden state
- Deterministic behavior where possible
