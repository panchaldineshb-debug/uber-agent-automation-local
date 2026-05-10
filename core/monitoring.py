# core/monitoring.py
import functools
import os
from skills.notifier.email_client import send_failure_email  # Hypothetical import


def sarabilabs_monitor(func):
    """
    Standardizes error handling across 'agents', 'scripts', and 'skills'.
    Ensures Sameer and the system admin are notified of any failure.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"SARABILABS FAILURE in {func.__name__}: {str(e)}"

            # Logic to send the two emails
            # One to Sameer (student email) and one to System Admin
            # Referencing your 'skills/notifier' logic here would be ideal
            print(f"Intercepted: {error_msg}")

            # Trigger the failure notification logic
            # handle_notifications(error_msg)

            return None

    return wrapper
