#!/usr/bin/env python3
"""Filter Quanta Magazine's official RSS for AI journalism."""
from pathlib import Path
from urllib.request import Request, urlopen
import re
import xml.etree.ElementTree as ET

SOURCE = "https://api.quantamagazine.org/feed/"
DEST = Path("quanta-feed.xml")
AI = re.compile(r"\b(?:AI|artificial intelligence|machine learning|deep learning|large language models?|LLMs?|ChatGPT|OpenAI|Anthropic|DeepMind|AlphaFold|neural networks?|AI[- ](?:assisted|generated|powered)|generative AI)\b", re.I)

def main():
    req = Request(SOURCE, headers={"User-Agent": "Mozilla/5.0 (compatible; QuantaAIReportingMonitor/1.0)", "Accept": "application/rss+xml, application/xml, */*"})
    with urlopen(req, timeout=45) as response:
        data = response.read()
    root = ET.fromstring(data)
    if root.tag != "rss":
        raise ValueError(f"Unexpected feed root: {root.tag!r}")
    items = root.findall("./channel/item")
    if not items:
        raise ValueError("Empty source feed; preserving existing mirror")
    out = ET.Element("rss", version="2.0")
    channel = ET.SubElement(out, "channel")
    for tag, value in (("title", "Quanta Magazine AI reporting"), ("link", "https://www.quantamagazine.org/tag/artificial-intelligence/"), ("description", "AI-related Quanta Magazine journalism filtered from the official RSS feed.")):
        ET.SubElement(channel, tag).text = value
    count = 0
    for item in items:
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        desc = item.findtext("description", "")
        categories = " ".join(e.text or "" for e in item.findall("category"))
        if not title or not link or not AI.search(" ".join((title, desc, categories))):
            continue
        copied = ET.SubElement(channel, "item")
        for tag in ("title", "link", "guid", "pubDate", "description"):
            value = item.findtext(tag)
            if value:
                ET.SubElement(copied, tag).text = value
        if copied.find("guid") is None:
            ET.SubElement(copied, "guid").text = link
        count += 1
    DEST.write_bytes(ET.tostring(out, encoding="utf-8", xml_declaration=True))
    print(f"Checked {len(items)} source entries, retained {count} AI journalism entries")

if __name__ == "__main__":
    main()
