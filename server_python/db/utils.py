from db import db 
from sqlalchemy.exc import SQLAlchemyError

def commit_changes():
    """Commit changes to the database and handle any errors."""
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def add_to_db(instance):
    """Add an instance to the database session."""
    try:
        db.session.add(instance)
        commit_changes()
        return instance
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def delete_from_db(instance):
    """Delete an instance from the database."""
    try:
        db.session.delete(instance)
        commit_changes()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def get_or_create(model, **kwargs):
    """Get an instance of a model or create it if it doesn't exist."""
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        add_to_db(instance)
        return instance, True 