"""The Unofficial Guide command-line interface."""
import argparse
from functools import cache

from .generation import answer, create_generator, render
from .retrieval import Index


def print_matches(matches):
    print("Retrieved evidence:")
    for match in matches:
        print(f"  {match.distance:.3f}  {match.chunk.title} [#{match.chunk.position}]")
        print(f"         {match.chunk.text}")


def main():
    parser = argparse.ArgumentParser(description="Ask the MIT first-year student guide.")
    parser.add_argument("question", help="A quoted plain-language question")
    parser.add_argument("--backend", choices=("local", "groq"), default="local")
    parser.add_argument("--show-retrieval", action="store_true", help="Print all five retrieved chunks")
    args = parser.parse_args()
    if not args.question.strip():
        parser.error("Enter a nonempty question.")

    index = Index()

    @cache
    def generator():
        return create_generator(args.backend)

    def complete(messages):
        return generator()(messages)

    matches = index.search(args.question)
    try:
        print(render(answer(args.question, matches, complete)))
    except (ImportError, ValueError) as exc:
        parser.exit(1, f"Generation error: {exc}\n")
    if args.show_retrieval:
        print_matches(matches)


if __name__ == "__main__":
    main()
