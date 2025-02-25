import pandas as pd

def load_users():
    return pd.read_csv("data/login.csv")

def authenticate(username, password):
    users = load_users()
    user = users[(users["username"] == username) & (users["password"] == password)]
    if not user.empty:
        return user.iloc[0]["role"]
    return None
