import json
import re
from pathlib import Path


SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"<[^>]+>", " ", text)  # 粗略去 html 标签
    text = SPACE_RE.sub(" ", text).strip()
    return text


def _is_excluded(text: str, exclude_keywords: list[str]) -> bool:
    low = text.lower()
    return any(k.lower() in low for k in exclude_keywords)


def _prefer_score(text: str, prefer_keywords: list[str]) -> int:
    low = text.lower()
    return sum(1 for k in prefer_keywords if k.lower() in low)


def clean_items(
    items: list[dict],
    exclude_keywords: list[str] | None = None,
    prefer_keywords: list[str] | None = None,
) -> list[dict]:
    exclude_keywords = exclude_keywords or []
    prefer_keywords = prefer_keywords or []

    out = []
    for x in items:
        title = normalize_text(x.get("title", ""))
        summary = normalize_text(x.get("summary", ""))
        if not title:
            continue

        full_text = f"{title} {summary}"
        if _is_excluded(full_text, exclude_keywords):
            continue

        out.append(
            {
                "source": x.get("source", ""),
                "title": title,
                "link": x.get("link", ""),
                "summary": summary,
                "published": x.get("published", ""),
                "fetched_at": x.get("fetched_at", ""),
                "tags": ["agent", "八股"],
                "score": _prefer_score(full_text, prefer_keywords),
            }
        )

    out.sort(key=lambda i: i.get("score", 0), reverse=True)
    return out


def save_clean(items: list[dict], out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
