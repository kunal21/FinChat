"""
Data source clients for fetching financial news and market data.
"""

from .finnhub_client import finnhub_fetch, parse_finnhub_article

__all__ = ["finnhub_fetch", "parse_finnhub_article"]
