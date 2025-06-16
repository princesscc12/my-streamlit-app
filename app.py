import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import base64

API_KEY = "969f9fd68e54e135160a7f0e1f118155"
anim_dir = os.path.join(os.path.dirname(__file__), "videos")

def get_weather_data(city, unit):
    unit_param = "metric" if unit == "Celsius" else "imperial"
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit_param}"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit_param}"
    try:
        current_data = requests.get(current_url).json()
        forecast_data = requests.get(forecast_url).json()
    except:
        current_data, forecast_data = {}, {}
    return current_data, forecast_data

def get_location_by_ip():
    try:
        res = requests.get("http://ip-api.com/json").json()
        return res.get("city", "Canberra")
    except:
        return "Canberra"

def weather_icon(description):
    desc = description.lower()
    if 'rain' in desc:
        return '🌧️'
    elif 'cloud' in desc:
        return '☁️'
    elif 'clear' in desc:
        return '☀️'
    elif 'snow' in desc:
        return '❄️'
    elif 'storm' in desc or 'thunder' in desc:
        return '⛈️'
    else:
        return '🌥️'

def weather_animation(description):
    desc = description.lower()
    if 'rain' in desc:
        return os.path.join(anim_dir, "hujan.gif")
    elif 'cloud' in desc:
        return os.path.join(anim_dir, "mendung.gif")
    elif 'clear' in desc:
        return os.path.join(anim_dir, "cerah.gif")
    elif 'storm' in desc or 'thunder' in desc:
        return os.path.join(anim_dir, "petir.gif")
    else:
        return os.path.join(anim_dir, "cerah.gif")

def main():
    st.set_page_config(page_title="Aplikasi Cuaca", page_icon="🌦️", layout="centered")

    st.markdown("""
        <style>
            .main {
                background: linear-gradient(to bottom, #76b6ec, #c2dfff);
                color: white;
            }
            h1, h2, h3, h4, h5, h6, p {
                color: white !important;
            }
            .block-container {
                padding-top: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>🌤️ Aplikasi Cuaca Modern</h1>", unsafe_allow_html=True)

    default_city = get_location_by_ip()
    city = st.text_input("Masukkan nama kota", default_city)
    unit = st.selectbox("Pilih satuan suhu", ["Celsius", "Fahrenheit"])

    if st.button("Lihat Cuaca"):
        current_data, forecast_data = get_weather_data(city, unit)

        if not current_data or current_data.get("cod") != 200:
            st.error("Kota tidak ditemukan atau terjadi kesalahan pada API.")
            return

        weather = current_data['weather'][0]
        temp = int(current_data['main']['temp'])
        desc = weather['description'].capitalize()
        icon = weather_icon(weather['main'])
        temp_max = int(current_data['main']['temp_max'])
        temp_min = int(current_data['main']['temp_min'])
        degree_sign = "°C" if unit == "Celsius" else "°F"

        anim_path = weather_animation(weather['main'])
        if os.path.exists(anim_path):
            with open(anim_path, "rb") as f:
                gif_bytes = f.read()
                encoded_gif = base64.b64encode(gif_bytes).decode()
        else:
            encoded_gif = ""

        # Cuaca saat ini
        st.markdown(f"""
        <div style="
            position: relative;
            width: 100%;
            max-width: 400px;
            height: 250px;
            margin: auto;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        ">
            <img src="data:image/gif;base64,{encoded_gif}" style="
                position: absolute;
                top: 0; left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                filter: brightness(0.55);
                z-index: 1;
            " />
            <div style="
                position: relative;
                z-index: 2;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                padding: 10px 20px;
                color: white;
                text-shadow: 0px 0px 6px rgba(0, 0, 0, 0.8);
                font-family: Arial, sans-serif;
            ">
                <div style="font-size: 20px; font-weight: 500;">📍 {city.title()}</div>
                <div style="font-size: 64px; font-weight: bold; margin-top: -10px;">{temp}{degree_sign}</div>
                <div style="font-size: 18px; margin-top: -5px;">{desc} {icon}</div>
                <div style="font-size: 14px; margin-top: 5px;">Tinggi: {temp_max}{degree_sign} | Rendah: {temp_min}{degree_sign}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Info tambahan
        st.markdown("""
        <div style='background-color:#2c70c8; border-radius:10px; padding:10px; color:white; margin-top:20px;'>
            <strong>⚠️ Luapan Air Sungai</strong><br>
            Australian Government Bureau of Meteorology: Luapan Air Sungai di Molonglo River.
        </div>
        """, unsafe_allow_html=True)

        # Ramalan per jam
        st.subheader("🌥️ Ramalan Per Jam (3 Jam Sekali)")
        hourly_df = pd.DataFrame(forecast_data.get('list', []))
        if not hourly_df.empty:
            hourly_df['dt_txt'] = pd.to_datetime(hourly_df['dt_txt'])
            next_hours = hourly_df.head(6)

            cols = st.columns(6)
            for i, col in enumerate(cols):
                hour = next_hours.iloc[i]['dt_txt'].strftime("%H:%M")
                temp_hour = int(next_hours.iloc[i]['main']['temp'])
                icon_hour = weather_icon(next_hours.iloc[i]['weather'][0]['main'])
                col.markdown(f"<center>{hour}<br>{icon_hour}<br>{temp_hour}{degree_sign}</center>", unsafe_allow_html=True)

            # Ramalan 5 hari
            st.subheader("☁️ Ramalan 5 Hari")
            hourly_df['date'] = hourly_df['dt_txt'].dt.date
            daily_forecast = hourly_df.groupby('date').agg(
                temp_min=('main', lambda x: min(item['temp_min'] for item in x)),
                temp_max=('main', lambda x: max(item['temp_max'] for item in x)),
                icon_desc=('weather', lambda x: x.iloc[0][0]['main'])
            ).reset_index()

            cols = st.columns(min(5, len(daily_forecast)))
            for i, col in enumerate(cols):
                day = daily_forecast.iloc[i]['date'].strftime("%a, %d %b")
                icon_desc = daily_forecast.iloc[i]['icon_desc']
                icon_day = weather_icon(icon_desc)
                temp_max = int(daily_forecast.iloc[i]['temp_max'])
                temp_min = int(daily_forecast.iloc[i]['temp_min'])
                col.markdown(f"""
                    <div style="text-align:center; font-family: Arial, sans-serif;">
                        <div style="font-weight:bold;">{day}</div>
                        <div style="font-size: 32px;">{icon_day}</div>
                        <div style="font-size: 14px;">{temp_max}{degree_sign} / {temp_min}{degree_sign}</div>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
