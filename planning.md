# Project 1 Planning

This write-up was revised with Codex after the build. The [original design notes](IMPLEMENTATION.md) and [five test questions](evaluation/questions.json) were committed before the pipeline code.

## Domain

The guide is about how MIT students get through their first year. A catalog can tell you which calculus classes exist. It takes a student account to explain why someone tried three levels before finding a good fit, or what it felt like to study physics with the same small group for two semesters. Those are the kinds of questions the guide should answer, with a link back to the student who described the experience.

## Documents

The ten posts cover class choices, academic help, and first-year learning communities. Each [local note](documents) summarizes one post in short sections. The [source manifest](documents/sources.json) records where each note came from so the guide can cite the original post.

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

Keep each note section together when it fits within 420 characters, including its heading. Most sections are just two or three sentences. For example, the calculus placement section has the names of all three courses and the order Yuliya tried them. Use zero overlap because the next section can be about a different topic, such as PE or advising. If a section is too long, break it between words and repeat the heading on the next chunk.

## Retrieval Approach

Use `sentence-transformers/all-MiniLM-L6-v2` to embed the notes and questions locally. Store the normalized vectors and source details in Chroma, then retrieve the five closest chunks by cosine distance. Five gives a question room to pull from multiple posts while keeping the prompt small enough to inspect. For a larger campus guide, test how well the model handles course numbers, student abbreviations, and questions in other languages. Longer source pages would also make the model’s input limit more important. For deployment, compare local hardware and response times with API fees, network latency, and whether queries can leave the device.

## Evaluation Plan

1. **Which three multivariable calculus subjects did Yuliya try in her first semester, in order?** She started in 18.014, moved to 18.022, then settled in 18.02.
2. **In Advice for the Incoming Froshies, which mechanics option covers the same material as 8.01 at a slower pace, and in what format?** 8.01L covers the same material over a longer period in lecture format.
3. **According to Suzuko's first-week post, what were the two environmental problems in the Terrascope project and where?** Water scarcity and heat waves in the Navajo Nation.
4. **In Exploring Classes, which tool combines Firehose and CourseRoad, and what two details can students look up in MIT Subject Evaluations?** FireRoad combines Firehose and CourseRoad. Subject Evaluations shows course ratings and reported weekly homework hours.
5. **Compare the student accounts of three learning communities. What was Richard's DesignPlus project, what was Suzuko's Terrascope project, and what were the two ESG physics subjects in the guest post?** DesignPlus worked on a vertical garden in Haiti. Terrascope worked on water scarcity and heat waves in the Navajo Nation. The ESG student took 8.012 in fall and 8.022 in spring.

Check each answer for all the facts listed above. A correct subset earns partially accurate. A wrong fact or a refusal on an answerable question earns inaccurate. Ask a separate question about the World Cup to check that the guide declines a question outside the collection.

## Anticipated Challenges

1. The difference between 8.01 and 8.01L matters. Since the codes look similar, vector search may turn up the wrong course. Check the ranked passages and compare them with BM25, which can match the full code.
2. A question about three learning communities needs evidence from three posts. Several high-ranking chunks from one post could fill the five available slots before the other posts reach the prompt.
3. The posts were written in different years. A source link lets the reader see when the student had that experience and judge whether it still applies.

## AI Tool Plan

- Use Codex to help build the loader and splitter from the note format and the 420-character limit. Check the printed chunks for intact advice and a usable link to the original post.
- Use Codex to help set up MiniLM and Chroma. Check the ranking on three questions by opening the passages and looking for the requested facts. A low distance alone does not make a passage relevant.
- Use Codex to connect the model and citation renderer. Check an in-scope answer against its cited post and use the World Cup question to check refusal.

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
