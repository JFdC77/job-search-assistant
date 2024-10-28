import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import logging
from bs4 import BeautifulSoup

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
    
    def search_linkedin_jobs():
        try:
            headers = {
                'Authorization': f'Bearer {st.secrets["linkedin"]["client_secret"]}',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            search_locations = ['Vienna,Austria', 'Stuttgart,Germany', 'Munich,Germany']
            search_keywords = ['HR Director', 'Head of HR', 'HR Leitung']
            
            for location in search_locations:
                for keyword in search_keywords:
                    endpoint = 'https://api.linkedin.com/v2/jobSearch'
                    
                    params = {
                        'keywords': keyword,
                        'location': location,
                        'count': 25,
                        'filters': {
                            'seniority': ['DIRECTOR', 'EXECUTIVE'],
                            'salary': {'minimum': 120000}
                        }
                    }
                    
                    logging.info(f"Suche Jobs: {keyword} in {location}")
                    response = requests.get(endpoint, headers=headers, params=params)
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        for job in results.get('elements', []):
                            score = calculate_match_score(job)
                            if score >= 60:
                                processed_job = {
                                    'title': job.get('title', 'Keine Angabe'),
                                    'company': job.get('companyName', 'Unbekannt'),
                                    'location': job.get('location', 'Unbekannt'),
                                    'salary': extract_salary(job),
                                    'description': clean_description(job.get('description', '')),
                                    'url': job.get('applyUrl', ''),
                                    'match_score': score,
                                    'posting_date': job.get('postedAt', datetime.now().strftime('%Y-%m-%d')),
                                    'match_details': analyze_match_details(job)
                                }
                                jobs.append(processed_job)
                                logging.info(f"Job gefunden: {processed_job['title']}")
                    else:
                        logging.error(f"API Fehler: {response.status_code}")
                        st.error(f"LinkedIn API Fehler: {response.status_code}")
                        
        except Exception as e:
            logging.error(f"Fehler bei LinkedIn Suche: {str(e)}")
            st.error(f"Fehler bei der Job-Suche: {str(e)}")
    
    def calculate_match_score(job):
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
        text = (
            job.get('title', '') + ' ' +
            job.get('description', '') + ' ' +
            job.get('companyName', '')
        ).lower()
        
        for word in keywords['high_value']:
            if word in text:
                score += 10
                logging.debug(f"High-Value Keyword gefunden: {word}")
        
        for word in keywords['medium_value']:
            if word in text:
                score += 5
                logging.debug(f"Medium-Value Keyword gefunden: {word}")
        
        return min(95, max(60, score))
    
    def extract_salary(job):
        salary_info = job.get('salary', {})
        if salary_info:
            min_salary = salary_info.get('minimum', 0)
            max_salary = salary_info.get('maximum', 0)
            if min_salary and max_salary:
                return f"{int(min_salary/1000)}k-{int(max_salary/1000)}k"
        return 'k.A.'
    
    def clean_description(html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text().strip()
    
    def analyze_match_details(job):
        description = job.get('description', '').lower()
        return {
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
    
    # Jobs suchen
    search_linkedin_jobs()
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
            
            # Job Details
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
            st.warning("Keine Jobs gefunden. Bitte andere Suchkriterien probieren.")

# Footer
st.markdown("---")
st.markdown("*Powered by LinkedIn API* • *JFdC/Claude, vX*")
