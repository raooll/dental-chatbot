# app/db/utils.py
import inspect
from functools import wraps
from app.db.database import get_db

def with_db(func):
    """Decorator to automatically inject a DB session if not provided."""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        params = sig.parameters
        
        # Only apply if the function has a 'db' argument
        if "db" not in params:
            return await func(*args, **kwargs)
        
        db = kwargs.get("db", None)
        
        # If a db session was not provided, open a new one
        if db is None:
            gen = get_db()
            db = await anext(gen)
            kwargs["db"] = db
        
        # Run the wrapped function
        return await func(*args, **kwargs)
    
    return wrapper
