import folium
import geopandas as gpd
import streamlit as st
import numpy as np
from branca.colormap import LinearColormap
from streamlit_folium import folium_static
from loguru import logger

def plot_h3_map(geodf: gpd.GeoDataFrame, color_by: str = 'work_count'):
    """
    Plot H3 hexagonal grid on a map with color coding
    
    Args:
        geodf: GeoDataFrame containing H3 hexagons
        color_by: Column to use for color coding ('work_count' or 'unique_permits')
    """
    try:
        if geodf.empty:
            st.warning("No H3 data to display")
            return
            
        # Get the bounds of all geometries
        total_bounds = geodf.total_bounds
        
        # Create the map
        m = folium.Map(tiles="cartodbpositron")
        m.fit_bounds([[total_bounds[1], total_bounds[0]], [total_bounds[3], total_bounds[2]]])
        
        # Prepare color mapping
        values = np.array(geodf[color_by].values, dtype=float)
        min_val, max_val = float(values.min()), float(values.max())
        
        # Create colormap
        colormap = LinearColormap(
            colors=['#E6F3FF', '#B3D9FF', '#80BFFF', '#4D9FFF', '#1A7FFF', '#0066CC'],
            vmin=min_val,
            vmax=max_val,
            caption=f'{color_by.replace("_", " ").title()}'
        )
        
        # Add hexagons to map
        for _, row in geodf.iterrows():
            if row.geometry is not None and not row.geometry.is_empty:
                color_value = row[color_by]
                fill_color = colormap(color_value)
                
                tooltip_content = f"""
                <b>H3 Cell:</b> {row.get('h3_cell', 'N/A')}<br>
                <b>Total Works:</b> {row.get('work_count', 0)}<br>
                <b>Unique Permits:</b> {row.get('unique_permits', 0)}<br>
                """
                folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda x, color=fill_color: {
                        'fillColor': color,
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7,
                        'opacity': 0.8
                    },
                    tooltip=folium.Tooltip(tooltip_content, max_width=300)
                ).add_to(m)
        
        # Add colormap to map
        colormap.add_to(m)
        
        # Show summary statistics BEFORE the map
        st.subheader("H3 Grid Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Hexagons", len(geodf))
        with col2:
            st.metric("Total Works", int(geodf['work_count'].sum())) # type: ignore
        with col3:
            avg_works = float(geodf['work_count'].mean()) # type: ignore
            st.metric("Avg Works per Hex", f"{avg_works:.1f}")
        with col4:
            st.metric("Max Works in Hex", int(geodf['work_count'].max())) # type: ignore
        
        # Display map
        folium_static(m, width=None, height=600)
        
        # Show top hexagons by activity
        st.subheader("Most Active Hexagons")
        top_hexes = geodf.nlargest(10, 'work_count')[['h3_cell', 'work_count', 'unique_permits', 'activity_types']]
        st.dataframe(top_hexes, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error plotting H3 map: {e}")
        raise 