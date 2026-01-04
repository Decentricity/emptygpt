# emptygpt

introducing: emptygpt, a generator for meaningless ChatGPT-like text.

Install:

    pip install emptygpt

Use:

    emptygpt
    emptygpt --seed 42
    emptygpt --paragraphs 2

Python API:

    from emptygpt import generate
    print(generate(seed=42, paragraphs=2))



(not a real LLM, runs fully offline)

uses:
- Lorem Ipsum replacement
- Research -- e.g., use to detect these snowclones in public text, psychological tests
- Obfuscation -- make human-written text sound machine-written

A tiny CLI that generates "EmptyGPT" style paragraphs.

