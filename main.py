import streamlit as st
from google_funcs import download_from_drive

# download database from google drive
download_from_drive('shopping.db')

home_page = st.Page(
    title='Home',
    page='views/home.py',
    default=True
)

pages = [home_page]
pg = st.navigation(pages=pages)
pg.run()
