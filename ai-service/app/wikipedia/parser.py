import requests
from bs4 import BeautifulSoup
from app.wikipedia.fetcher import WikipediaArticle, WikipediaSection


def article_to_text(article: WikipediaArticle) -> str:
    """
    Builds the full article text for indexing.
    Summary + all sections joined with a separator.
    """
    parts = [article.summary]

    for section in article.sections:
        if section.content.strip():
            parts.append(f"## {section.title}\n{section.content}")

    return "\n\n".join(parts)


def _fetch_html(url: str) -> str:
    """Fetches the HTML of a Wikipedia page."""
    headers = {"User-Agent": "prodigy-knowledge-bot/1.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def parse_html_fallback(url: str) -> WikipediaArticle | None:
    """
    BeautifulSoup fallback — parses the HTML directly.
    Used when the Wikipedia API returns empty content.
    """
    try:
        html = _fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        # Title
        title_el = soup.find("h1", {"id": "firstHeading"})
        title = title_el.get_text(strip=True) if title_el else ""

        # Main content
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            return None

        # Strip out service blocks
        for tag in content_div.find_all(["table", "sup", "style", "script"]):
            tag.decompose()

        # Summary — first paragraph
        paragraphs = content_div.find_all("p", recursive=True)
        summary = ""
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:
                summary = text
                break

        # Sections by H2
        sections = []
        for h2 in content_div.find_all("h2"):
            section_title = h2.get_text(strip=True).replace("[править | править код]", "").strip()
            content_parts = []
            for sibling in h2.find_next_siblings():
                if sibling.name == "h2":
                    break
                if sibling.name == "p":
                    text = sibling.get_text(strip=True)
                    if text:
                        content_parts.append(text)
            if content_parts:
                sections.append(WikipediaSection(
                    title=section_title,
                    content="\n".join(content_parts),
                ))

        lang = "ru" if "/ru.wikipedia.org/" in url else "en"

        return WikipediaArticle(
            title=title,
            url=url,
            summary=summary,
            sections=sections,
            lang=lang,
        )

    except Exception:
        return None
