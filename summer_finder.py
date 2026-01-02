import requests
import json
from datetime import datetime
from geopy.distance import great_circle
import os

def get_day_of_week(date_str):
    """Convert date string to day of week name."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day_name = date_obj.strftime('%A')
    return day_name

def load_config(config_file='config.json'):
    """Load configuration from JSON file."""
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'rt') as f:
            config = json.load(f)
    return config

def load_campgrounds(input_file='all-campgrounds.json'):
    """Load campgrounds from JSON file."""
    with open(input_file, "rt") as f:
        j = f.read()
        return json.loads(j)

def check_campground_weather(campground, min_high_temp, max_high_temp, home=None, max_miles=400):
    """Check weather for a single campground and return summer days if any."""
    name = campground["name"]
    lat, long = campground["location"].split(",")
    point = (float(lat), float(long))
    dist = great_circle(home, point).miles if home else 0
    
    if dist >= max_miles:
        return []
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=temperature_2m_max&timezone=auto&forecast_days=16&temperature_unit=fahrenheit"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        summer_days = []
        for index, temp in enumerate(data["daily"]["temperature_2m_max"]):
            if temp and temp >= min_high_temp and temp <= max_high_temp:
                date = data["daily"]["time"][index]
                day = get_day_of_week(date)
                if day in ["Saturday","Sunday"]:
                    summer_day = {
                        "dist": round(dist, 1),
                        "date": date,
                        "day": day,
                        "temp": temp,
                        "name": name
                    }
                    summer_days.append(summer_day)
        
        return summer_days
    except requests.RequestException as e:
        raise Exception(f"Error fetching weather for {name}: {e}")

def find_summer_days(max_miles=400, min_high_temp=70, max_high_temp=88, home_lat=None, home_long=None, 
                    config_file='config.json', input_file='all-campgrounds.json', progress_callback=None, prefer_waterfront=False):
    """
    Find campgrounds with summer-like weekend temperatures within specified distance.
    
    Args:
        max_miles: Maximum distance from home in miles
        min_high_temp: Minimum high temperature for summer day (Fahrenheit)
        max_high_temp: Maximum high temperature for summer day (Fahrenheit)
        home_lat: Home latitude (overrides config file)
        home_long: Home longitude (overrides config file)
        config_file: Path to config file
        input_file: Path to campgrounds JSON file
        progress_callback: Function to call with progress updates (optional)
        prefer_waterfront: If True, prioritize waterfront campgrounds in results
    
    Returns:
        List of summer day dictionaries sorted by distance and waterfront preference
    """
    config = load_config(config_file)
    home_lat = home_lat or config.get("home_lat")
    home_long = home_long or config.get("home_long")
    
    if home_lat and home_long:
        home = (home_lat, home_long)
    else:
        home = None
    
    campgrounds = load_campgrounds(input_file)
    all_summer_days = []
    
    # Filter campgrounds by distance first to get accurate count
    eligible_campgrounds = []
    for campground in campgrounds:
        lat, long = campground["location"].split(",")
        point = (float(lat), float(long))
        dist = great_circle(home, point).miles if home else 0
        if dist < max_miles:
            eligible_campgrounds.append((campground, dist))
    
    total_campgrounds = len(eligible_campgrounds)
    
    if progress_callback:
        progress_callback(f"Considering {total_campgrounds} campgrounds within {max_miles} miles of home {home if home else 'any location'}.")
    
    for i, (campground, dist) in enumerate(eligible_campgrounds):
        name = campground["name"]
        
        if progress_callback:
            progress_callback(f"Checking {name} ({i+1}/{total_campgrounds})")
        
        try:
            summer_days = check_campground_weather(
                campground, min_high_temp, max_high_temp, home, max_miles
            )
            
            for summer_day in summer_days:
                # Add waterfront information to the result
                waterfront = campground.get("waterfront", "none")
                summer_day["waterfront"] = waterfront
                
                if progress_callback:
                    waterfront_label = f" ({waterfront} waterfront)" if waterfront != "none" else ""
                    progress_callback(f"Found summer day at {name}{waterfront_label} - {summer_day['day']} {summer_day['date']} ({summer_day['temp']}°F)")
                all_summer_days.append(summer_day)
                
        except Exception as e:
            if progress_callback:
                progress_callback(str(e))
            continue
    
    if all_summer_days:
        # Sort by waterfront preference first, then by distance
        if prefer_waterfront:
            # Waterfront campgrounds first (non-"none"), then by distance
            sorted_summer_days = sorted(
                all_summer_days, 
                key=lambda d: (d.get('waterfront', 'none') == 'none', d['dist'])
            )
        else:
            # Just sort by distance
            sorted_summer_days = sorted(all_summer_days, key=lambda d: d['dist'])
        
        return sorted_summer_days
    else:
        return []

def send_sms_notification(phone, message):
    """Send SMS notification using textbelt API."""
    try:
        resp = requests.post('https://textbelt.com/text', {
            'phone': phone,
            'message': message,
            'key': 'textbelt',
        })
        return resp.json()
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}
