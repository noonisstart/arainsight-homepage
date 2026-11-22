import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.references = []
        self.headings = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        self.headings += tag == "h1"
        self.references.extend(attrs[key] for key in ("href","src") if key in attrs)

root = Path(sys.argv[1]).resolve()
pages = {}
prefix = "/arainsight-homepage/"
for file in root.rglob("index.html"):
    page = Page()
    page.feed(file.read_text(encoding="utf-8"))
    if page.headings != 1 or len(page.ids) != len(set(page.ids)):
        raise ValueError(f"Invalid headings or duplicated IDs: {file}")
    pages[prefix + file.relative_to(root).as_posix()] = page
if prefix + "index.html" not in pages:
    raise ValueError("Homepage missing")
for address, page in pages.items():
    for ref in page.references:
        url = urlsplit(urljoin(address,ref))
        if url.netloc:
            continue
        if not url.path.startswith(prefix) or not (root / unquote(url.path.removeprefix(prefix))).is_file():
            raise ValueError(f"Broken reference {ref} in {address}")
        if url.fragment and url.fragment not in pages[url.path].ids:
            raise ValueError(f"Missing target {ref} in {address}")
print(f"Verified {len(pages)} pages and their linked files.")
