import pandas as pd
import os

def load_data(file_path='data/regions and payment methods.csv'):
    df = pd.read_csv(file_path)
    df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
    df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
    df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
    df['payment_method'] = df['payment_method'].str.strip().str.lower()
    return df

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

os.makedirs(DATA_FOLDER, exist_ok=True)

# Struktur dataset yang diizinkan
DATASETS = {
    "merchant registered.csv": ["waktu", "provinsi", "kab_kota", "jumlah_merchant"],
    "regions and payment methods.csv": ["waktu", "payment_method", "prov_sekolah", "kota_kab_sekolah", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"],
    "Harian.csv": ["Bulan", "Tanggal", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"]
}

def preprocess_data(df, file_type):
    
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
        df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce').dt.date
        df = df.sort_values(by='waktu', ascending=True).reset_index(drop=True)
        df['waktu']
        df['provinsi'] = df['provinsi'].str.strip().str.title()
        df['kab_kota'] = df['kab_kota'].str.strip().str.title()
    
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
