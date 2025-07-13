import streamlit as st
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
    st.title("Explore Street Works Data")
    st.markdown("#### Select a highway authority and month, then choose a visualisation type.")

    # Highway authority options
    highway_authorities = [
        "All Authorities",
        "NEWCASTLE CITY COUNCIL",
        "SUNDERLAND CITY COUNCIL", 
        "DARLINGTON BOROUGH COUNCIL",
        "DURHAM COUNTY COUNCIL"
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
    
    # Layout
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_authority = st.selectbox(
            "Select Highway Authority:",
            options=highway_authorities
        )
    
    with col2:
        selected_month = st.selectbox(
            "Select Month:",
            options=list(months.keys()),
            index=5  # Default to June 2025
        )
    
    with col3:
        vis_type = st.selectbox(
            "Visualization Type:",
            options=["Points/Lines", "H3 Hex Grid"],
            index=1  # Default to H3 Grid
        )
    
    # H3 Resolution selection (only show if H3 is selected)
    if vis_type == "H3 Hex Grid":
        st.subheader("H3 Grid Settings")
        resolution_info = get_h3_resolution_info()
        
        col1, col2 = st.columns(2)
        with col1:
            resolution = st.selectbox(
                "Grid Resolution:",
                options=list(resolution_info.keys()),
                index=2,  # Default to resolution 8
                format_func=lambda x: f"Level {x}: {resolution_info[x]['description']}"
            )
        
        with col2:
            color_by = st.selectbox(
                "Color hexagons by:",
                options=["work_count", "unique_permits"],
                format_func=lambda x: "Total Works" if x == "work_count" else "Unique Permits"
            )

    if st.button(f"Load {selected_authority} Data for {selected_month}"):
        try:
            table_name = months[selected_month]
            
            if vis_type == "Points/Lines":
                if selected_authority == "All Authorities":
                    geodf = fetch_all_authorities_data(table_name)
                else:
                    geodf = fetch_data(selected_authority, table_name)
                
                if not geodf.empty:
                    st.success(f"Loaded {len(geodf)} records for {selected_authority} - {selected_month}")
                    plot_map_england(geodf)
                else:
                    st.warning(f"No data available for {selected_authority} - {selected_month}")
            
            else:  # H3 Hex Grid
                if selected_authority == "All Authorities":
                    geodf = create_h3_hex_grid_all_authorities(table_name, resolution)
                else:
                    geodf = create_h3_hex_grid(selected_authority, table_name, resolution)
                
                if not geodf.empty:
                    total_works = int(geodf['work_count'].sum()) # type: ignore
                    st.success(f"Generated {len(geodf)} hexagons with {total_works} total works for {selected_authority} - {selected_month}")
                    plot_h3_map(geodf, color_by)
                else:
                    st.warning(f"No H3 data generated for {selected_authority} - {selected_month}")
        
        except Exception as e:
            st.error(f"Error processing data: {e}")
            st.exception(e)

if __name__ == "__main__":
    main()
