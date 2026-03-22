from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict


def build_interview_messages(items: List[Dict]) -> List[Dict]:
    messages = []
    for x in items:
        text = (
            f"【AI转型八股 | {x['topic']}】\n"
            f"Q: {x['question']}\n"
            f"A: {x['answer']}\n"
            f"来源: {x['source']}"
        )
        messages.append({"msg_type": "text", "content": {"text": text}})
    return messages


def save_jsonl(items: List[Dict], out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
