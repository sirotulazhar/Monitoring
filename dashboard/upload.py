import streamlit as st
from data.data_loader import preprocess_data
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Nama-nama sheet yang sesuai dengan dataset
DATASETS = {
    "merchant registered.csv": ("merchant registered", ["waktu", "provinsi", "kab_kota", "jumlah_merchant"]),
    "regions and payment methods.csv": ("regions and payment methods", ["waktu", "payment_method", "prov_sekolah", "kota_kab_sekolah", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"]),
    "Harian.csv": ("Harian", ["Bulan", "Tanggal", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"])
}

class FileUploader:
    def __init__(self):
        pass

    def load_data(self, sheet_name):
        """Mengambil data dari Google Sheets berdasarkan nama sheet."""
        try:
            df = conn.read(worksheet=sheet_name)
            return df
        except Exception as e:
            st.error(f"🚨 Gagal membaca Google Sheets: {e}")
            return pd.DataFrame()

    def save_data(self, df, sheet_name):
        """Menambahkan data ke Google Sheets tanpa menghapus data lama."""
        try:
            existing_data = self.load_data(sheet_name)
            if not existing_data.empty:
                df_existing = existing_data.astype(str)  # Pastikan tipe data string untuk menghindari error
            else:
                df_existing = pd.DataFrame(columns=df.columns)

            # Gabungkan data baru dengan yang lama & hilangkan duplikasi
            df_combined = pd.concat([df_existing, df], ignore_index=True).drop_duplicates()

            # Simpan data ke Google Sheets
            conn.update(worksheet=sheet_name, data=df_combined)

            st.success(f"✅ Data berhasil ditambahkan '{sheet_name}'!")
        except Exception as e:
            st.error(f"🚨 Gagal memperbarui Google Sheets: {e}")

    def run(self):
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

        if uploaded_file:
            # df_new = pd.read_csv(uploaded_file, header=0)
            df_new = pd.read_csv(uploaded_file, header=0, encoding="utf-8")

            # Cek kecocokan file berdasarkan kolomnya
            matched_file = None
            for file_name, (sheet_name, expected_columns) in DATASETS.items():
                required_columns = set(expected_columns) - {"total_pajak", "Jumlah Pajak"}  # Kolom opsional
                if required_columns.issubset(df_new.columns):
                    matched_file = file_name
                    break

            if matched_file:
                # Ambil nama sheet yang sesuai
                sheet_name = DATASETS[matched_file][0]

                # Preprocess data sesuai tipe file
                file_type = "regions_payment" if matched_file == "regions and payment methods.csv" else \
                            "merchant_registered" if matched_file == "merchant registered.csv" else "harian"
                df_new = preprocess_data(df_new, file_type)

                df_new = df_new.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Hapus spasi ekstra
                df_new.replace(["", " ", "nan", "NaN"], pd.NA, inplace=True)  # Pastikan kosong benar-benar NaN
                df_new.dropna(how="all", inplace=True)  # Hapus baris yang semua kolomnya NaN
                df_new.reset_index(drop=True, inplace=True)  # Reset indeks setelah menghapus


                if st.button("📤 Simpan Data"):
                    with st.spinner("Mengunggah data..."):
                        self.save_data(df_new, sheet_name)

            else:
                st.error("🚨 Struktur kolom tidak sesuai dengan dataset yang tersedia!")
