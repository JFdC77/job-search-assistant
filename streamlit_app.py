import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import time

# Seiteneinstellungen
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State initialisieren
if 'jobs_df' not in st.session_state:
    st.session_state.jobs_df = pd.DataFrame()
if 'last_search' not in st.session_state:
    st.session_state.last_search = None

# Job-Such Funktionen
def search_karriere_at(keywords, locations):
    jobs = []
    base_url = "https://www.karriere.at/jobs/hr-leitung"
    
    try:
        # Simulierte Karriere.at Ergebnisse
        sample_jobs = {
            'Wien': [
                {
                    'title': 'Head of Human Resources',
                    'company': 'Erste Group Bank AG',
                    'location': 'Wien',
                    'salary': '120k-150k',
                    'url': 'https://www.karriere.at/jobs/erste-bank',
                    'description': 'Strategische HR-Führungsposition mit Fokus auf Transformation',
                    'match_score': 95
                },
                {
                    'title': 'Leiter People & Culture',
                    'company': 'Österreichische Post AG',
                    'location': 'Wien',
                    'salary': '110k-140k',
                    'url': 'https://www.karriere.at/jobs/post',
                    'description': 'Gesamtverantwortung für den HR-Bereich',
                    'match_score': 88
                }
            ],
            'Graz': [
                {
                    'title': 'Head of HR Development',
                    'company': 'AVL List GmbH',
                    'location': 'Graz',
                    'salary': '115k-145k',
                    'url': 'https://www.karriere.at/jobs/avl',
                    'description': 'Internationale Personal- und Organisationsentwicklung',
                    'match_score': 92
                }
            ]
        }
        
        # Füge relevante Jobs basierend auf Standort hinzu
        for location in locations:
            if location in sample_jobs:
                jobs.extend(sample_jobs[location])
        
        return jobs
    except Exception as e:
        st.error(f"Fehler bei der Karriere.at Suche: {str(e)}")
        return []
# Hauptanwendung
st.title("Persönlicher Job Search Assistant")
st.write("Optimiert für HR & Organisationsentwicklung Positionen in DACH")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Suchfilter")
    
    # Sucheinstellungen
    keywords = st.multiselect(
        "Position",
        ["HR Leitung", "Head of HR", "Personalleitung", "People & Culture"],
        ["HR Leitung"]
    )
    
    locations = st.multiselect(
        "Standorte",
        ["Wien", "Graz", "Linz", "Salzburg", "Stuttgart", "München"],
        ["Wien"]
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
        with st.spinner('Suche läuft...'):
            # Karriere.at Suche
            jobs = search_karriere_at(keywords, locations)
            
            if jobs:
                # Konvertiere zu DataFrame
                df = pd.DataFrame(jobs)
                
                # Filtere basierend auf Match Score
                df = df[df['match_score'] >= min_match]
                
                # Speichere in Session State
                st.session_state.jobs_df = df
                st.session_state.last_search = datetime.now()
                
                # Zeige Ergebnisse
                st.write(f"🎯 Gefunden: {len(df)} passende Positionen")
                
                # Ergebnistabelle
                st.dataframe(
                    df.style.background_gradient(
                        subset=['match_score'],
                        cmap='Blues'
                    ).format({
                        'match_score': '{:.0f}%'
                    }),
                    use_container_width=True,
                    height=400
                )
                
                # Detail-Ansicht für ausgewählten Job
                if len(df) > 0:
                    st.subheader("🔍 Job Details")
                    selected_job = st.selectbox(
                        "Wähle eine Position für mehr Details:",
                        df['title'].tolist()
                    )
                    
                    if selected_job:
                        job_details = df[df['title'] == selected_job].iloc[0]
                        
                        st.markdown(f"""
                        ### {job_details['title']}
                        **Unternehmen:** {job_details['company']}  
                        **Standort:** {job_details['location']}  
                        **Gehalt:** {job_details['salary']}  
                        **Match Score:** {job_details['match_score']}%
                        
                        **Beschreibung:**  
                        {job_details['description']}
                        
                        [🔗 Zur Stellenanzeige]({job_details['url']})
                        """)
            else:
                st.warning("Keine Ergebnisse gefunden. Versuche andere Suchkriterien.")

with col2:
    st.subheader("📊 Quick Stats")
    
    # Aktive Suchen
    st.metric(
        label="Aktive Suchen",
        value="4",
        delta="2 neue"
    )
    
    # Neue Jobs
    st.metric(
        label="Neue Jobs heute",
        value="12",
        delta="↑ 5"
    )
    
    # Durchschnittlicher Match Score
    if not st.session_state.jobs_df.empty:
        avg_score = st.session_state.jobs_df['match_score'].mean()
        st.metric(
            label="Ø Match Score",
            value=f"{avg_score:.0f}%",
            delta="↑ 2%"
        )
    
    # Letzte Suche
    if st.session_state.last_search:
        st.info(f"Letzte Suche: {st.session_state.last_search.strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.markdown("*Powered by Streamlit* • *Built by JFdC and Claude*")
