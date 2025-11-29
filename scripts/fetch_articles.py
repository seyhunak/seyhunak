import feedparser

# Add your Substack or Medium RSS URLs
FEEDS = [
    "https://seyhunak.substack.com/feed",
    "https://medium.com/feed/@seyhunak"
]

latest_articles = []

for feed_url in FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]:  # 5 latest per feed
        latest_articles.append(f"- [{entry.title}]({entry.link})")

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_tag = "<!-- ARTICLES START -->"
end_tag = "<!-- ARTICLES END -->"

if start_tag in content and end_tag in content:
    before = content.split(start_tag)[0] + start_tag + "\n"
    after = "\n" + content.split(end_tag)[1]
else:
    # If tags are missing, append at the end
    before = content + "\n" + start_tag + "\n"
    after = "\n" + end_tag

with open("README.md", "w", encoding="utf-8") as f:
    f.write(before + "\n".join(latest_articles) + after)
