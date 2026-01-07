import time
import functools

def retry_with_backoff(retries=3, backoff_in_seconds=1, allowed_exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    if x == retries:
                        print(f"[ERROR] Max retries reached. Last error: {e}")
                        raise e
                    sleep = (backoff_in_seconds * 2 ** x + 
                             0) # could add jitter
                    print(f"[WARN] Error: {e}. Retrying in {sleep}s...")
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator
