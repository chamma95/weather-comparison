# Weather Temperature Comparison

A Python tool that generates interactive HTML visualizations comparing weather temperature data across multiple cities and years.

## Features

- 📊 Interactive temperature charts with Chart.js
- 🌍 Multi-city comparison (Amsterdam, Braunschweig, Giethoorn)
- 📈 Three temperature metrics: Average, Highest, and Lowest
- 🎨 Year-based color coding with customizable year styles
- 🖱️ Dynamic tooltips showing temperatures on hover
- 🔘 City toggle buttons for easy switching between locations
- 🎯 Year legend with toggle functionality

## Setup

### Requirements
- Python 3.7+
- pandas

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/weather-comparison.git
cd weather-comparison
```

2. Install dependencies:
```bash
pip install pandas
```

3. Place your CSV files in the `Data/` folder

### CSV Format

Your CSV files should have the following columns:
- `date` - Date in YYYY-MM-DD format
- `tavg` - Average temperature (°C)
- `tmax` - Maximum temperature (°C)
- `tmin` - Minimum temperature (°C)

## Usage

1. Edit `generate_weather_chart.py` to configure:
   - CSV file paths in `CSV_FILES`
   - Current year (`CURRENT_YEAR`)
   - Year colors and styles (`YEAR_STYLES`)
   - Output filename (`OUTPUT`)

2. Run the script:
```bash
python generate_weather_chart.py
```

3. Open the generated `weather_comparison.html` in your web browser

## Configuration

### Adding Cities

Add paths to your CSV files in the `CSV_FILES` list:
```python
CSV_FILES = [
    'Data/Amsterdam.csv',
    'Data/Braunschweig.csv',
    'Data/Giethoorn.csv',
]
```

### Customizing Year Styles

Modify the `YEAR_STYLES` dictionary:
```python
YEAR_STYLES = {
    2023: ('#888888', 0.45, 1.4),  # (color, opacity, line_width)
    2024: ('#FF9800', 0.45, 1.4),
    2025: ('#4CAF50', 0.45, 1.4),
    2026: ('#E91E63', 1.0,  2.5),
}
```

## Features in Detail

- **City Toggle**: Click city buttons at the top to switch between locations
- **Year Legend**: Click year labels to show/hide data for specific years
- **Interactive Tooltips**: Hover over the charts to see exact temperature values
- **Responsive Design**: Works on desktop and mobile browsers

## Output

Generates a standalone HTML file (`weather_comparison.html`) that includes:
- All chart data embedded as JSON
- Full Chart.js library via CDN
- Responsive layout with dark theme
- No external dependencies required to view

## License

MIT

## Author

Created with data visualizations for weather analysis
