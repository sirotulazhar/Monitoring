import pandas as pd
import streamlit as st
import plotly.express as px
from dashboard.utils import format_rupiah

class Dashboardharian:
    def __init__(self,df):
        self.df= df
        self.df = self.load_data()
        self.df_filtered = self.df.copy()
    
    def load_data(self):
        df = pd.read_csv("data/regions and payment methods.csv")
        df["waktu"] = pd.to_datetime(df["waktu"])
        df["Bulan"] = df["waktu"].dt.to_period("M")
        hari_mapping = {
            "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
            "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
        }
        df["Hari"] = df["waktu"].dt.day_name().map(hari_mapping)
        return df

    def filter_data(self):
        # st.subheader("📆 Filter Rentang Waktu")  
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<style>div[data-testid='stDateInput'] {margin-top: -50px;}</style>", unsafe_allow_html=True)
        date_pilih = st.date_input("📆 Filter Rentang Waktu", value=self.df["waktu"].min().date())
        self.df_filtered = self.df[self.df["waktu"].dt.date == date_pilih]

    
    def semua_total(self):
        col1, col2, col3, col4 ,col5= st.columns(5)
        st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; } 
                    div[data-testid="stMetric"] { margin-top: -30px; }  
                </style>
            """, unsafe_allow_html=True)
        
        with col1:
            st.info("Total PO")
            total_po = self.df_filtered["jumlah_po"].sum()
            st.metric("", value=format_rupiah(total_po))
        
        with col2:
            st.info("Total Nominal")
            nominal = self.df_filtered["nominal_po"].sum()
            st.metric("", value=format_rupiah(nominal))
        
        with col3:
            st.info("Total PPh 22")
            total_pph = self.df_filtered["pph22"].sum()
            st.metric("", value=format_rupiah(total_pph))
        
        with col4:
            st.info("Total PPN")
            total_ppn = self.df_filtered["ppn"].sum()
            st.metric("", value=format_rupiah(total_ppn))
        
        with col5:
            st.info('Total Pajak') 
            total_pajak = self.df_filtered[["ppn", "pph22"]].sum().sum()
            st.metric("", value=format_rupiah(total_pajak))

    def show_po_tren(self):
        col1, _, col2 = st.columns([4.3,0.001, 1.7])  
        with col1:
            st.subheader("Tren PO per Kota/Kabupaten")
            st.markdown("<style>div[data-testid='stSelectbox'] {margin-top: -50px;}</style>", unsafe_allow_html=True)
            if not self.df_filtered.empty:
                po_bulanan = self.df_filtered.groupby("kota_kab_sekolah")["jumlah_po"].sum().reset_index()
                po_bulanan["kota_kab_sekolah"] = po_bulanan["kota_kab_sekolah"].astype(str)
                option = st.selectbox("", ["10 Terbesar", "10 Terkecil"])
                if option == "10 Terbesar":
                    po_bulanan = po_bulanan.nlargest(10, "jumlah_po").sort_values("jumlah_po", ascending=True)

                else:
                    po_bulanan = po_bulanan.nsmallest(10, "jumlah_po").sort_values("jumlah_po", ascending=True)

                # Plot data
                fig = px.bar(po_bulanan, x="jumlah_po", y="kota_kab_sekolah", 
                            labels={"kota_kab_sekolah": "Kota/Kabupaten", "jumlah_po": "Total PO"},
                            color_discrete_sequence=["#F2B949"], width=600, height=500,text_auto=True)

                fig.update_layout(margin=dict(t=10, b=100))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data pada tanggal tersebut.")

        with col2:
            if not self.df_filtered.empty:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.info("##### Total Kota/Kabupaten")  
                total_kota = self.df_filtered["kota_kab_sekolah"].nunique()
                st.metric(label="", value=f"{total_kota:,}")

                po_bulanan = self.df_filtered.groupby("kota_kab_sekolah").agg({
                    "jumlah_po": "sum",
                    "nominal_po": "sum"
                }).reset_index()

                if not po_bulanan.empty:
                    po_terbesar = po_bulanan.nlargest(1, "nominal_po").iloc[0]  
                    po_terkecil = po_bulanan.nsmallest(1, "nominal_po").iloc[0]  

                    with st.container():
                        st.write("#### 📌 PO Terbesar")
                        st.write(f"📍 **{po_terbesar['kota_kab_sekolah']}**")
                        st.write(f"Jumlah PO: **{format_rupiah(po_terbesar['jumlah_po'])}**") 
                        st.write(f"Nominal PO: **Rp {format_rupiah(po_terbesar['nominal_po'])}**")

                    with st.container():
                        st.write("#### 📌 PO Terkecil")
                        st.write(f"📍 **{po_terkecil['kota_kab_sekolah']}**")
                        st.write(f"Jumlah PO: **{format_rupiah(po_terkecil['jumlah_po'])}**")  
                        st.write(f"Nominal PO: **Rp {format_rupiah(po_terkecil['nominal_po'])}**")
                else:
                    st.warning("Tidak ada data tersedia.")

               
    def prov_tren(self):
        col1, _, col2 = st.columns([4.3, 0.001, 1.7])  
        with col1:
            st.subheader("Tren PO per Provinsi")
            st.markdown("<style>div[data-testid='stSelectbox'] {margin-top: -50px;}</style>", unsafe_allow_html=True)

            if self.df_filtered.empty:
                st.warning("Tidak ada data pada tanggal tersebut.")
                return
            prov_bulanan = self.df_filtered.groupby("prov_sekolah")["jumlah_po"].sum().reset_index()
            prov_bulanan["prov_sekolah"] = prov_bulanan["prov_sekolah"].astype(str)


            pilih = st.selectbox("", ["10 Terbesar", "10 Terkecil"], key="provinsi_selectbox")

            if pilih == "10 Terbesar":
                prov_bulanan = prov_bulanan.nlargest(10, "jumlah_po").sort_values("jumlah_po", ascending=True)
            else:
                prov_bulanan = prov_bulanan.nsmallest(10, "jumlah_po").sort_values("jumlah_po", ascending=True)

            # Plot data
            fig = px.bar(prov_bulanan, x="jumlah_po", y="prov_sekolah", 
                        labels={"prov_sekolah": "Provinsi", "jumlah_po": "Total PO"},
                        color_discrete_sequence=["#F2B949"], width=600, height=500,text_auto=True)
            fig.update_layout(margin=dict(t=10, b=100))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Metode Pembayaran Paling Sering Digunakan")

            if self.df_filtered.empty:
                st.warning("Tidak ada data pada tanggal tersebut.")
                return

            if "payment_method" not in self.df_filtered.columns:
                st.warning("Kolom 'payment_method' tidak ditemukan dalam data.")
                return

            payment_counts = self.df_filtered["payment_method"].value_counts().reset_index()
            payment_counts.columns = ["payment_method", "jumlah_transaksi"]
            fig_pie = px.pie(payment_counts, names="payment_method", values="jumlah_transaksi", hole=0.4, 
                            color_discrete_sequence=px.colors.qualitative.Set3)

            st.plotly_chart(fig_pie, use_container_width=True)

    def run(self):
        self.filter_data()
        self.semua_total()
        self.show_po_tren()
        self.prov_tren()
 
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.caption("Dashboard ©️ 2025 by Toko Ladang")

if __name__ == "__main__":
    dashboard = Dashboardharian()
    dashboard.run()
