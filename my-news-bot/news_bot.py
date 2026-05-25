from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import feedparser


DEFAULT_FEEDS = [
    "https://www.tagesschau.de/xml/rss2",
    "https://www.heise.de/rss/heise-atom.xml",
    "https://www.spiegel.de/schlagzeilen/tops/index.rss",
]

STOPWORDS = {
    "aber",
    "als",
    "auch",
    "auf",
    "aus",
    "bei",
    "das",
    "dem",
    "den",
    "der",
    "des",
    "die",
    "ein",
    "eine",
    "einem",
    "einen",
    "einer",
    "eines",
    "for",
    "from",
    "has",
    "ist",
    "mit",
    "nach",
    "nicht",
    "sich",
    "the",
    "und",
    "von",
    "was",
    "werden",
    "wie",
    "zu",
}


@dataclass(frozen=True)
class NewsItem:
    source: str
    title: str
    link: str
    summary: str
    published: datetime | None


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_datetime(entry: feedparser.FeedParserDict) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)


def fetch_feed(url: str) -> list[NewsItem]:
    parsed = feedparser.parse(url)
    source = clean_text(parsed.feed.get("title", url))
    items: list[NewsItem] = []

    for entry in parsed.entries:
        title = clean_text(entry.get("title", "Ohne Titel"))
        summary = clean_text(entry.get("summary", entry.get("description", "")))
        link = entry.get("link", "")
        items.append(
            NewsItem(
                source=source,
                title=title,
                link=link,
                summary=summary,
                published=parse_datetime(entry),
            )
        )

    return items


def fetch_news(feed_urls: Iterable[str], max_per_feed: int) -> list[NewsItem]:
    news: list[NewsItem] = []
    for url in feed_urls:
        try:
            news.extend(fetch_feed(url)[:max_per_feed])
        except Exception as exc:
            print(f"Warnung: Feed konnte nicht geladen werden: {url} ({exc})")

    return sorted(
        news,
        key=lambda item: item.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )


def keywords(text: str) -> set[str]:
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9]{4,}", text.lower())
    return {word for word in words if word not in STOPWORDS}


def rank_top_news(items: list[NewsItem], limit: int) -> list[NewsItem]:
    all_titles = " ".join(item.title for item in items)
    title_terms = keywords(all_titles)

    def score(item: NewsItem) -> tuple[int, datetime]:
        item_terms = keywords(f"{item.title} {item.summary}")
        relevance = len(item_terms & title_terms)
        published = item.published or datetime.min.replace(tzinfo=timezone.utc)
        return relevance, published

    return sorted(items, key=score, reverse=True)[:limit]


def summarize_item(item: NewsItem, max_sentences: int = 2) -> str:
    text = item.summary or item.title
    sentences = re.split(r"(?<=[.!?])\s+", text)
    compact = " ".join(sentence.strip() for sentence in sentences[:max_sentences] if sentence.strip())
    return compact or item.title


def format_date(value: datetime | None) -> str:
    if value is None:
        return "unbekannt"
    return value.astimezone().strftime("%Y-%m-%d %H:%M")


def render_markdown(items: list[NewsItem], top_items: list[NewsItem]) -> str:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# News Report",
        "",
        f"Generiert am: {generated_at}",
        "",
        "## Top-News",
        "",
    ]

    if not top_items:
        lines.append("Keine News gefunden.")
    else:
        for index, item in enumerate(top_items, start=1):
            lines.extend(
                [
                    f"### {index}. {item.title}",
                    "",
                    f"- Quelle: {item.source}",
                    f"- Veröffentlicht: {format_date(item.published)}",
                    f"- Link: {item.link or 'nicht verfügbar'}",
                    f"- Zusammenfassung: {summarize_item(item)}",
                    "",
                ]
            )

    lines.extend(["## Alle Schlagzeilen", ""])
    for item in items:
        link = f" ([Link]({item.link}))" if item.link else ""
        lines.append(f"- **{item.title}** - {item.source}, {format_date(item.published)}{link}")

    lines.append("")
    return "\n".join(lines)


def load_feeds(path: Path | None) -> list[str]:
    if path is None:
        return DEFAULT_FEEDS

    feeds = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return feeds or DEFAULT_FEEDS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ein einfacher RSS-News-Bot.")
    parser.add_argument("--feeds", type=Path, help="Textdatei mit einer RSS-URL pro Zeile.")
    parser.add_argument("--output", type=Path, default=Path("news_report.md"), help="Markdown-Zieldatei.")
    parser.add_argument("--top", type=int, default=5, help="Anzahl der Top-News.")
    parser.add_argument("--max-per-feed", type=int, default=10, help="Maximale Artikel pro Feed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feeds = load_feeds(args.feeds)
    items = fetch_news(feeds, max_per_feed=args.max_per_feed)
    top_items = rank_top_news(items, limit=args.top)
    markdown = render_markdown(items, top_items)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"{len(items)} Schlagzeilen gespeichert in {args.output}")


if __name__ == "__main__":
    main()
