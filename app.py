from flask import Flask, request, render_template_string, send_from_directory
from functools import wraps
import os
import pandas as pd

# Title information for locations
title_info = {
    'ballito': ['Ballito, Dolphin Coast, South Africa', 'SAST', 2, -29.532778, 31.224722],
    'bells': ['Bells Beach, Victoria, Australia', 'AEST', 10, -38.372778, 144.28],
    'cloudbreak': ['Cloudbreak, Fiji', 'FST', 12, -17.885833, 177.186667],
    'el_salvador': ['Surf City, El Salvador', 'CST', -6, 13.491389, -89.381111],
    'gland': ['G-Land, Banyuwangi, Indonesia', 'WIB', 7, -8.747222, 114.348611],
    'huntington': ['Huntington Beach, California, USA', 'PDT', -7, 33.653611, -118.003611],
    'jbay': ["Jeffreys's Bay, South Africa", 'SAST', 2, -34.033611, 24.934722],
    'margies': ['Margaret River, Western Australia, Australia', 'AWST', 8, -33.976389, 114.9825],
    'narrabeen': ['North Narrabeen, NSW, Australia', 'AEST', 10, -33.704722, 151.307778],
    'oahu': ['North Shore, Oahu, Hawaii', 'HST', -10, 21.6640, -158.0539],
    'peniche': ['Supertubos, Peniche, Portugal', 'WEST', 1, 39.343889, -9.365278],
    'raglan': ['Raglan, New Zealand', 'NZST', 12, -37.810556, 174.828333],
    'saquarema': ['Saquarema, Rio Di Janeiro, Brazil', 'BST', -3, -22.936944, -42.4825],
    'snapper': ['Snapper Rocks, Queensland, Australia', 'AEST', 10, -28.161389, 153.549444],
    'teahupoo': ['Teahupoo, Tahiti, French Polynesia', 'THAT', -10, -17.865556, -149.253056]
}

position_ranges = {
        'ballito': {
            'wave_left': [65, 65, 65, 65],
            'wave_top': [35, 45, 55, 65],
            'wind_left': [50, 48, 46, 44],
            'wind_top': [35, 45, 55, 65]
        }, 
        'bells': {
            'wave_left': [55, 52, 49, 46],
            'wave_top': [40, 50, 60, 70],
            'wind_left': [40, 45, 50, 55],
            'wind_top': [40, 30, 20, 10]
        },
        'cloudbreak': {
            'wave_left': [40, 41, 42, 43],
            'wave_top': [35, 45, 55, 65],
            'wind_left': [60, 61, 62, 63],
            'wind_top': [25, 35, 45, 55]
        },
        'el_salvador': {
            'wave_left': [45, 48, 51, 54],
            'wave_top': [50, 50, 50, 50],
            'wind_left': [40, 45, 50, 55],
            'wind_top': [12, 12, 12, 12]
        },
        'gland': {
            'wave_left': [45, 48, 51, 54],
            'wave_top': [55, 55, 55, 55],
            'wind_left': [45, 48, 51, 54],
            'wind_top': [30, 30, 30, 30]
        },
        'huntington': {
            'wave_left': [43, 46, 49, 52],
            'wave_top': [35, 38, 41, 44],
            'wind_left': [57, 62, 67, 72],
            'wind_top': [2, 12, 22, 32]
        },
        'jbay': {
            'wave_left': [56, 52, 48, 44],
            'wave_top': [50, 50, 50, 50],
            'wind_left': [56, 52, 48, 44],
            'wind_top': [10, 10, 10, 10]
        },
        'margies': {
            'wave_left': [42, 42, 42, 42],
            'wave_top': [22, 27, 32, 37],
            'wind_left': [53, 53, 53, 53],
            'wind_top': [50, 60, 70, 80]
        },
        'narrabeen': {
            'wave_left': [56, 54, 52, 50],
            'wave_top': [30, 45, 60, 75],
            'wind_left': [39, 38, 37, 36],
            'wind_top': [15, 25, 35, 45]
        },
        'oahu': {
            'wave_left': [50, 45, 40, 35],
            'wave_top': [20, 35, 50, 65],
            'wind_left': [67, 64, 61, 58],
            'wind_top': [30, 40, 50, 60]
        },
        'peniche': {
            'wave_left': [43, 39, 35, 31],
            'wave_top': [12, 24, 36, 48],
            'wind_left': [66, 66, 66, 66],
            'wind_top': [60, 70, 80, 90]
        },
        'raglan': {
            'wave_left': [46, 44, 42, 40],
            'wave_top': [30, 42, 54, 66],
            'wind_left': [60, 58, 56, 54],
            'wind_top': [34, 46, 58, 70]
        },
        'saquarema': {
            'wave_left': [54, 51, 48, 45],
            'wave_top': [60, 60, 60, 60],
            'wind_left': [54, 51, 48, 45],
            'wind_top': [20, 20, 20, 20]
        },
        'snapper': {
            'wave_left': [55, 55, 55, 55],
            'wave_top': [30, 45, 60, 75],
            'wind_left': [35, 35, 35, 35],
            'wind_top': [15, 30, 45, 60]
        },
        'teahupoo': {
            'wave_left': [40, 47, 54, 61],
            'wave_top': [45, 45, 45, 45],
            'wind_left': [40, 47, 54, 61],
            'wind_top': [5, 5, 5, 5]
        }
    }

# Flask app initialization
app = Flask(__name__, static_folder='static')

# Directory paths
FORECAST_PLOTS_DIR = 'forecast_plots'
TIDE_PLOTS_DIR = 'tide_plots'

# Password protection
USERNAME = "SurfingAustralia"
PASSWORD = ""

def password_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return ("Access Denied. Please provide valid credentials.", 401, 
                    {"WWW-Authenticate": "Basic realm='Login Required'"})
        return f(*args, **kwargs)
    return decorated_function

# Homepage: Show links to locations
@app.route("/")
@password_required
def index():
    # Get available dates
    plots = os.listdir(os.path.join(FORECAST_PLOTS_DIR, "corrected"))
    
    # Extract the forecast date from filenames
    date = plots[0].split('_')[1].split('.')[0] if plots else "No Plots Available"
    print(date)
    # Get unique locations
    locations = title_info.keys()
    locations = [
        {"name": title_info[loc][0], "lat": title_info[loc][3], "lon": title_info[loc][4], "url": f"/location/{loc}"}
        for loc in title_info
    ]

    # Render HTML
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Surf Forecasts Map</title>
        
        <!-- Leaflet CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />

        <style>
            #map {
                height: 600px;
                width: 100%;
            }
        </style>
    </head>
    <body>

        <h1>Surf Forecasts for {{ date }} UTC</h1>
        <h2>Click on a location to view the forecast.</h2>

        <!-- Map Container -->
        <div id="map"></div>

        <!-- Leaflet JS -->
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script>
            // Initialize Map
            var map = L.map('map').setView([0, 0], 2); // Centered on the world
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add location markers
            var locations = {{ locations | tojson }};
            locations.forEach(function(loc) {
                var marker = L.marker([loc.lat, loc.lon]).addTo(map);
                marker.bindPopup(`<b>${loc.name}</b><br><a href="${loc.url}">View Forecast</a>`);
            });
        </script>

    </body>
    </html>
    """
    return render_template_string(html, locations=locations, title_info=title_info, date=date)

@app.route("/location/<location>")
@password_required
def location_page(location):
    corrected_plot = next((f for f in os.listdir(os.path.join(FORECAST_PLOTS_DIR, "corrected")) if f.startswith(location)), None)
    tide_plot = next((t for t in os.listdir(TIDE_PLOTS_DIR) if t.startswith(location)), None)
    location_name = title_info.get(location, [location])[0]

    location_image_path = os.path.join('static', 'location_images', f"{location}.png")

    # Load the forecast DataFrames
    gfs_location_forecast_df = pd.read_csv(os.path.join('static', 'forecast_dfs', 'gfs', f'{location}.csv'))
    gfs_timesteps = gfs_location_forecast_df["DateTime"].tolist()
    gfs_forecast_data = gfs_location_forecast_df.to_dict(orient="records")

    ecmwf_location_forecast_df = pd.read_csv(os.path.join('static', 'forecast_dfs', 'ecmwf', f'{location}.csv'))
    ecmwf_timesteps = ecmwf_location_forecast_df["DateTime"].tolist()
    ecmwf_forecast_data = ecmwf_location_forecast_df.to_dict(orient="records")

    corrected_location_forecast_df = pd.read_csv(os.path.join('static', 'forecast_dfs', 'corrected', f'{location}.csv'))
    corrected_timesteps = corrected_location_forecast_df["DateTime"].tolist()
    corrected_forecast_data = corrected_location_forecast_df.to_dict(orient="records")


    arrow_positioning = position_ranges[location]

    html = """
   <!DOCTYPE html>
    <html>
        <head>
            <title>{{ location_name }} Forecast</title>
            <style>
                iframe {
                    width: 100%;
                    height: 600px;
                    border: none;
                    margin-bottom: 20px;
                }
                .toggle-button {
                    display: inline-block;
                    margin: 10px;
                    padding: 10px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .toggle-button:hover {
                    background-color: #0056b3;
                }
                #location-image-container {
                    position: relative;
                    display: inline-block;
                }
                .arrow {
                    position: absolute;
                    width: 0;
                    height: 0;
                    border-left: 15px solid transparent; /* Larger arrow */
                    border-right: 15px solid transparent; /* Larger arrow */
                    border-bottom: 30px solid red; /* Larger arrow */
                    transform-origin: bottom center; /* Rotate from the bottom */
                }
                .arrow::after {
                    content: '';
                    position: absolute;
                    width: 2px;
                    height: 50px; /* Tail length */
                    background: red; /* Tail color */
                    top: 100%; /* Position below the arrow */
                    left: 50%;
                    transform: translateX(-50%);
                }
                .wind-arrow {
                    border-bottom-color: chartreuse; /* Color for wind direction */
                }
                .wind-arrow::after {
                    background: chartreuse; /* Tail color for wind direction */
                }
                .arrow-label {
                    position: absolute;
                    font-size: 12px;
                    color: white;
                    background: rgba(0, 0, 0, 0.7);
                    padding: 2px 5px;
                    border-radius: 3px;
                    white-space: nowrap;
                    top: -40px; /* Position above the arrow */
                    left: 50%;
                    transform: translateX(-50%);
                    opacity: 0; /* Hidden by default */
                    transition: opacity 0.2s;
                }
                .arrow:hover .arrow-label {
                    opacity: 1; /* Show label on hover */
                }
                /* Key (Legend) Styles */
                .key {
                    position: absolute;
                    top: 40px; /* Position at the top */
                    right: 40px; /* Position at the right */
                    background: rgba(255, 255, 255, 0.8); /* Semi-transparent white background */
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    z-index: 10; /* Ensure it's above other elements */
                }
                .key-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 5px;
                }
                .key-item:last-child {
                    margin-bottom: 0;
                }
                .key-color {
                    width: 20px;
                    height: 20px;
                    margin-right: 10px;
                    border-radius: 3px;
                }
                .key-text {
                    font-size: 14px;
                    color: #333;
                }
                .model-message {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #f7f7f7;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                    color: #333;
                }   
            </style>
            <script>
                const gfsForecastData = {{ gfs_forecast_data | tojson }};
                const ecmwfForecastData = {{ ecmwf_forecast_data | tojson }};
                const correctedForecastData = {{ corrected_forecast_data | tojson }}
                const arrow_pos = {{ arrow_positioning | tojson }};
                let currentForecastData = correctedForecastData; // Default to corrected data
    
                let selectedTimestep = null; // Variable to store the selected timestep
                
                function updateAnnotations() {
                    const timestep = document.getElementById('timestep-selector').value;
                    selectedTimestep = timestep; // Store the selected timestep
                    const data = currentForecastData.find(entry => entry.DateTime === timestep);

                    if (!data) {
                        console.error("No data found for timestep:", timestep);
                        return;
                    }

                    const imageContainer = document.getElementById('location-image-container');
                    imageContainer.innerHTML = `
                        <img src="{{ url_for('static', filename='location_images/' + location_name + '.png') }}" alt="{{ location_name }}">
                        <div class="key">
                            <div class="key-item">
                                <div class="key-color" style="background: red;"></div>
                                <div class="key-text">Wave Direction</div>
                            </div>
                            <div class="key-item">
                                <div class="key-color" style="background: chartreuse;"></div>
                                <div class="key-text">Wind Direction</div>
                            </div>
                        </div>
                    `;

                    // Define positions for wave arrows (bottom-left corner)
                    const wavePositions = [
                        { left: `${arrow_pos.wave_left[0]}%`, top: `${arrow_pos.wave_top[0]}%` },
                        { left: `${arrow_pos.wave_left[1]}%`, top: `${arrow_pos.wave_top[1]}%` },
                        { left: `${arrow_pos.wave_left[2]}%`, top: `${arrow_pos.wave_top[2]}%` },
                        { left: `${arrow_pos.wave_left[3]}%`, top: `${arrow_pos.wave_top[3]}%` }
                    ];

                    // Add multiple wave direction arrows
                    wavePositions.forEach(pos => {
                        const waveArrow = document.createElement('div');
                        waveArrow.className = 'arrow';
                        waveArrow.style.left = pos.left;
                        waveArrow.style.top = pos.top;
                        waveArrow.style.transform = `rotate(${data.Wdir_forecast + 180}deg)`; // Rotate 180° to indicate source

                        const hsigForecast = data.Hsig_forecast.toFixed(2);
                        const tpeakForecast = data.Tpeak_forecast.toFixed(0);
                        const wdirForecast = data.Wdir_forecast.toFixed(0);

                        waveArrow.title = `Hs: ${hsigForecast}m, Tp: ${tpeakForecast}s, Wdir ${wdirForecast}°`; // Tooltip for wave direction


                        imageContainer.appendChild(waveArrow);
                    });

                    // Define positions for wind arrows (top-right corner)
                    const windPositions = [
                        { left: `${arrow_pos.wind_left[0]}%`, top: `${arrow_pos.wind_top[0]}%` },
                        { left: `${arrow_pos.wind_left[1]}%`, top: `${arrow_pos.wind_top[1]}%` },
                        { left: `${arrow_pos.wind_left[2]}%`, top: `${arrow_pos.wind_top[2]}%` },
                        { left: `${arrow_pos.wind_left[3]}%`, top: `${arrow_pos.wind_top[3]}%` }
                    ];

                    // Add multiple wind direction arrows
                    windPositions.forEach(pos => {
                        const windArrow = document.createElement('div');
                        windArrow.className = 'arrow wind-arrow';
                        windArrow.style.left = pos.left;
                        windArrow.style.top = pos.top;
                        windArrow.style.transform = `rotate(${(data.wind_direction + 180).toFixed(2)}deg)`; // Rotate 180° to indicate source

                        // Format wind speed and direction to 2 decimal places
                        const windSpeed = data.wind_speed.toFixed(0);
                        const windDirection = data.wind_direction.toFixed(0);
                        
                        windArrow.title = `Wind Speed: ${windSpeed} kts, Wind Direction: ${windDirection}°`; // Tooltip for wind direction

                        imageContainer.appendChild(windArrow);
                    });

                }

                // Load the timesteps when the page loads
                function loadTimesteps() {
                    const timesteps = {{ corrected_timesteps | tojson }}; // Adjust this according to the model
                    const selector = document.getElementById('timestep-selector');
                    selector.innerHTML = timesteps.map(ts => `<option value="${ts}">${ts}</option>`).join('');

                    // Set the default selected timestep to the previously selected timestep or the first one
                    selector.value = selectedTimestep || timesteps[0]; // Default to previously selected or first timestep
                    updateAnnotations(); // Update annotations for the selected timestep
                }

                // Toggle between models
                function toggleModel(model) {
                    const modelMessageDiv = document.getElementById('model-message');

                    let timesteps = [];
                    // Update the data source based on the selected model
                    if (model === 'GFSWave-v16') {
                        currentForecastData = gfsForecastData; // Load GFS data
                        timesteps = {{ gfs_timesteps | tojson }};
                        modelMessageDiv.innerHTML = "You are viewing the GFSWave-v16 forecast model.";
                    } else if (model === 'ECMWF-WAM') {
                        currentForecastData = ecmwfForecastData; // Load ECMWF data
                        timesteps = {{ ecmwf_timesteps | tojson }};
                        modelMessageDiv.innerHTML = "You are viewing the ECMWF-WAM forecast model.";
                    } else if (model === 'corrected') {
                        currentForecastData = correctedForecastData; // Load corrected data
                        timesteps = {{ corrected_timesteps | tojson }};
                        modelMessageDiv.innerHTML = "You are viewing the Corrected forecast model.";
                    }

                    // Update the timestep selector with the correct timesteps for the selected model
                    const selector = document.getElementById('timestep-selector');
                    selector.innerHTML = timesteps.map(ts => `<option value="${ts}">${ts}</option>`).join('');

                    // Make sure the selected timestep is the same as before or the first one
                    selector.value = selectedTimestep || timesteps[0]; // Use the previously selected timestep, if any

                    // Trigger updateAnnotations with the selected timestep
                    updateAnnotations();
                    
                }



                window.onload = loadTimesteps;
            </script>
        </head>
        <body>
            <h1>{{ location_name }}</h1>
            
            <h2>Below is the wave forecast, tide and wind forecast for the closest grid point to the specified surf location (or nearest wave buoy if accessible).</h2> 
            
            <h3>Please note that the wave forecasts are for deep-water wave conditions, and so do not account for near-shore dynamics.</h3>
            
            <body>The user can toggle between the Corrected, GFSWave-v16 or ECMWF-WAM forecasts.
            
            Wave height is visualised by the height of the column. Columns are coloured based on wave period, and the blue arrows above indicate wave direction.

            The size of wind arrows indicate the forecasted wind speed. This forecast is not corrected, and is obtained from the ECMWF weather model for the closest grid point to the surf location.</body>

            <iframe id="forecast-iframe" src="/forecast_plots/corrected/{{ corrected_plot if corrected_plot }}"></iframe>
         


            {% if tide_plot %}
                <iframe src="/tide_plots/{{ tide_plot }}"></iframe>
            {% else %}
                <p>No tide plot available.</p>
            {% endif %}
            

            
            <body>

            Below the user can visualise the forecasted wind and wave direction for the specific location for a given timestep in a given forecast.

            The yellow box highlights the grid point for which the forecast is provided for. Green arrows visualise wind direction, while red arrows visualise wave direction.

            The user can choose which model to visualise the data from by toggling between them. The timestep can be selected from the drop-down menu. All times are shown in the local timezone.
            
            
            </body>


            <div>
                <a class="toggle-button" onclick="toggleModel('corrected')">Corrected</a>
                <a class="toggle-button" onclick="toggleModel('GFSWave-v16')">GFSWave-v16</a>
                <a class="toggle-button" onclick="toggleModel('ECMWF-WAM')">ECMWF-WAM</a>
                
            </div>
            <!-- Model Usage Message -->
            <div id="model-message" class="model-message">
                You are viewing the Corrected forecast model.
            </div>
            <select id="timestep-selector" onchange="updateAnnotations()"></select>
            <div id="location-image-container">
                <img src="{{ url_for('static', filename='location_images/' + location_name + '.png') }}" alt="{{ location_name }}">
            </div>

            <p><a href="/">Back to All Locations</a></p>
        </body>
    </html>
    """
    return render_template_string(html, location_name=location_name, corrected_plot=corrected_plot, tide_plot=tide_plot, location_image_path=location_image_path, gfs_timesteps=gfs_timesteps, ecmwf_timesteps=ecmwf_timesteps, corrected_timesteps=corrected_timesteps, gfs_forecast_data=gfs_forecast_data, ecmwf_forecast_data=ecmwf_forecast_data, corrected_forecast_data=corrected_forecast_data, arrow_positioning=arrow_positioning)

# Serve forecast plots dynamically by model
@app.route("/forecast_plots/<model>/<filename>")
@password_required
def get_forecast_plot(model, filename):
    return send_from_directory(os.path.join(FORECAST_PLOTS_DIR, model), filename)

# Serve tide plots
@app.route("/tide_plots/<filename>")
@password_required
def get_tide_plot(filename):
    return send_from_directory(TIDE_PLOTS_DIR, filename)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)