from __future__ import annotations

from typing import Dict

from db import db as flask_db
from models.article import Article
from models.deadletter import Deadletter


def _get_db(db_handle):
    """Get database instance from handle."""
    return db_handle or flask_db


def _get_session(db_handle):
    """Get session from database handle."""
    if hasattr(db_handle, "session"):
        return db_handle.session
    return db_handle


def article_exists_by_canonical_url(db_handle, canonical_url: str) -> bool:
    """
    Check if an article with the given canonical URL already exists.

    Args:
        db_handle: Database handle or session
        canonical_url: Canonicalized article URL

    Returns:
        True if article exists, False otherwise
    """
    db = _get_db(db_handle)
    session = _get_session(db)
    return session.query(Article.id).filter(Article.canonical_url == canonical_url).first() is not None


def insert_deadletter(db_handle, deadletter_row: Dict) -> None:
    """
    Insert a deadletter record for failed operations.

    Args:
        db_handle: Database handle or session
        deadletter_row: Dict with id, stage, url, error, payload_json
    """
    db = _get_db(db_handle)
    session = _get_session(db)
    deadletter = Deadletter(**deadletter_row)
    session.add(deadletter)
    session.commit()
