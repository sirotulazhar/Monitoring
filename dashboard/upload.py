from data.data_loader import preprocess_data
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit as st
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
    def load_data(self, sheet_name):
        try:
            df = conn.read(worksheet=sheet_name)

            numeric_cols = ["jumlah_merchant", "jumlah_po", "nominal_po", "pph22", "ppn", "total_pajak", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            
            return df.fillna(0)  # Pastikan tidak ada NaN

        except Exception as e:
            st.error(f"🚨 Gagal membaca Google Sheets: {e}")
            return pd.DataFrame()


    def save_data(self, df, sheet_name):
        try:
            existing_data = self.load_data(sheet_name)

            if not existing_data.empty:
                existing_data = existing_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            else:
                existing_data = pd.DataFrame(columns=df.columns)

            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df.replace(["", " ", "nan", "NaN"], pd.NA, inplace=True)
            df.dropna(how="all", inplace=True)

            # Format tanggal dengan konsisten
            if "Tanggal" in df.columns:
                df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce").dt.strftime("%Y-%m-%d")
            if "waktu" in df.columns:
                df["waktu"] = pd.to_datetime(df["waktu"], errors="coerce").dt.strftime("%Y-%m-%d")

            # Validasi bulan agar tidak ada nilai salah
            valid_months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

            if "Bulan" in df.columns:
                df["Bulan"] = df["Bulan"].apply(lambda x: x if x in valid_months else None)
                df = df.dropna(subset=["Bulan"])

            # Hapus duplikat dengan mempertahankan data terbaru
            unique_cols = [col for col in df.columns if col in existing_data.columns]
            df_combined = pd.concat([existing_data, df], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=unique_cols, keep="last").reset_index(drop=True)

            # Simpan ke Google Sheets
            conn.update(worksheet=sheet_name, data=df_combined)
            st.success(f"✅ Data berhasil disimpan di '{sheet_name}'")

        except Exception as e:
            st.error(f"🚨 Gagal memperbarui Google Sheets: {e}")

    def run(self):
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

        if uploaded_file:
            df_new = pd.read_csv(uploaded_file, dtype=str, encoding="utf-8", sep=",")
            df_new.columns = df_new.columns.str.strip()

            matched_file = None
            for file_name, (sheet_name, expected_columns) in DATASETS.items():
                if uploaded_file.name == file_name:
                    matched_file = file_name
                    break

            if matched_file:
                sheet_name = DATASETS[matched_file][0]
                expected_columns = DATASETS[matched_file][1]

                # Jika kolom total_pajak belum ada, buat kolom baru dengan menjumlahkan PPh 22 dan PPN
                if "total_pajak" not in df_new.columns:
                    if "pph22" in df_new.columns and "ppn" in df_new.columns:
                        df_new["total_pajak"] = df_new["pph22"].astype(float) + df_new["ppn"].astype(float)
                    else:
                        df_new["total_pajak"] = 0  # Jika kolom tidak ditemukan, isi dengan 0

                # Sekarang, df_new sudah memiliki semua kolom yang dibutuhkan
                df_new = df_new[expected_columns]

                if "Tanggal" in df_new.columns:
                    df_new["Tanggal"] = pd.to_datetime(df_new["Tanggal"], errors="coerce").dt.strftime("%Y-%m-%d")
                if "waktu" in df_new.columns:
                    df_new["waktu"] = pd.to_datetime(df_new["waktu"], errors="coerce").dt.strftime("%Y-%m-%d")

                file_type = "regions_payment" if matched_file == "regions and payment methods.csv" else "merchant_registered" if matched_file == "merchant registered.csv" else "harian"
                df_new = preprocess_data(df_new, file_type)

                unique_cols = [col for col in expected_columns if col in df_new.columns]
                df_new.drop_duplicates(subset=unique_cols, inplace=True)
     
                if st.button("📤 Simpan Data"):
                    if "data_uploaded" not in st.session_state:
                        st.session_state["data_uploaded"] = False

                    if not st.session_state["data_uploaded"]:
                        with st.spinner("Mengunggah data..."):
                            self.save_data(df_new, sheet_name)

                        st.session_state["data_uploaded"] = True
                        time.sleep(10)

                        st.rerun()
            else:
                st.error("🚨 Nama file tidak cocok dengan dataset yang tersedia!")
