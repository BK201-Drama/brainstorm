from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Dict

import urllib.request
import re


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
        "topic": "agentic",
        "source": "ProjectPro - Agentic Workflows",
        "url": "https://www.projectpro.io/article/agentic-workflows/1092",
    },
]


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    html = re.sub(r"<script[\\s\\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\\s\\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\\s+", " ", text).strip()
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
                "text": text[:30000],
                "fetched_at": now,
            }
        )
    return out
