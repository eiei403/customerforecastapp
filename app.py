import streamlit as st
import time
from datetime import timedelta
from config import insert_forecast_to_mssql
import matplotlib.pyplot as plt
from forecast_2017 import forecast_2017 
from customerforecast import plot_forecast

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="Predictive Sales Modeling", layout="centered")
st.title("📈Sales Forecasting")

# ---------- Initialize Session State ----------
if 'forecast_sales_ready' not in st.session_state:
    st.session_state.forecast_sales_ready = False

# ---------- SECTION 1: Forecast Sales ----------
st.header("🧾📊 Forecast Sales")

# ---------- Run Forecast Button ----------
if st.button("🔁 Run Forecast Sales"):
    status_info = st.empty()
    progress_bar = st.progress(0)

    status_info.info("Running forecast Sales...")

    def update_progress(current, total, cust_key=None, item_key=None):
        percent = int((current / total) * 100)
        progress_bar.progress(percent)
        status_info.text(f"⏳ {percent}% - Cust:{cust_key} Item:{item_key} ({current}/{total})")

    # Run actual forecast
    with st.spinner("🧠 Finalizing forecast..."):
        forecast_df, accuracy = forecast_2017()

    st.session_state.forecast_df_sales = forecast_df
    st.session_state.forecast_accuracy = accuracy
    st.session_state.forecast_sales_ready = True  # ✅ Set ready flag
    progress_bar.empty()
    status_info.success("✅ Forecast completed.")
    st.info("📡 Generating graph...")


# ---------- Reset Button ----------
if st.button("🔄 Reset Forecast"):
    st.session_state.forecast_sales_ready = False
    st.session_state.pop("forecast_df_sales", None)
    st.session_state.pop("forecast_accuracy", None)
    st.info("Session reset. Ready to forecast again.")

# ---------- Display Graph ----------
if st.session_state.forecast_sales_ready:
    st.subheader("📊 Sales Forecast Visualization")
    st.metric("🎯 Forecast Accuracy (Nov-Dec 2016)", f"{st.session_state.forecast_accuracy}%")

    # Optional: show top rows of forecast
    st.dataframe(st.session_state.forecast_df_sales.head(10))

    # Plot forecast
    fig = plot_forecast()
    st.pyplot(fig)

    if st.button("✅ Confirm Upload Sales Forecast to SQL Server"):
        insert_forecast_to_mssql(st.session_state.forecast_df_sales)
        st.success("📥 Sales Forecast Uploaded to MSSQL Successfully!")
