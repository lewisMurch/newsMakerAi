
from datetime import datetime
def get_ordinal_suffix(day):
    # Function to get the ordinal suffix for a given day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix

def get_formatted_date():
    # Get the current date
    now = datetime.now()
    day = now.day
    month = now.strftime('%B')
    year = now.year
    
    # Get the ordinal suffix for the day
    suffix = get_ordinal_suffix(day)
    
    # Format the date
    formatted_date = f"{day}{suffix} {month}, {year}"
    
    return formatted_date