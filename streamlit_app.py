import streamlit as st
import pandas as pd
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO)

# Seiteneinstellungen
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_job_data():
    jobs = []
    
    # RSS Feeds holen
    def get_rss_jobs():
        logging.info("Starte Job-Suche...")
        feeds = [
            # Karriere.at - Wien
            'https://www.karriere.at/jobs/feed?q=HR+Leitung&loc=wien',
            'https://www.karriere.at/jobs/feed?q=Head+of+HR&loc=wien',
            'https://www.karriere.at/jobs/feed?q=Personalleitung&loc=wien',
            'https://www.karriere.at/jobs/feed?q=HR+Director&loc=wien',
            'https://www.karriere.at/jobs/feed?q=People+Culture&loc=wien',
            # Österreich - andere Städte
            'https://www.karriere.at/jobs/feed?q=HR+Leitung&loc=graz',
            'https://www.karriere.at/jobs/feed?q=HR+Leitung&loc=linz',
            'https://www.karriere.at/jobs/feed?q=HR+Leitung&loc=salzburg',
            # Deutschland
            'https://www.karriere.at/jobs/feed?q=HR+Leitung&loc=stuttgart',
            'https://www.karriere.at/jobs/feed?q=HR+Leitung&loc=munchen',
            # Zusätzliche Suchbegriffe
            'https://www.karriere.at/jobs/feed?q=Organisationsentwicklung',
            'https://www.karriere.at/jobs/feed?q=Change+Management',
            'https://www.karriere.at/jobs/feed?q=HR+Business+Partner',
            'https://www.karriere.at/jobs/feed?q=HR+Manager'
        ]
        
        rss_jobs = []
        for feed_url in feeds:
            try:
                logging.info(f"Prüfe Feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                logging.info(f"Gefundene Einträge in Feed: {len(feed.entries)}")
                
                for entry in feed.entries:
                    logging.info(f"Analysiere Job: {entry.title}")
                    score = calculate_match_score(entry.title, entry.description)
                    logging.info(f"Match Score: {score}")
                    
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
                        logging.info(f"Job hinzugefügt: {job['title']} ({job['company']})")
                        rss_jobs.append(job)
            except Exception as e:
                logging.error(f"Fehler beim Feed {feed_url}: {str(e)}")
                
        logging.info(f"Insgesamt gefunden: {len(rss_jobs)} Jobs")
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
        logging.debug(f"Analysiere Text für Score: {title}")
        
        for word in keywords['high_value']:
            if word in text:
                score += 10
                logging.debug(f"High-Value Keyword gefunden: {word} (+10)")
        for word in keywords['medium_value']:
            if word in text:
                score += 5
                logging.debug(f"Medium-Value Keyword gefunden: {word} (+5)")
                
        final_score = min(95, max(60, score))
        logging.debug(f"Finaler Score: {final_score}")
        return final_score
            def extract_location(text):
        locations = ['Wien', 'Stuttgart', 'München', 'Graz', 'Linz', 'Salzburg']
        text = text.lower()
        found_locations = [loc for loc in locations if loc.lower() in text]
        location = found_locations[0] if found_locations else 'Unbekannt'
        logging.debug(f"Extrahierter Standort: {location}")
        return location

    def extract_salary(description):
        logging.debug("Analysiere Gehaltsangaben")
        if 'EUR' in description or '€' in description:
            if '120' in description:
                logging.debug("Gehalt gefunden: 120k-150k")
                return '120k-150k'
            elif '100' in description:
                logging.debug("Gehalt gefunden: 100k-130k")
                return '100k-130k'
        logging.debug("Kein Gehalt gefunden")
        return 'k.A.'

    def clean_description(html):
        soup = BeautifulSoup(html, 'html.parser')
        cleaned = soup.get_text().strip()
        logging.debug(f"Beschreibung gereinigt: {len(cleaned)} Zeichen")
        return cleaned

    def analyze_match_details(description):
        logging.debug("Analysiere Match Details")
        description = description.lower()
        matches = {
            'perfect_matches': [
                skill for skill in [
                    'Führungserfahrung', 
                    'Transformationserfahrung',
                    'Internationale Teams',
                    'Sprachkenntnisse'
                ] if skill.lower() in description
            ],
            'good_matches': [
                skill for skill in [
                    'Change Management',
                    'Digitalisierung',
                    'Talent Development'
                ] if skill.lower() in description
            ],
            'development_areas': [
                'Branchenspezifische Kenntnisse',
                'Lokale Marktexpertise'
            ]
        }
        logging.debug(f"Gefundene Matches: {len(matches['perfect_matches'])} perfect, {len(matches['good_matches'])} good")
        return matches

    # Jobs aus allen Quellen sammeln
    jobs.extend(get_rss_jobs())
    logging.info(f"Job-Suche abgeschlossen. Gefundene Jobs: {len(jobs)}")
    return jobs

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
        # Debug Info anzeigen
        st.info("Debug Information wird gesammelt...")
        
        # Jobs suchen
        jobs = get_job_data()
        
        if jobs:
            df = pd.DataFrame(jobs)
            st.success(f"🎯 Gefunden: {len(df)} passende Positionen")
            
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
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    ### {job['title']}
                    
                    **Unternehmen:** {job['company']}  
                    **Standort:** {job['location']}  
                    **Gehalt:** {job['salary']}  
                    **Match Score:** {job['match_score']}%
                    
                    {job['description']}
                    
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
        else:
            st.warning("Keine passenden Jobs gefunden. Versuche andere Suchkriterien.")

else:
    st.info("👆 Starte die Suche mit den ausgewählten Filtern")

# Footer
st.markdown("---")
st.markdown("*Powered by Streamlit* • *JFdC/Claude*")
