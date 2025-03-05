import streamlit as st
from data.data_loader import preprocess_data
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Nama-nama sheet yang sesuai dengan dataset
DATASETS = {
    "merchant registered.csv": ("merchant registered", ["waktu", "provinsi", "kab_kota", "jumlah_merchant"]),
    "regions and payment methods.csv": ("regions and payment methods", ["waktu", "payment_method", "prov_sekolah", "kota_kab_sekolah", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"]),
    "Harian.csv": ("Harian", ["Bulan", "Tanggal", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"])
}

class FileUploader:
    def load_data(self, sheet_name):
        """Mengambil data dari Google Sheets berdasarkan nama sheet."""
        try:
            df = conn.read(worksheet=sheet_name)
            
            numeric_cols = ["jumlah_merchant", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            
            return df
        except Exception as e:
            st.error(f"🚨 Gagal membaca Google Sheets: {e}")
            return pd.DataFrame()

    def save_data(self, df, sheet_name):
        """Menambahkan data ke Google Sheets tanpa menghapus data lama."""
        try:
            existing_data = self.load_data(sheet_name)

            if not existing_data.empty:
                # Pastikan format & tipe data konsisten
                if "waktu" in existing_data.columns:
                    existing_data["waktu"] = pd.to_datetime(existing_data["waktu"], errors="coerce")

                df_existing = existing_data.astype(str).apply(lambda x: x.str.strip())
            else:
                df_existing = pd.DataFrame(columns=df.columns)

            if "waktu" in df.columns:
                df["waktu"] = pd.to_datetime(df["waktu"], errors="coerce")

            # Bersihkan data
            df = df.astype(str).apply(lambda x: x.str.strip())  
            df.replace(["", " ", "nan", "NaN"], pd.NA, inplace=True)
            df.dropna(how="all", inplace=True)

            # **Gunakan pd.concat untuk menghindari error pada merge**
            df_combined = pd.concat([df_existing, df], ignore_index=True).drop_duplicates().reset_index(drop=True)

            # Simpan data ke Google Sheets
            conn.update(worksheet=sheet_name, data=df_combined)

            st.success(f"✅ Data berhasil disimpan di '{sheet_name}'!")
        except Exception as e:
            st.error(f"🚨 Gagal memperbarui Google Sheets: {e}")


    def run(self):
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

        if uploaded_file:
            df_new = pd.read_csv(uploaded_file, dtype=str, encoding="utf-8", sep=",")
            df_new["waktu"] = df_new["waktu"].str.replace(r"[\/]", "-", regex=True)

            matched_file = None
            for file_name, (sheet_name, expected_columns) in DATASETS.items():
                required_columns = set(expected_columns) - {"total_pajak", "Jumlah Pajak"}
                if required_columns.issubset(df_new.columns):
                    matched_file = file_name
                    break

            if matched_file:
                sheet_name = DATASETS[matched_file][0]
                file_type = "regions_payment" if matched_file == "regions and payment methods.csv" else \
                            "merchant_registered" if matched_file == "merchant registered.csv" else "harian"
                df_new = preprocess_data(df_new, file_type)

                df_new.drop_duplicates(subset=["waktu", "provinsi", "kab_kota", "jumlah_merchant"], inplace=True)
                
                if st.button("📤 Simpan Data"):
                    if "data_uploaded" not in st.session_state:
                        st.session_state["data_uploaded"] = False

                    if not st.session_state["data_uploaded"]:
                        with st.spinner("Mengunggah data..."):
                            self.save_data(df_new, sheet_name)
                        st.session_state["data_uploaded"] = True

                        st.rerun()
                    else:
                        st.warning("⚠️ Data sudah diunggah sebelumnya!")
            else:
                st.error("🚨 Struktur kolom tidak sesuai dengan dataset yang tersedia!")
