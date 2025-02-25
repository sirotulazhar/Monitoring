import streamlit as st
import altair as alt
import pandas as pd
from dashboard.bs_dashboard import BaseDashboard
from dashboard.utils import format_angka

class MerchantDashboard(BaseDashboard):
    def filter_data(self):
        df = pd.read_csv('cleaned_merchant.csv')
        df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')
        df['provinsi'] = df['provinsi'].str.strip().str.title()

        return df
    
    def show_metrics(self):
        self.df = self.filter_data()

        if self.df is None or self.df.empty:
            st.warning("Data tidak tersedia atau kosong.")
            return
        
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            start_date, end_date = st.date_input(
                    "Rentang Waktu",
                    value=[self.df['waktu'].min(), self.df['waktu'].max()],
                    min_value=self.df['waktu'].min(),
                    max_value=self.df['waktu'].max()
                )
            
        with col2:
            self.selected_provinsi = st.selectbox("Provinsi", options=self.df['provinsi'].unique())\
            
        with col3:
            self.selected_kota = st.selectbox("Kota/Kabupaten", options=self.df[self.df['provinsi'] == self.selected_provinsi]['kab_kota'].unique())

        self.filtered_df = self.df[
                (self.df['waktu'] >= pd.Timestamp(start_date)) &
                (self.df['waktu'] <= pd.Timestamp(end_date)) &
                (self.df['provinsi'] == self.selected_provinsi) &
                (self.df['kab_kota'] == self.selected_kota)
            ]

        if self.filtered_df.empty:
            st.warning("Tidak ada data dalam rentang waktu yang dipilih.")
            return
        
        delta_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days

        if delta_days > 31:  
            self.filtered_df['periode'] = self.filtered_df['waktu'].dt.to_period('M').astype(str)
        elif delta_days > 7:  
            self.filtered_df['periode'] = self.filtered_df['waktu'].dt.to_period('W').astype(str)
        else:  
            self.filtered_df['periode'] = self.filtered_df['waktu'].dt.strftime('%Y-%m-%d')

        df_grouped = (
            self.filtered_df.groupby('periode', as_index=False)['jumlah_merchant'].sum()
        )

        if df_grouped.empty:
            st.warning("Tidak ada data transaksi pada periode yang dipilih.")
            return
    
        col4, _, col5 = st.columns([4, 0.12, 1.2])

        with col4:
            with st.container():
                chart = alt.Chart(df_grouped).mark_bar(color="#0083B8").encode(
                    x=alt.X("periode:O", title="Waktu", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("jumlah_merchant:Q", title="Jumlah Merchant"),
                    tooltip=["periode", "jumlah_merchant"]
                ).properties(width=800, height=400)

                df_grouped["formatted_jumlah"] = df_grouped["jumlah_merchant"].apply(format_angka)

                text = chart.mark_text(
                    align='center',
                    baseline='bottom',
                    dy=-5  
                ).encode(
                    text="formatted_jumlah"  
                )

                st.altair_chart(chart + text, use_container_width=True)

        st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; } 
                    div[data-testid="stMetric"] { margin-top: -30px; }  
                </style>
            """, unsafe_allow_html=True)

        st.markdown("""
            <style>
                .stAlert { margin-bottom: 0px !important; } 
                div[data-testid="stInfo"] { margin-top: -30px; }  
            </style>
        """, unsafe_allow_html=True)
        with col5:

            total_merchant = self.filtered_df['jumlah_merchant'].sum()

            st.info('Jumlah Merchant')
            st.metric(label="", value=format_angka(total_merchant))

    def show_visualization(self):
        pass
