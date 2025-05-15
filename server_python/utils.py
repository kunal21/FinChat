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