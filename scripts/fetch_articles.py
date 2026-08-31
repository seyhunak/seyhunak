import sys
import feedparser

# Add your Substack RSS URLs
FEEDS = [
    "https://seyhunak.substack.com/feed"
]

README = "README.md"
START_TAG = "<!-- ARTICLES START -->"
END_TAG = "<!-- ARTICLES END -->"

latest_articles = []

for feed_url in FEEDS:
    feed = feedparser.parse(feed_url)
    if feed.bozo:
        print(f"warning: could not parse {feed_url}: {feed.bozo_exception}", file=sys.stderr)
    for entry in feed.entries[:5]:  # 5 latest per feed
        latest_articles.append(f"- [{entry.title}]({entry.link})")

# A transient feed outage must not silently wipe the existing list.
if not latest_articles:
    print("error: no articles fetched, leaving README unchanged", file=sys.stderr)
    sys.exit(1)

with open(README, "r", encoding="utf-8") as f:
    content = f.read()

# Rebuild the block from scratch so a missing or duplicated marker heals
# instead of accumulating. `head`/`tail` are everything outside the block.
head, has_start, rest = content.partition(START_TAG)
if has_start:
    _, has_end, tail = rest.partition(END_TAG)
    if not has_end:
        # Stale list with no closing marker: drop it, we regenerate below.
        tail = ""
else:
    head, tail = content.rstrip("\n") + "\n\n", ""

block = START_TAG + "\n" + "\n".join(latest_articles) + "\n" + END_TAG
content = head + block + (tail if tail.startswith("\n") else "\n" + tail)

with open(README, "w", encoding="utf-8") as f:
    f.write(content)
