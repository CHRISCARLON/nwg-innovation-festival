import streamlit as st
from functions.fetch_data import fetch_data
from functions.map_prep_england import plot_map_england

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
    st.markdown("#### Select a highway authority and month, then click the button to load and display the data on the map.")

    # Highway authority options
    highway_authorities = [
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
    
    col1, col2 = st.columns(2)
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

    if st.button(f"Load {selected_authority} Data for {selected_month}"):
        try:
            table_name = months[selected_month]
            geodf = fetch_data(selected_authority, table_name)
            
            if not geodf.empty:
                st.success(f"Loaded {len(geodf)} records for {selected_authority} - {selected_month}")
                plot_map_england(geodf)
            else:
                st.warning(f"No data available for {selected_authority} - {selected_month}")
        
        except Exception as e:
            st.error(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
