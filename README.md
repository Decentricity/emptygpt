# emptygpt

A tiny CLI that generates "EmptyGPT" style paragraphs.

Install:

    pip install emptygpt

Use:

    emptygpt
    emptygpt --seed 42
    emptygpt --paragraphs 2

Python API:

    from emptygpt import generate
    print(generate(seed=42, paragraphs=2))
