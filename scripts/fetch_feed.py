#!/usr/bin/env python3
"""Fetch Science AI RSS (RSS 1.0/RDF or RSS 2.0) and validate it."""
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SOURCE = "https://www.science.org/action/showFeed?ui=0&mi=p69fzi&type=search&feed=rss&query=%2526ConceptID%253D551012%2526target%253Dtopic"
DEST = Path("feed.xml")
RSS1 = "{http://purl.org/rss/1.0/}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"

def main():
    request = Request(SOURCE, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ScienceAIRSSMirror/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    })
    with urlopen(request, timeout=45) as response:
        data = response.read()
    root = ET.fromstring(data)
    if root.tag == "rss":
        items = root.findall("./channel/item")
        fields = ("title", "link")
    elif root.tag == RDF:
        items = root.findall(f"./{RSS1}item")
        fields = (f"{RSS1}title", f"{RSS1}link")
    else:
        raise ValueError(f"Unsupported feed root: {root.tag!r}")
    if not items:
        raise ValueError("No items; refusing to overwrite existing mirror")
    for item in items:
        if not all(item.findtext(field) for field in fields):
            raise ValueError("RSS item missing title or link")
    DEST.write_bytes(data)
    print(f"Validated {len(items)} items ({root.tag})")

if __name__ == "__main__":
    main()
