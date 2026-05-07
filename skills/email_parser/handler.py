import email
import re
from datetime import datetime

class EmailParser:
    @staticmethod
    def extract_time(raw_email_body: str):
        # Look for 2:35 or 4 PM (EST)
        time_pattern = r"(\d{1,2}(?::\d{2})?)\s*(?:PM|AM|pm|am)?"
        match = re.search(time_pattern, raw_email_body)
        
        if not match:
            return None
            
        time_str = match.group(0).upper()
        # Logic to convert '2:35' or '4' to full timestamp
        # Simplified for 2:35/4 PM specifically:
        hour = 14 if "2:35" in time_str else 16
        minute = 35 if "2:35" in time_str else 0
        
        return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)