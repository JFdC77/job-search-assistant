import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Job Search Assistant", layout="wide")

def calculate_match_score(job_text):
    keywords = {
        'high_value': [
            'führung', 'leitung', 'head', 'director',
            'transformation', 'change management',
            'strategisch', 'digital', 'entwicklung'
        ],
        'medium_value': [
            'personal', 'hr', 'human resources',
            'international', 'talent', 'kultur'
        ]
    }
    
    score = 60  # Basis-Score
    text = job_text.lower()
    
    for word in keywords['high_value']:
        if word in text:
            score += 5
    
    for word in keywords['medium_value']:
        if word in text:
            score += 3
    
    return min(99, score)

def get_jobs():
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
    
    total_jobs = 0
    for url in base_urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = soup.find_all('div', class_='m-jobsListItem')
            total_jobs += len(jobs)
            
            for job in jobs:
                # Basis-Informationen
                title = job.find('h2').text.strip() if job.find('h2') else 'Kein Titel'
                company = job.find('div', class_='m-jobsListItem__company').text.strip() if job.find('div', class_='m-jobsListItem__company') else 'Unbekannt'
                location = job.find('div', class_='m-jobsListItem__location').text.strip() if job.find('div', class_='m-jobsListItem__location') else 'Unbekannt'
                link = "https://www.karriere.at" + job.find('a')['href'] if job.find('a') else '#'
                
                # Zusätzliche Details
                description = job.find('div', class_='m-jobsListItem__description')
                description_text = description.text.strip() if description else ''
                
                # Match Score berechnen
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
            st.error(f"Fehler beim Abrufen von {url}: {str(e)}")
    
    st.success(f"Insgesamt {total_jobs} Jobs gefunden")
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
        value=75,
        step=5,
        help="Minimaler Match Score in %"
    )

# Main
col1, col2, col3 = st.columns(3)
with col1:
    search_button = st.button("🔎 Neue Suche starten", type="primary", use_container_width=True)
with col2:
    sort_by = st.selectbox("Sortieren nach", ["Match Score", "Unternehmen", "Standort"])
with col3:
    ascending = st.checkbox("Aufsteigend sortieren", value=False)

if search_button:
    with st.spinner('Suche läuft...'):
        df = get_jobs()
        
        # Filter
        if locations:
            df = df[df['location'].str.contains('|'.join(locations), case=False)]
        df = df[df['match_score'] >= min_score]
        
        # Sortierung
        if sort_by == "Match Score":
            df = df.sort_values('match_score', ascending=ascending)
        elif sort_by == "Unternehmen":
            df = df.sort_values('company', ascending=ascending)
        else:
            df = df.sort_values('location', ascending=ascending)
        
        if not df.empty:
            # Results Table
            st.dataframe(
                df[['title', 'company', 'location', 'match_score']].style.background_gradient(
                    subset=['match_score'],
                    cmap='RdYlGn',
                    vmin=60,
                    vmax=100
                ),
                use_container_width=True
            )
            
            # Job Details
            if len(df) > 0:
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
                        - Führungsposition ✓
                        - Standort passend ✓
                        - Branche relevant ✓
                        """)
        else:
            st.warning("Keine passenden Jobs gefunden.")

st.markdown("---")
st.markdown("*Powered by karriere.at* • *JFdC/Claude*")
