import sys
import json
import urllib.request

README = "README.md"
START_TAG = "<!-- DEVTO ARTICLES START -->"
END_TAG = "<!-- DEVTO ARTICLES END -->"

USERNAME = "seyhunak"
URL = f"https://dev.to/api/articles?username={USERNAME}&per_page=5"

articles = []

try:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
        for entry in data:
            articles.append(f"- [{entry.get('title', 'Untitled')}]({entry.get('url', '#')})")
except Exception as e:
    print(f"error: could not fetch Dev.to articles: {e}", file=sys.stderr)
    sys.exit(1)

if not articles:
    print("error: no articles fetched, leaving README unchanged", file=sys.stderr)
    sys.exit(1)

with open(README, "r", encoding="utf-8") as f:
    content = f.read()

head, has_start, rest = content.partition(START_TAG)
if has_start:
    _, has_end, tail = rest.partition(END_TAG)
    if not has_end:
        tail = ""
else:
    head, tail = content.rstrip("\n") + "\n\n", ""

block = START_TAG + "\n" + "\n".join(articles) + "\n" + END_TAG
content = head + block + (tail if tail.startswith("\n") else "\n" + tail)

with open(README, "w", encoding="utf-8") as f:
    f.write(content)
