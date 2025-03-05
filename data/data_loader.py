import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

conn = st.connection("gsheets", type=GSheetsConnection)


def load_data(sheet_name):
    """Mengambil data dari Google Sheets berdasarkan nama sheet."""
    df = conn.read(worksheet=sheet_name)

    return df

def load_regions_data():
    df = load_data("regions and payment methods")
    df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
    df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
    df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
    df['payment_method'] = df['payment_method'].str.strip().str.lower()
    
    return df

def load_merchant():
    df = load_data("merchant registered")
    df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
    df['provinsi'] = df['provinsi'].str.strip().str.title()
    df['kab_kota'] = df['kab_kota'].str.strip().str.title()
    if "jumlah_merchant" in df.columns:
        df["jumlah_merchant"] = pd.to_numeric(df["jumlah_merchant"], errors="coerce").fillna(0).astype(int)
    return df

def load_users():
    """Mengambil data username, password, dan role dari sheet 'login'."""
    df = load_data("login")
    return df

def load_transaksi():
    df = load_data("Harian")

    def parse_mixed_date(date_str):
        try:
            # Coba parsing sebagai format DD/MM/YYYY
            return pd.to_datetime(date_str, format="%d/%m/%Y")
        except ValueError:
            try:
                # Jika gagal, coba parsing sebagai format YYYY-MM-DD
                return pd.to_datetime(date_str, format="%Y-%m-%d")
            except ValueError:
                return pd.NaT  # Jika masih gagal, set sebagai NaT

    # Terapkan fungsi parsing ke kolom "Tanggal"
    df["Tanggal"] = df["Tanggal"].astype(str).apply(parse_mixed_date)

    df["Bulan"] = df["Tanggal"].dt.to_period("M")
    hari_mapping = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    df["Hari"] = df["Tanggal"].dt.day_name().map(hari_mapping)
    return df

def load_harian():
    df = load_data("regions and payment methods")
    df["waktu"] = pd.to_datetime(df["waktu"])
    df["Bulan"] = df["waktu"].dt.to_period("M")
    hari_mapping = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    df["Hari"] = df["waktu"].dt.day_name().map(hari_mapping)
    return df

# Struktur dataset yang diizinkan
DATASETS = {
    "merchant registered.csv": ["waktu", "provinsi", "kab_kota", "jumlah_merchant"],
    "regions and payment methods.csv": ["waktu", "payment_method", "prov_sekolah", "kota_kab_sekolah", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"],
    "Harian.csv": ["Bulan", "Tanggal", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"]
}

def preprocess_data(df, file_type):
    """Fungsi untuk melakukan preprocessing berdasarkan jenis file."""

    if file_type == "regions_payment":
        df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce').dt.strftime('%m/%d/%Y')
        df['waktu'].fillna(df['waktu'].fillna(method='ffill'), inplace=True)
        df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
        df['prov_sekolah'].fillna(df['prov_sekolah'].mode()[0], inplace=True)
        df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
        df['kota_kab_sekolah'].fillna(df['kota_kab_sekolah'].mode()[0], inplace=True)
        df['payment_method'] = df['payment_method'].str.strip()
        df['payment_method'].fillna(df['payment_method'].mode()[0], inplace=True)
        df['nominal_po'] = df['nominal_po'].astype(str).str.replace(',', '.', regex=True)
        df['nominal_po'] = pd.to_numeric(df['nominal_po'], errors='coerce')
        df['nominal_po'].fillna(df['nominal_po'].median(), inplace=True)
        df['ppn'] = df['ppn'].astype(str).str.replace(',', '.', regex=True)
        df['ppn'] = pd.to_numeric(df['ppn'], errors='coerce')
        df['ppn'].fillna(df['ppn'].median(), inplace=True)
        df['pph22'] = df['pph22'].astype(str).str.replace(',', '.', regex=True)
        df['pph22'] = pd.to_numeric(df['pph22'], errors='coerce')
        df['pph22'].fillna(df['pph22'].median(), inplace=True)
        df["jumlah_po"] = pd.to_numeric(df["jumlah_po"], errors="coerce").fillna(0).astype(int)
        df['jumlah_po'].fillna(df['jumlah_po'].median(), inplace=True)
        if "total_pajak" not in df.columns:
            df["total_pajak"] = df["pph22"] + df["ppn"]

    # .dt.date
    elif file_type == "merchant_registered":
        df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
        df['provinsi'] = df['provinsi'].str.strip().str.title()
        df['kab_kota'] = df['kab_kota'].str.strip().str.title()
        df["jumlah_merchant"] = pd.to_numeric(df["jumlah_merchant"], errors="coerce").fillna(0).astype(int)
    
    elif file_type == "harian":
        df['Bulan'] = df['Bulan'].str.strip().str.title()

        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce').dt.strftime('%m/%d/%Y')
        df = df.sort_values(by='Tanggal', ascending=True).reset_index(drop=True)

        df['Jumlah Nominal'] = df['Jumlah Nominal'].astype(str).str.replace(',', '.', regex=True)
        df['Jumlah Nominal'] = pd.to_numeric(df['Jumlah Nominal'], errors='coerce')
        df['PPN'] = df['PPN'].astype(str).str.replace(',', '.', regex=True)
        df['PPN'] = pd.to_numeric(df['PPN'], errors='coerce')
        df['PPh 22'] = df['PPh 22'].astype(str).str.replace(',', '.', regex=True)
        df['PPh 22'] = pd.to_numeric(df['PPh 22'], errors='coerce')
    
    df.fillna(method='ffill', inplace=True)
    
    return df
