"""Turn the saved source notes into source-addressable chunks."""
import html
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "documents"
MAX_CHARS = 420
HEADING = re.compile(r"^# ([^\n]+)\n", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    id: str
    source_id: str
    title: str
    url: str
    section: str
    position: int
    text: str

    @property
    def evidence_key(self):
        return f"{self.source_id}|{self.section}"


def clean(text):
    text = unicodedata.normalize("NFC", html.unescape(text))
    return " ".join(text.split())


def sections(raw):
    headings = list(HEADING.finditer(raw))
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(raw)
        body = clean(raw[heading.end():end])
        if body:
            yield clean(heading[1]), body


def section_chunks(items):
    for heading, body in items:
        available = MAX_CHARS - len(heading) - 2
        if available <= 0:
            raise ValueError(f"Section heading exceeds the chunk budget: {heading}")
        while len(body) > available:
            split = body.rfind(" ", 0, available + 1)
            split = split if split > 0 else available
            yield heading, f"{heading}. {body[:split]}"
            body = body[split:].lstrip()
        yield heading, f"{heading}. {body}"


def load_chunks(corpus=CORPUS, splitter=section_chunks):
    manifest = json.loads((corpus / "sources.json").read_text(encoding="utf-8"))
    seen = set()
    chunks = []
    for source in manifest:
        if source["id"] in seen:
            raise ValueError(f"Duplicate source ID: {source['id']}")
        seen.add(source["id"])
        raw = (corpus / source["file"]).read_text(encoding="utf-8-sig")
        parts = list(splitter(sections(raw)))
        if not parts:
            raise ValueError(f"No sections found in {source['file']}")
        for position, (heading, body) in enumerate(parts, start=1):
            chunks.append(Chunk(
                f"{source['id']}:{position}", source["id"], source["title"],
                source["url"], heading, position, body,
            ))
    return chunks


if __name__ == "__main__":
    chunks = load_chunks()
    print(json.dumps([asdict(chunk) for chunk in chunks], ensure_ascii=False, indent=2))
