import requests
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self):
        self.base_urls = [
            "https://www.karriere.at/jobs/hr-leitung",
            "https://www.karriere.at/jobs/personalleitung",
            "https://www.karriere.at/jobs/head-of-hr",
            "https://www.karriere.at/jobs/hr-director",
            "https://www.karriere.at/jobs/people-culture"
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15'
        }

    def fetch_jobs(self):
        raw_jobs = []
        for url in self.base_urls:
            try:
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs = soup.find_all('div', class_='m-jobsListItem')
                raw_jobs.extend(jobs)
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
        return raw_jobs
