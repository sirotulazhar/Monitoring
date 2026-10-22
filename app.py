import streamlit as st

st.set_page_config(
    page_title="Toko Azhar",
    page_icon="🛒",
    layout="wide"
)

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

def use_demo_account():
    st.session_state.login_username = "admin@gmail.com"
    st.session_state.login_password = "admin123"

if not st.session_state.logged_in:
    # Inisialisasi nilai input login
    if "login_username" not in st.session_state:
        st.session_state.login_username = ""

    if "login_password" not in st.session_state:
        st.session_state.login_password = ""

    st.markdown(
        """
        <style>
            .login-container {
                max-width: 600px;
                margin: auto;
                border-radius: 12px;
                background-color: white;
                text-align: center;
            }

            .demo-info {
                padding: 16px 20px;
                margin-top: 12px;
                margin-bottom: 10px;
                border: 1px solid #dbeafe;
                border-radius: 10px;
                background-color: #eff6ff;
                color: #1e3a8a;
            }

            .demo-info p {
                margin-bottom: 6px;
                font-size: 14px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.title("Login")

        
with st.form("Login"):
    username = st.text_input(
        "Username",
        key="login_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    login_btn = st.form_submit_button(
        "Login",
        use_container_width=True
    )

    # Informasi akun demo
    st.markdown(
        """
        <div style="
            padding: 16px;
            margin-top: 12px;
            margin-bottom: 10px;
            border: 1px solid #dbeafe;
            border-radius: 10px;
            background-color: #eff6ff;
            color: #1e3a8a;
        ">
            <strong>🧪 Akun Demo untuk Testing</strong>
            <p>Gunakan akun berikut untuk mencoba fitur dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.button(
        "Pakai Akun Demo",
        use_container_width=True,
        on_click=use_demo_account
    )

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
    # st.set_page_config(page_title='Toko Azhar', page_icon='🛒', layout='wide')
    st.markdown("""
                <style>
                    .stAlert { margin-bottom: 0px !important; }  /* Hapus jarak bawah info */
                    div[data-testid="stMetric"] { margin-top: -90px; }  /* Naikkan metric */
                </style>
            """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="padding: 5px; border-radius: 5px; margin-left: 75px;">
            <h1 style='font-size: 35px; text-align: center;'>Monitoring Transaksi Toko Azhar</h1>
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
