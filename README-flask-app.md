# Summer Campground Finder Web App

A Flask-based web application that provides a browser-based interface for finding campgrounds with perfect summer weather for weekend getaways.

## Features

- **Interactive Web Interface**: Modern, responsive UI with Bootstrap styling
- **Real-time Weather Search**: Uses Open-Meteo API to get weather forecasts
- **Customizable Search Parameters**:
  - Home location (latitude/longitude)
  - Maximum distance from home
  - Temperature preferences (min/max)
- **Distance-based Sorting**: Results sorted by proximity to your home
- **Weekend-focused**: Only shows Saturday and Sunday dates
- **Beautiful UI**: Gradient backgrounds, card-based layout, smooth animations

## Installation

1. Install dependencies:
```bash
pip install -r requirements-flask.txt
```

2. Ensure you have the required data files:
   - `all-campgrounds.json` - List of campgrounds
   - `config.json` - Default home location (optional)

## Running the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Usage

1. Enter your home coordinates (latitude and longitude)
2. Set your search preferences:
   - Maximum distance from home (miles)
   - Minimum comfortable temperature (°F)
   - Maximum comfortable temperature (°F)
3. Click "Find Summer Weekends" to search
4. View results showing campgrounds with perfect summer weather

## API Endpoints

- `GET /` - Main search interface
- `POST /search` - Search for summer weekends (JSON response)

## Configuration

The app reads from `config.json` for default values:
```json
{
  "home_lat": 40.7128,
  "home_long": -74.0060,
  "phone": "+1234567890"
}
```

## Data Sources

- **Weather Data**: Open-Meteo API (https://api.open-meteo.com/)
- **Campground Data**: Local JSON file with campground locations

## Technical Details

- **Backend**: Flask web framework
- **Frontend**: Bootstrap 5, custom CSS with gradients
- **Weather API**: Open-Meteo forecast API
- **Distance Calculation**: Geopy great-circle distance
- **Temperature Unit**: Fahrenheit
