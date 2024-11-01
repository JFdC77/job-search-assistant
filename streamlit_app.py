import streamlit as st
import pandas as pd
import feedparser
from datetime import datetime
import logging

st.set_page_config(page_title="Job Search Assistant", layout="wide")

# Debug Mode
DEBUG = True

def get_karriere_at_jobs():
    jobs = []
    st.info("Suche Jobs auf karriere.at...")
    
    # RSS Feeds für verschiedene Suchbegriffe
    feeds = [
        "https://www.karriere.at/jobs/hr-leitung/rss",
        "https://www.karriere.at/jobs/personalleitung/rss",
        "https://www.karriere.at/jobs/head-of-hr/rss",
        "https://www.karriere.at/jobs/hr-direktor/rss"
    ]
    
    total_entries = 0
    for feed_url in feeds:
        if DEBUG:
            st.write(f"Prüfe Feed: {feed_url}")
        
        feed = feedparser.parse(feed_url)
        entries = feed.entries
        total_entries += len(entries)
        
        if DEBUG:
            st.write(f"Gefundene Einträge: {len(entries)}")
        
        for entry in entries:
            job = {
                'title': entry.title,
                'company': entry.author if hasattr(entry, 'author') else 'Unbekannt',
                'location': extract_location(entry.title),
                'description': entry.description,
                'link': entry.link,
                'published': entry.published
            }
            jobs.append(job)
    
    st.success(f"Insgesamt {total_entries} Jobs gefunden")
    return pd.DataFrame(jobs)

def extract_location(title):
    locations = ['Wien', 'Graz', 'Linz', 'Salzburg', 'Innsbruck', 'Klagenfurt', 
                'Stuttgart', 'München']
    for loc in locations:
        if loc in title:
            return loc
    return 'Andere'

# UI
st.title("Job Search Assistant")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Filter")
    selected_locations = st.multiselect(
        "Standorte",
        ['Wien', 'Graz', 'Linz', 'Salzburg', 'Stuttgart', 'München'],
        default=['Wien']
    )

# Main
if st.button("🔎 Jobs suchen"):
    with st.spinner('Suche läuft...'):
        df = get_karriere_at_jobs()
        
        # Filter by location
        if selected_locations:
            df = df[df['location'].isin(selected_locations)]
        
        # Show results
        if not df.empty:
            st.write("### Gefundene Positionen")
            st.dataframe(
                df[['title', 'company', 'location', 'published']],
                use_container_width=True
            )
            
            # Detailed view
            st.write("### Job Details")
            selected_job = st.selectbox(
                "Position auswählen:",
                df['title'].tolist()
            )
            
            if selected_job:
                job = df[df['title'] == selected_job].iloc[0]
                st.write(f"**Unternehmen:** {job['company']}")
                st.write(f"**Standort:** {job['location']}")
                st.write(f"**Veröffentlicht:** {job['published']}")
                st.write("**Beschreibung:**")
                st.markdown(job['description'])
                st.markdown(f"[➡️ Zur Ausschreibung]({job['link']})")
        else:
            st.warning("Keine Jobs gefunden")

st.markdown("---")
st.markdown("*Powered by karriere.at RSS* • *Built with Streamlit*")
