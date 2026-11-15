# Project 1 Planning

This Codex-assisted working draft is based on the [design notes committed before implementation](IMPLEMENTATION.md). The course asks the student to write the final plan in their own words. The draft records the actual project decisions and is available for that review.

## Domain

The domain is MIT students' first-year academic transition. Course catalogs show what is offered, but students often use peer advice to decide how to pace technical requirements, seek help, and pick a first-year community. The guide makes those individual experiences easy to find and trace back to the writer.

## Documents

The local files in [documents](documents) contain curated paraphrases of the first-person experiences in these posts. The source manifest maps each local file to its original URL.

- How to decide which classes to take — [local notes](documents/how-to-pick-classes.txt) · [original post](https://mitadmissions.org/blogs/entry/how-to-pick-classes/)
- Before you Register for Classes: Tools, Tips, and Resources — [local notes](documents/claaass.txt) · [original post](https://mitadmissions.org/blogs/entry/claaass/)
- 24 Things I Learned in My First Semester and a Half — [local notes](documents/24-things-i-learned-in-my-first-semester-and-a-half.txt) · [original post](https://mitadmissions.org/blogs/entry/24-things-i-learned-in-my-first-semester-and-a-half/)
- How I chose my classes — [local notes](documents/how-i-chose-my-classes.txt) · [original post](https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/)
- Advice for the Incoming Froshies — [local notes](documents/advice-for-the-incoming-froshies.txt) · [original post](https://mitadmissions.org/blogs/entry/advice-for-the-incoming-froshies/)
- would’ve, could’ve, should’ve — [local notes](documents/wouldve-couldve-shouldve.txt) · [original post](https://mitadmissions.org/blogs/entry/wouldve-couldve-shouldve/)
- [Guest Post] Reflecting on the great memories of my freshman year — [local notes](documents/guest-post-reflecting-on-the-great-memories-of-my-freshman-year.txt) · [original post](https://mitadmissions.org/blogs/entry/guest-post-reflecting-on-the-great-memories-of-my-freshman-year/)
- my “first” “week” of “classes” at mit — [local notes](documents/my-first-week-of-classes-at-mit.txt) · [original post](https://mitadmissions.org/blogs/entry/my-first-week-of-classes-at-mit/)
- Exploring Classes — [local notes](documents/exploring-classes.txt) · [original post](https://mitadmissions.org/blogs/entry/exploring-classes/)
- Pictures from a Month into Classes — [local notes](documents/pictures-from-a-month-into-classes.txt) · [original post](https://mitadmissions.org/blogs/entry/pictures-from-a-month-into-classes/)

## Chunking Strategy

Use a 420-character cap, including the section title, and 0 characters of overlap. Each note section describes a single class decision or experience, usually in two to three sentences. Retaining the section heading preserves the topic, and a 420-character ceiling also leaves room for the encoder's tokenization. Copying text across section boundaries would blend unrelated subjects such as calculus and PE. If a future section exceeds 420 characters, split on a word boundary and repeat its heading.

## Retrieval Approach

Use sentence-transformers/all-MiniLM-L6-v2 locally. Store normalized embeddings and source metadata in a Chroma cosine collection. Retrieve the top five chunks. Those five leave room for multi-source questions without sending the full corpus into generation. In production, compare recall on MIT abbreviations and course numbers, performance on multilingual questions, and truncation rates on longer pages. A hosted embedding API can simplify scaling and multilingual coverage, with per-request cost, network latency and external data handling. A local model can keep queries on-device but needs its own hardware and capacity planning.

## Evaluation Plan

1. **Which three multivariable calculus subjects did Yuliya try in her first semester, in order?** She started in 18.014, moved to 18.022, then settled in 18.02.
2. **In Advice for the Incoming Froshies, which mechanics option covers the same material as 8.01 at a slower pace, and in what format?** 8.01L covers the same material over a longer period in lecture format.
3. **According to Suzuko's first-week post, what were the two environmental problems in the Terrascope project and where?** Water scarcity and heat waves in the Navajo Nation.
4. **In Exploring Classes, which tool combines Firehose and CourseRoad, and what two details can students look up in MIT Subject Evaluations?** FireRoad combines Firehose and CourseRoad. Subject Evaluations shows course ratings and reported weekly homework hours.
5. **Compare the student accounts of three learning communities. What was Richard's DesignPlus project, what was Suzuko's Terrascope project, and what were the two ESG physics subjects in the guest post?** DesignPlus worked on a vertical garden in Haiti. Terrascope worked on water scarcity and heat waves in the Navajo Nation. The ESG student took 8.012 in fall and 8.022 in spring.

A response is accurate when it gives every requested fact, partially accurate when it gives some supported facts, and inaccurate when it gives a wrong fact or refuses an answerable question. An extra out-of-scope probe checks refusal.

## Anticipated Challenges

1. Course codes such as 8.01 and 8.01L differ by one character. Dense similarity could rank a passage about the wrong course above the evidence. Inspect retrieval scores and later compare with BM25 that retains course codes.
2. A comparison of three learning communities needs passages from three authors. A fixed top-five budget may favor two well-matched sources and leave the third outside the prompt.
3. Student experiences span different years. Preserve authorship and evidence links so a historical anecdote can be read in context.

## AI Tool Plan

- Give Codex the source manifest, the section format, and the letter of the chunking requirement. Ask for a loader and chunker. Use the emitted JSON to inspect lengths and confirm the original URLs survive.
- Give Codex the top-five requirement and the evaluation queries. Ask for a persistent Chroma index and inspect the three retrieval traces before wiring up the generation model.
- Give Codex the evidence-only requirement and ask it to generate an extractive answer with validated source IDs. Review the exact evidence sentences for a supported answer and an unsupported question.

## Architecture

```text
Ingest (UTF-8 notes + JSON manifest)
   -> Chunk (Python section splitter)
   -> Embed and store (MiniLM + persistent Chroma)
   -> Retrieve (cosine top five)
   -> Generate (Qwen Instruct or Groq + Python citation validation)
```

## Stretch plan

1. **Hybrid search.** Add BM25 over the same chunks and combine dense and sparse ranks using equal-weight reciprocal rank fusion. Preserve exact dotted course codes. Compare semantic-only and hybrid at the same k on the predeclared five questions. Count evidence groups covered and report cases that improve or regress.
2. **Chunking comparison.** Implement a second splitter using 220-character windows with 45-character overlap across sections in each document. Use the same model, queries and top five results. Compute evidence group coverage using named source IDs and predeclared fact strings; a group may be recovered from content in multiple retrieved windows from that source.
3. **Metadata filtering.** Add a source slug option. Restrict Chroma and BM25 candidates before ranking, and verify that unselected source URLs cannot appear in the retrieved context.
4. **Conversational memory.** Add an interactive terminal session. Use the last answered query as optional retrieval context for follow-up wording and support a reset command. Re-run retrieval on follow-ups and treat the previous question as context only.
