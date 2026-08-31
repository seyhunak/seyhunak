import sys
import json
import urllib.request

README = "README.md"
START_TAG = "<!-- RELEASES START -->"
END_TAG = "<!-- RELEASES END -->"

USER = "seyhunak"
REPOS = [
    "seyhunak/twitter-bootstrap-rails",
    "seyhunak/craftedcode",
    "seyhunak/awesome-banking",
    "seyhunak/awesome-omarchy",
    "seyhunak/awesome-bots",
    "seyhunak/awesome-job",
    "seyhunak/seyhunak",
]

releases = []

for repo in REPOS:
    url = f"https://api.github.com/repos/{repo}/releases?per_page=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            if data and isinstance(data, list) and len(data) > 0:
                r = data[0]
                releases.append(f"- [{r.get('name', r.get('tag_name', 'Release'))}]({r.get('html_url', '#')}) — {r.get('published_at', '')[:10]}")
    except Exception as e:
        print(f"warning: could not fetch releases for {repo}: {e}", file=sys.stderr)

if not releases:
    print("error: no releases fetched, leaving README unchanged", file=sys.stderr)
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

block = START_TAG + "\n" + "\n".join(releases) + "\n" + END_TAG
content = head + block + (tail if tail.startswith("\n") else "\n" + tail)

with open(README, "w", encoding="utf-8") as f:
    f.write(content)
