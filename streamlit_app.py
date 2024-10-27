import streamlit as st
import pandas as pd
from datetime import datetime

# Seiteneinstellungen
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide"
)

# Job-Such Funktionen
def search_jobs(keywords, locations):
    # Simulierte Suchergebnisse
    jobs_data = [
        {
            'title': 'Head of Human Resources',
            'company': 'Erste Group Bank AG',
            'location': 'Wien',
            'salary': '120k-150k',
            'match_score': 95,
            'description': 'Strategische HR-Führungsposition mit Fokus auf Transformation'
        },
        {
            'title': 'Leiter People & Culture',
            'company': 'Österreichische Post AG',
            'location': 'Wien',
            'salary': '110k-140k',
            'match_score': 88,
            'description': 'Gesamtverantwortung für den HR-Bereich'
        }
    ]
    return pd.DataFrame(jobs_data)

# Hauptanwendung
st.title("Persönlicher Job Search Assistant")
st.write("Optimiert für HR & Organisationsentwicklung Positionen in DACH")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Suchfilter")
    
    # Position
    keywords = st.multiselect(
        "Position",
        ["HR Leitung", "Head of HR", "Personalleitung", "People & Culture"],
        ["HR Leitung"]
    )
    
    # Standort
    locations = st.multiselect(
        "Standorte",
        ["Wien", "Graz", "Linz", "Salzburg", "Stuttgart", "München"],
        ["Wien"]
    )
    
    # Gehalt
    salary_range = st.slider(
        "Gehaltsrange (k€)",
        min_value=80,
        max_value=200,
        value=(120, 160),
        step=10
    )
    
    # Match Score
    min_match = st.slider(
        "Minimum Match Score",
        min_value=0,
        max_value=100,
        value=80,
        format="%d%%"
    )

# Hauptbereich
if st.button("🔎 Neue Suche starten", type="primary"):
    with st.spinner('Suche läuft...'):
        # Jobs suchen
        df = search_jobs(keywords, locations)
        
        # Ergebnisse anzeigen
        if not df.empty:
            st.write(f"🎯 Gefunden: {len(df)} passende Positionen")
            
            # Ergebnistabelle
            st.dataframe(df)
            
            # Job Details
            st.subheader("🔍 Job Details")
            selected_job = st.selectbox(
                "Wähle eine Position für mehr Details:",
                df['title'].tolist()
            )
            
            if selected_job:
                job = df[df['title'] == selected_job].iloc[0]
                st.markdown(f"""
                ### {job['title']}
                **Unternehmen:** {job['company']}  
                **Standort:** {job['location']}  
                **Gehalt:** {job['salary']}  
                **Match Score:** {job['match_score']}%
                
                **Beschreibung:**  
                {job['description']}
                """)
        else:
            st.warning("Keine Ergebnisse gefunden.")

# Footer
st.markdown("---")
st.markdown("*Powered by Streamlit* • *JFdCxClaude*")
