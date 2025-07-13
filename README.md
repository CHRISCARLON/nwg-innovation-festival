# Street Works Hex Grid Explorer

A Streamlit application for exploring street works data from multiple highway authorities in the North East of England using H3 hexagonal grids for spatial analysis.

## Overview

This app visualises completed street works data using H3 hexagonal grids.

Street works are grouped into hexagonal cells at various resolution levels, allowing you to explore patterns and density across different geographical scales.

## Features

### H3 Hexagonal Grid Analysis

- **Multi-Resolution Grids**: Choose from 6 different H3 resolution levels (6-11) ranging from regional (~3.2km) to street-level (~25m) detail
- **Spatial Aggregation**: Street works are aggregated into hexagonal cells showing work counts and unique permits
- **Interactive Visualisation**: Color-coded hexagons with tooltips showing detailed statistics
- **Activity Analysis**: View the most active hexagons and activity type distributions

### Data Visualisation Options

- **H3 Hex Grid** (Default): Advanced hexagonal spatial analysis with configurable resolution
- **Points/Lines**: Traditional point and line visualisation for raw data exploration

### Multi-Authority Support

- **Individual Authorities**: Newcastle, Sunderland, Darlington, Durham County Council
- **Combined Analysis**: "All Authorities" option for regional overview
- **Monthly Data**: Select data from January to June 2025

### Interactive Features

- **Color Coding**: Choose to color hexagons by total work count or unique permits
- **Summary Statistics**: Real-time metrics showing hexagon counts, work totals, and averages
- **Top Hexagons**: Table showing the most active hexagonal areas
- **Responsive Maps**: Auto-fitting maps with detailed tooltips

## H3 Resolution Levels

| Level | Average Edge | Description  | Best For                      |
| ----- | ------------ | ------------ | ----------------------------- |
| 6     | ~3.2km       | Regional     | City-wide patterns            |
| 7     | ~1.2km       | District     | Area analysis                 |
| 8     | ~460m        | Locality     | Standard resolution (default) |
| 9     | ~170m        | Neighborhood | Detailed view                 |
| 10    | ~65m         | Block        | High detail                   |
| 11    | ~25m         | Street       | Maximum detail                |

## Setup

1. **Create Virtual Environment**

   ```bash
   uv venv
   ```

2. **Install Dependencies**

   ```bash
   poetry install --no-root
   ```

3. **Activate Virtual Environment**

   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

4. **Configure Database Connection**

   - Update `.streamlit/secrets.toml` with your MotherDuck credentials:

   ```toml
   db = "your_database_name"
   token = "your_motherduck_token"
   schema = "raw_data_2025"
   ```

5. **Run the App**
   ```bash
   streamlit run main.py
   ```

## Usage

1. **Select Highway Authority**: Choose from individual councils or "All Authorities"
2. **Choose Month**: Select data from January to June 2025
3. **Pick Visualisation**: Choose "H3 Hex Grid" (recommended) or "Points/Lines"
4. **Configure H3 Settings** (for hex grid):
   - Select grid resolution level (6-11)
   - Choose color coding (work count or unique permits)
5. **Load Data**: Click the load button to generate the visualization
6. **Explore Results**:
   - View summary statistics
   - Interact with the color-coded map
   - Examine top active hexagons

## Data Processing

The app processes completed street works data with the following filters:

- Work status = 'completed'
- Event type = 'WORK_STOP'
- Data is deduplicated by permit reference number

For H3 analysis, the app:

- Converts point/line geometries to centroids
- Maps coordinates to H3 hexagonal cells
- Aggregates work counts and unique permits per hexagon
- Generates hexagon boundaries for visualization

## Technical Stack

- **Frontend**: Streamlit with Folium for interactive maps
- **Spatial Processing**: H3 hexagonal indexing system via DuckDB
- **Data Processing**: GeoPandas, Pandas
- **Database**: MotherDuck (cloud DuckDB)
- **Mapping**: Folium with custom styling and tooltips

## Requirements

- Python 3.11+
- uv (for virtual environment)
- Poetry (for dependency management)
- MotherDuck database access
- DuckDB with H3 extension support
