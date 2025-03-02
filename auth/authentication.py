import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import os

# Mengambil konfigurasi dari secrets
db_secrets = st.secrets.get("connections", {}).get("postgresql", {})

DB_USER = db_secrets.get("DB_USER", "")
DB_PASSWORD = db_secrets.get("DB_PASSWORD", "")
DB_HOST = db_secrets.get("DB_HOST", "")
DB_PORT = db_secrets.get("DB_PORT", "")
DB_NAME = db_secrets.get("DB_NAME", "")

def get_db_connection():
        """Membuat koneksi ke database PostgreSQL"""
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        return engine

def load_users():
    """Mengambil data dari PostgreSQL"""
    engine = get_db_connection()
    query = """
    SELECT username, password, role
    FROM login
    """
    return pd.read_sql(query, engine)

def authenticate(username, password):
    users = load_users()
    user = users[(users["username"] == username) & (users["password"] == password)]
    if not user.empty:
        return user.iloc[0]["role"]
    return None
