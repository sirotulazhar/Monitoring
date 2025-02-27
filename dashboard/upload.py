import streamlit as st
from data_loader import preprocess_data
import pandas as pd
import time
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

DATASETS = {
    "merchant registered.csv": ["waktu", "provinsi", "kab_kota", "jumlah_merchant"],
    "regions and payment methods.csv": ["waktu", "payment_method", "prov_sekolah", "kota_kab_sekolah", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"],
    "Harian.csv": ["Bulan", "Tanggal", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"]
}

class FileUploader:
    def __init__(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

    def run(self):
        st.subheader("")
        uploaded_file = st.file_uploader("Pilih file CSV untuk diunggah", type=["csv"])

        if uploaded_file:
            df_new = pd.read_csv(uploaded_file)

            # Cek kecocokan file berdasarkan kolomnya
            matched_file = None
            for file_name, expected_columns in DATASETS.items():
                required_columns = set(expected_columns) - {"total_pajak", "Jumlah Pajak"}  # Kolom opsional
                if required_columns.issubset(df_new.columns):
                    matched_file = file_name
                    break

            if matched_file:
                file_path = os.path.join(DATA_FOLDER, matched_file)
                # st.success(f"✅ File cocok dengan: {matched_file}")

                # Tentukan tipe file untuk preprocessing
                file_type = "regions_payment" if matched_file == "regions and payment methods.csv" else \
                            "merchant_registered" if matched_file == "merchant registered.csv" else "harian"
                
                df_new = preprocess_data(df_new, file_type)

                # Cek apakah file lama ada
                if os.path.exists(file_path):
                    df_existing = pd.read_csv(file_path)
                else:
                    df_existing = pd.DataFrame(columns=DATASETS[matched_file])  # Data kosong

                # Gabungkan data lama dengan yang baru
                df_combined = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates()

                if st.button("💾 Simpan Data"):
                    progress_bar = st.progress(0)
                    
                    # Simulasi proses penyimpanan data
                    for percent in range(0, 101, 10):
                        time.sleep(0.1)  
                        progress_bar.progress(percent)  
                    
                    df_combined.to_csv(file_path, index=False)
                    
                    progress_bar.empty()
                    st.success(f"📂 Data berhasil disimpan di: {file_path}")
            else:
                st.error("🚨 Struktur kolom tidak sesuai dengan dataset yang tersedia!")
