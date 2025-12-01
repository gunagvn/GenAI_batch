import streamlit as st
import requests
import pandas as pd

# ---------------- CONFIG ----------------
GEOAPIFY_API_KEY = "4d75df18faa64896b8b231bb251db3cd"  # <--- REPLACE WITH YOUR OWN KEY

# ---------------- CUSTOM CSS ----------------
def load_css():
    st.markdown("""
        <style>
        .place-card {
            border: 1px solid #2c2c2c;
            background: #1d1d1d;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 12px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.2);
            transition: transform 0.2s ease;
        }
        .place-card:hover {
            transform: scale(1.01);
            border-color: #ff4b4b;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------- API HELPERS ----------------
def get_coordinates(city_name):
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": city_name, "limit": 1, "apiKey": GEOAPIFY_API_KEY}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        if data["features"]:
            return data["features"][0]["properties"]
    return None


def get_nearby_places(lat, lon, category_key):
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": category_key,
        "filter": f"circle:{lon},{lat},5000",
        "limit": 12,
        "apiKey": GEOAPIFY_API_KEY
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()["features"]
    return []


def get_place_details(place_id):
    url = f"https://api.geoapify.com/v2/place-details"
    params = {"id": place_id, "apiKey": GEOAPIFY_API_KEY}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        if data["features"]:
            return data["features"][0]["properties"]
    return None


# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="City Explorer Pro", page_icon="🌍", layout="wide")
load_css()

# Sidebar
with st.sidebar:
    st.title("🛠 Explorer Settings")
    st.image("https://cdn-icons-png.flaticon.com/512/854/854878.png", width=100)

    search_type = st.radio(
        "Choose Category:",
        ("Tourist Attractions", "Temples", "Supermarkets", "Restaurants", "Hospitals", "Hotels")
    )

    st.info("Results shown within 5 km radius.")

category_map = {
    "Tourist Attractions": "tourism.sights,tourism.attraction",
    "Temples": "religion.place_of_worship",
    "Supermarkets": "commercial.supermarket",
    "Restaurants": "catering.restaurant",
    "Hospitals": "healthcare.hospital",
    "Hotels": "accommodation.hotel"
}

# Session State
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

# Header
st.title(f"🔍 Discover {search_type}")

city = st.text_input("Enter city name (e.g., 'Thanjavur', 'Delhi'):")

if city:
    location = get_coordinates(city)

    if location:
        lat, lon = location["lat"], location["lon"]
        formatted_addr = location.get("formatted", city)

        places = get_nearby_places(lat, lon, category_map[search_type])

        st.success(f"📍 Showing results near *{formatted_addr}*")

        if places:
            cols = st.columns(2)

            for idx, place in enumerate(places):
                props = place["properties"]
                name = props.get("name", "Unnamed Place")
                addr = props.get("formatted", "Address not available")
                place_id = props.get("place_id")

                with cols[idx % 2]:
                    st.markdown(f"<div class='place-card'><h3>{name}</h3><p>{addr}</p></div>", unsafe_allow_html=True)
                    if st.button(f"View Details - {name}", key=f"btn_{place_id}"):
                        st.session_state.selected_place = place

        else:
            st.warning("No places found within 5 km.")

    else:
        st.error("City not found!")


# ---------------- DETAILS VIEW ----------------
if st.session_state.selected_place:
    st.markdown("---")
    st.header("📌 Place Details")

    place = st.session_state.selected_place
    props = place["properties"]
    name = props.get("name", "Unnamed")
    address = props.get("formatted", "Address not available")
    lat, lon = props["lat"], props["lon"]
    place_id = props.get("place_id")

    # Fetch full details
    details = get_place_details(place_id)

    description = details.get("description", "No description available.") if details else "Not available"
    opening_hours = details.get("opening_hours", "Not available") if details else "Not available"
    categories = ", ".join(details.get("categories", [])) if details else "Not available"

    # IMAGE (Unsplash auto)
    image_url = f"https://source.unsplash.com/800x500/?{name.replace(' ', '%20')}"

    st.image(image_url, use_container_width=True)

    st.subheader(name)
    st.caption(address)

    st.write(f"### 🕒 Opening Hours\n{opening_hours}")
    st.write(f"### 🧭 Category\n{categories}")
    st.write(f"### 📘 Description\n{description}")

    st.subheader("📍 Map Location")
    map_df = pd.DataFrame([{"lat": lat, "lon": lon}])
    st.map(map_df, size=60)

    if st.button("Close Details"):
        st.session_state.selected_place = None
