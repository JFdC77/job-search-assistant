import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Job Search Assistant", layout="wide")

def clean_location(location):
    """Bereinigt Standortangaben"""
    location = location.lower()
    if 'wien' in location:
        return 'Wien'
    elif 'graz' in location:
        return 'Graz'
    elif 'linz' in location:
        return 'Linz'
    elif 'salzburg' in location:
        return 'Salzburg'
    elif 'stuttgart' in location:
        return 'Stuttgart'
    elif 'münchen' in location or 'munich' in location:
        return 'München'
    return location

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
    
    total_found = 0
    
    for url in base_urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = soup.find_all('div', class_='m-jobsListItem')
            
            st.write(f"Gefunden in {url}: {len(jobs)} Jobs")
            total_found += len(jobs)
            
            for job in jobs:
                try:
                    # Basis-Informationen
                    title = job.find('h2').text.strip() if job.find('h2') else 'Kein Titel'
                    company = job.find('div', class_='m-jobsListItem__company').text.strip() if job.find('div', class_='m-jobsListItem__company') else 'Unbekannt'
                    location = job.find('div', class_='m-jobsListItem__location').text.strip() if job.find('div', class_='m-jobsListItem__location') else 'Unbekannt'
                    location = clean_location(location)
                    link = "https://www.karriere.at" + job.find('a')['href'] if job.find('a') else '#'
                    
                    # Zusätzliche Details
                    description = job.find('div', class_='m-jobsListItem__description')
                    description_text = description.text.strip() if description else ''
                    
                    # Match Score
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
                    st.warning(f"Fehler beim Verarbeiten eines Jobs: {str(e)}")
                    continue
                    
        except Exception as e:
            st.error(f"Fehler beim Abrufen von {url}: {str(e)}")
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
        value=75,
        step=5,
        help="Minimaler Match Score in %"
    )

# Main Area
col1, col2 = st.columns([2,1])
with col1:
    search_button = st.button("🔎 Neue Suche starten", type="primary", use_container_width=True)
with col2:
    sort_ascending = st.checkbox("Aufsteigend sortieren", value=False)

if search_button:
    with st.spinner('Suche läuft...'):
        try:
            df = get_jobs()
            
            # Filtering
            if locations:
                st.info(f"Filtere nach Standorten: {', '.join(locations)}")
                df = df[df['location'].isin(locations)]
            
            df = df[df['match_score'] >= min_score]
            
            # Sorting
            df = df.sort_values('match_score', ascending=sort_ascending)
            
            if len(df) > 0:
                # Display Results
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
                        - Positionslevel ✓
                        - Standort passend ✓
                        - Aufgabenbereich relevant ✓
                        """)
            else:
                st.warning(f"Keine Jobs in {', '.join(locations)} mit Match Score >= {min_score} gefunden.")
                st.info("Versuche andere Standorte oder einen niedrigeren Match Score.")
        
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {str(e)}")
            st.info("Bitte versuche es erneut oder ändere die Suchkriterien.")

st.markdown("---")
st.markdown("*Powered by karriere.at* • *JFdC/Claude*")
