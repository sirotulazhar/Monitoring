import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

# Mengambil variabel dari secrets Streamlit
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]

def get_db_connection():
    """Membuat koneksi ke database PostgreSQL"""
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    return engine

def load_users():
    """Mengambil data dari PostgreSQL"""
    engine = get_db_connection()
    query = "SELECT username, password, role FROM login"
    return pd.read_sql(query, engine)

def authenticate(username, password):
    users = load_users()
    user = users[(users["username"] == username) & (users["password"] == password)]
    if not user.empty:
        return user.iloc[0]["role"]
    return None
