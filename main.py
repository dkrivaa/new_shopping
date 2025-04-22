import streamlit as st
from google_funcs import download_from_drive

if 'db_loaded' not in st.session_state:
    # Download database from Google Drive
    download_from_drive('shopping.db')
    st.session_state.db_loaded = True

home_page = st.Page(
    title='Home',
    page='views/home.py',
    default=True
)

pages = [home_page]
pg = st.navigation(pages=pages)
pg.run()
