import streamlit as st
import requests
import pandas as pd
import json

# Configuration
BASE_URL = "https://environmentsensor-c9fc0-default-rtdb.firebaseio.com/"

def fetch_data():
    """Fetches all data from the Firebase Realtime Database."""
    try:
        response = requests.get(f"{BASE_URL}.json")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching data from Firebase: {e}")
        return None

def main():
    st.set_page_config(page_title="Environment Sensor Dashboard", layout="wide")
    st.title("Environment Sensor Dashboard")

    # Fetch data
    data = fetch_data()

    if not data:
        st.warning("No data available.")
        return

    # Sidebar: Select Home
    home_names = list(data.keys())
    selected_home = st.sidebar.selectbox("Select Home", home_names)

    if selected_home:
        home_data = data[selected_home]
        
        # Sidebar: Select Room
        room_names = list(home_data.keys()) if home_data else []
        selected_room = st.sidebar.selectbox("Select Room", room_names)

        if selected_room:
            room_data = home_data[selected_room]

            # Display Data
            st.header(f"{selected_home} - {selected_room}")

            # Extract lists, handling potential missing keys or empty lists gracefully
            times = room_data.get("Time", [])
            temps = room_data.get("Temperature", [])
            humidities = room_data.get("Humidity", [])

            # Metrics
            col1, col2 = st.columns(2)
            
            current_temp = temps[-1] if temps else "N/A"
            current_humidity = humidities[-1] if humidities else "N/A"
            
            col1.metric("Temperature", f"{current_temp} °C")
            col2.metric("Humidity", f"{current_humidity} %")

            # Charts
            if times:
                # Create a DataFrame for easier plotting
                # Ensure all lists are of same length to avoid pandas errors
                min_len = min(len(times), len(temps), len(humidities))
                
                df = pd.DataFrame({
                    "Time": times[:min_len],
                    "Temperature": temps[:min_len],
                    "Humidity": humidities[:min_len]
                })

                # Tabs for different views
                tab1, tab2 = st.tabs(["Temperature", "Humidity"])

                with tab1:
                    st.subheader("Temperature over Time")
                    st.line_chart(df.set_index("Time")["Temperature"])

                with tab2:
                    st.subheader("Humidity over Time")
                    st.line_chart(df.set_index("Time")["Humidity"])
            else:
                st.info("No timeseries data available for charts.")

if __name__ == "__main__":
    main()
