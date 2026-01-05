from __future__ import annotations

import hashlib
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


_DROP_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "ref",
    "referrer",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _DROP_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    normalized_path = parsed.path.rstrip("/") or "/"
    normalized_query = urlencode(query_items, doseq=True)
    normalized = parsed._replace(path=normalized_path, query=normalized_query, fragment="")
    return urlunparse(normalized)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def article_id_from(canonical_url: str, title: str, published_at: str) -> str:
    return sha256_text(f"{canonical_url}\n{title}\n{published_at}")


def build_clean_text(
    title: Optional[str], description: Optional[str], content: Optional[str]
) -> str:
    parts = [part.strip() for part in (title, description, content) if part and part.strip()]
    return "\n\n".join(parts)
