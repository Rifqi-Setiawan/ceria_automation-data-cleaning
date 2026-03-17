import streamlit as st
import pandas as pd
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_data(ttl=3600)
def fetch_master_data():
    try:
        supabase = get_supabase_client()
        response = supabase.table("vw_master_data").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch from database: {str(e)}")
        return pd.DataFrame()
