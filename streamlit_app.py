import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Job Search Assistant", layout="wide")

def get_jobs():
    st.info("Suche Jobs...")
    all_jobs = []
    
    # Basis URLs
    base_urls = [
        "https://www.karriere.at/jobs/hr-leitung",
        "https://www.karriere.at/jobs/personalleitung",
        "https://www.karriere.at/jobs/head-of-hr"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15'
    }
    
    for url in base_urls:
        try:
            st.write(f"Suche: {url}")
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Finde alle Job-Listings
            jobs = soup.find_all('div', class_='m-jobsListItem')
            
            for job in jobs:
                title = job.find('h2').text.strip() if job.find('h2') else 'Kein Titel'
                company = job.find('div', class_='m-jobsListItem__company').text.strip() if job.find('div', class_='m-jobsListItem__company') else 'Unbekannt'
                location = job.find('div', class_='m-jobsListItem__location').text.strip() if job.find('div', class_='m-jobsListItem__location') else 'Unbekannt'
                link = "https://www.karriere.at" + job.find('a')['href'] if job.find('a') else '#'
                
                all_jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': link
                })
                
        except Exception as e:
            st.error(f"Fehler beim Abrufen von {url}: {str(e)}")
    
    return pd.DataFrame(all_jobs)

# UI
st.title("Job Search Assistant")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Filter")
    locations = st.multiselect(
        "Standorte",
        ['Wien', 'Graz', 'Linz', 'Salzburg', 'Stuttgart', 'München'],
        default=['Wien']
    )

# Main
if st.button("🔎 Jobs suchen", type="primary"):
    with st.spinner('Suche läuft...'):
        df = get_jobs()
        
        # Location Filter
        if locations:
            df = df[df['location'].str.contains('|'.join(locations), case=False)]
        
        if not df.empty:
            st.success(f"{len(df)} Jobs gefunden")
            
            # Results Table
            st.dataframe(
                df[['title', 'company', 'location']],
                use_container_width=True
            )
            
            # Job Details
            if len(df) > 0:
                st.subheader("Job Details")
                selected_job = st.selectbox(
                    "Wähle eine Position:",
                    df['title'].tolist()
                )
                
                if selected_job:
                    job = df[df['title'] == selected_job].iloc[0]
                    
                    st.markdown(f"""
                    ### {job['title']}
                    **Unternehmen:** {job['company']}  
                    **Standort:** {job['location']}  
                    
                    [Zur Stellenanzeige]({job['link']})
                    """)
        else:
            st.warning("Keine passenden Jobs gefunden.")

st.markdown("---")
st.markdown("*Powered by karriere.at* • *JFdC/Claude*")
