"""Pobieranie i ekstrakcja cen ze stron PlayStation Store."""

import html
import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen

PRICE_RE = re.compile(r"(?P<amount>\d+(?:[.,]\d{2})?)\s*(?:zl|zł)")


class TextExtractor(HTMLParser):
    """Zbiera widoczny tekst z dokumentu HTML."""

    def __init__(self):
        super().__init__()
        self.lines = []

    def handle_data(self, data):
        cleaned = " ".join(data.split())
        if cleaned:
            self.lines.append(html.unescape(cleaned))


def fetch_product_html(url: str) -> str:
    """Pobiera HTML strony produktu z PlayStation Store."""
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8")


def parse_price_value(raw_value: str) -> float:
    """Normalizuje zapis ceny do float."""
    cleaned = str(raw_value or "").replace("\xa0", " ").strip().lower()
    match = PRICE_RE.search(cleaned)
    if not match:
        cleaned = re.sub(r"[^0-9,.\-]", "", cleaned)
    else:
        cleaned = match.group("amount")
    cleaned = cleaned.replace(",", ".")
    if not cleaned:
        raise RuntimeError(f"Nie mozna zinterpretowac ceny: {raw_value}")
    return float(cleaned)


def extract_text_lines(page_html: str) -> list[str]:
    """Zwraca oczyszczone linie tekstu z dokumentu."""
    parser = TextExtractor()
    parser.feed(page_html)
    return parser.lines


def _normalize_text(value: str) -> str:
    return " ".join(str(value or "").lower().split())


def _is_platform_line(value: str) -> bool:
    normalized = _normalize_text(value)
    return normalized.startswith("ps4") or normalized.startswith("ps5")


def _extract_candidates(lines: list[str]) -> list[dict]:
    candidates = []
    for index, line in enumerate(lines):
        if not PRICE_RE.search(line.lower()):
            continue

        title = ""
        platform = ""
        if index > 0 and _is_platform_line(lines[index - 1]):
            platform = lines[index - 1]
            if index > 1:
                title = lines[index - 2]
        elif index > 0:
            title = lines[index - 1]

        candidates.append(
            {
                "title": title,
                "platform": platform,
                "price": parse_price_value(line),
            }
        )
    return candidates


def choose_variant_price(
    candidates: list[dict], expected_name: str, reference_price: str
) -> float:
    """Wybiera najwlasciwsza cene wariantu na podstawie nazwy i ceny bazowej."""
    if not candidates:
        raise RuntimeError("Nie znaleziono zadnej ceny na stronie produktu.")

    reference_price_value = parse_price_value(reference_price)
    normalized_name = _normalize_text(expected_name)

    name_matches = [
        candidate
        for candidate in candidates
        if normalized_name and normalized_name in _normalize_text(candidate["title"])
    ]
    if name_matches:
        matching_price = [
            candidate
            for candidate in name_matches
            if candidate["price"] == reference_price_value
        ]
        if matching_price:
            return matching_price[0]["price"]
        return name_matches[0]["price"]

    price_matches = [
        candidate for candidate in candidates if candidate["price"] == reference_price_value
    ]
    if price_matches:
        return price_matches[0]["price"]

    return candidates[0]["price"]


def extract_current_price(page_html: str, expected_name: str, reference_price: str) -> float:
    """Ekstrahuje cene aktualnie monitorowanego wariantu produktu."""
    lines = extract_text_lines(page_html)
    candidates = _extract_candidates(lines)
    return choose_variant_price(candidates, expected_name, reference_price)
