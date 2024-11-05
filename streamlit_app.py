import streamlit as st
import pandas as pd
from scraper import JobScraper
from parser import JobParser
from matcher import JobMatcher
from ranker import JobRanker

st.set_page_config(page_title="Job Search Assistant", layout="wide")

class JobSearchApp:
    def __init__(self):
        self.scraper = JobScraper()
        self.parser = JobParser()
        self.matcher = JobMatcher()
        self.ranker = JobRanker()

    def run_search(self, locations, min_score):
        """Hauptsuchfunktion"""
        with st.spinner('Suche läuft...'):
            # Scrape
            raw_jobs = self.scraper.fetch_jobs()
            
            # Parse
            jobs = []
            for raw_job in raw_jobs:
                job = self.parser.parse_job(raw_job)
                if job:
                    job['location'] = self.parser.clean_location(job['location'])
                    job['match_score'] = self.matcher.calculate_match_score(job)
                    job['match_details'] = self.matcher.get_matching_details(job)
                    jobs.append(job)
            
            # Rank
            df = self.ranker.rank_jobs(jobs, locations, min_score)
            
            return df, self.ranker.get_statistics(df)

def main():
    st.title("Job Search Assistant")
    st.write("Optimiert für JFdC")

    # Sidebar
    with st.sidebar:
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
            step=5
        )

    # Main
    app = JobSearchApp()
    
    if st.button("🔎 Neue Suche starten", type="primary"):
        df, stats = app.run_search(locations, min_score)
        
        if not df.empty:
            st.success(f"{stats['total_jobs']} passende Positionen gefunden")
            # Display results...
            # (Rest der UI-Logik wie zuvor)

if __name__ == "__main__":
    main()
