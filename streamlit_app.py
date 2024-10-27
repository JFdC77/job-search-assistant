import streamlit as st
import pandas as pd
from datetime import datetime

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

def get_job_data():
    jobs = []
    
    # Karriere.at
    def scrape_karriere_at():
        try:
            search_terms = [
                'Head+HR',
                'Personalleitung',
                'Head+of+People',
                'HR+Director'
            ]
            
            base_url = "https://www.karriere.at/jobs"
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15'
            }
            
            for term in search_terms:
                url = f"{base_url}/{term}"
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_listings = soup.find_all('div', class_='m-jobsListItem')
                
                for job in job_listings:
                    try:
                        title = job.find('h2', class_='m-jobsListItem__title').text.strip()
                        company = job.find('div', class_='m-jobsListItem__company').text.strip()
                        location = job.find('div', class_='m-jobsListItem__location').text.strip()
                        url = "https://www.karriere.at" + job.find('a')['href']
                        
                        # Get detailed job info
                        job_response = requests.get(url, headers=headers)
                        job_soup = BeautifulSoup(job_response.text, 'html.parser')
                        
                        description = job_soup.find('div', class_='m-jobDetail__description')
                        description = description.text.strip() if description else "Keine Beschreibung verfügbar"
                        
                        salary = job_soup.find('div', class_='m-jobDetail__salary')
                        salary = salary.text.strip() if salary else "Gehalt auf Anfrage"
                        
                        # Calculate match score based on keywords
                        match_score = calculate_match_score(title, description)
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location,
                            'salary': salary,
                            'match_score': match_score,
                            'description': description,
                            'url': url,
                            'source': 'karriere.at',
                            'posting_date': datetime.now().strftime('%Y-%m-%d'),  # Echtes Datum extrahieren
                            'match_details': analyze_match_details(description)
                        })
                        
                        time.sleep(1)  # Höflichkeitspause zwischen Requests
                        
                    except Exception as e:
                        print(f"Fehler beim Parsen eines Jobs: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Fehler beim Scraping von karriere.at: {str(e)}")
    
    # Match Score Berechnung
    def calculate_match_score(title, description):
        keywords = {
            'high_value': [
                'führung', 'leitung', 'head', 'director', 'transformation',
                'change management', 'strategisch', 'digital'
            ],
            'medium_value': [
                'personal', 'hr', 'human resources', 'entwicklung',
                'international', 'talent', 'kultur'
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
                
        return min(95, max(60, score))  # Score zwischen 60 und 95
    
    # Match Details Analyse
    def analyze_match_details(description):
        skills_matches = {
            'perfect_matches': [],
            'good_matches': [],
            'development_areas': []
        }
        
        text = description.lower()
        
        # Skill-Matching Logik
        leadership_keywords = ['führung', 'leitung', 'management']
        digital_keywords = ['digital', 'transformation', 'change']
        hr_keywords = ['personal', 'hr', 'recruiting', 'talent']
        
        if any(keyword in text for keyword in leadership_keywords):
            skills_matches['perfect_matches'].append('Führungserfahrung')
        
        if any(keyword in text for keyword in digital_keywords):
            skills_matches['perfect_matches'].append('Digitale Transformation')
        
        if any(keyword in text for keyword in hr_keywords):
            skills_matches['good_matches'].append('HR Expertise')
        
        return skills_matches
    
    # Scraping starten
    scrape_karriere_at()
    
    return jobs

def search_jobs(keywords, locations, salary_range, min_match):
    all_jobs = get_job_data()
    df = pd.DataFrame(all_jobs)
    
    # Filter basierend auf den Suchkriterien
    if locations:
        df = df[df['location'].isin(locations)]
    
    # Gehaltsfilter
    min_salary = int(df['salary'].str.extract('(\d+)k').astype(float).min())
    if min_salary < salary_range[0]:
        df = df[df['salary'].str.extract('(\d+)k').astype(float) >= salary_range[0]]
    
    # Match Score Filter
    if min_match:
        df = df[df['match_score'] >= min_match]
    
    return df

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
