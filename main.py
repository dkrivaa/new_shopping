import streamlit as st
from database import create_db

# Check if database exist, create if not
create_db('shopping.db')

home_page = st.Page(
    title='Home',
    page='views/home.py',
    default=True
)

pages = [home_page]
pg = st.navigation(pages=pages)
pg.run()
