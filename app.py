import streamlit as st
from data_loader import load_data
from provinsi import ProvinceDashboard
from kota import CityDashboard
from payment import PaymentDashboard
from merchant import MerchantDashboard
import seaborn as sns
from streamlit_option_menu import option_menu


sns.set(style='dark')
st.set_page_config(page_title='Toko Ladang', page_icon='🛒', layout='wide')

st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; }  /* Hapus jarak bawah info */
                    div[data-testid="stMetric"] { margin-top: -50px; }  /* Naikkan metric */
                </style>
            """, unsafe_allow_html=True)

st.markdown(
    """
    <div style='background-color: #f0f0f0; padding: 5px; border-radius: 5px;'>
        <h1 style='font-size: 32px; text-align: center;'>Monitoring Transaksi SIPLah Toko Ladang 2024, 2025</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .css-1e5imcs { font-size: 10px !important; }  /* Untuk teks menu */
    .css-10trblm { font-size: 10px !important; }  /* Untuk teks yang terpilih */
    .css-1d391kg { font-size: 10px !important; }  /* Untuk teks sub-menu */
    </style>
    """,
    unsafe_allow_html=True
)

# Load dataset
df = load_data()

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard", 
            "Detail Harian Transaksi",  
            "Wilayah Provinsi",  
            "Wilayah Kota / Kabupaten",  
            "Per Metode Pembayaran",  
            "Pendaftaran Merchant"
        ],
        icons=[
            "speedometer",  
            "calendar-check",  
            "globe", 
            "building",  
            "credit-card",  
            "shop",  
        ],
        menu_icon="list",  # Ikon menu utama
    )

# Menjalankan Dashboard yang Dipilih
if selected == 'Dashboard':
    st.title(f'hello')
elif selected == 'Detail Harian Transaksi':
    st.title(f'hello')
elif selected == 'Wilayah Provinsi':
    ProvinceDashboard(df).run()
elif selected == 'Wilayah Kota / Kabupaten':
    CityDashboard(df).run()
elif selected == 'Per Metode Pembayaran':
    PaymentDashboard(df).run()
elif selected == 'Pendaftaran Merchant':
    MerchantDashboard(df).run()
