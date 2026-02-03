import streamlit as st
import requests
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def delete_room_data(home, room):
    """Deletes the room data from Firebase."""
    try:
        url = f"{BASE_URL}/{home}/{room}.json"
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        st.error(f"Error deleting data: {e}")
        return False

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
                # Create figure with secondary y-axis
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # Add Temperature trace
                fig.add_trace(
                    go.Scatter(
                        x=df['Time'], 
                        y=df['Temperature'], 
                        name="Temperature (°C)",
                        mode='lines+markers', 
                        line=dict(color='#FF5733', width=2, shape='spline'),
                        marker=dict(size=6)
                    ),
                    secondary_y=False,
                )

                # Add Humidity trace
                fig.add_trace(
                    go.Scatter(
                        x=df['Time'], 
                        y=df['Humidity'], 
                        name="Humidity (%)",
                        mode='lines+markers', 
                        line=dict(color='#33C1FF', width=2, shape='spline'),
                        marker=dict(size=6)
                    ),
                    secondary_y=True,
                )

                # Add figure title and layout updates
                fig.update_layout(
                    title_text=f"Environment Data - {selected_room}",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white",
                    height=500
                )

                # Set x-axis title
                fig.update_xaxes(title_text="Time")

                # Set y-axes titles
                fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False, title_font=dict(color="#FF5733"))
                fig.update_yaxes(title_text="Humidity (%)", secondary_y=True, title_font=dict(color="#33C1FF"))

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeseries data available for charts.")

            # Clear Data Button
            st.divider()
            if st.button("Clear Room Data", type="primary"):
                if delete_room_data(selected_home, selected_room):
                    st.success(f"Cleared data for {selected_room} in {selected_home}!")
                    st.rerun()

if __name__ == "__main__":
    main()
