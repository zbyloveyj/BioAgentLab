"""Tiny deterministic example that requires no external API key."""

from bioagent import __version__
from bioagent.core import CallableLLMClient
from bioagent.supervisor import ScientificSupervisor


def toy_model(prompt: str) -> str:
    if "Candidate #1" in prompt:
        return (
            "Reduced microbial butyrate production increases peripheral inflammatory "
            "signaling and shifts microglia-related host transcription."
        )
    if "Candidate #2" in prompt:
        return (
            "Altered microbial bile-acid metabolism changes circulating bile acids, "
            "shifting peripheral T-cell state and downstream neuroimmune signaling."
        )
    if "Candidate #3" in prompt:
        return (
            "Microbial tryptophan catabolism changes circulating indole metabolites, "
            "altering barrier-related signaling and a measurable neural phenotype."
        )
    if "skeptical scientific reviewer" in prompt:
        return (
            "The direction of causality is not established and requires longitudinal "
            "or perturbational validation."
        )
    if "Improve the hypothesis" in prompt:
        return "Revised hypothesis requiring explicit perturbation and temporal validation."
    return "No completion rule matched."


def main() -> None:
    llm = CallableLLMClient(toy_model)
    supervisor = ScientificSupervisor(llm)
    question = "How could gut microbial metabolism influence immune and neural phenotypes?"
    result = supervisor.run(question, n=3)

    print(f"BioAgentLab v{__version__}")
    print(f"Question: {result['question']}\n")
    for hypothesis in result["hypotheses"]:
        print(f"{hypothesis.identifier} | score={hypothesis.score:.3f}")
        print(hypothesis.statement)
        print("Critique:", hypothesis.critiques[0] if hypothesis.critiques else "None")
        print()
    print("Meta-review:", result["meta_review"])


if __name__ == "__main__":
    main()
