# Shared Core Architecture

The summer campground finder now uses a shared core module (`summer_finder.py`) that provides the same functionality for both the command-line and web applications.

## Architecture

### Core Module: `summer_finder.py`
Contains all the shared functionality:
- **`find_summer_days()`**: Main search function with progress callback support
- **`check_campground_weather()`**: Weather API calls for individual campgrounds
- **`load_config()`** & **`load_campgrounds()`**: Data loading utilities
- **`get_day_of_week()`**: Date formatting utility
- **`send_sms_notification()`**: SMS notification functionality

### Command-Line App: `find_summer.py`
- Uses shared core functions
- Handles argument parsing
- Provides console progress output via progress_callback
- Maintains original CLI interface

### Web App: `app.py`
- Uses shared core functions
- Implements streaming responses for real-time web progress
- Provides browser-based interface
- Same underlying search logic as CLI

## Benefits

1. **Single Source of Truth**: Core functionality is defined once
2. **Consistent Results**: Both apps produce identical results
3. **Easy Maintenance**: Updates to core logic automatically apply to both apps
4. **Progress Callbacks**: Flexible progress reporting for different interfaces
5. **Modular Design**: Each function has a single responsibility

## Usage Examples

### Command Line:
```bash
python find_summer.py --max_miles 100 --min_high_temp 75 --max_high_temp 85
```

### Web Interface:
Visit http://localhost:5000 and use the interactive form

## Testing Both Apps

Both applications now use the same core search algorithm. You can verify they produce identical results by:

1. Running the command-line app with specific parameters
2. Using the web app with the same parameters
3. Comparing the results (they should match exactly)

## Future Enhancements

Any improvements to the core functionality in `summer_finder.py` will automatically be available to both interfaces:
- Better weather data handling
- Enhanced filtering options
- Improved error handling
- New features like weather alerts or recommendations
