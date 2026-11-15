"""The Unofficial Guide command-line interface."""
import argparse
import json
import re
from functools import cache

from .generation import answer, create_generator, render
from .ingest import CORPUS
from .retrieval import Index

FOLLOW_UP = re.compile(r"^(and\b|(?:what|how) about\b)|\b(it|its|they|them|their|that (?:group|class|project))\b", re.I)


def print_matches(matches):
    print("Retrieved evidence (cosine distance):")
    for match in matches:
        print(f"  {match.distance:.3f}  {match.chunk.title} [#{match.chunk.position}]")
        print(f"         {match.chunk.text}")


def main():
    parser = argparse.ArgumentParser(description="Ask the MIT first-year student guide.")
    parser.add_argument("question", nargs="?", help="A quoted plain-language question")
    parser.add_argument("--backend", choices=("local", "groq"), default="local")
    parser.add_argument("--mode", choices=("semantic", "hybrid"), default="semantic")
    parser.add_argument("--source", help="Limit retrieval to one source slug")
    parser.add_argument("--list-sources", action="store_true", help="List source slugs and post titles")
    parser.add_argument("--chat", action="store_true", help="Open a session with follow-up memory")
    parser.add_argument("--show-retrieval", action="store_true", help="Print all retrieved chunks")
    args = parser.parse_args()
    sources = json.loads((CORPUS / "sources.json").read_text(encoding="utf-8"))
    if args.list_sources:
        for source in sources:
            print(f"{source['id']}  —  {source['title']}")
        return
    if args.source and args.source not in {source["id"] for source in sources}:
        parser.error("Unknown source slug. Run python -m guide --list-sources.")
    if args.chat and args.question is not None:
        parser.error("Choose a one-shot question or --chat.")
    if not args.chat and (args.question is None or not args.question.strip()):
        parser.error("Enter a nonempty question or use --chat.")

    index = Index()

    @cache
    def generator():
        return create_generator(args.backend)

    def complete(messages):
        return generator()(messages)

    def respond(question, previous=None):
        context = f"Previous question: {previous}\nFollow-up: {question}" if previous and FOLLOW_UP.search(question) else question
        matches = index.search(context, mode=args.mode, source=args.source)
        result = answer(context, matches, complete)
        print(render(result))
        if args.show_retrieval:
            print_matches(matches)
        return result

    try:
        if not args.chat:
            respond(args.question)
            return
        print("MIT first-year student guide. Use /reset to clear context or /quit to exit.")
        previous = None
        while True:
            try:
                question = input("\nQuestion> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if question == "/quit":
                break
            if question == "/reset":
                previous = None
                print("Context cleared.")
            elif question and respond(question, previous).sources:
                previous = question
    except (ImportError, ValueError) as exc:
        parser.exit(1, f"Generation error: {exc}\n")


if __name__ == "__main__":
    main()
