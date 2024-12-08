import os
import pandas as pd

# Setting up the file directory
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(current_directory, 'final.csv')  # Replace with your CSV file name

# Load data from CSV
data = pd.read_csv(csv_file)

# Check if required columns are present
required_columns = ['latitude', 'longitude', 'Encryption']
for column in required_columns:
    if column not in data.columns:
        raise ValueError(f"CSV file must contain '{column}' column")

# Extract valid rows where latitude and longitude are not null
valid_data = data[['latitude', 'longitude', 'Encryption']].dropna()

# Grouping data based on Encryption type
grouped_data = {
    "WPA3": valid_data[valid_data['Encryption'].str.lower() == 'wpa3'][['latitude', 'longitude']].values.tolist(),
    "Open": valid_data[valid_data['Encryption'].str.lower() == 'none'][['latitude', 'longitude']].values.tolist(),
    "WEP": valid_data[valid_data['Encryption'].str.lower() == 'wep'][['latitude', 'longitude']].values.tolist(),
    "WPA": valid_data[valid_data['Encryption'].str.lower() == 'wpa'][['latitude', 'longitude']].values.tolist(),
    "WPA2": valid_data[valid_data['Encryption'].str.lower() == 'wpa2'][['latitude', 'longitude']].values.tolist(),
    "Unknown": valid_data[valid_data['Encryption'].str.lower() == 'unknown'][['latitude', 'longitude']].values.tolist()
}

# Compute map center
all_locations = [loc for locations in grouped_data.values() for loc in locations]
if len(all_locations) > 0:
    avg_lat = sum([loc[0] for loc in all_locations]) / len(all_locations)
    avg_lng = sum([loc[1] for loc in all_locations]) / len(all_locations)
else:
    raise ValueError("No valid latitude and longitude data found in the CSV file")

# Colors for each group
colors = {"Open": "red", "WEP": "orange", "WPA": "yellow", "WPA2": "green", "WPA3": "blue", "Unknown": "gray"}

# HTML Template
html_file = os.path.join(current_directory, 'map.html')
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Encryption </title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <style>
        #map {{
            height: 90vh;
            width: 100%;
        }}
        #menu {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: white;
            padding: 10px;
            border-bottom: 1px solid #ddd;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        #menu button {{
            margin: 0 5px;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            background-color: grey;
            color: white;
            cursor: pointer;
        }}
        #menu button:hover {{
            background-color: #0056b3;
        }}
        #menu button.active {{
            background-color: #004080;
        }}
        .legend {{
            line-height: 18px;
            color: #555;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .legend-color {{
            width: 15px;
            height: 15px;
            margin-right: 10px;
            border: 1px solid #000;
        }}
    </style>
</head>
<body>
    <div id="menu"></div>
    <div id="map"></div>
    <script>
        let map = L.map('map').setView([{avg_lat}, {avg_lng}], 15);

        // Load and display OpenStreetMap tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }}).addTo(map);

        const markerGroups = {{}};

        function showOnlyMarkers(groupName) {{
            // Hide all markers
            for (const group in markerGroups) {{
                markerGroups[group].forEach(marker => marker.remove());
            }}
            // Show selected group markers
            if (groupName === "ALL") {{
                for (const group in markerGroups) {{
                    markerGroups[group].forEach(marker => marker.addTo(map));
                }}
            }} else if (markerGroups[groupName]) {{
                markerGroups[groupName].forEach(marker => marker.addTo(map));
            }}

            // Update active button style
            document.querySelectorAll('#menu button').forEach(button => {{
                button.classList.remove('active');
            }});
            document.getElementById(`btn-${{groupName}}`).classList.add('active');
        }}

        // Marker data
        const groupedData = {grouped_data};
        const colors = {colors};

        // Create markers and menu buttons
        const allMarkers = [];
        for (const [groupName, locations] of Object.entries(groupedData)) {{
            const color = colors[groupName];
            markerGroups[groupName] = locations.map(([lat, lng]) => {{
                const marker = L.circleMarker([lat, lng], {{
                    radius: 5,
                    fillColor: color,
                    color: color,
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }}).addTo(map); // All markers visible by default for "ALL"
                allMarkers.push(marker);
                return marker;
            }});
        }}
        markerGroups["ALL"] = allMarkers;

        // Create menu buttons
        const menuButtons = ["ALL", ...Object.keys(groupedData)];
        menuButtons.forEach(groupName => {{
            const button = document.createElement('button');
            button.id = `btn-${{groupName}}`;
            button.textContent = groupName;
            button.onclick = () => showOnlyMarkers(groupName);
            if (groupName === "ALL") {{
                button.classList.add('active'); // Set "ALL" as active by default
            }}
            document.getElementById('menu').appendChild(button);
        }});

        // Create a legend control and add it to the map
        const legend = L.control({{ position: 'topright' }});

        legend.onAdd = function (map) {{
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<strong>Encryption Types</strong><br>';

            for (const [groupName, color] of Object.entries(colors)) {{
                const count = groupedData[groupName].length; // Get the count for each encryption type
                div.innerHTML += `
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: ${'{'}color{'}'}"></div>
                        <span>${'{'}groupName{'}'} (${'{'}count{'}'})</span>
                    </div>
                `;
            }}

            return div;
        }};

        legend.addTo(map);
    </script>
</body>
</html>
"""

# Write HTML content to file
with open(html_file, 'w') as file:
    file.write(html_content)

print(f"Interactive OpenStreetMap with 'ALL' menu and legend (including counts) on the map has been successfully generated and saved to {html_file}")
