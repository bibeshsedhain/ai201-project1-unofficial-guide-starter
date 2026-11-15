# Demo video script

Use this script to record your own voice walkthrough. The prompts and evidence come from the running guide, and the timestamps are approximate.

## 0:00 — The Unofficial Guide

**On screen**  Open the repository README and show the pipeline overview.

The Unofficial Guide answers questions about starting academic life at M I T. The sources are ten first-person student blogs. A course catalog can show which subjects exist, but students share the practical decisions: which level felt right, where they got help, and what learning communities were like. This walkthrough uses captured output from the running guide.

## 0:23 — A calculus placement question

**On screen**  Run the displayed command. Point to the answer and its numbered source, then show the top result using --show-retrieval.

First, I ask which calculus subjects Yuliya tried and in what order. The first retrieved chunk keeps the three course numbers together under the calculus placement heading. That makes it a strong retrieval match. The answer attaches a source number and prints the original post link, so someone else can verify the sequence independently. Lower cosine distance means a closer match. These scores compare passages for retrieval and do not grade the answer.

## 0:53 — The slower mechanics option

**On screen**  Run the displayed command. Point to the answer and its numbered source, then show the top result using --show-retrieval.

Now I ask a question where one character matters. The source describes eight oh one L as covering the material from eight oh one over more time, in a lecture format. The code and format are in the same topical chunk. The citation identifies the author’s post, so a viewer can see the advice in its original context.

## 1:14 — What Terrascope worked on

**On screen**  Run the displayed command. Point to the answer and its numbered source, then show the top result using --show-retrieval.

Next, I ask about Suzuko’s Terrascope project. This question needs two environmental problems plus a location. The strongest result contains water scarcity and heat waves in the Navajo Nation. The application renders the model’s chosen passage and assigns its citation. That keeps the answer traceable to this particular student account.

## 1:37 — A case that needs several sources

**On screen**  Run question 5. Then open its retrieval trace in evaluation/run.json and compare it with the expected facts in the README.

Question five is where the system struggles. It asks about three different posts at once. The guide recovers the two E S G physics courses, but it cannot name the two projects from the retrieved evidence. The Terrascope passage is twelfth, and the Design Plus project is thirteenth. Neither reached the five-passage prompt. Separate retrieval for each community could address that coverage gap.

## 2:03 — Unsupported question

**On screen**  Run the World Cup question and show the refusal.

The corpus covers an academic transition, so it has no evidence about the World Cup winner. This question shows how the guide responds when that evidence is missing. There are no source numbers in a refusal, because no source supports an answer. Related questions still need real evidence. A citation only means the passage can be traced back, so relevance still matters.

## 2:27 — Reading the evaluation

**On screen**  Open README.md at Evaluation report. Compare the question, expected answer, actual response, and judgment for each row.

The README lists all five questions, what a correct answer needed to contain, and the response the system actually gave. Three answers get all the requested facts. Two are partial. Question four found both source passages in retrieval, but the generation step left out part of the answer. Question five had insufficient retrieval coverage. Looking at both traces helps distinguish the two failures.

## 2:53 — Stretch checks and reproduction

**On screen**  Show evaluation/run.json and the CLI options. Point to the video and evaluation links in README.md.

The project also compares hybrid retrieval and fixed windows against the same semantic baseline. The source filter narrows candidate passages before ranking, and the chat session can carry a previous question into a follow-up. The evaluation command reruns the answers and records the evidence. Open the README for the setup, individual results, limitations, and bonus comparisons. The raw run log also records all five returned chunks for each retrieval strategy so someone else can check the comparison directly.

**Estimated running time**  3:27
