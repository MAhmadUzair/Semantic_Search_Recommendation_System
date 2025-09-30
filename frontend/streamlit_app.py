import streamlit as st
import httpx

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Semantic Ads Demo", layout="wide")

st.title("Semantic Ads — Demo")
st.markdown("Enter a natural language query (e.g., 'I have a football product, suggest spots near stadiums')")

with st.sidebar:
    st.header("Demo Settings")
    backend = st.text_input("Backend URL", value=BACKEND_URL)
    top_k = st.slider("Top K results", min_value=1, max_value=20, value=6)
    lat = st.number_input("Your latitude (optional)", value=0.0, format="%.6f")
    lon = st.number_input("Your longitude (optional)", value=0.0, format="%.6f")
    use_location = st.checkbox("Provide lat/lon", value=False)

query = st.text_input("Search query", value="I want to advertise a football kit near stadiums")
if st.button("Search"):
    payload = {
        "query": query,
        "top_k": top_k,
    }
    if use_location:
        payload["lat"] = lat
        payload["lon"] = lon
        payload["radius_km"] = 25.0

    with st.spinner("Searching..."):
        try:
            r = httpx.post(f"{backend}/search/semantic", json=payload, timeout=20.0)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            if not results:
                st.info("No results found.")
            else:
                for item in results:
                    st.markdown(f"### {item['title']}  \n**Score**: {item['final_score']:.3f} • **Semantic**: {item['semantic_score']:.3f}")
                    st.markdown(f"- Description: {item.get('description')}")
                    st.markdown(f"- Distance (km): {item.get('distance_km')}")
                    st.markdown(f"- Estimated impressions/day: {item.get('traffic_estimate')} ({item.get('traffic_confidence')})")
                    st.markdown("---")
        except Exception as e:
            st.error(f"Search failed: {e}")
