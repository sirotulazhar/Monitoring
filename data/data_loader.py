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
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        try:
            engine = create_engine( DATABASE_URL)
            conn = engine.connect()
            print("Koneksi berhasil!")
            conn.close()
        except Exception as e:
            print(f"Error koneksi: {e}")
                
        engine = create_engine(DATABASE_URL)
        return engine

def load_data():
    """Mengambil data dari PostgreSQL"""
    engine = get_db_connection()
    query = """
    SELECT waktu, payment_method, prov_sekolah, kota_kab_sekolah, jumlah_po, nominal_po, pph22, ppn, total_pajak
    FROM regions_and_payment_methods;
    """
    df = pd.read_sql(query, engine)
    df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
    df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
    df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
    df['payment_method'] = df['payment_method'].str.strip().str.lower()
    return df

DATASETS = {
    "merchant registered.csv": ["waktu", "provinsi", "kab_kota", "jumlah_merchant"],
    "regions and payment methods.csv": ["waktu", "payment_method", "prov_sekolah", "kota_kab_sekolah", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"],
}

def preprocess_data(df, file_type):
    """Fungsi untuk melakukan preprocessing berdasarkan jenis file."""

    if file_type == "regions_payment":
        df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce').dt.strftime('%m/%d/%Y')
        df = df.sort_values(by='waktu', ascending=True).reset_index(drop=True)
        df['waktu']
        df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
        df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
        df['payment_method'] = df['payment_method'].str.strip().str.lower()
        df['nominal_po'] = df['nominal_po'].astype(str).str.replace(',', '.', regex=True)
        df['nominal_po'] = pd.to_numeric(df['nominal_po'], errors='coerce')
        df['ppn'] = df['ppn'].astype(str).str.replace(',', '.', regex=True)
        df['ppn'] = pd.to_numeric(df['ppn'], errors='coerce')
        df['pph22'] = df['pph22'].astype(str).str.replace(',', '.', regex=True)
        df['pph22'] = pd.to_numeric(df['pph22'], errors='coerce')
        if "total_pajak" not in df.columns:
            df["total_pajak"] = df["pph22"] + df["ppn"]

    elif file_type == "merchant_registered":
        df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce').dt.strftime('%m/%d/%Y') 
        df = df.sort_values(by='waktu', ascending=True).reset_index(drop=True)
        df['waktu']
        df['provinsi'] = df['provinsi'].str.strip().str.title()
        df['kab_kota'] = df['kab_kota'].str.strip().str.title()
    
    df.fillna(method='ffill', inplace=True)
    
    return df

def save_to_postgres(df, table_name):
    """Menyimpan data ke PostgreSQL."""
    engine = get_db_connection()
    
    with engine.connect() as conn:
        df.to_sql(table_name, con=conn, index=False, if_exists="append")
    
    return f"✅ Data berhasil dimasukkan ke tabel '{table_name}'"
