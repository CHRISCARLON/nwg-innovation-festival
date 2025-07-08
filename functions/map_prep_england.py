import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
from loguru import logger

def plot_map_england(geodf):
    try:
        if not isinstance(geodf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame")

        # Get the bounds of all geometries in the geodataframe
        total_bounds = geodf.total_bounds

        # Create the map and set bounds to the data area
        m = folium.Map(tiles="cartodbpositron")
        m.fit_bounds([[total_bounds[1], total_bounds[0]], [total_bounds[3], total_bounds[2]]])

        # Add features to map - simple markers for points or lines
        for _, row in geodf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda x: {
                        'color': '#1f77b4',
                        'weight': 3,
                        'opacity': 0.8
                    },
                    tooltip=folium.Tooltip(
                        f"Permit: {row.get('permit_reference_number', 'N/A')}<br>"
                        f"Work Status: {row.get('work_status_ref', 'N/A')}<br>"
                        f"Event Type: {row.get('event_type', 'N/A')}<br>"
                        f"Activity Type: {row.get('activity_type', 'N/A')}<br>"
                    )
                ).add_to(m)

        # Display map using folium_static - responsive width
        folium_static(m, width=None, height=600)

        # Show basic data info
        st.subheader("Data Summary")
        st.write(f"Total records: {len(geodf)}")
        
        # Show the dataframe without geometry column to avoid Arrow conversion issues
        # You wouldn't really need to display the geometry column anyway
        st.subheader("Raw Data")
        display_df = geodf.drop(columns=['geometry'])
        st.dataframe(display_df)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise
