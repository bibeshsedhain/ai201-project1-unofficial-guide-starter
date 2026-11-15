"""LLM-generated extracts with deterministic evidence validation and citations."""
import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REFUSAL = "I don't have enough information in the collected student sources to answer that."
QWEN_REPO = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
QWEN_REVISION = "91cad51170dc346986eccefdc2dd33a9da36ead9"
QWEN_FILE = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
SYSTEM = """You answer questions about MIT using only the candidate passages.
Produce a JSON object with the single field "passages", an array of passage numbers.
For a single question select the best passage that contains the specific requested facts.
For a multi-part question select one passage for each part that the evidence supports.
A passage about the same topic is irrelevant if it does not state a requested fact.
If the question specifies a source, select evidence from that source only.
Use the previous question only to resolve a reference in the current question.
Return {"passages": []} when no passage answers the question."""


@dataclass(frozen=True)
class Answer:
    text: str
    sources: tuple


def create_generator(backend):
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    if backend == "groq":
        from groq import Groq

        key = os.environ.get("GROQ_API_KEY")
        if not key or key == "your_key_here":
            raise ValueError("Set GROQ_API_KEY in .env to use --backend groq.")
        model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        client = Groq(api_key=key, timeout=30.0)

        def complete(messages):
            result = client.chat.completions.create(
                model=model, messages=messages, temperature=0,
                max_completion_tokens=100, response_format={"type": "json_object"},
            )
            return result.choices[0].message.content or ""

        return complete

    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    path = Path(os.environ.get("GUIDE_GGUF") or hf_hub_download(
        QWEN_REPO, QWEN_FILE, revision=QWEN_REVISION,
    )).expanduser().absolute()
    llm = Llama(
        model_path=str(path), chat_format="chatml", n_ctx=4096,
        n_threads=4, n_gpu_layers=0, verbose=False,
    )

    def complete(messages):
        result = llm.create_chat_completion(
            messages=messages, max_tokens=40, temperature=0,
            response_format={"type": "json_object"},
        )
        return result["choices"][0]["message"]["content"] or ""

    return complete


def answer(question, matches, complete, *, previous=None):
    if not matches or min(match.distance for match in matches) > 0.72:
        return Answer(REFUSAL, ())

    passages = "\n".join(
        f"[{number}] {match.chunk.title} — {match.chunk.text}"
        for number, match in enumerate(matches, 1)
    )
    prompt = f"Question: {question}\nPassages:\n{passages}\nJSON answer:"
    if previous:
        prompt = f"Previous question: {previous}\n{prompt}"
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt},
    ]
    try:
        result = json.loads(complete(messages))
    except json.JSONDecodeError:
        return Answer(REFUSAL, ())
    ids = result.get("passages") if isinstance(result, dict) else None
    if not isinstance(ids, list) or not ids or any(type(x) is not int or not 1 <= x <= len(matches) for x in ids):
        return Answer(REFUSAL, ())

    source_numbers = {}
    sources = []
    lines = []
    for number in dict.fromkeys(ids):
        chunk = matches[number - 1].chunk
        passage = chunk.text.removeprefix(f"{chunk.section}. ")
        if chunk.source_id not in source_numbers:
            sources.append((chunk.title, chunk.url))
            source_numbers[chunk.source_id] = len(sources)
        lines.append(f"{passage} [{source_numbers[chunk.source_id]}]")
    return Answer("\n".join(lines), tuple(sources))


def render(result):
    lines = [f"Answer: {result.text}"]
    if result.sources:
        lines.append("Sources:")
        lines.extend(f"  [{i}] {title} — {url}" for i, (title, url) in enumerate(result.sources, 1))
    return "\n".join(lines)
