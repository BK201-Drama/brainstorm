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

BAD = ("projectpro", "start free", "related blogs", "cookie", "login", "pricing", "{{", "}}")

# 强过滤：只保留四类
TOPIC_KEYWORDS = {
    "rag": ("rag", "retrieval-augmented", "vector search", "embedding", "rerank", "chunk"),
    "langchain": ("langchain", "lcel", "runnable", "langgraph", "retriever"),
    "agent": (" ai agent", "agent ", "tool calling", "function calling", "react agent", "planner"),
    "agentic_search": ("agentic search", "multi-hop", "search loop", "query planning", "evidence retrieval"),
}

STRICT_CORE = ("rag", "langchain", "agent", "agentic", "llm", "vector search", "embedding", "retrieval-augmented", "tool calling", "transformer", "retrieval")


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


def _has_kw(text: str, kw: str) -> bool:
    if " " in kw or "-" in kw:
        return kw in text
    return re.search(rf"\b{re.escape(kw)}\b", text) is not None


def _classify_topic(q_low: str) -> str | None:
    if not any(_has_kw(q_low, k) for k in STRICT_CORE):
        return None
    for t, kws in TOPIC_KEYWORDS.items():
        if any(_has_kw(q_low, k) for k in kws):
            return t
    return None


def build_interview_qa(seed_materials: List[Dict], max_per_source: int = 40) -> List[Dict]:
    out: List[Dict] = []

    for s in seed_materials:
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

            topic = _classify_topic(q_low)
            if not topic:
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
                    "tags": ["interview", "extracted", topic, "strict_filtered"],
                }
            )
            count += 1
            if count >= max_per_source:
                break

    uniq = {}
    for x in out:
        uniq.setdefault(x["question"], x)
    return list(uniq.values())
