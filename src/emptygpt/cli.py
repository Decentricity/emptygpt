import argparse
from .api import generate

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="emptygpt", description="Generate EmptyGPT-style jargon paragraphs.")
    p.add_argument("--seed", type=int, default=None, help="Random seed (int).")
    p.add_argument("--paragraphs", type=int, default=None, help="Exact number of paragraphs (default: 2).")
    args = p.parse_args(argv)
    print(generate(seed=args.seed, paragraphs=args.paragraphs))
    return 0
