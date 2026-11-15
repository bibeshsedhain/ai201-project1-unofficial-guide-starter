"""Record answers and compare evidence coverage across retrieval variants."""
import argparse
import json
import re
from dataclasses import asdict
from functools import cache
from pathlib import Path

from .generation import answer, create_generator, render
from .ingest import fixed_chunks, load_chunks
from .retrieval import Index

EVAL = Path(__file__).resolve().parents[1] / "evaluation"
OUT_OF_SCOPE = "Who won the 2018 FIFA World Cup?"
MEMORY_FIRST = "Which first-year learning community did Richard join for applied design?"
MEMORY_FOLLOW_UP = "What did they build?"


def covered(matches, groups):
    hits = []
    for source, terms in groups:
        text = " ".join(match.chunk.text for match in matches if match.chunk.source_id == source)
        if all(re.search(rf"(?<![\w.]){re.escape(term)}(?!\w|\.\d)", text, re.I) for term in terms):
            hits.append([source, terms])
    return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("local", "groq"), default="local")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    questions = json.loads((EVAL / "questions.json").read_text(encoding="utf-8"))
    facts = json.loads((EVAL / "facts.json").read_text(encoding="utf-8"))
    index = Index()
    fixed = Index(chunks=load_chunks(splitter=fixed_chunks), model=index.model)

    @cache
    def generator():
        return create_generator(args.backend)

    def complete(messages):
        return generator()(messages)

    results = []
    for case in questions:
        question = case["question"]
        matches = index.search(question)
        groups = facts[case["id"]]
        alternatives = {
            "section_semantic": matches,
            "section_hybrid": index.search(question, mode="hybrid"),
            "fixed_semantic": fixed.search(question),
        }
        result = {
            **case,
            "response": render(answer(question, matches, complete)),
            "retrieval": {
                name: {"covered": covered(rows, groups), "matches": [asdict(row) for row in rows]}
                for name, rows in alternatives.items()
            },
        }
        results.append(result)
        print(f"{case['id']} {result['response']}", flush=True)

    unsupported = index.search(OUT_OF_SCOPE)
    first = index.search(MEMORY_FIRST)
    follow_up = index.search(f"Previous question: {MEMORY_FIRST}\nFollow-up: {MEMORY_FOLLOW_UP}")
    filtered = index.search(questions[2]["question"], mode="hybrid", source="my-first-week-of-classes-at-mit")
    assert filtered and all(hit.chunk.source_id == "my-first-week-of-classes-at-mit" for hit in filtered)
    report = {
        "backend": args.backend,
        "chunk_counts": {"section": len(index.chunks), "fixed": len(fixed.chunks)},
        "evaluation": results,
        "out_of_scope": {
            "question": OUT_OF_SCOPE,
            "response": render(answer(OUT_OF_SCOPE, unsupported, complete)),
            "best_distance": min(row.distance for row in unsupported),
        },
        "memory": {
            "first_question": MEMORY_FIRST,
            "first_answer": render(answer(MEMORY_FIRST, first, complete)),
            "follow_up": MEMORY_FOLLOW_UP,
            "follow_up_answer": render(answer(MEMORY_FOLLOW_UP, follow_up, complete, previous=MEMORY_FIRST)),
            "fresh_answer": render(answer(MEMORY_FOLLOW_UP, index.search(MEMORY_FOLLOW_UP), complete)),
        },
        "filtered_hybrid": [asdict(row) for row in filtered],
    }
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("out_of_scope", "memory")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
