import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.utils import format_rupiah

class TokoLadangDashboard:
    def __init__(self,df):
        self.df= df
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
        col1, col2, col3 = st.columns(3)
        
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
        col1, _, col2 = st.columns([5, 0.001, 1.7])  
        with col1:
            st.subheader("Tren PO per Bulan")
            if not self.df_filtered.empty:
                po_bulanan = self.df_filtered.groupby("Bulan")["Jumlah PO"].sum().reset_index()
                po_bulanan["Bulan"] = po_bulanan["Bulan"].astype(str)
                fig = px.line(po_bulanan, x="Bulan", y="Jumlah PO", labels={"Bulan": "Bulan", "Jumlah PO": "Total PO"},color_discrete_sequence=["#F2B949"])
                fig.update_layout(margin=dict(t=10, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan.")

        with col2:
            st.markdown('<br>',unsafe_allow_html=True)
            st.subheader("Transaksi Terbesar dan Terkecil")
            if not self.df_filtered.empty:
                po_terbesar = self.df_filtered.loc[self.df_filtered["Jumlah Nominal"].idxmax()]
                po_terkecil = self.df_filtered.loc[self.df_filtered["Jumlah Nominal"].idxmin()]
                
                with st.container():
                    st.write("PO Terbesar")
                    st.data_editor(po_terbesar[["Tanggal", "Jumlah Nominal"]].
                                   to_frame().T,hide_index=True)

                with st.container():
                    st.write("PO Terkecil")
                    st.data_editor(po_terkecil[["Tanggal", "Jumlah Nominal"]].
                                   to_frame().T,hide_index=True)
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
        fig.update_layout(showlegend=False, height=380,margin=dict(t=27, b=48) )
        st.subheader("Perbandingan Tren Transaksi per Hari")
        st.plotly_chart(fig, use_container_width=True)

    def pendapatan_perbulan(self):
        st.subheader("Tren Pendapatan per Bulan")
        nominal_bulanan = self.df_filtered.groupby("Bulan")["Jumlah Nominal"].sum().reset_index()
        nominal_bulanan["Bulan"] = nominal_bulanan["Bulan"].astype(str)
        fig = px.line(nominal_bulanan, x="Bulan", y="Jumlah Nominal", labels={"Bulan": "Bulan", "Jumlah Nominal": "Total Nominal"},
                      color_discrete_sequence=['#F2B949'])
        fig.update_layout(margin=dict(t=5, b=30))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("") 
    
    def perpajakan(self):
        kol1, kol2 = st.columns(2,gap="large")  
        with kol1:
            st.subheader("Tren Pajak per Bulan")
            pajak_perbulan = self.df_filtered.groupby("Bulan")["Jumlah Pajak"].sum().reset_index()
            pajak_perbulan["Bulan"] = pajak_perbulan["Bulan"].astype(str)
            fig = px.line(pajak_perbulan, x="Bulan", y="Jumlah Pajak", labels={"Bulan": "Bulan", "Jumlah Pajak": "Total Pajak"},
                          color_discrete_sequence=['#F2B949'])
            fig.update_layout(margin=dict(t=5, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with kol2:
            # Rasio Pajak per Bulan
            st.subheader("Rasio Pajak per Bulan")
            self.df_filtered["Rasio Pajak (%)"] = (self.df_filtered["Jumlah Pajak"] / self.df_filtered["Jumlah Nominal"]) * 100
            rasio_pajak_per_bulan = self.df_filtered.groupby("Bulan")["Rasio Pajak (%)"].mean().reset_index()
            rasio_pajak_per_bulan["Bulan"] = rasio_pajak_per_bulan["Bulan"].astype(str)
            fig = px.line(
                rasio_pajak_per_bulan, x="Bulan", y="Rasio Pajak (%)",
                labels={"Bulan": "Bulan", "Rasio Pajak (%)": "Rata-rata Rasio Pajak (%)"},
                color_discrete_sequence=['#F2B949'])
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
