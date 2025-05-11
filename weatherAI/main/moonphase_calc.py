import math
import datetime
def get_moon_phase():
    """
    Calculate the moon phase for now data
    Returns a value between 0 and 1, where:
    0 = New Moon
    0.25 = First Quarter
    0.5 = Full Moon
    0.75 = Last Quarter
    
    """
    
    
    date = datetime.datetime.now()
    
    # Known new moon date for reference
    known_new_moon = datetime.datetime(2000, 1, 6, 18, 14, 0)
    
    # Calculate days since known new moon
    days_since = (date - known_new_moon).total_seconds() / (24 * 3600)
    
    # Moon cycle is 29.53059 days
    moon_cycle = 29.53059
    
    # Calculate phase
    phase = (days_since % moon_cycle) / moon_cycle
    
    return phase