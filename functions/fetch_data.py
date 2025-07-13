import duckdb
import streamlit as st
import geopandas as gpd
from typing import Optional, List

from loguru import logger
from .geo_prep import convert_to_geodf

@st.cache_resource
def connect_to_motherduck() -> duckdb.DuckDBPyConnection:
    """
    Create a database connection object to MotherDuck
    """
    # Define secrets
    database = st.secrets["db"]
    token = st.secrets["token"]

    # Check if token exists
    if token is None:
        raise ValueError("Env variable not present")

    # Connection string
    connection_string = f'md:{database}?motherduck_token={token}'

    # Attempt connection
    try:
        con = duckdb.connect(connection_string)
        return con
    except Exception as e:
        logger.warning(f"An error occured: {e}")
        raise

def get_work_category_filter(selected_categories: Optional[List[str]]) -> str:
    """
    Convert selected normalized categories back to database values for filtering
    """
    if not selected_categories:
        return "1=1"  # No filter
    
    db_categories = []
    
    for category in selected_categories:
        if category == "Major":
            # Include Major and Major (PAA)
            db_categories.extend(["Major", "Major (PAA)"])
        elif category == "Emergency":
            # Include both emergency types
            db_categories.extend(["Immediate - emergency", "Immediate - urgent"])
        elif category == "Standard":
            db_categories.append("Standard")
        elif category == "Minor":
            db_categories.append("Minor")
    
    if db_categories:
        # Create IN clause with proper SQL escaping
        category_list = "', '".join(db_categories)
        return f"work_category IN ('{category_list}')"
    else:
        return "1=1"  # No filter

@st.cache_data
def fetch_data(highway_authority: str, table_name: str, selected_categories: Optional[List[str]] = None) -> gpd.GeoDataFrame:
    """
    Fetch DataFrame containing data for specified highway authority and convert to GeoDataFrame
    """
    # Attempt connection and processing logic
    try:
        con = connect_to_motherduck()
        # Define table and schema
        schema = st.secrets["schema"]
        
        # Build work category filter
        category_filter = get_work_category_filter(selected_categories)
        
        # Execute query for specified highway authority with specific filters
        query = f"""
        SELECT DISTINCT ON (permit_reference_number) *,
               CASE 
                   WHEN work_category IN ('Major', 'Major (PAA)') THEN 'Major'
                   WHEN work_category IN ('Immediate - emergency', 'Immediate - urgent') THEN 'Emergency'
                   WHEN work_category = 'Standard' THEN 'Standard'
                   WHEN work_category = 'Minor' THEN 'Minor'
                   ELSE 'Other'
               END as normalized_work_category
        FROM {schema}."{table_name}"
        WHERE highway_authority = ?
        AND work_status_ref = 'completed'
        AND event_type = 'WORK_STOP'
        AND ({category_filter})
        """
        result = con.execute(query, [highway_authority])
        df = result.fetchdf()
        df = convert_to_geodf(df)
        if df.empty:
            logger.warning(f"The Dataframe is empty for {highway_authority} with the specified filters")
        return df
    except KeyError as ke:
        error_msg = f"Missing key in st.secrets: {ke}"
        logger.error(error_msg)
        raise ke
    except duckdb.Error as quack:
        logger.error(f"A duckdb error occurred: {quack}")
        raise quack
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e

@st.cache_data
def fetch_all_authorities_data(table_name: str, selected_categories: Optional[List[str]] = None) -> gpd.GeoDataFrame:
    """
    Fetch DataFrame containing data for all highway authorities and convert to GeoDataFrame
    """
    try:
        con = connect_to_motherduck()
        schema = st.secrets["schema"]
        
        # Build work category filter
        category_filter = get_work_category_filter(selected_categories)
        
        query = f"""
        SELECT DISTINCT ON (permit_reference_number) *,
               CASE 
                   WHEN work_category IN ('Major', 'Major (PAA)') THEN 'Major'
                   WHEN work_category IN ('Immediate - emergency', 'Immediate - urgent') THEN 'Emergency'
                   WHEN work_category = 'Standard' THEN 'Standard'
                   WHEN work_category = 'Minor' THEN 'Minor'
                   ELSE 'Other'
               END as normalized_work_category
        FROM {schema}."{table_name}"
        WHERE highway_authority IN ('NEWCASTLE CITY COUNCIL', 'SUNDERLAND CITY COUNCIL', 'DARLINGTON BOROUGH COUNCIL', 'DURHAM COUNTY COUNCIL', 'SOUTH TYNESIDE COUNCIL', 'NORTH TYNESIDE COUNCIL')
        AND work_status_ref = 'completed'
        AND event_type = 'WORK_STOP'
        AND ({category_filter})
        """
        result = con.execute(query)
        df = result.fetchdf()
        df = convert_to_geodf(df)
        if df.empty:
            logger.warning(f"The Dataframe is empty for all authorities")
        return df
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e

