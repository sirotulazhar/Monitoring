import streamlit as st
from data.data_loader import load_regions_data,load_merchant,load_transaksi,load_harian
from dashboard.provinsi import ProvinceDashboard
from dashboard.kota import CityDashboard
from dashboard.payment import PaymentDashboard
from dashboard.merchant import MerchantDashboard
from dashboard.harian import Dashboardharian
from dashboard.laman_1 import TokoLadangDashboard
from dashboard.upload import FileUploader
import seaborn as sns
from streamlit_option_menu import option_menu
from auth.authentication import authenticate
from auth.authorization import handler

sns.set(style='dark')

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.set_page_config(page_title="Login - Toko Ladang", page_icon="🛒", layout="centered")
    st.markdown(
    """
    <style>
        .login-container {
            max-width: -10000000px;  /* Atur lebar login box */
            margin: auto;  /* Tengah layar */
            border-radius: 0px;
            background-color: white;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
    </style>
    <div class="login-container">
    """,
    unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])  # Tengah = 2 kali lebih besar

    with col2:  # Menempatkan form di tengah
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        with st.form("Login"):
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

        st.markdown('</div>', unsafe_allow_html=True)

    if login_btn:
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Username atau password salah!")

else:
    st.set_page_config(page_title='Toko Ladang', page_icon='🛒', layout='wide')
    st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; }  /* Hapus jarak bawah info */
                    div[data-testid="stMetric"] { margin-top: -90px; }  /* Naikkan metric */
                </style>
            """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="padding: 5px; border-radius: 5px; margin-left: 75px;">
            <h1 style='font-size: 35px; text-align: center;'>Monitoring Transaksi SIPLah Toko Ladang</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    all_menu_options = [
        "Dashboard", 
        "Detail Harian Transaksi",  
        "Wilayah Provinsi",  
        "Wilayah Kota / Kabupaten",  
        "Per Metode Pembayaran",  
        "Pendaftaran Merchant",
        "Upload Data"
    ]

    all_icons = [
        "speedometer",  
        "calendar-check",  
        "globe", 
        "building",  
        "credit-card",  
        "shop",
        "upload"
    ]
            
    col6, col7 = st.columns([0.24, 0.7])  

    filtered_menu_options = [feature for feature in all_menu_options if handler.handle(st.session_state.role, feature)]
    filtered_icons = [icon for feature, icon in zip(all_menu_options, all_icons) if feature in filtered_menu_options]

    with col6:
        st.markdown(
            f"""
            <div style="border-radius: 5px; text-align: center;">
                <h3> 👨‍💻 {st.session_state.role} </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
            
        selected = option_menu(
            menu_title="",
            options=filtered_menu_options,
            icons=filtered_icons,
            default_index=0
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    with col7:
        if selected == 'Dashboard':
            st.cache_data.clear()
            TokoLadangDashboard(load_transaksi()).run()
        elif selected == 'Detail Harian Transaksi':
            st.cache_data.clear()
            Dashboardharian(load_harian()).run()
        elif selected == 'Wilayah Provinsi':
            st.cache_data.clear()
            ProvinceDashboard(load_regions_data()).run()
        elif selected == 'Wilayah Kota / Kabupaten':
            st.cache_data.clear()
            CityDashboard(load_regions_data()).run()
        elif selected == 'Per Metode Pembayaran':
            st.cache_data.clear()
            PaymentDashboard(load_regions_data()).run()
        elif selected == 'Pendaftaran Merchant':
            st.cache_data.clear()
            MerchantDashboard(load_merchant()).run()

        elif selected == "Upload Data":
            FileUploader().run()
