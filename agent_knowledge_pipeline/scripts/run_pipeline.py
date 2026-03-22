#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fetch.rss_fetcher import fetch_rss, save_raw
from src.clean.cleaner import clean_items, save_clean
from src.store.local_store import save_jsonl
from src.deliver.feishu_formatter import build_messages, save_messages_jsonl


ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs" / "sources.json"
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"
LOCAL_DIR = ROOT / "data" / "local"


def main():
    cfg = json.loads(CFG.read_text(encoding="utf-8"))

    filters = cfg.get("filters", {})
    exclude_keywords = filters.get("exclude_keywords", [])
    prefer_keywords = filters.get("prefer_keywords", [])

    all_clean = []
    for s in cfg.get("sources", []):
        if not s.get("enabled", False):
            continue
        if s.get("type") != "rss":
            continue

        name = s["name"]
        try:
            items = fetch_rss(s["url"], name)
        except Exception as e:
            print(f"skip source={name}, err={e}")
            continue

        raw_file = RAW_DIR / f"{name.replace(' ', '_').lower()}.json"
        save_raw(items, raw_file)

        cleaned = clean_items(
            items,
            exclude_keywords=exclude_keywords,
            prefer_keywords=prefer_keywords,
        )
        clean_file = CLEAN_DIR / f"{name.replace(' ', '_').lower()}.json"
        save_clean(cleaned, clean_file)

        all_clean.extend(cleaned)

    save_jsonl(all_clean, LOCAL_DIR / "articles.jsonl")
    msgs = build_messages(all_clean)
    save_messages_jsonl(msgs, LOCAL_DIR / "feishu_messages.jsonl")

    print(f"done: articles={len(all_clean)}, messages={len(msgs)}")
    print(f"output: {LOCAL_DIR / 'articles.jsonl'}")
    print(f"output: {LOCAL_DIR / 'feishu_messages.jsonl'}")


if __name__ == "__main__":
    main()
