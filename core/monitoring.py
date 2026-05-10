import functools
from skills.notifier.email_client import send_failure_email


def sarabilabs_monitor(func):
    """Catches exceptions, notifies Sameer and admin via email, then returns None."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"SARABILABS FAILURE in {func.__name__}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            try:
                send_failure_email(error_msg, func.__name__)
            except Exception as notify_err:
                print(f"[ERROR] Failed to send failure email: {notify_err}")
            return None

    return wrapper
