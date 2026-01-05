from datetime import datetime


def sanitize_user(user):
    """Sanitizes user data"""
    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


def sanitize_item(item):
    """Sanitizes item data"""
    return {
        "id": item.id,
        "user_id": item.user_id,
        "plaid_institution_id": item.plaid_institution_id,
        "status": item.status,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None
    }

def sanitize_account(account):
    """Sanitizes account data"""
    return {
        "id": account.id,
        "item_id": account.item_id,
        "user_id": account.user_id,
        "name": account.name,
        "mask": account.mask,
        "official_name": account.official_name,
        "current_balance": float(account.current_balance) if account.current_balance else None,
        "available_balance": float(account.available_balance) if account.available_balance else None,
        "iso_currency_code": account.iso_currency_code,
        "unofficial_currency_code": account.unofficial_currency_code,
        "type": account.type,
        "subtype": account.subtype,
        "created_at": account.created_at.isoformat() if account.created_at else None,
        "updated_at": account.updated_at.isoformat() if account.updated_at else None
    }


def sanitize_transaction(transaction):
    """Sanitizes transaction"""
    return {
        "id": transaction.id,
        "account_id": transaction.account_id,
        "user_id": transaction.user_id,
        "name": transaction.name,
        "amount": float(transaction.amount) if transaction.amount else None,
        "date": transaction.date.isoformat() if transaction.date else None,
        "category": transaction.category,
        "personal_finance_category_primary": transaction.personal_finance_category_primary,
        "personal_finance_category_detailed": transaction.personal_finance_category_detailed,
        "type": transaction.type,
        "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
        "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
    }

def sanitize_message(message):
    """Sanitizes message data"""
    return {
        "id": message.id,
        "user_id": message.user_id,
        "text": message.text,
        "created_at": message.created_at.isoformat() if message.created_at else None,
        "updated_at": message.updated_at.isoformat() if message.updated_at else None,
        "author": message.author,
    }

def sanitize_asset(asset):
    """Sanitizes asset data"""
    return {
        "id": asset.id,
        "user_id": asset.user_id,
        "description": asset.description,
        "value": float(asset.value) if asset.value else None,
        "created_at": asset.created_at.isoformat() if asset.created_at else None,
        "updated_at": asset.updated_at.isoformat() if asset.updated_at else None
    }


def sanitize_holding(holding):
    """Sanitizes holding data"""
    return {
        "id": holding.id,
        "account_id": holding.account_id,
        "plaid_account_id": holding.plaid_account_id,
        "security_id": holding.security_id,
        "name": holding.name,
        "ticker_symbol": holding.ticker_symbol,
        "security_type": holding.security_type,
        "quantity": float(holding.quantity) if holding.quantity is not None else None,
        "institution_price": (
            float(holding.institution_price) if holding.institution_price is not None else None
        ),
        "institution_price_as_of": (
            holding.institution_price_as_of.isoformat()
            if holding.institution_price_as_of
            else None
        ),
        "institution_value": (
            float(holding.institution_value) if holding.institution_value is not None else None
        ),
        "cost_basis": float(holding.cost_basis) if holding.cost_basis is not None else None,
        "iso_currency_code": holding.iso_currency_code,
        "unofficial_currency_code": holding.unofficial_currency_code,
        "created_at": holding.created_at.isoformat() if holding.created_at else None,
        "updated_at": holding.updated_at.isoformat() if holding.updated_at else None,
    }


def sanitize_user_impact(impact):
    """Sanitizes user impact data with article details"""
    return {
        "id": impact.id,
        "user_id": impact.user_id,
        "article_id": impact.article_id,
        "ticker": impact.ticker,
        "impact_level": impact.impact_level,
        "impact_summary": impact.impact_summary,
        "estimated_effect": impact.estimated_effect,
        "read": impact.read,
        "dismissed": impact.dismissed,
        "created_at": impact.created_at.isoformat() if impact.created_at else None,
        # Include article details
        "article": {
            "id": impact.article.id,
            "title": impact.article.title,
            "summary": impact.article.summary,
            "url": impact.article.url,
            "source": impact.article.source,
            "published_at": impact.article.published_at.isoformat() if impact.article.published_at else None,
        } if impact.article else None,
    }


def parse_plaid_datetime(value):
    if not value:
        return None
    if hasattr(value, "isoformat"):
        return value
    try:
        if "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except ValueError:
        return None


 
