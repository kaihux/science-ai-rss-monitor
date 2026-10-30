#!/usr/bin/env python3
"""Fetch Science AI RSS and reject invalid/empty responses."""
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SOURCE = "https://www.science.org/action/showFeed?ui=0&mi=p69fzi&type=search&feed=rss&query=%2526ConceptID%253D551012%2526target%253Dtopic"
DEST = Path("feed.xml")

def main():
    request = Request(SOURCE, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ScienceAIRSSMirror/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    })
    with urlopen(request, timeout=45) as response:
        data = response.read()
    root = ET.fromstring(data)
    if root.tag != "rss":
        raise ValueError(f"Expected RSS, got {root.tag!r}")
    items = root.findall("./channel/item")
    if not items:
        raise ValueError("No items; refusing to overwrite existing mirror")
    for item in items:
        if not item.findtext("title") or not item.findtext("link"):
            raise ValueError("RSS item missing title or link")
    DEST.write_bytes(data)
    print(f"Validated {len(items)} items")

if __name__ == "__main__":
    main()
