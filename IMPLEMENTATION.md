# Implementation notes

These Codex-authored notes record design inputs for the reference implementation. The course reserves [planning.md](planning.md) for the student's own spec.

## Domain and inputs

The guide covers starting academic life at MIT from a student perspective. Official schedules and degree charts list requirements. Peer accounts explain how students pick classes, use office hours, and experience small learning communities. [The source manifest](documents/sources.json) identifies ten first-person posts and the local notes linked to each.

## Baseline design

```text
UTF-8 source notes + JSON manifest (Python)
  -> section-based chunks (Python)
  -> embeddings (all-MiniLM-L6-v2) + persistent Chroma cosine index
  -> top 5 by cosine distance (Chroma)
  -> evidence-only response (Qwen 2.5 Instruct or Groq) -> terminal
```

- Chunk at the section headings. Each compact note is already one topic. Cap each chunk at 420 characters including the heading and use 0 characters of overlap because consecutive sections usually describe different topics. Split longer sections at word boundaries and retain their heading. Keep the source title, URL, and ordinal with every chunk.
- Start with cosine top-5. Five chunks are enough to compare a few short notes while limiting distractors. Use the English all-MiniLM-L6-v2 model locally. A larger context window would matter for longer material. For production, compare accuracy on course numbers and multilingual paraphrases, memory and hardware cost for local inference, and per-request cost, privacy, and p95 latency for an API.
- Give the LLM the query and labeled retrieved passages. Have it generate an extractive answer using only complete sentences copied from those passages. Validate the source and exact sentence before rendering citations. Refuse when there is no supporting evidence.
- Keep the CLI available as a single command for repeatable evaluation.

## Expected failure modes

- Similar-sounding course numbers can be near neighbors in embedding space. Returning a passage about a different physics course can yield a confident but contextually wrong answer.
- Several posts use first-person language and reflect different years. Dropping titles or mixing examples across authors can turn a single author's experience into an apparent rule.
- Multi-source questions can need evidence for two or more parts. One subject may occupy most of the top five and leave the generation model with incomplete context.

## Evaluation inputs

The five questions and their independently checked expected answers live in [evaluation/questions.json](evaluation/questions.json). Judge a response accurate when it gives every requested fact, partially accurate when it gives supported facts but omits a requested part, and inaccurate when it gives a wrong fact or refuses an answerable query. Record the first relevant result rank and the retrieved chunks used to diagnose any failure.

## AI review prompts for the student

- Ingestion and chunking. Give the assistant the source manifest and the chunking rules from your own plan. Ask it to explain how it preserves source identity and handles a long section. Compare printed chunks against the notes and decide which boundaries to keep.
- Generation. Give the assistant the grounding requirement and the expected answer format. Ask how citations are validated. Run an in-scope question and an unsupported one, inspect the evidence, and direct a revision if the output makes an unsupported claim.
