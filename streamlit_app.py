import streamlit as st
import pandas as pd

# Seiteneinstellungen
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide"
)

# Titel und Einführung
st.title("Persönlicher Job Search Assistant")
st.write("Optimiert für HR & Organisationsentwicklung Positionen in DACH")

# Sidebar für Filter
with st.sidebar:
    st.header("🔍 Suchfilter")
    
    locations = st.multiselect(
        "Standorte",
        ["Wien", "Niederösterreich", "Oberösterreich", 
         "Steiermark", "Salzburg", "Stuttgart", "München"],
        ["Wien", "Stuttgart"]
    )
    
    salary_range = st.slider(
        "Gehaltsrange (k€)",
        min_value=80,
        max_value=200,
        value=(120, 160),
        step=10
    )
    
    min_match = st.slider(
        "Minimum Match Score",
        min_value=0,
        max_value=100,
        value=80,
        format="%d%%"
    )

# Hauptbereich
col1, col2 = st.columns([3,1])

with col1:
    if st.button("🔎 Neue Suche starten", type="primary", use_container_width=True):
        # Example data
        data = {
            'Titel': [
                'Head of HR Development',
                'Leiter Organisationsentwicklung',
                'Head of People & Culture',
                'HR Director'
            ],
            'Unternehmen': [
                'Erste Group',
                'STRABAG',
                'Red Bull',
                'Siemens'
            ],
            'Ort': [
                'Wien',
                'Stuttgart',
                'Salzburg',
                'München'
            ],
            'Gehalt': [
                '120k-150k',
                '130k-160k',
                '125k-155k',
                '135k-165k'
            ],
            'Match Score': [92, 88, 85, 90]
        }
        
        df = pd.DataFrame(data)
        
        # Show results
        st.write(f"🎯 Gefunden: {len(df)} passende Positionen")
        st.dataframe(
            df.style.background_gradient(
                subset=['Match Score'],
                cmap='Blues'
            ).format({
                'Match Score': '{:.0f}%'
            }),
            use_container_width=True
        )

with col2:
    st.subheader("📊 Quick Stats")
    st.metric(
        label="Aktive Suchen",
        value="4",
        delta="2 neue"
    )
    st.metric(
        label="Neue Jobs heute",
        value="12",
        delta="↑ 5"
    )
    st.metric(
        label="Ø Match Score",
        value="88%",
        delta="↑ 2%"
    )

# Footer
st.markdown("---")
st.markdown("*Powered by Streamlit* • *Built for iPad*")
