# The Unofficial Guide
## MIT's first year through student accounts

Ask a plain-language question about choosing subjects, getting academic support, or joining a first-year learning community at MIT. The guide answers with evidence from ten student-authored MIT Admissions blogs. The course catalog shows prerequisites and approved subjects. These accounts describe decisions that are harder to look up, such as why a student switched calculus levels or how a study group grew out of a small physics class. Each post reflects its author and time period.

[Silent demo video](demo/unofficial-guide-demo.mp4) · [Video script](demo/VIDEO_SCRIPT.md) · [Planning draft](planning.md) · [Evaluation run](evaluation/run.json)

## Run locally

Use Python 3.11. The CPU backend downloads MiniLM and a roughly 1 GB Qwen weight file on first use. It uses llama.cpp for quantized CPU inference. Installing the Python binding can require a C++ compiler, such as the Xcode Command Line Tools on macOS. Chat mode keeps the models loaded between queries.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
CMAKE_ARGS="-DGGML_METAL=OFF -DGGML_NATIVE=OFF -DGGML_ACCELERATE=OFF -DGGML_BLAS=OFF" \
  python -m pip install -r requirements-local.txt
python -m guide --chat
```

For one question from the terminal, use the positional input. For a hosted generation backend, install `requirements.txt`, copy `.env.example` to `.env`, set `GROQ_API_KEY`, and add `--backend groq`. The embedding model and vector store still run locally. The documented evaluation uses the CPU backend.

```sh
python -m guide "Which three multivariable calculus subjects did Yuliya try in her first semester, in order?" --show-retrieval
python -m guide --list-sources
python -m guide.evaluate --output evaluation/run.json
```

## Document sources

Each UTF-8 file contains curated paraphrases of relevant first-person passages from a single post. During collection, the corpus omits navigation, captions, comment widgets, and unrelated material. For ingestion, Python reads [the source manifest](documents/sources.json), splits each local file at its headings, normalizes Unicode and whitespace, decodes HTML entities, and skips empty bodies. Each generated chunk retains the original title, URL, section, and its position within the document.

- How to decide which classes to take · [Local notes](documents/how-to-pick-classes.txt) · [Original post](https://mitadmissions.org/blogs/entry/how-to-pick-classes/)
- Before you Register for Classes: Tools, Tips, and Resources · [Local notes](documents/claaass.txt) · [Original post](https://mitadmissions.org/blogs/entry/claaass/)
- 24 Things I Learned in My First Semester and a Half · [Local notes](documents/24-things-i-learned-in-my-first-semester-and-a-half.txt) · [Original post](https://mitadmissions.org/blogs/entry/24-things-i-learned-in-my-first-semester-and-a-half/)
- How I chose my classes · [Local notes](documents/how-i-chose-my-classes.txt) · [Original post](https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/)
- Advice for the Incoming Froshies · [Local notes](documents/advice-for-the-incoming-froshies.txt) · [Original post](https://mitadmissions.org/blogs/entry/advice-for-the-incoming-froshies/)
- would’ve, could’ve, should’ve · [Local notes](documents/wouldve-couldve-shouldve.txt) · [Original post](https://mitadmissions.org/blogs/entry/wouldve-couldve-shouldve/)
- [Guest Post] Reflecting on the great memories of my freshman year · [Local notes](documents/guest-post-reflecting-on-the-great-memories-of-my-freshman-year.txt) · [Original post](https://mitadmissions.org/blogs/entry/guest-post-reflecting-on-the-great-memories-of-my-freshman-year/)
- my “first” “week” of “classes” at mit · [Local notes](documents/my-first-week-of-classes-at-mit.txt) · [Original post](https://mitadmissions.org/blogs/entry/my-first-week-of-classes-at-mit/)
- Exploring Classes · [Local notes](documents/exploring-classes.txt) · [Original post](https://mitadmissions.org/blogs/entry/exploring-classes/)
- Pictures from a Month into Classes · [Local notes](documents/pictures-from-a-month-into-classes.txt) · [Original post](https://mitadmissions.org/blogs/entry/pictures-from-a-month-into-classes/)

## Chunking strategy

The production splitter caps chunks at **420 characters including the section heading**, with **0 characters of overlap**. Most source sections are two to three short sentences about one topic. Keeping a section together keeps the class number alongside the student's experience. For example, the three calculus subjects and their order travel together. Overlapping neighboring sections would mix unrelated advice, such as changing calculus levels with trying to get a spot in PE. An oversized future section splits at a word boundary and repeats its heading for context.

**Final count:** 50 chunks from 10 documents. Run `python -m guide.ingest` to inspect the complete chunk text and metadata.

## Sample chunks

**Chunk 1 — How to decide which classes to take (how-to-pick-classes:1)**

> Starting schedule. CJ suggests starting with a science GIR such as 8.01 mechanics or 18.01 calculus, an introduction to a potential major, a humanities, arts, or social sciences class, and a fourth subject from one of those groups.

**Chunk 2 — 24 Things I Learned in My First Semester and a Half (24-things-i-learned-in-my-first-semester-and-a-half:1)**

> Working together. The author recommends finding one or two people in each class to work through problem sets and ask questions with. Class group chats and a friend in each subject helped the author avoid working through everything alone.

**Chunk 3 — Advice for the Incoming Froshies (advice-for-the-incoming-froshies:1)**

> Associate advising. The author describes meeting a faculty advisor and one or more associate advisors during orientation to work out a first-semester schedule. An associate advisor can offer a student's perspective, while the faculty advisor helps with academic planning.

**Chunk 4 — [Guest Post] Reflecting on the great memories of my freshman year (guest-post-reflecting-on-the-great-memories-of-my-freshman-year:1)**

> ESG community. The blogger joined the Experimental Study Group (ESG) and took General Institute Requirements in small classes alongside other ESG students. The post mentions Friday community lunches cooked by students and a shared space where first-years could spend time.

**Chunk 5 — Exploring Classes (exploring-classes:1)**

> Long-term course planning. The author uses CourseRoad to sketch several possible multi-year class plans. FireRoad combines functions of Firehose and CourseRoad, and the author describes it as a way to lay out multiple years and see projected class times.

## Embedding model and retrieval

[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) embeds the notes and queries on the CPU. Chroma stores normalized vectors with source metadata and returns **five** results sorted by cosine distance. Lower distance indicates a closer match. The collection name fingerprints the model revision and chunk contents so edits produce a fresh index. The index is built automatically on the first query.

For production, compare local inference memory and p95 latency with the cost and network dependency of a hosted embedding API. The English MiniLM model fits these small notes. A multilingual model could improve queries from incoming international students, and a model with a longer input limit might help if the corpus adds full-length guides. Use a held-out query set with abbreviations, course codes, and multilingual paraphrases to test any replacement.

## Retrieval test results

These results show semantic search against the section index, before generation. Scores are cosine distances rounded to three decimals. The [run log](evaluation/run.json) contains full results and metadata.

### Retrieval test 1

**Query**  Which three multivariable calculus subjects did Yuliya try in her first semester, in order?

1. **Before you Register for Classes: Tools, Tips, and Resources (claaass:1)** · distance 0.182
   > Calculus placement. Yuliya tried three versions of multivariable calculus in the first semester. The author started in 18.014, transferred to 18.022, and then settled on 18.02. The experience is presented as a reason to adjust levels when the pace or format is a poor fit.
2. **Before you Register for Classes: Tools, Tips, and Resources (claaass:2)** · distance 0.524
   > Balancing technical subjects. Yuliya's first schedule packed in technical GIRs to take advantage of Pass/No Record. The plan felt overloaded within a month, and the author worked with an advisor to shed courses or move down a level. Yuliya advises leaving room to explore interests.
3. **How I chose my classes (how-i-chose-my-classes:1)** · distance 0.588
   > Three questions. The author sorts elective choices into three questions: whether the class fits their circumstances that semester, whether it will be enjoyable and engaging, and what they will gain from taking it.
4. **Before you Register for Classes: Tools, Tips, and Resources (claaass:3)** · distance 0.592
   > Switching levels. Yuliya advises contacting the instructor of the class you are moving into so they can tell you whether you need to make up material. The post gives physics and chemistry level changes as examples alongside the author's calculus changes.
5. **[Guest Post] Reflecting on the great memories of my freshman year (guest-post-reflecting-on-the-great-memories-of-my-freshman-year:2)** · distance 0.624
   > Fall and spring physics. The blogger took 8.012, a proof-oriented mechanics course, in the fall through ESG. The same five students stayed together and took 8.022 in the spring with the same professor in the same room.

**Relevance**  The top hit gives the three subject numbers in order and explicitly identifies Yuliya. Other Yuliya chunks describe workload or changing levels but lack the sequence.

### Retrieval test 2

**Query**  In Advice for the Incoming Froshies, which mechanics option covers the same material as 8.01 at a slower pace, and in what format?

1. **Advice for the Incoming Froshies (advice-for-the-incoming-froshies:4)** · distance 0.487
   > Physics with a slower pace. The author recommends 8.01L to a student who felt underprepared in physics. The post describes it as covering the same material as 8.01 over more time in a lecture format.
2. **Advice for the Incoming Froshies (advice-for-the-incoming-froshies:2)** · distance 0.628
   > Choosing calculus. The author suggests considering the 18.01A/18.02A sequence when a review of single-variable calculus would help. The post also describes moving to 18.01 if the faster format proves unsuitable.
3. **Advice for the Incoming Froshies (advice-for-the-incoming-froshies:3)** · distance 0.629
   > Chemistry options. The author describes 5.111 as introductory chemistry with more attention to liquid-state systems and 5.112 as an advanced option. The author personally enjoyed 3.091 for its focus on solid-state materials.
4. **would’ve, could’ve, should’ve (wouldve-couldve-shouldve:5)** · distance 0.763
   > Hands-on growth. The author ultimately enjoyed challenging practical work in Mechanical Engineering. Working outside their comfort zone helped Veronica better appreciate what it takes to make a design work.
5. **Before you Register for Classes: Tools, Tips, and Resources (claaass:3)** · distance 0.791
   > Switching levels. Yuliya advises contacting the instructor of the class you are moving into so they can tell you whether you need to make up material. The post gives physics and chemistry level changes as examples alongside the author's calculus changes.

**Relevance**  The top hit identifies 8.01L, compares it directly with 8.01, and gives the lecture format. Nearby chemistry and calculus hits discuss variants of introductory classes, so they are distractors.

### Retrieval test 3

**Query**  According to Suzuko's first-week post, what were the two environmental problems in the Terrascope project and where?

1. **my “first” “week” of “classes” at mit (my-first-week-of-classes-at-mit:1)** · distance 0.326
   > Terrascope project. Suzuko describes Terrascope as a first-year learning community for environmental sustainability. The cohort's group project centered on water scarcity and heat waves in the Navajo Nation.
2. **my “first” “week” of “classes” at mit (my-first-week-of-classes-at-mit:2)** · distance 0.366
   > Group project transition. Suzuko sees Terrascope as a continuation of their Discover Course 1 pre-orientation experience because both involve group work on environmental problems. The author expected to grow by tackling open-ended problems with a group.
3. **would’ve, could’ve, should’ve (wouldve-couldve-shouldve:2)** · distance 0.708
   > First-year communities. Veronica knew students who enjoyed Terrascope and DesignPlus and sees these communities as low-pressure ways to meet classmates and faculty. DesignPlus staff let Veronica join friends at weekly lunches despite being outside the group.
4. **How I chose my classes (how-i-chose-my-classes:4)** · distance 0.728
   > Using campus resources. One reason the author chose some hardware courses was access to resources that would be hard to reproduce independently, including cleanroom equipment and quantum optics hardware. Individual feedback and instructor access also mattered.
5. **Advice for the Incoming Froshies (advice-for-the-incoming-froshies:5)** · distance 0.771
   > Advising formats. The author discusses traditional advising, advising seminars, and communities such as Terrascope. A credit-bearing seminar may be appealing, but the author says to budget time for its work alongside regular classes.

**Relevance**  The top hit identifies the project and location. The second hit explains the transition from Discover Course 1 into Terrascope without giving the two requested problems. Distance alone cannot assign evidentiary support.

## Grounded generation

The LLM sees the question and the numbered retrieved passages. The system prompt tells it to output only the passage numbers that contain the requested facts and to return an empty list when evidence is missing. The application validates each number and renders the model-selected passage text verbatim from the local notes. It attaches the matching source title and URL to every passage. The app also refuses when there are zero retrieval results, when the closest result has cosine distance above 0.72, or when the model returns invalid or empty selections. The cutoff is a heuristic for this corpus. A valid ID guarantees traceable text. Its relevance still depends on whether the model chose the right passage.

The local evaluation used [Qwen2.5-1.5B-Instruct, Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) via llama.cpp on CPU. The optional hosted path uses a configurable Groq model.

## Example responses

**Query**  Which three multivariable calculus subjects did Yuliya try in her first semester, in order?

```text
Answer: Yuliya tried three versions of multivariable calculus in the first semester. The author started in 18.014, transferred to 18.022, and then settled on 18.02. The experience is presented as a reason to adjust levels when the pace or format is a poor fit. [1]
Yuliya's first schedule packed in technical GIRs to take advantage of Pass/No Record. The plan felt overloaded within a month, and the author worked with an advisor to shed courses or move down a level. Yuliya advises leaving room to explore interests. [1]
The author sorts elective choices into three questions: whether the class fits their circumstances that semester, whether it will be enjoyable and engaging, and what they will gain from taking it. [2]
Sources:
  [1] Before you Register for Classes: Tools, Tips, and Resources — https://mitadmissions.org/blogs/entry/claaass/
  [2] How I chose my classes — https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/
```

**Query**  According to Suzuko's first-week post, what were the two environmental problems in the Terrascope project and where?

```text
Answer: Suzuko describes Terrascope as a first-year learning community for environmental sustainability. The cohort's group project centered on water scarcity and heat waves in the Navajo Nation. [1]
Suzuko sees Terrascope as a continuation of their Discover Course 1 pre-orientation experience because both involve group work on environmental problems. The author expected to grow by tackling open-ended problems with a group. [1]
Sources:
  [1] my “first” “week” of “classes” at mit — https://mitadmissions.org/blogs/entry/my-first-week-of-classes-at-mit/
```

**Query**  Who won the 2018 FIFA World Cup?

```text
Answer: I don't have enough information in the collected student sources to answer that.
```

## Query interface

Enter a question as a quoted terminal argument, or launch `--chat` for the `Question>` prompt. The **Answer** field shows one or more passages with inline source numbers. The **Sources** field maps those numbers to titles and URLs. Use `--show-retrieval` to display all returned passages and cosine distances. You can also set `--source` to a single post slug or `--mode hybrid` to combine semantic and keyword ranks. In chat, `/reset` clears the previous question and `/quit` exits.

```text
$ python -m guide "In Advice for the Incoming Froshies, which mechanics option covers the same material as 8.01 at a slower pace, and in what format?"
Answer: The author recommends 8.01L to a student who felt underprepared in physics. The post describes it as covering the same material as 8.01 over more time in a lecture format. [1]
Sources:
  [1] Advice for the Incoming Froshies — https://mitadmissions.org/blogs/entry/advice-for-the-incoming-froshies/
```

## Evaluation report

The five questions and expected answers were recorded before pipeline implementation. Each expected answer is verifiable against the specific passages identified in [the evaluation inputs](evaluation/questions.json). Responses below are from the actual CPU run with semantic top-5 and section chunking.

### Q1. Which three multivariable calculus subjects did Yuliya try in her first semester, in order?

**Expected answer**  She started in 18.014, moved to 18.022, then settled in 18.02.

**System response**

```text
Answer: Yuliya tried three versions of multivariable calculus in the first semester. The author started in 18.014, transferred to 18.022, and then settled on 18.02. The experience is presented as a reason to adjust levels when the pace or format is a poor fit. [1]
Yuliya's first schedule packed in technical GIRs to take advantage of Pass/No Record. The plan felt overloaded within a month, and the author worked with an advisor to shed courses or move down a level. Yuliya advises leaving room to explore interests. [1]
The author sorts elective choices into three questions: whether the class fits their circumstances that semester, whether it will be enjoyable and engaging, and what they will gain from taking it. [2]
Sources:
  [1] Before you Register for Classes: Tools, Tips, and Resources — https://mitadmissions.org/blogs/entry/claaass/
  [2] How I chose my classes — https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/
```

**Retrieval quality**  Relevant (1/1 evidence groups).

**Accuracy judgment**  Accurate. All three subjects appear in the correct order. The answer also returns unrelated background about schedules and electives.

### Q2. In Advice for the Incoming Froshies, which mechanics option covers the same material as 8.01 at a slower pace, and in what format?

**Expected answer**  8.01L covers the same material over a longer period in lecture format.

**System response**

```text
Answer: The author recommends 8.01L to a student who felt underprepared in physics. The post describes it as covering the same material as 8.01 over more time in a lecture format. [1]
Sources:
  [1] Advice for the Incoming Froshies — https://mitadmissions.org/blogs/entry/advice-for-the-incoming-froshies/
```

**Retrieval quality**  Relevant (1/1 evidence groups).

**Accuracy judgment**  Accurate. The reply gives 8.01L, the slower pace, and the lecture format from the requested post.

### Q3. According to Suzuko's first-week post, what were the two environmental problems in the Terrascope project and where?

**Expected answer**  Water scarcity and heat waves in the Navajo Nation.

**System response**

```text
Answer: Suzuko describes Terrascope as a first-year learning community for environmental sustainability. The cohort's group project centered on water scarcity and heat waves in the Navajo Nation. [1]
Suzuko sees Terrascope as a continuation of their Discover Course 1 pre-orientation experience because both involve group work on environmental problems. The author expected to grow by tackling open-ended problems with a group. [1]
Sources:
  [1] my “first” “week” of “classes” at mit — https://mitadmissions.org/blogs/entry/my-first-week-of-classes-at-mit/
```

**Retrieval quality**  Relevant (1/1 evidence groups).

**Accuracy judgment**  Accurate. The response identifies both environmental problems and the location. The extra pre-orientation context is supported.

### Q4. In Exploring Classes, which tool combines Firehose and CourseRoad, and what two details can students look up in MIT Subject Evaluations?

**Expected answer**  FireRoad combines Firehose and CourseRoad. Subject Evaluations shows course ratings and reported weekly homework hours.

**System response**

```text
Answer: The author uses CourseRoad to sketch several possible multi-year class plans. FireRoad combines functions of Firehose and CourseRoad, and the author describes it as a way to lay out multiple years and see projected class times. [1]
Sources:
  [1] Exploring Classes — https://mitadmissions.org/blogs/entry/exploring-classes/
```

**Retrieval quality**  Relevant (2/2 evidence groups).

**Accuracy judgment**  Partially accurate. The reply identifies FireRoad but omits ratings and weekly homework hours. Both required chunks were retrieved, including the Subject Evaluations chunk at rank 1, so generation omitted available evidence.

### Q5. Compare the student accounts of three learning communities. What was Richard's DesignPlus project, what was Suzuko's Terrascope project, and what were the two ESG physics subjects in the guest post?

**Expected answer**  DesignPlus worked on a vertical garden in Haiti. Terrascope worked on water scarcity and heat waves in the Navajo Nation. The ESG student took 8.012 in fall and 8.022 in spring.

**System response**

```text
Answer: The blogger often worked on physics problem sets with the four other 8.012 students. They also started getting a meal together every week and got to know one another outside class. [1]
The blogger joined the Experimental Study Group (ESG) and took General Institute Requirements in small classes alongside other ESG students. The post mentions Friday community lunches cooked by students and a shared space where first-years could spend time. [1]
Food-accessibility peers, the DesignPlus cohort, and the Chocolate City living community helped Richard find a place at MIT. Richard describes exploring makerspaces with the DesignPlus group. [2]
The blogger took 8.012, a proof-oriented mechanics course, in the fall through ESG. The same five students stayed together and took 8.022 in the spring with the same professor in the same room. [1]
One reason the author chose some hardware courses was access to resources that would be hard to reproduce independently, including cleanroom equipment and quantum optics hardware. Individual feedback and instructor access also mattered. [3]
Sources:
  [1] [Guest Post] Reflecting on the great memories of my freshman year — https://mitadmissions.org/blogs/entry/guest-post-reflecting-on-the-great-memories-of-my-freshman-year/
  [2] Pictures from a Month into Classes — https://mitadmissions.org/blogs/entry/pictures-from-a-month-into-classes/
  [3] How I chose my classes — https://mitadmissions.org/blogs/entry/how-i-chose-my-classes/
```

**Retrieval quality**  Partially relevant (1/3 evidence groups).

**Accuracy judgment**  Partially accurate. The reply gives the ESG physics courses and term order but omits both project descriptions. Two evidence passages were outside the retrieval budget.

## Failure case analysis

Question 5 requires evidence from three posts. Its default cosine top five contained three passages from the ESG guest post, including the right physics sequence at rank 4 (distance 0.494). The Terrascope project was at rank 12 (0.608) and Richard's DesignPlus project was at rank 13 (0.617). Neither was available to the model at k=5. The top five included a general student communities passage mentioning DesignPlus, which lacked the Haiti project. This is a retrieval coverage failure. The generated answer recovered the ESG sequence and included some unrelated student-life details, leaving two of the three requested parts unanswered.

Split comparison questions into one retrieval query per community, combine the distinct results, and rerun the same evaluation. Simply increasing k to thirteen would add many unrelated passages.

## Stretch features

### Hybrid search

Use `--mode hybrid`. BM25 tokenization keeps dotted course codes together. Each positive keyword hit and each semantic hit contributes `1 / (10 + rank)`. Both signals have equal weight. At the same k, topical semantic search covered **6/8** evidence groups and topical hybrid covered **7/8**. Hybrid moved the Terrascope and DesignPlus project passages into the top five for Q5, but dropped the ESG physics sequence. The comparison is based on retrieved evidence groups, with the final answer evaluation above using semantic search.

### Chunking strategy comparison

The fixed alternative generated **70** windows of **220 characters** with **45 characters** of overlap. Section-aware splitting generated **50** chunks. Both used the same model, cosine ranking, and five questions. Mark a group covered when every predeclared fact string occurs across the top five passages from its expected source. Totals were **6/8** for section chunks and **6/8** for fixed windows. The section approach put all the slower mechanics evidence in the top chunk for Q2. The fixed approach still recovered the evidence, but its top hit begins inside the chemistry section and only reaches the start of the physics note. The second-ranked window contains the actual mechanics facts. The aggregate is a tie on this small set. Topical boundaries preserve a readable standalone citation and avoid the extra embeddings.

### Source metadata filter

```sh
python -m guide --mode hybrid --source my-first-week-of-classes-at-mit "What did the Terrascope team work on?" --show-retrieval
```

The evaluator asserted that all **5** results from a filtered hybrid query had the selected source ID. Chroma constrains its candidates using source metadata. BM25 scores only chunks with that same ID.

### Conversational memory

The CLI retains the last answered question for follow-up phrases such as “What did they build?” The follow-up gets freshly retrieved evidence, and the LLM sees the previous question only for reference resolution. In the diagnostic run, adding Richard's previous question moved the DesignPlus garden passage from rank 3 (0.701) to rank 1 (0.447). With remembered context, the answer cited Richard’s Haiti garden. The standalone question selected Discover Course 1 projects instead.

```text
Question> Which first-year learning community did Richard join for applied design?
Answer: Richard describes learning applied design through DesignPlus, a first-year learning community. The author was working with other students on a vertical garden project in Haiti. [1]
Sources:
  [1] Pictures from a Month into Classes — https://mitadmissions.org/blogs/entry/pictures-from-a-month-into-classes/

Question> What did they build?
Answer: Richard describes learning applied design through DesignPlus, a first-year learning community. The author was working with other students on a vertical garden project in Haiti. [1]
Sources:
  [1] Pictures from a Month into Classes — https://mitadmissions.org/blogs/entry/pictures-from-a-month-into-classes/
```


## Spec reflection

The section-anchored design made source IDs a required part of each chunk. That choice let the CLI, citations, filter, and evaluation share the same provenance without matching on titles. In the pre-code design, the model selected individual sentences. A pilot on the calculus question selected the lead-in while skipping the sentence that held the course numbers. The final pipeline lets the model select a complete topical passage. This preserves nearby details at the cost of occasionally returning extra background. The 0.72 distance gate was also added during implementation to give clearly unrelated queries a deterministic refusal.

## AI Usage


1. AI helped clarify the scope and plan the coding implmentation
2. it helped me figure out and map the exact delivarables.
3. it helped me create a video script and final reports 
