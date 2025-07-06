import duckdb
import streamlit as st
import geopandas as gpd
import pandas as pd

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

@st.cache_data
def fetch_data(highway_authority: str, table_name: str) -> gpd.GeoDataFrame:
    """
    Fetch DataFrame containing data for specified highway authority and convert to GeoDataFrame
    """
    # Attempt connection and processing logic
    try:
        con = connect_to_motherduck()
        # Define table and schema
        schema = st.secrets["schema"]
        # Execute query for specified highway authority with specific filters
        query = f"""
        SELECT DISTINCT ON (permit_reference_number) *
        FROM {schema}."{table_name}"
        WHERE highway_authority = ?
        AND work_status_ref = 'completed'
        AND event_type = 'WORK_STOP'
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

