import json
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import xml.etree.ElementTree as ET


def _first_text(node, tags):
    for tag in tags:
        el = node.find(tag)
        if el is not None and el.text:
            return el.text.strip()
    return ""


def _parse_rss(root, source_name: str):
    items = []
    for item in root.findall(".//item"):
        items.append(
            {
                "source": source_name,
                "title": _first_text(item, ["title"]),
                "link": _first_text(item, ["link"]),
                "summary": _first_text(item, ["description"]),
                "published": _first_text(item, ["pubDate"]),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def _parse_atom(root, source_name: str):
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for entry in root.findall("a:entry", ns):
        link = ""
        link_el = entry.find("a:link", ns)
        if link_el is not None:
            link = (link_el.attrib.get("href") or "").strip()

        title_el = entry.find("a:title", ns)
        summary_el = entry.find("a:summary", ns) or entry.find("a:content", ns)
        pub_el = entry.find("a:published", ns) or entry.find("a:updated", ns)

        items.append(
            {
                "source": source_name,
                "title": (title_el.text or "").strip() if title_el is not None else "",
                "link": link,
                "summary": (summary_el.text or "").strip() if summary_el is not None else "",
                "published": (pub_el.text or "").strip() if pub_el is not None else "",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def fetch_rss(url: str, source_name: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    root = ET.fromstring(data)

    if root.tag.endswith("feed"):
        return _parse_atom(root, source_name)
    return _parse_rss(root, source_name)


def save_raw(items: list[dict], out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
