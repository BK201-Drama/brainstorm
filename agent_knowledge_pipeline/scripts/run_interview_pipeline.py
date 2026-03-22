#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fetch.interview_seed_fetcher import fetch_seed_materials
from src.clean.interview_qa_cleaner import build_interview_qa
from src.deliver.interview_feishu_formatter import build_interview_messages, save_jsonl


RAW_DIR = ROOT / "data" / "raw"
LOCAL_DIR = ROOT / "data" / "local"


def main():
    seeds = fetch_seed_materials()
    (RAW_DIR / "interview_seed_materials.json").write_text(
        json.dumps(seeds, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    qa_items = build_interview_qa(seeds)
    save_jsonl(qa_items, LOCAL_DIR / "interview_qa.jsonl")

    msgs = build_interview_messages(qa_items)
    save_jsonl(msgs, LOCAL_DIR / "interview_feishu_messages.jsonl")

    print(f"done: qa={len(qa_items)}, messages={len(msgs)}")
    print(f"output: {LOCAL_DIR / 'interview_qa.jsonl'}")
    print(f"output: {LOCAL_DIR / 'interview_feishu_messages.jsonl'}")


if __name__ == "__main__":
    main()
