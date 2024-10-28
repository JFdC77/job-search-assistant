import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

# Für Error Handling
import logging
logging.basicConfig(level=logging.INFO)

# Seiteneinstellungen
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
from bs4 import BeautifulSoup
import time

import feedparser
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)

def get_job_data():
    jobs = []
    
    # RSS Feeds holen
    def get_rss_jobs():
        feeds = [
            'https://www.karriere.at/jobs/feed?q=HR+Leitung',
            'https://www.karriere.at/jobs/feed?q=Head+of+HR',
            'https://www.karriere.at/jobs/feed?q=Personalleitung'
        ]
        
        rss_jobs = []
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    # Match-Score berechnen
                    score = calculate_match_score(entry.title, entry.description)
                    if score >= 60:  # Nur relevante Jobs
                        job = {
                            'title': entry.title,
                            'company': entry.get('author', 'Unbekannt'),
                            'location': extract_location(entry.title + ' ' + entry.description),
                            'salary': extract_salary(entry.description),
                            'description': clean_description(entry.description),
                            'url': entry.link,
                            'match_score': score,
                            'posting_date': entry.published,
                            'match_details': analyze_match_details(entry.description)
                        }
                        rss_jobs.append(job)
            except Exception as e:
                logging.error(f"Fehler beim Feed {feed_url}: {str(e)}")
        return rss_jobs
    
    def calculate_match_score(title, description):
        keywords = {
            'high_value': [
                'führung', 'leitung', 'head', 'director', 
                'transformation', 'change management', 
                'strategisch', 'digital'
            ],
            'medium_value': [
                'personal', 'hr', 'human resources', 
                'entwicklung', 'international', 
                'talent', 'kultur'
            ]
        }
        
        score = 0
        text = (title + ' ' + description).lower()
        
        for word in keywords['high_value']:
            if word in text:
                score += 10
        for word in keywords['medium_value']:
            if word in text:
                score += 5
                
        return min(95, max(60, score))

    def extract_location(text):
        locations = ['Wien', 'Stuttgart', 'München', 'Graz', 'Linz', 'Salzburg']
        text = text.lower()
        found_locations = [loc for loc in locations if loc.lower() in text]
        return found_locations[0] if found_locations else 'Unbekannt'

    def extract_salary(description):
        # Einfache Gehaltsextraktion
        if 'EUR' in description or '€' in description:
            if '120' in description:
                return '120k-150k'
            elif '100' in description:
                return '100k-130k'
        return 'k.A.'

    def clean_description(html):
        # HTML Tags entfernen und Text säubern
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text().strip()

    def analyze_match_details(description):
        return {
            'perfect_matches': [
                skill for skill in [
                    'Führungserfahrung', 
                    'Transformationserfahrung',
                    'Internationale Teams',
                    'Sprachkenntnisse'
                ] if skill.lower() in description.lower()
            ],
            'good_matches': [
                skill for skill in [
                    'Change Management',
                    'Digitalisierung',
                    'Talent Development'
                ] if skill.lower() in description.lower()
            ],
            'development_areas': [
                'Branchenspezifische Kenntnisse',
                'Lokale Marktexpertise'
            ]
        }

    # Jobs aus allen Quellen sammeln
    jobs.extend(get_rss_jobs())
    
    return jobs

def search_jobs(keywords, locations, salary_range, min_match):
    try:
        all_jobs = get_job_data()
        if not all_jobs:  # Wenn keine Jobs gefunden wurden
            return pd.DataFrame()  # Leeres DataFrame zurückgeben
            
        df = pd.DataFrame(all_jobs)
        
        # Sicherstellen, dass alle erforderlichen Spalten existieren
        required_columns = ['title', 'company', 'location', 'salary', 'match_score', 'description']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Filter anwenden
        if locations:
            df = df[df['location'].isin(locations)]
        
        if min_match:
            df = df[df['match_score'] >= min_match]
        
        return df
        
    except Exception as e:
        logging.error(f"Fehler in search_jobs: {str(e)}")
        return pd.DataFrame()  # Im Fehlerfall leeres DataFrame zurückgeben

# Hauptanwendung
st.title("Persönlicher Job Search Assistant")
st.write("Optimiert für HR & Organisationsentwicklung Positionen in DACH")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Suchfilter")
    
    # Keywords/Position
    keywords = st.multiselect(
        "Position",
        ["HR Leitung", "Head of HR", "Personalleitung", "People & Culture"],
        ["HR Leitung"]
    )
    
    # Locations
    locations = st.multiselect(
        "Standorte",
        ["Wien", "Graz", "Linz", "Salzburg", "Stuttgart", "München"],
        ["Wien"]
    )
    
    # Salary Range
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
        df = search_jobs(keywords, locations, salary_range, min_match)
        
        if not df.empty:
            st.write(f"🎯 Gefunden: {len(df)} passende Positionen")
            
            # Ergebnistabelle
            st.dataframe(
                df[['title', 'company', 'location', 'salary', 'match_score', 'description']],
                use_container_width=True,
                hide_index=True
            )
            
            # Job Details Section
            st.subheader("🔍 Job Details")
            selected_job = st.selectbox(
                "Wähle eine Position für mehr Details:",
                df['title'].tolist()
            )
            
            if selected_job:
                job = df[df['title'] == selected_job].iloc[0]
                
                # Zwei Spalten Layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    ### {job['title']}
                    
                    **Unternehmen:** {job['company']}  
                    **Standort:** {job['location']}  
                    **Gehalt:** {job['salary']}  
                    **Match Score:** {job['match_score']}%
                    
                    {job['description']}
                    
                    **Benefits:**
                    {"".join([f"• {benefit}  \n" for benefit in job['company_benefits']])}
                    
                    [🔗 Zur Stellenanzeige]({job['url']})
                    """)
                
                with col2:
                    st.markdown("### Match Analysis")
                    
                    st.markdown("#### 🎯 Perfect Matches")
                    for match in job['match_details']['perfect_matches']:
                        st.markdown(f"✅ {match}")
                    
                    st.markdown("#### 👍 Gute Übereinstimmung")
                    for match in job['match_details']['good_matches']:
                        st.markdown(f"✓ {match}")
                    
                    st.markdown("#### 📚 Entwicklungsfelder")
                    for area in job['match_details']['development_areas']:
                        st.markdown(f"• {area}")
                    
                    st.markdown(f"**Bewerbungsfrist:** {job['application_deadline']}")

else:
    st.info("👆 Starte die Suche mit den ausgewählten Filtern")

# Footer
st.markdown("---")
st.markdown("*Powered by Streamlit* • *JFdC/Claude*")
