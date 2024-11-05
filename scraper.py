import requests
from bs4 import BeautifulSoup

Funktion, die die Jobliste von einer gegebenen URL abruft und den HTML-Code zurückgibt:
def fetch_job_list(url):
    response = requests.get(url)
    return response.text

Funktion, die den HTML-Code parst und die relevanten Daten extrahiert:
def parse_job_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []
    for job_elem in soup.select('.m-jobsListItem__dataContainer'):
        job = {
            'title': job_elem.select_one('.m-jobsListItem__title').text.strip(),
            'company': job_elem.select_one('.m-jobsListItem__company').text.strip(),
            'location': job_elem.select_one('.m-jobsListItem__meta--location').text.strip(),
            'salary': job_elem.select_one('.m-jobsListItem__meta--salary').text.strip(),
            'url': 'https://www.karriere.at' + job_elem.select_one('.m-jobsListItem__titleLink')['href'],
            'description': job_elem.select_one('.m-jobsListItem__snippet').text.strip()
        }
        jobs.append(job)
    return jobs

Main-Funktion, die alles zusammenfügt:
def main():
    url = 'https://www.karriere.at/jobs/data-science?jobfields%5B%5D=1622'
    html = fetch_job_list(url)
    jobs = parse_job_list(html)
    print(f'Found {len(jobs)} jobs:')
    for job in jobs:
        print(job)

if __name__ == '__main__':
    main()
