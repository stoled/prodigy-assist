import requests
from bs4 import BeautifulSoup
from app.wikipedia.fetcher import WikipediaArticle, WikipediaSection


def article_to_text(article: WikipediaArticle) -> str:
    """
    Собирает полный текст статьи для индексации.
    Summary + все разделы через разделитель.
    """
    parts = [article.summary]

    for section in article.sections:
        if section.content.strip():
            parts.append(f"## {section.title}\n{section.content}")

    return "\n\n".join(parts)


def _fetch_html(url: str) -> str:
    """Загружает HTML страницы Wikipedia."""
    headers = {"User-Agent": "prodigy-knowledge-bot/1.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def parse_html_fallback(url: str) -> WikipediaArticle | None:
    """
    BeautifulSoup fallback — парсит HTML напрямую.
    Используется когда Wikipedia API возвращает пустой контент.
    """
    try:
        html = _fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        # Заголовок
        title_el = soup.find("h1", {"id": "firstHeading"})
        title = title_el.get_text(strip=True) if title_el else ""

        # Основной контент
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            return None

        # Убираем служебные блоки
        for tag in content_div.find_all(["table", "sup", "style", "script"]):
            tag.decompose()

        # Summary — первый параграф
        paragraphs = content_div.find_all("p", recursive=True)
        summary = ""
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:
                summary = text
                break

        # Разделы по H2
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
