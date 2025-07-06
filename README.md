# Street Works Data Explorer

A Streamlit application for exploring street works data from multiple highway authorities in the North East of England.

## Overview

This app allows you to visualise completed street works data on an interactive map.

You can filter by highway authority and month to explore different datasets.

## Features

- **Interactive Map**: View street works locations on a map with tooltips showing permit details
- **Multiple Authorities**: Choose from Newcastle, Sunderland, Darlington, or Durham
- **Monthly Data**: Select data from January to June 2025
- **Data Table**: View raw data below the map

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

1. Select a highway authority from the dropdown
2. Choose a month (January - June 2025)
3. Click the "Load Data" button
4. Explore the map and data table below

## Data

The app displays completed street works where:

- Work status = 'completed'
- Event type = 'WORK_STOP'
- Data is deduplicated by permit reference number

## Requirements

- Python 3.11+
- uv (for virtual environment)
- Poetry (for dependency management)
- MotherDuck database access
