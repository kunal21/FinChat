import os
from sqlalchemy.engine.url import URL

class DatabaseConfig:
    """Database configuration settings (secure by default)."""

    # --- required credentials (fail fast if missing) ---
    POSTGRES_USER     = os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
    POSTGRES_DB       = os.environ['POSTGRES_DB']

    # --- non-sensitive defaults ---
    DB_HOST_NAME = os.environ.get('DB_HOST_NAME', 'db')
    DB_PORT      = os.environ.get('DB_PORT', '5432')

    SSL_MODE = os.environ.get('DB_SSL_MODE', 'disable')

    # --- build the URL with SSL enforced ---
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername='postgresql+psycopg2',
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=DB_HOST_NAME,
        port=DB_PORT,
        database=POSTGRES_DB,
        query={'sslmode': SSL_MODE}
    )

    # --- engine options keep the password out of logs/traces ---
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'sslmode': SSL_MODE
        }
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
