"""Add triggers & views

Revision ID: 518879ffc637
Revises: 053a5b9975bd
Create Date: 2025-04-29 05:26:41.956088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '518879ffc637'
down_revision = '053a5b9975bd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION trigger_set_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    tables = ['users_table', 'items_table', 'assets_table', 
                    'accounts_table', 'transactions_table']
        
    for table in tables:
        trigger_name = f"{table}_updated_at_timestamp"

        # 1) Drop the old trigger if it already exists
        op.execute(sa.text(f"""
            DROP TRIGGER IF EXISTS {trigger_name}
            ON {table} CASCADE;
        """))

        # 2) (Re)create the trigger
        op.execute(sa.text(f"""
            CREATE TRIGGER {trigger_name}
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE PROCEDURE trigger_set_timestamp();
        """))

    """Create all database views"""
    op.execute(sa.text("""
    CREATE OR REPLACE VIEW users AS
    SELECT id, username, created_at, updated_at
    FROM users_table;
    """))

    op.execute(sa.text("""
    CREATE OR REPLACE VIEW items AS
    SELECT id, plaid_item_id, user_id, plaid_access_token, plaid_institution_id,
           status, created_at, updated_at, transactions_cursor
    FROM items_table;
    """))   

    op.execute(sa.text("""
    CREATE OR REPLACE VIEW assets AS
    SELECT id, user_id, value, description, created_at, updated_at
    FROM assets_table;
    """))

    op.execute(sa.text("""
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

    op.execute(sa.text("""
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
    # ### end Alembic commands ###


def downgrade():
    # 2) Drop the views (in reverse order of creation)
    for view in ['transactions', 'accounts', 'assets', 'items', 'users']:
        op.execute(sa.text(f"DROP VIEW IF EXISTS {view};"))

    # 3) Drop the triggers on each table
    tables = [
        'transactions_table',
        'accounts_table',
        'assets_table',
        'items_table',
        'users_table',
    ]
    for table in tables:
        trigger_name = f"{table}_updated_at_timestamp"
        op.execute(sa.text(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table} CASCADE;"))

    # 4) Drop the trigger function
    op.execute(sa.text("DROP FUNCTION IF EXISTS trigger_set_timestamp() CASCADE;"))

