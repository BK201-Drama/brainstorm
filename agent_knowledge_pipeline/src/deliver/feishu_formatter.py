import json
from pathlib import Path


def to_feishu_text(item: dict) -> str:
    return (
        f"【Agent八股】{item.get('title','')}\n"
        f"来源：{item.get('source','')}\n"
        f"摘要：{item.get('summary','')[:180]}\n"
        f"链接：{item.get('link','')}"
    )


def build_messages(items: list[dict]) -> list[dict]:
    return [{"msg_type": "text", "content": {"text": to_feishu_text(x)}} for x in items]


def save_messages_jsonl(msgs: list[dict], out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
