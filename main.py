import streamlit as st
import pandas as pd
import geopandas as gpd
from functions.fetch_data import fetch_data, fetch_all_authorities_data
from functions.map_prep_england import plot_map_england
from functions.h3_processing import create_h3_hex_grid, create_h3_hex_grid_all_authorities, get_h3_resolution_info
from functions.map_prep_h3 import plot_h3_map

# Set page config as wide by default
st.set_page_config(layout="wide")

def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom CSS
load_css(".streamlit/style.css") 

def main():
    """
    Streamlit Application Launch
    """
    st.title("Hex Grid Visualisations of Street Works Data")
    st.markdown("#### Select highway authorities, months, work categories, then choose a visualisation type.")

    # Highway authority options
    highway_authorities = [
        "NEWCASTLE CITY COUNCIL",
        "SUNDERLAND CITY COUNCIL", 
        "DARLINGTON BOROUGH COUNCIL",
        "DURHAM COUNTY COUNCIL",
        "SOUTH TYNESIDE COUNCIL",
        "NORTH TYNESIDE COUNCIL"
    ]
    
    # Month options
    months = {
        "January 2025": "01_2025",
        "February 2025": "02_2025", 
        "March 2025": "03_2025",
        "April 2025": "04_2025",
        "May 2025": "05_2025",
        "June 2025": "06_2025"
    }
    
    # Work category options (normalized)
    work_categories = [
        "Major",
        "Standard", 
        "Emergency",
        "Minor"
    ]
    
    # Layout - First row for main selections
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Highway Authorities**")
        # Add "Select All" checkbox for highway authorities
        select_all_authorities = st.checkbox("Select All Highway Authorities")
        
        if select_all_authorities:
            selected_authorities = highway_authorities
            # Show selected authorities in a more compact way
            st.multiselect(
                "Selected Authorities:",
                options=highway_authorities,
                default=highway_authorities,
                disabled=True,
                key="disabled_authorities"
            )
        else:
            selected_authorities = st.multiselect(
                "Select Highway Authorities:",
                options=highway_authorities,
                default=["NEWCASTLE CITY COUNCIL"]  # Default selection
            )
    
    with col2:
        st.write("**Months**")
        # Add "Select All" checkbox for months
        select_all_months = st.checkbox("Select All Months")
        
        if select_all_months:
            selected_months = list(months.keys())
            # Show selected months in a more compact way
            st.multiselect(
                "Selected Months:",
                options=list(months.keys()),
                default=list(months.keys()),
                disabled=True,
                key="disabled_months"
            )
        else:
            selected_months = st.multiselect(
                "Select Months:",
                options=list(months.keys()),
                default=["June 2025"]  # Default selection
            )
    
    with col3:
        st.write("**Work Categories**")
        # Add "Select All" checkbox for work categories
        select_all_categories = st.checkbox("Select All Work Categories")
        
        if select_all_categories:
            selected_categories = work_categories
            # Show selected categories in a more compact way
            st.multiselect(
                "Selected Categories:",
                options=work_categories,
                default=work_categories,
                disabled=True,
                key="disabled_categories"
            )
        else:
            selected_categories = st.multiselect(
                "Select Work Categories:",
                options=work_categories,
                default=work_categories  # Default to all categories
            )
    
    # Second row for visualization settings
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Visualization Type**")
        vis_type = st.selectbox(
            "Choose Visualization:",
            options=["Points/Lines", "H3 Hex Grid"],
            index=1  # Default to H3 Grid
        )
    
    # H3 Resolution selection (only show if H3 is selected)
    if vis_type == "H3 Hex Grid":
        with col2:
            st.write("**H3 Grid Settings**")
            resolution_info = get_h3_resolution_info()
            
            resolution = st.selectbox(
                "Grid Resolution:",
                options=list(resolution_info.keys()),
                index=2,  # Default to resolution 8
                format_func=lambda x: f"Level {x}: {resolution_info[x]['description']}"
            )
        
        # Color by option in a separate row
        st.write("**Color Settings**")
        color_by = st.selectbox(
            "Color hexagons by:",
            options=["work_count", "unique_permits"],
            format_func=lambda x: "Total Works" if x == "work_count" else "Unique Permits"
        )

    # Validation
    if not selected_authorities:
        st.warning("Please select at least one highway authority.")
        return
    
    if not selected_months:
        st.warning("Please select at least one month.")
        return
        
    if not selected_categories:
        st.warning("Please select at least one work category.")
        return

    # Create descriptive button text
    auth_text = "All Authorities" if select_all_authorities else f"{len(selected_authorities)} Authorities"
    month_text = "All Months" if select_all_months else f"{len(selected_months)} Months"
    category_text = "All Categories" if select_all_categories else f"{len(selected_categories)} Categories"
    
    if st.button(f"Load Data for {auth_text} - {month_text} - {category_text}"):
        with st.spinner("Loading data and generating visualization..."):
            try:
                all_geodfs = []
                
                # Create a progress bar for processing combinations
                total_combinations = len(selected_authorities) * len(selected_months)
                progress_bar = st.progress(0)
                current_combination = 0
                
                # Process each combination of authority and month
                for authority in selected_authorities:
                    for month_display in selected_months:
                        table_name = months[month_display]
                        
                        # Update progress
                        current_combination += 1
                        progress_text = f"Processing {authority} - {month_display} ({current_combination}/{total_combinations})"
                        progress_bar.progress(current_combination / total_combinations, text=progress_text)
                        
                        if vis_type == "Points/Lines":
                            with st.spinner(f"Fetching data for {authority} - {month_display}..."):
                                geodf = fetch_data(authority, table_name, selected_categories)
                                if not geodf.empty:
                                    # Add metadata for identification
                                    geodf['authority'] = authority
                                    geodf['month'] = month_display
                                    all_geodfs.append(geodf)
                        
                        else:  # H3 Hex Grid
                            with st.spinner(f"Creating H3 grid for {authority} - {month_display}..."):
                                geodf = create_h3_hex_grid(authority, table_name, resolution, selected_categories)
                                if not geodf.empty:
                                    # Add metadata for identification
                                    geodf['authority'] = authority
                                    geodf['month'] = month_display
                                    all_geodfs.append(geodf)
                
                # Clear progress bar
                progress_bar.empty()
                
                if all_geodfs:
                    with st.spinner("Combining and processing data..."):
                        # Combine all data - use pd.concat first, then convert to GeoDataFrame
                        combined_df = pd.concat(all_geodfs, ignore_index=True)
                        combined_geodf = gpd.GeoDataFrame(combined_df, geometry='geometry', crs="EPSG:4326") # type: ignore
                
                    # Display the visualization
                    if vis_type == "Points/Lines":
                        with st.spinner("Generating map visualization..."):
                            plot_map_england(combined_geodf)
                    else:  # H3 Hex Grid
                        # For H3, we need to re-aggregate the combined data
                        # since we might have overlapping hexagons from different authorities/months
                        if len(selected_authorities) > 1 or len(selected_months) > 1:
                            with st.spinner("Re-aggregating overlapping hexagons..."):
                                # Re-aggregate overlapping hexagons
                                aggregated_df = combined_geodf.groupby('h3_cell').agg({
                                    'work_count': 'sum',
                                    'unique_permits': 'sum',
                                    'activity_types': lambda x: list(set([item for sublist in x for item in sublist])),  # Flatten and deduplicate
                                    'geometry': 'first'  # Use first geometry (they should be identical for same h3_cell)
                                }).reset_index()
                                
                                # Recreate GeoDataFrame with explicit type conversion
                                final_geodf = gpd.GeoDataFrame(
                                    aggregated_df, 
                                    geometry='geometry', 
                                    crs="EPSG:4326"
                                ) # type: ignore
                                
                                # Convert to float first, then int with proper type handling
                                total_works_value = final_geodf['work_count'].sum()
                                total_works = int(float(total_works_value)) if pd.notna(total_works_value) else 0 # type: ignore
                                st.success(f"Generated {len(final_geodf)} unique hexagons with {total_works} total works")
                            
                            with st.spinner("Generating H3 hexagon map..."):
                                plot_h3_map(final_geodf, color_by)
                        else:
                            # Single authority and month, no need to re-aggregate
                            total_works_value = combined_geodf['work_count'].sum()
                            total_works = int(float(total_works_value)) if pd.notna(total_works_value) else 0 # type: ignore
                            st.success(f"Generated {len(combined_geodf)} hexagons with {total_works} total works")
                            
                            with st.spinner("Generating H3 hexagon map..."):
                                plot_h3_map(combined_geodf, color_by)
                    
                    with st.spinner("Generating summary tables..."):
                        # Show summary by authority, month, and category
                        st.subheader("Data Summary")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if 'authority' in combined_geodf.columns and 'month' in combined_geodf.columns:
                                summary = combined_geodf.groupby(['authority', 'month']).size().reset_index().rename(columns={0: 'record_count'})
                                st.write("**Records by Authority and Month:**")
                                st.dataframe(summary, use_container_width=True)
                        
                        with col2:
                            if 'normalized_work_category' in combined_geodf.columns:
                                category_summary = combined_geodf.groupby('normalized_work_category').size().reset_index().rename(columns={0: 'record_count'})
                                st.write("**Records by Work Category:**")
                                st.dataframe(category_summary, use_container_width=True)
                    
                else:
                    st.warning("No data found for the selected authorities, months, and work categories.")
            
            except Exception as e:
                st.error(f"Error processing data: {e}")
                st.exception(e)

if __name__ == "__main__":
    main()
