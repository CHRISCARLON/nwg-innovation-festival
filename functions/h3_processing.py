import duckdb
import streamlit as st
import geopandas as gpd
import pandas as pd

from .fetch_data import fetch_data, fetch_all_authorities_data
from loguru import logger


@st.cache_data
def get_h3_resolution_info():
    """
    Return information about H3 resolution levels for user selection
    """
    return {
        6: {"avg_edge_km": 3.23, "description": "Regional (~3.2km) - Good for city-wide patterns"},
        7: {"avg_edge_km": 1.22, "description": "District (~1.2km) - Ideal for area analysis"},
        8: {"avg_edge_km": 0.46, "description": "Locality (~460m) - Standard resolution"},
        9: {"avg_edge_km": 0.17, "description": "Neighborhood (~170m) - Detailed view"},
        10: {"avg_edge_km": 0.065, "description": "Block (~65m) - High detail"},
        11: {"avg_edge_km": 0.025, "description": "Street (~25m) - Maximum detail"}
    }

@st.cache_data
def create_h3_hex_grid(highway_authority: str, table_name: str, resolution: int = 9) -> gpd.GeoDataFrame:
    """
    Create H3 hexagonal grid from street works data using Python processing
    
    Args:
        highway_authority: The highway authority to filter data for
        table_name: The table name to query
        resolution: H3 resolution level (0-15, higher = smaller hexes)
                   9 is good for city-level analysis (~105m avg edge length)
    
    Returns:
        GeoDataFrame with H3 hexagons and aggregated data
    """
    try:
        geodf_points = fetch_data(highway_authority, table_name)
        
        if geodf_points.empty:
            logger.warning(f"No point data found for {highway_authority}")
            return gpd.GeoDataFrame()
        
        # Extract coordinates from geometries in Python
        coords_data = []
        for _, row in geodf_points.iterrows():
            geom = row.geometry
            if geom is not None and not geom.is_empty:
                if hasattr(geom, 'centroid'):
                    # For lines, use centroid
                    point = geom.centroid
                else:
                    # For points, use directly
                    point = geom
                
                lat, lon = point.y, point.x
                coords_data.append({
                    'permit_reference_number': row.get('permit_reference_number'),
                    'activity_type': row.get('activity_type'),
                    'latitude': lat,
                    'longitude': lon
                })
        
        if not coords_data:
            logger.warning(f"No valid coordinates extracted for {highway_authority}")
            return gpd.GeoDataFrame()
        
        # Create DataFrame with coordinates
        coords_df = pd.DataFrame(coords_data)
        
        # Create a new DuckDB connection for H3 processing
        con = duckdb.connect(':memory:')
        
        # Install and load H3 extension
        con.execute("INSTALL h3 FROM community;")
        con.execute("LOAD h3;")
        
        # Register the pandas DataFrame as a table
        con.register('coords_data', coords_df)
        
        # Create H3 cells and aggregate using the correct function names
        h3_query = f"""
        WITH h3_cells AS (
            SELECT 
                h3_latlng_to_cell_string(latitude, longitude, {resolution}) as h3_cell,
                permit_reference_number,
                activity_type,
                latitude,
                longitude
            FROM coords_data
            WHERE latitude IS NOT NULL 
            AND longitude IS NOT NULL
            AND latitude BETWEEN -90 AND 90
            AND longitude BETWEEN -180 AND 180
        ),
        aggregated AS (
            SELECT 
                h3_cell,
                COUNT(*) as work_count,
                COUNT(DISTINCT permit_reference_number) as unique_permits,
                LIST(DISTINCT activity_type) as activity_types,
                AVG(latitude) as center_lat,
                AVG(longitude) as center_lng
            FROM h3_cells
            GROUP BY h3_cell
        )
        SELECT 
            h3_cell,
            work_count,
            unique_permits,
            activity_types,
            center_lat,
            center_lng,
            h3_cell_to_boundary_wkt(h3_string_to_h3(h3_cell)) as hex_geometry
        FROM aggregated
        ORDER BY work_count DESC
        """
        
        result = con.execute(h3_query)
        df = result.fetchdf()
        
        # Close the connection
        con.close()
        
        if df.empty:
            logger.warning(f"No H3 data generated for {highway_authority}")
            return gpd.GeoDataFrame()
        
        # Convert WKT hex boundaries to geometry
        df['geometry'] = gpd.GeoSeries.from_wkt(df['hex_geometry'])
        
        # Create GeoDataFrame
        geodf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326") # type: ignore
        
        logger.info(f"Generated {len(geodf)} H3 hexagons for {highway_authority}")
        return geodf
        
    except Exception as e:
        logger.error(f"Error creating H3 hex grid: {e}")
        raise e

@st.cache_data
def create_h3_hex_grid_all_authorities(table_name: str, resolution: int = 9) -> gpd.GeoDataFrame:
    """
    Create H3 hexagonal grid from all highway authorities data
    """
    try:
        geodf_points = fetch_all_authorities_data(table_name)
        
        if geodf_points.empty:
            return gpd.GeoDataFrame()
        
        # Extract coordinates from geometries in Python
        coords_data = []
        for _, row in geodf_points.iterrows():
            geom = row.geometry
            if geom is not None and not geom.is_empty:
                if hasattr(geom, 'centroid'):
                    # For lines, use centroid
                    point = geom.centroid
                else:
                    # For points, use directly
                    point = geom
                
                lat, lon = point.y, point.x
                coords_data.append({
                    'permit_reference_number': row.get('permit_reference_number'),
                    'activity_type': row.get('activity_type'),
                    'latitude': lat,
                    'longitude': lon
                })
        
        if not coords_data:
            logger.warning(f"No valid coordinates extracted for all authorities")
            return gpd.GeoDataFrame()
        
        # Create DataFrame with coordinates
        coords_df = pd.DataFrame(coords_data)
        
        # Create a new DuckDB connection for H3 processing
        con = duckdb.connect(':memory:')
        
        # Install and load H3 extension
        con.execute("INSTALL h3 FROM community;")
        con.execute("LOAD h3;")
        
        # Register the pandas DataFrame as a table
        con.register('coords_data', coords_df)
        
        # Create H3 cells and aggregate using the correct function names
        h3_query = f"""
        WITH h3_cells AS (
            SELECT 
                h3_latlng_to_cell_string(latitude, longitude, {resolution}) as h3_cell,
                permit_reference_number,
                activity_type,
                latitude,
                longitude
            FROM coords_data
            WHERE latitude IS NOT NULL 
            AND longitude IS NOT NULL
            AND latitude BETWEEN -90 AND 90
            AND longitude BETWEEN -180 AND 180
        ),
        aggregated AS (
            SELECT 
                h3_cell,
                COUNT(*) as work_count,
                COUNT(DISTINCT permit_reference_number) as unique_permits,
                LIST(DISTINCT activity_type) as activity_types,
                AVG(latitude) as center_lat,
                AVG(longitude) as center_lng
            FROM h3_cells
            GROUP BY h3_cell
        )
        SELECT 
            h3_cell,
            work_count,
            unique_permits,
            activity_types,
            center_lat,
            center_lng,
            h3_cell_to_boundary_wkt(h3_string_to_h3(h3_cell)) as hex_geometry
        FROM aggregated
        ORDER BY work_count DESC
        """
        
        result = con.execute(h3_query)
        df = result.fetchdf()
        
        # Close the connection
        con.close()
        
        if df.empty:
            logger.warning(f"No H3 data generated for all authorities")
            return gpd.GeoDataFrame()
        
        # Convert WKT hex boundaries to geometry
        df['geometry'] = gpd.GeoSeries.from_wkt(df['hex_geometry'])
        
        # Create GeoDataFrame
        geodf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326") # type: ignore
        
        logger.info(f"Generated {len(geodf)} H3 hexagons for all authorities")
        return geodf
        
    except Exception as e:
        logger.error(f"Error creating H3 hex grid for all authorities: {e}")
        raise e