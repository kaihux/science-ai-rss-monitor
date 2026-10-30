#!/usr/bin/env python3
"""Build a conservative Nature AI journalism feed from Nature's journal RSS."""
from urllib.request import Request, urlopen
from pathlib import Path
import xml.etree.ElementTree as ET
import re

SOURCE = "https://www.nature.com/nature.rss"
DEST = Path("nature-feed.xml")
AI = re.compile(r"\b(?:AI|artificial intelligence|machine learning|deep learning|large language models?|LLMs?|ChatGPT|OpenAI|Anthropic|DeepMind|AlphaFold|generative AI|AI agents?)\b", re.I)
REPORTING = {"news", "news feature", "news explainer", "feature", "technology feature", "editorial"}
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
RSS1 = "{http://purl.org/rss/1.0/}"
DC = "{http://purl.org/dc/elements/1.1/}"

def main():
    req = Request(SOURCE, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/rss+xml,application/xml,*/*"})
    with urlopen(req, timeout=45) as response:
        root = ET.fromstring(response.read())
    if root.tag == "rss":
        items = root.findall("./channel/item")
        get = lambda item, key: item.findtext(key, "")
    elif root.tag == RDF:
        items = root.findall(f"./{RSS1}item")
        get = lambda item, key: item.findtext(f"{RSS1}{key}", "")
    else:
        raise ValueError(f"Unexpected Nature feed root {root.tag!r}")
    if not items:
        raise ValueError("Nature feed empty; preserving previous output")
    out = ET.Element("rss", version="2.0")
    channel = ET.SubElement(out, "channel")
    for name, value in [("title","Nature AI news and reporting (filtered)"),("link","https://www.nature.com/nature"),("description","AI-related Nature reporting only; conservative article-type filter.")]:
        ET.SubElement(channel,name).text=value
    kept=0
    for item in items:
        title=get(item,"title")
        description=get(item,"description")
        link=get(item,"link")
        if not title or not link or not AI.search(title+" "+description):
            continue
        categories=[(e.text or "").strip().lower() for e in item.findall("category")]
        categories += [(e.text or "").strip().lower() for e in item.findall(f"{DC}type")]
        # Reject unknown article types rather than accidentally send research papers.
        if not any(c in REPORTING for c in categories):
            continue
        node=ET.SubElement(channel,"item")
        for key,val in [("title",title),("link",link),("guid",link),("description",description),("pubDate",get(item,"pubDate") or item.findtext(f"{DC}date",""))]:
            if val: ET.SubElement(node,key).text=val
        kept+=1
    DEST.write_bytes(ET.tostring(out,encoding="utf-8",xml_declaration=True))
    print(f"Read {len(items)} Nature items; selected {kept} confirmed reporting items")

if __name__ == "__main__":
    main()
