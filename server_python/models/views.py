from db import db
from sqlalchemy import text

def create_database_views():
    """Create all database views"""
    db.session.execute(text("""
    CREATE OR REPLACE VIEW users AS
    SELECT id, username, created_at, updated_at
    FROM users_table;
    """))

    db.session.execute(text("""
    CREATE OR REPLACE VIEW items AS
    SELECT id, plaid_item_id, user_id, plaid_access_token, plaid_institution_id,
           status, created_at, updated_at, transactions_cursor
    FROM items_table;
    """))   

    db.session.execute(text("""
    CREATE OR REPLACE VIEW assets AS
    SELECT id, user_id, value, description, created_at, updated_at
    FROM assets_table;
    """))

    db.session.execute(text("""
    CREATE OR REPLACE VIEW accounts AS
    SELECT 
        a.id,
        a.plaid_account_id,
        a.item_id,
        i.plaid_item_id,
        i.user_id,
        a.name,
        a.mask,
        a.official_name,
        a.current_balance,
        a.available_balance,
        a.iso_currency_code,
        a.unofficial_currency_code,
        a.type,
        a.subtype,
        a.created_at,
        a.updated_at
    FROM accounts_table a
    LEFT JOIN items i ON i.id = a.item_id;
    """))

    db.session.execute(text("""
    CREATE OR REPLACE VIEW transactions AS
    SELECT 
        t.id,
        t.plaid_transaction_id,
        t.account_id,
        a.plaid_account_id,
        a.item_id,
        a.plaid_item_id,
        a.user_id,
        t.category,
        t.personal_finance_category_primary,
        t.personal_finance_category_detailed,
        t.type,
        t.name,
        t.amount,
        t.iso_currency_code,
        t.unofficial_currency_code,
        t.date,
        t.pending,
        t.account_owner,
        t.created_at,
        t.updated_at
    FROM transactions_table t
    LEFT JOIN accounts a ON t.account_id = a.id;
    """))

    db.session.commit()
