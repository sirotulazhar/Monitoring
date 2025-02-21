import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Setup Streamlit
sns.set(style='dark')

# Load cleaned dataset
df = pd.read_csv('Submission\\Dashboard\\PRSA_Data_cleaned.csv')

# Convert the 'date' column to datetime format for better handling
df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])

# Sidebar
with st.sidebar:
    st.image("Submission\\Dashboard\\logo.jpeg", width=100)

    # Date Range Selection
    min_date = df['datetime'].min()
    max_date = df['datetime'].max()

    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter data based on selected date range
filtered_df = df[(df['datetime'] >= pd.to_datetime(start_date)) & (df['datetime'] <= pd.to_datetime(end_date))]

# Main Title
st.title("PRSA PM2.5 Analysis Dashboard")

# PM2.5 Trend Over Time
st.subheader("Trend of PM2.5 Over Time")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x=filtered_df['datetime'], y=filtered_df['PM2.5'], marker='o', color='b', ax=ax)
plt.axhline(y=filtered_df['PM2.5'].mean(), color='r', linestyle='--', label='Average PM2.5')
plt.title('PM2.5 Concentration Over Time', fontsize=16)
plt.xlabel('Date')
plt.ylabel('PM2.5 Concentration')
plt.xticks(rotation=45)
st.pyplot(fig)

# Weather Impact on PM2.5
st.subheader("Weather Factors Impacting PM2.5")

# Scatterplot - PM2.5 vs Temperature
st.write("**PM2.5 vs Temperature**")
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(x=filtered_df['TEMP'], y=filtered_df['PM2.5'], ax=ax)
plt.title('PM2.5 vs Temperature', fontsize=16)
plt.xlabel('Temperature (°C)')
plt.ylabel('PM2.5 Concentration')
st.pyplot(fig)

# Scatterplot - PM2.5 vs Kelembaban
st.write("**PM2.5 vs Kelembaban**")
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(x=filtered_df['DEWP'], y=filtered_df['PM2.5'], ax=ax)
plt.title('PM2.5 vs Kelembaban', fontsize=16)
plt.xlabel('Kelembaban (%)')
plt.ylabel('PM2.5 Concentration')
st.pyplot(fig)

# Correlation Heatmap
st.subheader("Correlation Between Variables")
corr = filtered_df[['PM2.5', 'TEMP', 'DEWP', 'PRES']].corr()
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
plt.title('Correlation Heatmap', fontsize=16)
st.pyplot(fig)

# Add any additional charts or explanations as needed

st.caption("PRSA Air Quality Analysis Dashboard - Copyright (C) Siti Sirotul Azhar 2024")
