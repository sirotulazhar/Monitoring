import streamlit as st
import pandas as pd
from data.data_loader import load_data
from dashboard.provinsi import ProvinceDashboard
from dashboard.kota import CityDashboard
from dashboard.payment import PaymentDashboard
from dashboard.merchant import MerchantDashboard
from dashboard.harian import Dashboardharian
from dashboard.laman_1 import TokoLadangDashboard
import seaborn as sns
from streamlit_option_menu import option_menu
from auth.authentication import authenticate
from auth.authorization import handler

sns.set(style='dark')
st.set_page_config(page_title='Toko Ladang', page_icon='🛒', layout='wide')

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()

        else:
            st.error("Username atau password salah!")
else:
    st.sidebar.write(f"**Logged in as:** `{st.session_state.username}` ({st.session_state.role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


    st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; }  /* Hapus jarak bawah info */
                    div[data-testid="stMetric"] { margin-top: -90px; }  /* Naikkan metric */
                </style>
            """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style= padding: 5px; border-radius: 5px;'>
            <h1 style='font-size: 32px; text-align: center;'>Monitoring Transaksi SIPLah Toko Ladang</h1>
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

    df = load_data()

    col6, col7 = st.columns([0.24, 0.7])  

    with col6:
        selected = option_menu(
            menu_title="",  # Judul menu (opsional)
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
            default_index=0
        )

    with col7:
        if not handler.handle(st.session_state.role, selected):
            st.error("Anda tidak memiliki akses ke fitur ini.")

        else:
            if selected == 'Dashboard':
                TokoLadangDashboard(df).run()
            elif selected == 'Detail Harian Transaksi':
                Dashboardharian(df).run()
            elif selected == 'Wilayah Provinsi':
                ProvinceDashboard(df).run()
            elif selected == 'Wilayah Kota / Kabupaten':
                CityDashboard(df).run()
            elif selected == 'Per Metode Pembayaran':
                PaymentDashboard(df).run()
            elif selected == 'Pendaftaran Merchant':
                MerchantDashboard(df).run()
