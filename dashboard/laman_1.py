import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.utils import format_rupiah

class TokoLadangDashboard:
    def __init__(self,df):
        self.df=df
        self.df = self.load_data()
        self.df_filtered = self.df.copy()
    
    def load_data(self):
        df = pd.read_csv("data/transaksi harian.csv")
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df["Bulan"] = df["Tanggal"].dt.to_period("M")
        hari_mapping = {
            "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
            "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
        }
        df["Hari"] = df["Tanggal"].dt.day_name().map(hari_mapping)
        return df

    def filter_data(self):
        # st.subheader("📆 Filter Rentang Waktu")
        col1, col2, col3,col4 = st.columns(4)
        
        with col1:
            start_date = st.date_input("Start Date", min_value=self.df["Tanggal"].min().date(),
                                       max_value=self.df["Tanggal"].max().date(),
                                       value=self.df["Tanggal"].min().date())
        
        with col2:
            end_date = st.date_input("End Date", min_value=self.df["Tanggal"].min().date(),
                                     max_value=self.df["Tanggal"].max().date(),
                                     value=self.df["Tanggal"].max().date())
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Semua Data"):
                start_date = self.df["Tanggal"].min().date()
                end_date = self.df["Tanggal"].max().date()
       
        self.df_filtered = self.df[(self.df["Tanggal"].dt.date >= start_date) &
                                   (self.df["Tanggal"].dt.date <= end_date)]
        # with col4:
        self.df_filtered["Minggu"] = self.df_filtered["Tanggal"].dt.to_period("W").astype(str)
        self.df_filtered["Tanggal"] = pd.to_datetime(self.df_filtered["Tanggal"])
        
    def filter_tampilan (self, column):
        if self.filter_option == "Harian":
            grouped_data = self.df_filtered.groupby("Tanggal")[column].sum().reset_index()
            x_label = "Tanggal"
        elif self.filter_option == "Mingguan":
            grouped_data = self.df_filtered.groupby("Minggu")[column].sum().reset_index()
            x_label = "Minggu"
        else:  
            grouped_data = self.df_filtered.groupby("Bulan")[column].sum().reset_index()
            x_label = "Bulan"

        grouped_data[x_label] = grouped_data[x_label].astype(str)
        return grouped_data, x_label

    def semua_total(self):
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; } 
                    div[data-testid="stMetric"] { margin-top: -30px; }  
                </style>
            """, unsafe_allow_html=True)
        
        with col1:
            st.info("Total PO")
            total_po = self.df_filtered["Jumlah PO"].sum()
            st.metric("", value=format_rupiah(total_po))
        
        with col2:
            st.info("Total Nominal")
            nominal = self.df_filtered["Jumlah Nominal"].sum()
            st.metric("", value=format_rupiah(nominal))
        
        with col3:
            st.info("Total PPh 22")
            total_pph = self.df_filtered["PPh 22"].sum()
            st.metric("", value=format_rupiah(total_pph))
        
        with col4:
            st.info("Total PPN")
            total_ppn = self.df_filtered["PPN"].sum()
            st.metric("", value=format_rupiah(total_ppn))

    def show_po_tren(self):
        col7, col8 = st.columns([5, 2])
        col1, _, col2 = st.columns([5, 0.001, 1.7])  
        
        with col1:

            with col8:
                # Hitung rentang tanggal untuk filter otomatis
                min_date = self.df_filtered["Tanggal"].min()
                max_date = self.df_filtered["Tanggal"].max()
                date_range = (max_date - min_date).days

                if date_range <= 7:
                    default_filter = "Harian"
                elif date_range <= 30:
                    default_filter = "Mingguan"
                else:
                    default_filter = "Bulanan"

                # Selectbox yang bisa diubah user
                self.filter_option = st.selectbox(
                    "Pilih Tampilan",
                    options=["Harian", "Mingguan", "Bulanan"],
                    index=["Harian", "Mingguan", "Bulanan"].index(default_filter)
                )

            with col7:
                st.subheader(f"Tren PO per {self.filter_option}")
            if not self.df_filtered.empty:
                po_filtered, x_label = self.filter_tampilan("Jumlah PO")
                fig = px.line(po_filtered, x=x_label, y="Jumlah PO", 
                            labels={x_label: x_label, "Jumlah PO": "Total PO"},
                            color_discrete_sequence=["#F2B949"],markers=True)
                fig.update_layout(margin=dict(t=10, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:   
                st.warning("Tidak ada data untuk ditampilkan.")

        with col2:
            st.subheader("Transaksi Terbesar dan Terkecil")
            if not self.df_filtered.empty:
                po_terbesar = self.df_filtered.loc[self.df_filtered["Jumlah Nominal"].idxmax()]
                po_terkecil = self.df_filtered.loc[self.df_filtered["Jumlah Nominal"].idxmin()]
                
                with st.container():
                    st.write("📌 **PO Terbesar**")
                    st.write(f"**Tanggal:** {po_terbesar['Tanggal'].strftime('%Y-%m-%d')}")
                    st.write(f"**Jumlah Nominal:** Rp {format_rupiah(po_terbesar['Jumlah Nominal'])}")

                with st.container():
                    st.write("📌 **PO Terkecil**")
                    st.write(f"**Tanggal:** {po_terkecil['Tanggal'].strftime('%Y-%m-%d')}")
                    st.write(f"**Jumlah Nominal:** Rp {format_rupiah(po_terkecil['Jumlah Nominal'])}")

            else:
                st.warning("Tidak ada data untuk ditampilkan.")

    def rerata_perhari (self):
        total_per_hari_seminggu = self.df_filtered.groupby("Hari").agg({
            "Jumlah PO": "mean",
            "Jumlah Nominal": "mean"}).reindex(["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]).reset_index()
        total_per_hari_seminggu["Jumlah PO Text"] = total_per_hari_seminggu["Jumlah PO"].apply(format_rupiah)
        total_per_hari_seminggu["Jumlah Nominal Text"] = total_per_hari_seminggu["Jumlah Nominal"].apply(format_rupiah)

        fig = make_subplots(
            rows=1, cols=2, 
            subplot_titles=["Rata-rata PO per Hari", "Rata-rata Nominal per Hari"])

        fig.add_trace(
            go.Bar(
                x=total_per_hari_seminggu["Hari"], 
                y=total_per_hari_seminggu["Jumlah PO"], 
                text=total_per_hari_seminggu["Jumlah PO Text"],  
                textposition="outside",  
                marker_color="#F2B949",
                name="Jumlah PO"),row=1, col=1)
        fig.add_trace(
            go.Bar(
                x=total_per_hari_seminggu["Hari"], 
                y=total_per_hari_seminggu["Jumlah Nominal"], 
                text=total_per_hari_seminggu["Jumlah Nominal Text"],  
                textposition="outside",  
                marker_color="#A3E0CA",
                name="Jumlah Nominal"),row=1, col=2)
        fig.update_xaxes(tickangle=-0)
        fig.update_layout(showlegend=False, height=400,margin=dict(t=20, b=40) )
        st.subheader("Perbandingan Tren Transaksi per Hari")
        st.plotly_chart(fig, use_container_width=True)

    def pendapatan_perbulan(self):
        st.subheader(f"Tren Pendapatan per {self.filter_option}")
        if not self.df_filtered.empty:
            nominal_bulanan, x_label = self.filter_tampilan("Jumlah Nominal")
            fig = px.line(nominal_bulanan, x=x_label, y="Jumlah Nominal", 
                        labels={x_label: x_label, "Jumlah Nominal": "Total Nominal"},
                        color_discrete_sequence=["#F2B949"],markers=True)
            fig.update_layout(margin=dict(t=10, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("") 
        else:
            st.warning("Tidak ada data untuk ditampilkan.")
        
    def perpajakan(self):
        kol1, kol2 = st.columns(2,gap="large")  
        with kol1:
            st.subheader(f"Tren Pajak per {self.filter_option}")
            if not self.df_filtered.empty:
                pajak_perbulan, x_label = self.filter_tampilan("Jumlah Pajak")
                # pajak_perbulan = self.df_filtered.groupby("Bulan")["Jumlah Pajak"].sum().reset_index()
                # pajak_perbulan["Bulan"] = pajak_perbulan["Bulan"].astype(str)
                fig = px.line(pajak_perbulan, x=x_label, y="Jumlah Pajak", 
                        labels={x_label: x_label, "Jumlah Pajak": "Total Pajak"},
                        color_discrete_sequence=["#F2B949"],markers=True)
                fig.update_layout(margin=dict(t=5, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan.")

        with kol2:
            st.subheader(f"Rasio Pajak per {self.filter_option}")
            self.df_filtered["Rasio Pajak (%)"] = (self.df_filtered["Jumlah Pajak"] / self.df_filtered["Jumlah Nominal"]) * 100

            if self.filter_option == "Harian":
                rasio_pajak = self.df_filtered.groupby("Tanggal")["Rasio Pajak (%)"].mean().reset_index()
                x_label = "Tanggal"
            elif self.filter_option == "Mingguan":
                rasio_pajak = self.df_filtered.groupby("Minggu")["Rasio Pajak (%)"].mean().reset_index()
                x_label = "Minggu"
            else:  # Bulanan
                rasio_pajak = self.df_filtered.groupby("Bulan")["Rasio Pajak (%)"].mean().reset_index()
                x_label = "Bulan"

            rasio_pajak[x_label] = rasio_pajak[x_label].astype(str)

            fig = px.line(
                rasio_pajak, x=x_label, y="Rasio Pajak (%)",
                labels={x_label: x_label, "Rasio Pajak (%)": "Rata-rata Rasio Pajak (%)"},
                color_discrete_sequence=['#F2B949'],markers=True)
            fig.update_layout(margin=dict(t=5, b=20)) 
            st.plotly_chart(fig, use_container_width=True)


    def run(self):
        self.filter_data()
        self.semua_total()
        self.show_po_tren()
        self.rerata_perhari()
        self.pendapatan_perbulan()
        self.perpajakan()   
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.caption("Dashboard ©️ 2025 by Toko Ladang")

if __name__ == "__main__":
    dashboard = TokoLadangDashboard()
    dashboard.run()
