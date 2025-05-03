import os

class DatabaseConfig:
    """Database configuration settings."""
    
    # PostgreSQL connection settings
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    DB_HOST_NAME = os.getenv('DB_HOST_NAME', 'db')
    DB_PORT = os.getenv('DB_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{DB_HOST_NAME}:{DB_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False 