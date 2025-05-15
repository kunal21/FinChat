from flask_sqlalchemy import SQLAlchemy
from .config import DatabaseConfig
from flask_migrate import Migrate
from sqlalchemy import text

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize the database with the Flask app."""
    from models import create_timestamp_trigger, create_database_views
    app.config.from_object(DatabaseConfig)
    
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)
        db.create_all()
        
        create_timestamp_trigger()

        # Create triggers for each table
        tables = ['users_table', 'items_table', 'assets_table', 
                    'accounts_table', 'transactions_table']
        
        for table in tables:
            trigger_name = f"{table}_updated_at_timestamp"

            # 1) Drop the old trigger if it already exists
            db.session.execute(text(f"""
                DROP TRIGGER IF EXISTS {trigger_name}
                ON {table} CASCADE;
            """))

            # 2) (Re)create the trigger
            db.session.execute(text(f"""
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE PROCEDURE trigger_set_timestamp();
            """))
        
        db.session.commit()