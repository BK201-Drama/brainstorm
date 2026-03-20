"""
小说章节文本存储与读取
规范：stories/<novel_name>/chapter-001.txt
"""
from __future__ import annotations

import os
import re
from pathlib import Path


def _safe_novel_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    return name or "untitled_novel"


def chapter_filename(chapter: str | int) -> str:
    if isinstance(chapter, int):
        return f"chapter-{chapter:03d}.txt"

    s = str(chapter).strip().lower().replace("chapter-", "")
    if s.isdigit():
        return f"chapter-{int(s):03d}.txt"
    raise ValueError(f"invalid chapter: {chapter}")


def chapter_path(project_root: str, novel_name: str, chapter: str | int) -> str:
    novel_dir = Path(project_root) / "stories" / _safe_novel_name(novel_name)
    novel_dir.mkdir(parents=True, exist_ok=True)
    return str(novel_dir / chapter_filename(chapter))


def save_chapter_text(project_root: str, novel_name: str, chapter: str | int, text: str) -> str:
    path = chapter_path(project_root, novel_name, chapter)
    Path(path).write_text(text.strip() + "\n", encoding="utf-8")
    return path


def load_story_text(*, story_file: str | None, project_root: str, novel_name: str | None, chapter: str | int | None) -> tuple[str, str]:
    """
    Returns:
      (story_text, source_path)
    """
    if story_file:
        p = Path(story_file)
        if not p.exists():
            raise FileNotFoundError(f"story file not found: {story_file}")
        return p.read_text(encoding="utf-8").strip(), str(p)

    if novel_name and chapter is not None:
        p = Path(chapter_path(project_root, novel_name, chapter))
        if not p.exists():
            raise FileNotFoundError(f"chapter file not found: {p}")
        return p.read_text(encoding="utf-8").strip(), str(p)

    raise ValueError("story source missing: provide --story-file OR (--novel-name and --chapter)")
