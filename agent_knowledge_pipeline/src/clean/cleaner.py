import json
import re
from pathlib import Path


SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"<[^>]+>", " ", text)  # 粗略去 html 标签
    text = SPACE_RE.sub(" ", text).strip()
    return text


def clean_items(items: list[dict]) -> list[dict]:
    out = []
    for x in items:
        title = normalize_text(x.get("title", ""))
        summary = normalize_text(x.get("summary", ""))
        if not title:
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
            }
        )
    return out


def save_clean(items: list[dict], out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
