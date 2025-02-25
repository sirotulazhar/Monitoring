import streamlit as st
import altair as alt
import pandas as pd
from dashboard.bs_dashboard import BaseDashboard
from dashboard.utils import format_rupiah

class ProvinceDashboard(BaseDashboard):
    def filter_data(self):
        pass

    def show_metrics(self):
        col3, col4 = st.columns([2, 2])
        col1, _, col2 = st.columns([4, 0.12, 1.2])
        
        with col1:  # Chart di sebelah kiri
            st.markdown("""
            <style>
                .stAlert { margin-bottom: -20px !important; } 
                div[data-testid="stDateInput"] { margin-top: -30px; }  
            </style>
        """, unsafe_allow_html=True)

            # with st.container():
            
            with col3:
                start_date, end_date = st.date_input(
                "Rentang Waktu",
                value=[self.df['waktu'].min(), self.df['waktu'].max()],
                min_value=self.df['waktu'].min(),
                max_value=self.df['waktu'].max()
            )

            with col4:
                st.markdown("""
                    <style>
                        .stAlert { margin-bottom: -20px !important; } 
                        div[data-testid="stSelectbox"] { margin-top: -45px; }  
                    </style>
                """, unsafe_allow_html=True)
                self.selected_provinsi = st.selectbox("Provinsi", options=self.df['prov_sekolah'].unique())

            self.filtered_df = self.df[
                (self.df['waktu'] >= pd.Timestamp(start_date)) &
                (self.df['waktu'] <= pd.Timestamp(end_date)) &
                (self.df['prov_sekolah'] == self.selected_provinsi)
            ]

            if self.filtered_df.empty:
                st.warning("Tidak ada data dalam rentang waktu yang dipilih.")
                return

            total_pembelian = self.filtered_df['jumlah_po'].sum()
            total_nominal = self.filtered_df['nominal_po'].sum()
            total_pajak = self.filtered_df['total_pajak'].sum()
            # **=== Dynamic Grouping ===**
            delta_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days

            if delta_days > 31:  
                self.filtered_df['periode'] = self.filtered_df['waktu'].dt.to_period('M').astype(str)
            elif delta_days > 7:  
                self.filtered_df['periode'] = self.filtered_df['waktu'].dt.to_period('W').astype(str)
            else:  
                self.filtered_df['periode'] = self.filtered_df['waktu'].dt.strftime('%Y-%m-%d')

            df_grouped = (
                self.filtered_df.groupby('periode', as_index=False)['nominal_po'].sum()
            )

            if df_grouped.empty:
                st.warning("Tidak ada data transaksi pada periode yang dipilih.")
                return

            df_grouped["nominal"] = df_grouped["nominal_po"] / 1_000_000
            df_grouped["formatted_nominal"] = df_grouped["nominal_po"].apply(format_rupiah)

            # with st.container():
            chart = alt.Chart(df_grouped).mark_bar(color="#0083B8").encode(
                x=alt.X("periode:O", title="Periode", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("nominal:Q", title="Total Transaksi"),
                tooltip=["periode", "formatted_nominal"]
            ).properties(width=600, height=400)

            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5
            ).encode(
                text="formatted_nominal"
            )

            st.altair_chart(chart + text, use_container_width=True)

        st.markdown("<h3 style='margin-bottom: 5px;'></h3>", unsafe_allow_html=True)
        st.markdown("""
                <style>
                    div[data-testid="stMetric"] {
                        margin-top: -15px !important; 
                    }
                </style>
            """, unsafe_allow_html=True)

        with col2:
            
            st.info('Jumlah PO', icon="🛒")
            st.metric(label='', value=format_rupiah(total_pembelian))

            st.info('Jumlah Nominal', icon="💰")
            st.metric(label='', value=format_rupiah(total_nominal))

            st.info('Jumlah Pajak', icon="📊")
            st.metric(label='', value=format_rupiah(total_pajak))

        st.caption("Dashboard ©️ 2025 by Toko Ladang")

    def show_visualization(self):
        pass
