from flask import Flask, render_template, request, jsonify, Response
import json
import requests
from summer_finder import find_summer_days

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/geocode', methods=['GET'])
def geocode():
    """Geocoding API for city autocomplete using Open-Meteo Geocoding API"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Use Open-Meteo Geocoding API
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'results' in data:
            for item in data['results']:
                results.append({
                    'name': item['name'],
                    'country': item.get('country', ''),
                    'admin1': item.get('admin1', ''),
                    'latitude': item['latitude'],
                    'longitude': item['longitude']
                })
        
        return jsonify(results)
    except requests.RequestException as e:
        return jsonify({'error': f'Geocoding request failed: {str(e)}'})
    except Exception as e:
        return jsonify({'error': f'Geocoding error: {str(e)}'})

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    
    max_miles = float(data.get('max_miles', 400))
    min_high_temp = float(data.get('min_high_temp', 70))
    max_high_temp = float(data.get('max_high_temp', 88))
    prefer_waterfront = data.get('prefer_waterfront', False)
    all_days = data.get('all_days', False)
    weekends_only = not all_days
    
    # Handle home coordinates from city search form data
    form_home_lat = data.get('home_lat')
    form_home_long = data.get('home_long')
    
    def generate():
        try:
            # Create a progress callback that yields messages for streaming
            def progress_callback(message):
                yield f"data: {message}\n\n"
            
            # Use only the coordinates from the city search (form data)
            home_lat = form_home_lat
            home_long = form_home_long
            
            if home_lat and home_long:
                home = (float(home_lat), float(home_long))
            else:
                return "ERROR: Home coordinates are required. Please select a city from the search."
            
            # find_summer_days returns a list, so we need to handle it differently
            # We'll create a custom implementation that yields progress
            from summer_finder import load_campgrounds, check_campground_weather, get_day_of_week
            from geopy.distance import great_circle
            
            campgrounds = load_campgrounds()
            all_summer_days = []
            
            # Filter campgrounds by distance first
            eligible_campgrounds = []
            for campground in campgrounds:
                lat, long = campground["location"].split(",")
                point = (float(lat), float(long))
                dist = great_circle(home, point).miles if home else 0
                if dist < max_miles:
                    eligible_campgrounds.append((campground, dist))
            
            total_campgrounds = len(eligible_campgrounds)
            
            yield f"data: Considering {total_campgrounds} campgrounds within {max_miles} miles of home {home if home else 'any location'}.\n\n"
            
            for i, (campground, dist) in enumerate(eligible_campgrounds):
                name = campground["name"]
                
                yield f"data: Checking {name} ({i+1}/{total_campgrounds})\n\n"
                
                try:
                    summer_days = check_campground_weather(
                        campground, min_high_temp, max_high_temp, home, max_miles, weekends_only, progress_callback
                    )
                    
                    for summer_day in summer_days:
                        # Add waterfront information to the result
                        waterfront = campground.get("waterfront", "none")
                        summer_day["waterfront"] = waterfront
                        
                        waterfront_label = f" ({waterfront} waterfront)" if waterfront != "none" else ""
                        yield f"data: Found summer day at {name}{waterfront_label} - {summer_day['day']} {summer_day['date']} ({summer_day['temp']}°F)\n\n"
                        all_summer_days.append(summer_day)
                        
                except Exception as e:
                    yield f"data: {str(e)}\n\n"
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
                
                yield f"data: SEARCH_COMPLETE:{json.dumps(sorted_summer_days)}\n\n"
            else:
                yield f"data: SEARCH_COMPLETE:[]\n\n"
                
        except Exception as e:
            yield f"data: ERROR:{str(e)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
