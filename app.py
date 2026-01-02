from flask import Flask, render_template, request, jsonify, Response
import json
from summer_finder import find_summer_days, load_config

app = Flask(__name__)

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    
    max_miles = float(data.get('max_miles', 400))
    min_high_temp = float(data.get('min_high_temp', 70))
    max_high_temp = float(data.get('max_high_temp', 88))
    home_lat = float(data.get('home_lat')) if data.get('home_lat') else None
    home_long = float(data.get('home_long')) if data.get('home_long') else None
    
    def generate():
        try:
            # Create a progress callback that yields messages for streaming
            def progress_callback(message):
                yield f"data: {message}\n\n"
            
            # Get the generator from find_summer_days
            summer_days_generator = find_summer_days(
                max_miles=max_miles,
                min_high_temp=min_high_temp,
                max_high_temp=max_high_temp,
                home_lat=home_lat,
                home_long=home_long,
                progress_callback=progress_callback
            )
            
            # find_summer_days returns a list, so we need to handle it differently
            # We'll create a custom implementation that yields progress
            from summer_finder import load_campgrounds, check_campground_weather, get_day_of_week
            from geopy.distance import great_circle
            
            config = load_config()
            home_lat = home_lat or config.get("home_lat")
            home_long = home_long or config.get("home_long")
            
            if home_lat and home_long:
                home = (home_lat, home_long)
            else:
                home = None
            
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
                        campground, min_high_temp, max_high_temp, home, max_miles
                    )
                    
                    for summer_day in summer_days:
                        yield f"data: Found summer day at {name} - {summer_day['day']} {summer_day['date']} ({summer_day['temp']}°F)\n\n"
                        all_summer_days.append(summer_day)
                        
                except Exception as e:
                    yield f"data: {str(e)}\n\n"
                    continue
            
            if all_summer_days:
                sorted_summer_days = sorted(all_summer_days, key=lambda d: d['dist'])
                yield f"data: SEARCH_COMPLETE:{json.dumps(sorted_summer_days)}\n\n"
            else:
                yield f"data: SEARCH_COMPLETE:[]\n\n"
                
        except Exception as e:
            yield f"data: ERROR:{str(e)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
