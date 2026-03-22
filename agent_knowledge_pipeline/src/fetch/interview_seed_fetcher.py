from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Dict

import urllib.request
import re
from html.parser import HTMLParser
from html import unescape


SEED_URLS = [
    {
        "topic": "rag",
        "source": "LangChain RAG Docs",
        "url": "https://docs.langchain.com/oss/python/langchain/rag",
    },
    {
        "topic": "agent",
        "source": "Lilian Weng - LLM Powered Autonomous Agents",
        "url": "https://lilianweng.github.io/posts/2023-06-23-agent/",
    },
    {
        "topic": "ai_engineer",
        "source": "InterviewQuery - AI Engineer Interview Questions",
        "url": "https://www.interviewquery.com/p/ai-engineer-interview-questions",
    },
]


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self.skip = False

    def handle_data(self, data):
        if not self.skip and data and data.strip():
            self.parts.append(data.strip())


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    parser = _TextExtractor()
    parser.feed(html)
    text = unescape(" ".join(parser.parts))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_seed_materials() -> List[Dict]:
    out: List[Dict] = []
    now = datetime.now(timezone.utc).isoformat()
    for item in SEED_URLS:
        try:
            text = _fetch_text(item["url"])
        except Exception:
            text = ""
        out.append(
            {
                "topic": item["topic"],
                "source": item["source"],
                "url": item["url"],
                "text": text[:50000],
                "fetched_at": now,
            }
        )
    return out
