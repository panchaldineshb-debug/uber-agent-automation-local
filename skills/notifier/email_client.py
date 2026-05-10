def get_failure_bodies(error_msg, func_name):
    """Returns a tuple of (Sameer_Body, Admin_Body)"""
    
    sameer_body = (
        f"Hi Sameer,\n\nThe Uber ride automation failed.\n"
        f"ACTION: Call Dad or use your own app immediately.\n\n"
        f"Error Ref: {func_name}"
    )
    
    admin_body = (
        f"SARABILABS ALERT\n"
        f"Function '{func_name}' crashed on M4 Mini.\n\n"
        f"ERROR DETAILS:\n{error_msg}\n\n"
        f"Check logs in your 'logs/' folder for tracebacks."
    )
    
    return sameer_body, admin_body

def send_confirmation(to_address, body):
    # This function would contain the actual email sending logic, 
    # similar to the one in 'skills/email_reply/handler.py'.
    pass

def send_failure_email(error_msg, func_name):
    sameer_body, admin_body = get_failure_bodies(error_msg, func_name)
    
    # Send email to Sameer
    send_confirmation(SON_EMAIL, sameer_body)
    
    # Send email to Admin (assuming ADMIN_EMAIL is defined)
    send_confirmation(ADMIN_EMAIL, admin_body)  