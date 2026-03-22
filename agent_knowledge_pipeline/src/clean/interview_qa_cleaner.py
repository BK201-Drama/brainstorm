from __future__ import annotations

from typing import List, Dict
import re


# 只抽“独立问句”，避免拼接噪音
PATTERNS = [
    r"(?:^|[\.!。！？]\s+)(How\s(?:would|do|can|to)[^?]{15,170}\?)",
    r"(?:^|[\.!。！？]\s+)(What\s[^?]{15,170}\?)",
    r"(?:^|[\.!。！？]\s+)(Why\s[^?]{15,170}\?)",
    r"(?:^|[\.!。！？]\s+)(When\s[^?]{15,170}\?)",
    r"(?:^|[\.!。！？]\s+)(Can\s[^?]{15,170}\?)",
]

KW = ("rag", "retrieval", "langchain", "agent", "agentic", "search", "tool", "llm", "ai", "transformer")
BAD = ("projectpro", "start free", "related blogs", "cookie", "login", "pricing", "{{", "}}")


def _norm(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def _extract_questions(text: str) -> list[tuple[str, int]]:
    found = []
    for p in PATTERNS:
        for m in re.finditer(p, text):
            q = _norm(m.group(1).strip('"“”'))
            found.append((q, m.start(1)))
    found.sort(key=lambda x: x[1])
    return found


def build_interview_qa(seed_materials: List[Dict], max_per_source: int = 40) -> List[Dict]:
    out: List[Dict] = []

    for s in seed_materials:
        topic = s.get("topic", "general")
        source = s.get("source", "unknown")
        url = s.get("url", "")
        text = _norm(s.get("text", ""))
        if not text:
            continue

        qs = _extract_questions(text)
        count = 0
        for q, pos in qs:
            q_low = q.lower()
            if any(b in q_low for b in BAD):
                continue
            if len(q) < 20 or len(q) > 180:
                continue

            if topic != "ai_engineer" and not any(k in q_low for k in KW):
                continue
            if topic == "ai_engineer" and not any(k in q_low for k in ("agent", "rag", "retrieval", "search", "llm", "transformer", "ai")):
                continue

            tail = text[pos + len(q): pos + len(q) + 450]
            a = ""
            for sent in re.split(r"(?<=[\.!。！？])\s+", tail):
                sent = _norm(sent)
                if 25 <= len(sent) <= 320 and "?" not in sent and "？" not in sent and not any(b in sent.lower() for b in BAD):
                    a = sent
                    break

            out.append(
                {
                    "topic": topic,
                    "question": q,
                    "answer": a,
                    "source": source,
                    "source_url": url,
                    "extracted": True,
                    "tags": ["interview", "extracted", topic],
                }
            )
            count += 1
            if count >= max_per_source:
                break

    uniq = {}
    for x in out:
        uniq.setdefault(x["question"], x)
    return list(uniq.values())
