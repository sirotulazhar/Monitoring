import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go
import altair as alt

# Setup Streamlit
sns.set(style='dark')
st.set_page_config(page_title='Dashboard', page_icon='🌎', layout='wide')
st.title('Monitoring Transaksi SIPLah Toko Ladang 2024, 2025')
st.markdown('##')


# Load cleaned dataset
df = pd.read_csv('cleaned_data.csv')

# Convert the 'date' column to datetime format for better handling
df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')

# Konversi kolom waktu ke datetime agar bisa difilter
df['waktu'] = pd.to_datetime(df['waktu'], errors='coerce')

# Ambil rentang waktu minimum dan maksimum dari dataset
min_date = df['waktu'].min().date()  # Pastikan dalam format date
max_date = df['waktu'].max().date()

# Pilih rentang waktu di sidebar
start_date, end_date = st.sidebar.date_input(
    label="Pilih Rentang Waktu",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Pastikan nilai start_date dan end_date dikonversi ke datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)


# Normalisasi teks agar seragam
df['prov_sekolah'] = df['prov_sekolah'].str.strip().str.title()
df['kota_kab_sekolah'] = df['kota_kab_sekolah'].str.strip().str.title()
df['payment_method'] = df['payment_method'].str.strip().str.lower()

# Pilihan kabupaten/kota unik
prov_list = df['prov_sekolah'].unique()
selected_provinsi = st.sidebar.selectbox("Provinsi", options=prov_list)

kota_list = df['kota_kab_sekolah'].unique()
selected_kota = st.sidebar.selectbox("Kota/Kabupaten", options=kota_list)

# Filter data berdasarkan yang dipilih
filtered_df = df[
    (df['waktu'] >= pd.to_datetime(start_date)) & 
    (df['waktu'] >= pd.to_datetime(start_date)) &
    (df['prov_sekolah'] == selected_provinsi)
]

# PROVINSI
st.subheader(f"{selected_provinsi}")

st.write(f"Rentang waktu: {start_date} sampai {end_date}")

# Fungsi untuk membulatkan angka besar
def format_rupiah(value):
    if value >= 1_000_000_000_000:  
        return f"{value/1_000_000_000_000:.1f} T"
    elif value >= 1_000_000_000:  
        return f"{value/1_000_000_000:.1f} M"
    elif value >= 1_000_000:  
        return f"{value/1_000_000:.1f} Jt"
    else:
        return f"Rp {value:,.0f}"

# Menampilkan metrik utama
total_pembelian = filtered_df['jumlah_po'].sum()
total_nominal = filtered_df['nominal_po'].sum()
total_pajak = filtered_df['total_pajak'].sum()

# Buat layout dalam 3 kolom
total1, total2, total3 = st.columns(3, gap='small')

with total1:
    st.info('Jumlah PO', icon="🛒")
    st.metric(label="Total", value=f"{total_pembelian}")

with total2:
    st.info('Jumlah Nominal', icon="💰")
    st.metric(label="Nominal", value=format_rupiah(total_nominal))

with total3:
    st.info('Jumlah Pajak', icon="📊")
    st.metric(label="Pajak", value=format_rupiah(total_pajak))

df_monthly = (
    filtered_df.groupby(filtered_df['waktu'].dt.to_period('M'))['nominal_po']
    .sum()
    .reset_index()
)

df_monthly['waktu'] = df_monthly['waktu'].astype(str) 
df_monthly["nominal"] = df_monthly["nominal_po"] / 1_000_000
df_monthly["formatted_nominal"] = df_monthly["nominal_po"].apply(format_rupiah) 

if not df_monthly.empty:
    # Buat bar chart dengan Altair
    chart = alt.Chart(df_monthly).mark_bar(color="#0083B8").encode(
        x=alt.X("waktu:O", title="Bulan", sort=None),
        y=alt.Y("nominal:Q", title="Total Transaksi"),
        tooltip=["waktu", alt.Tooltip("nominal:Q", format=".2f")]
    ).properties(
        width=800,
        height=400
    )

    # Tambahkan label total transaksi dalam format rupiah di atas batang
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5  # Geser ke atas sedikit
    ).encode(
        text="formatted_nominal"  # Pakai format rupiah
    )

    # Gabungkan bar chart dan labelnya
    st.altair_chart(chart + text, use_container_width=True)

else:
    st.warning(f"Tidak ada data transaksi untuk {selected_provinsi} dalam rentang waktu {start_date} - {end_date}.")

# KOTA/KABUPATEN
kota_list = filtered_df['kota_kab_sekolah'].unique()
selected_kota = st.sidebar.selectbox("Kota/Kabupaten", options=kota_list)

filtered_df_kota = filtered_df[
    (filtered_df['kota_kab_sekolah'] == selected_kota)
]

df_monthly_kota = (
    filtered_df_kota.groupby(filtered_df_kota['waktu'].dt.to_period('M'))['nominal_po']
    .sum()
    .reset_index()
)

df_monthly_kota['waktu'] = df_monthly_kota['waktu'].astype(str)
df_monthly_kota["nominal"] = df_monthly_kota["nominal_po"] / 1_000_000
df_monthly_kota["formatted_nominal"] = df_monthly_kota["nominal_po"].apply(format_rupiah)

if not df_monthly_kota.empty:
    chart_kota = alt.Chart(df_monthly_kota).mark_bar(color="#FF5733").encode(
        x=alt.X("waktu:O", title="Bulan", sort=None),
        y=alt.Y("nominal:Q", title="Total Transaksi"),
        tooltip=["waktu", alt.Tooltip("nominal:Q", format=".2f")]
    ).properties(
        width=800,
        height=400
    )

    text_kota = chart_kota.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text="formatted_nominal"
    )

    st.altair_chart(chart_kota + text_kota, use_container_width=True)
else:
    st.warning(f"Tidak ada data transaksi untuk {selected_kota} dalam rentang waktu {start_date.date()} - {end_date.date()}.")
