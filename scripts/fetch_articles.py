import re
import sys
import time
import urllib.request

import feedparser

# Add your Substack RSS URLs
FEEDS = [
    "https://seyhunak.substack.com/feed"
]

README = "README.md"
START_TAG = "<!-- ARTICLES START -->"
END_TAG = "<!-- ARTICLES END -->"

# The nightly job runs from GitHub-hosted runners, whose IPs get served an
# occasional Cloudflare interstitial instead of the feed. That arrives as
# malformed XML, which made feedparser return zero entries and the job fail.
# Ask like a browser, retry, and strip characters XML 1.0 forbids outright.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Control chars (except tab/LF/CR) and lone surrogates are never legal in
# XML 1.0; if a feed embeds one, expat aborts the whole document.
# Bytes, so multi-byte sequences are written as UTF-8 escapes.
_ILLEGAL_XML = re.compile(
    rb"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f"
    rb"\xed\xa0-\xed\xbf"  # UTF-8 encoded surrogates
    rb"\xef\xbf\xbe\xef\xbf\xff]"  # U+FFFE / U+FFFF
)


def fetch(url, attempts=3):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
            if not raw.strip():
                raise ValueError("empty response body")
            return _ILLEGAL_XML.sub(b"", raw)
        except Exception as e:  # noqa: BLE001 - retry on any transport error
            last = e
            if i < attempts - 1:
                time.sleep(2 * (i + 1))
    raise last


def parse(url):
    """Return up to 5 entries, tolerating a bozo parse if entries survived."""
    raw = fetch(url)
    feed = feedparser.parse(raw)
    if feed.bozo:
        print(
            f"warning: {url} parsed with warnings: {feed.bozo_exception}",
            file=sys.stderr,
        )
    return feed.entries[:5]


latest_articles = []

for feed_url in FEEDS:
    try:
        for entry in parse(feed_url):
            latest_articles.append(f"- [{entry.title}]({entry.link})")
    except Exception as e:  # noqa: BLE001 - one bad feed must not kill the rest
        print(f"warning: could not fetch {feed_url}: {e}", file=sys.stderr)

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
