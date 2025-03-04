import streamlit as st
from data.data_loader import load_users

def authenticate(username, password):
    users = load_users()
    user = users[(users["username"] == username) & (users["password"] == password)]
    if not user.empty:
        return user.iloc[0]["role"]
    return None
