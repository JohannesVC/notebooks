from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

limiter = Limiter(key_func=get_remote_address,
                  storage_uri=os.getenv('MONGO_URI'),
                  strategy="fixed-window", 
                )

@limiter.request_filter
def exempt_users():
    return False