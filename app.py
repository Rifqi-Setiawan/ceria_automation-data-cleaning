import streamlit as st
import pandas as pd
from pipeline import render_validation_pipeline
from master_data import render_master_data_management

st.set_page_config(
    page_title="CERIA Candidate Data Validation Assistant",
    page_icon="✨",
    layout="wide"
)

if "validation_done" not in st.session_state:
    st.session_state.validation_done = False
if "ready_df" not in st.session_state:
    st.session_state.ready_df = pd.DataFrame()
if "error_df" not in st.session_state:
    st.session_state.error_df = pd.DataFrame()
if "missing_df" not in st.session_state:
    st.session_state.missing_df = pd.DataFrame()

def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8636/8636906.png", width=100) 
    st.sidebar.title("Navigasi CERIA")
    st.sidebar.markdown("Silakan pilih menu:")
    
    menu = st.sidebar.radio(
        "Menu Utama",
        ("1. Data Validation Pipeline", "2. Master Data Management"),
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("*CERIA AI Candidate Assistant*")
    
    if menu == "1. Data Validation Pipeline":
        render_validation_pipeline()
    elif menu == "2. Master Data Management":
        render_master_data_management()

if __name__ == "__main__":
    main()
