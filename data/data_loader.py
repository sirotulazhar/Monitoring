import pandas as pd

def load_data(file_path='data/regions and payment methods.csv'):
    df = pd.read_csv(file_path)
    df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
    df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
    df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
    df['payment_method'] = df['payment_method'].str.strip().str.lower()
    return df
