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
]

releases = []


def _get(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def _newest_release(repo):
    """Prefer a published GitHub Release, but fall back to the newest tag.

    Most of these repos are tagged without ever cutting a formal Release, so
    querying /releases alone returns nothing and would empty the block.
    """
    try:
        data = _get(f"https://api.github.com/repos/{repo}/releases?per_page=1")
        if isinstance(data, list) and data:
            r = data[0]
            name = r.get("name") or r.get("tag_name") or "Release"
            published = (r.get("published_at") or "")[:10]
            line = f"- [{name}]({r['html_url']})"
            return f"{line} — {published}" if published else line
    except Exception as e:
        print(f"note: no release for {repo} ({e}); trying tags", file=sys.stderr)

    data = _get(f"https://api.github.com/repos/{repo}/tags?per_page=1")
    if not isinstance(data, list) or not data:
        return None
    tag = data[0]["name"]
    date = ""
    try:
        sha = data[0].get("commit", {}).get("sha")
        if sha:
            commit = _get(f"https://api.github.com/repos/{repo}/commits/{sha}")
            date = (commit.get("commit", {}).get("committer", {}) or {}).get("date", "")[:10]
    except Exception as e:
        print(f"warning: could not date tag {tag} for {repo}: {e}", file=sys.stderr)
    return f"- [{tag}](https://github.com/{repo}/releases/tag/{tag})" + (f" — {date}" if date else "")


for repo in REPOS:
    try:
        line = _newest_release(repo)
        if line:
            releases.append(line)
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
