from bioagent import ScientificSupervisor


if __name__ == "__main__":
    question = "Do psychiatric disorders alter gut microbial horizontal gene transfer?"
    ranked, review = ScientificSupervisor().run(question)
    for index, item in enumerate(ranked, 1):
        print(f"{index}. {item.title} | score={item.score:.2f}")
        print(f"   falsifier: {item.falsifiers[0]}")
    print("meta-review:", review)

