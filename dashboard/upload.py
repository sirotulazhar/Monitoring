from streamlit_gsheets import GSheetsConnection
from data.data_loader import preprocess_data
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


def remove_duplicate_headers(df):
    # Pastikan baris pertama adalah header yang benar
    header = df.columns.tolist()

    # Hapus baris yang memiliki nilai yang sama dengan header (duplikasi header)
    df = df[~df.apply(lambda row: row.tolist() == header, axis=1)]

    return df


class FileUploader:
    def load_data(self, sheet_name):
        try:
            df = conn.read(worksheet=sheet_name)

            numeric_cols = ["jumlah_merchant", "jumlah_po", "nominal_po", "pph22", "ppn",
                            "total_pajak", "Jumlah PO", "Jumlah Nominal", "PPh 22", "PPN", "Jumlah Pajak"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(
                        df[col], errors="coerce").fillna(0).astype(int)

            return df.fillna(0)  # Pastikan tidak ada NaN

        except Exception as e:
            st.error(f"🚨 Gagal membaca Google Sheets: {e}")
            return pd.DataFrame()

    def save_data(self, df, sheet_name):
        """Menyimpan data ke Google Sheets tanpa menghapus data lama"""
        try:
            # Ambil data lama
            existing_data = self.load_data(sheet_name)

            # **Cek apakah data baru benar-benar ada**
            if df.empty:
                st.error("🚨 Data baru kosong! Pastikan file yang diunggah memiliki data.")
                return

            if not existing_data.empty:
                existing_data = existing_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            else:
                existing_data = pd.DataFrame(columns=df.columns)

            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df.replace(["", " ", "nan", "NaN"], pd.NA, inplace=True)
            df.dropna(how="all", inplace=True)

            if not existing_data.empty:
                df_combined = pd.concat([existing_data, df], ignore_index=True)
            else:
                df_combined = df

            df_combined["waktu"] = pd.to_datetime(df_combined["waktu"], errors="coerce").dt.strftime("%Y-%m-%d")
            df_combined = df_combined.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df_combined.drop_duplicates(subset=df_combined.columns.tolist(), keep="first", inplace=True)
            df_combined = remove_duplicate_headers(df_combined)
            
            conn.update(worksheet=sheet_name, data=df_combined)

            st.session_state["data_uploaded"] = True

        except Exception as e:
            st.error(f"🚨 Gagal memperbarui Google Sheets: {e}")

    def run(self):
        """Menjalankan proses upload dan penyimpanan data"""
        st.subheader("Upload File")

        if "data_uploaded" not in st.session_state:
            st.session_state["data_uploaded"] = False

        if "show_popup" not in st.session_state:
            st.session_state["show_popup"] = False

        if "uploader_key" not in st.session_state:
            st.session_state["uploader_key"] = 0
 
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], key=f"uploader_{st.session_state['uploader_key']}")
        if uploaded_file:
            st.session_state["uploaded_file"] = uploaded_file 
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

                # Hitung total pajak jika kolomnya belum ada
                if "total_pajak" not in df_new.columns:
                    if "pph22" in df_new.columns and "ppn" in df_new.columns:
                        df_new["total_pajak"] = df_new["pph22"].astype(float) + df_new["ppn"].astype(float)
                    else:
                        df_new["total_pajak"] = 0

                df_new = df_new[expected_columns]

                if "Tanggal" in df_new.columns:
                    df_new["Tanggal"] = pd.to_datetime(df_new["Tanggal"], errors="coerce").dt.strftime("%Y-%m-%d")
                
                if "waktu" in df_new.columns:
                    df_new["waktu"] = pd.to_datetime(df_new["waktu"], errors="coerce").dt.strftime("%Y-%m-%d")

                # Preprocessing sesuai jenis data
                file_type = "regions_payment" if matched_file == "regions and payment methods.csv" else \
                            "merchant_registered" if matched_file == "merchant registered.csv" else "harian"
                df_new = preprocess_data(df_new, file_type)

                # Hapus duplikat berdasarkan kolom unik
                unique_cols = [
                    col for col in expected_columns if col in df_new.columns]
                df_new.drop_duplicates(subset=unique_cols, inplace=True)
                if not st.session_state["data_uploaded"]:
                    if st.session_state["uploaded_file"] and st.button("📤 Simpan Data"):
                            with st.spinner("Mengunggah data..."):
                                self.save_data(df_new, sheet_name)
                                
                            st.session_state["data_uploaded"] = True
                            st.success("✅ Data berhasil disimpan!")

                            st.session_state["show_popup"] = False
                            st.session_state["uploaded_file"] = None  # Hapus file dari session state
                            st.session_state["uploader_key"] += 1  # Paksa uploader refresh
                            time.sleep(2)
                            st.rerun()
                    
            else:
                st.error("🚨 Nama file tidak cocok dengan dataset yang tersedia!")
