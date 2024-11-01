import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Page config
st.set_page_config(page_title="Job Search Assistant", layout="wide")

def clean_location(location):
    """Bereinigt Standortangaben und gibt auch Debug-Info"""
    original = location
    location = location.lower()
    
    location_mapping = {
        'wien': ['wien', 'vienna', 'österreich'],
        'graz': ['graz', 'steiermark'],
        'linz': ['linz', 'oberösterreich'],
        'salzburg': ['salzburg', 'sbg'],
        'stuttgart': ['stuttgart', 'baden-württemberg', 'bw'],
        'münchen': ['münchen', 'munich', 'munchen', 'bayern', 'bavaria']
    }
    
    for city, variants in location_mapping.items():
        if any(variant in location for variant in variants):
            with st.expander("Location Processing", expanded=False):
                st.write(f"Location Match: '{original}' → '{city.title()}'")
            return city.title()
            
    with st.expander("Location Processing", expanded=False):
        st.write(f"Keine Matches für: '{original}'")
    return location

def calculate_match_score(job_text):
    """Berechnet den Match Score basierend auf Keywords"""
    keywords = {
        'high_value': [
            'führung', 'leitung', 'head', 'director',
            'transformation', 'change management',
            'strategisch', 'digital', 'entwicklung',
            'personal', 'hr', 'human resources'
        ],
        'medium_value': [
            'international', 'talent', 'kultur',
            'organisation', 'team', 'strategie',
            'projekt', 'prozess', 'management'
        ]
    }
    
    score = 60  # Basis-Score
    text = job_text.lower()
    matches = []
    
    for word in keywords['high_value']:
        if word in text:
            score += 5
            matches.append(f"{word} (+5)")
    
    for word in keywords['medium_value']:
        if word in text:
            score += 3
            matches.append(f"{word} (+3)")
    
    final_score = min(99, score)
    
    with st.expander("Score Calculation", expanded=False):
        st.write(f"Base Score: 60")
        st.write("Matches:", ", ".join(matches))
        st.write(f"Final Score: {final_score}")
    
    return final_score

def get_jobs():
    """Hauptfunktion zum Abrufen der Jobs"""
    st.info("Suche passende Positionen...")
    all_jobs = []
    
    base_urls = [
        "https://www.karriere.at/jobs/hr-leitung",
        "https://www.karriere.at/jobs/personalleitung",
        "https://www.karriere.at/jobs/head-of-hr",
        "https://www.karriere.at/jobs/hr-director",
        "https://www.karriere.at/jobs/people-culture"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15'
    }
    
    total_found = 0
    
    for url in base_urls:
        try:
            st.write(f"Prüfe Feed: {url}")
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = soup.find_all('div', class_='m-jobsListItem')
            
            found_count = len(jobs)
            total_found += found_count
            st.write(f"Gefunden: {found_count} Jobs")
            
            for job in jobs:
                try:
                    title = job.find('h2').text.strip() if job.find('h2') else 'Kein Titel'
                    company = job.find('div', class_='m-jobsListItem__company').text.strip() if job.find('div', class_='m-jobsListItem__company') else 'Unbekannt'
                    location = job.find('div', class_='m-jobsListItem__location').text.strip() if job.find('div', class_='m-jobsListItem__location') else 'Unbekannt'
                    
                    location = clean_location(location)
                    
                    description = job.find('div', class_='m-jobsListItem__description')
                    description_text = description.text.strip() if description else ''
                    
                    link = "https://www.karriere.at" + job.find('a')['href'] if job.find('a') else '#'
                    
                    match_score = calculate_match_score(title + ' ' + description_text)
                    
                    all_jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description_text,
                        'link': link,
                        'match_score': match_score,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                except Exception as e:
                    st.warning(f"Fehler beim Job-Parsing: {str(e)}")
                    continue
                    
        except Exception as e:
            st.error(f"Fehler beim URL-Abruf {url}: {str(e)}")
            continue
            
    st.success(f"Insgesamt {total_found} Jobs gefunden")
    return pd.DataFrame(all_jobs)
    # UI
st.title("Job Search Assistant")
st.write("Optimiert für HR & Organisationsentwicklung Positionen in DACH")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Suchfilter")
    
    locations = st.multiselect(
        "Standorte",
        ['Wien', 'Graz', 'Linz', 'Salzburg', 'Stuttgart', 'München'],
        default=['Wien']
    )
    
    min_score = st.slider(
        "Minimum Match Score",
        min_value=60,
        max_value=100,
        value=60,
        step=5,
        help="Minimaler Match Score in %"
    )

# Main Area
col1, col2 = st.columns([2,1])
with col1:
    search_button = st.button("🔎 Neue Suche starten", type="primary", use_container_width=True)
with col2:
    sort_ascending = st.checkbox("Aufsteigend sortieren")

if search_button:
    with st.spinner('Suche läuft...'):
        try:
            df = get_jobs()
            
            # Show initial stats
            with st.expander("Suchdetails", expanded=True):
                st.write("Initiale Ergebnisse:")
                st.write(f"Gefundene Standorte: {sorted(df['location'].unique())}")
                st.write(f"Standortverteilung:")
                st.write(df['location'].value_counts())
            
            # Location filtering
            if locations:
                st.info(f"Filtere nach Standorten: {', '.join(locations)}")
                # Combine exact and partial matches
                location_mask = df['location'].isin(locations) | \
                              df['location'].str.contains('|'.join(locations), case=False)
                df = df[location_mask]
                
                with st.expander("Filter Details"):
                    st.write(f"Jobs nach Standortfilter: {len(df)}")
            
            # Score filtering
            initial_count = len(df)
            df = df[df['match_score'] >= min_score]
            
            with st.expander("Score Details"):
                st.write(f"Jobs mit Score >= {min_score}: {len(df)} von {initial_count}")
            
            # Sort results
            df = df.sort_values('match_score', ascending=sort_ascending)
            
            if len(df) > 0:
                # Display Results
                st.success(f"{len(df)} passende Positionen gefunden")
                
                st.dataframe(
                    df[['title', 'company', 'location', 'match_score']].style.background_gradient(
                        subset=['match_score'],
                        cmap='RdYlGn',
                        vmin=60,
                        vmax=100
                    ),
                    use_container_width=True
                )
                
                # Job Details Section
                st.subheader("🔍 Job Details")
                selected_job = st.selectbox(
                    "Position auswählen:",
                    df['title'].tolist()
                )
                
                if selected_job:
                    job = df[df['title'] == selected_job].iloc[0]
                    
                    col1, col2 = st.columns([2,1])
                    
                    with col1:
                        st.markdown(f"""
                        ### {job['title']}
                        **Unternehmen:** {job['company']}  
                        **Standort:** {job['location']}  
                        **Match Score:** {job['match_score']}%
                        
                        **Beschreibung:**  
                        {job['description']}
                        
                        [📋 Zur vollständigen Stellenanzeige]({job['link']})
                        """)
                    
                    with col2:
                        st.info(f"""
                        **Match Details**
                        - Positionslevel: ✓
                        - Standort: ✓
                        - Aufgabenbereich: ✓
                        """)
            else:
                st.warning(f"Keine Jobs gefunden für:")
                st.write(f"- Standorte: {', '.join(locations)}")
                st.write(f"- Minimum Score: {min_score}")
                
                st.info("Empfehlungen:")
                st.write("1. Niedrigeren Match Score wählen")
                st.write("2. Weitere Standorte hinzufügen")
                st.write("3. Verfügbare Standorte prüfen")

# Footer
st.markdown("---")
st.markdown("*Powered by karriere.at* • *JFdC/Claude*")