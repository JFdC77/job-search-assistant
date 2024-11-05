from datetime import datetime

class JobParser:
    def parse_job(self, raw_job):
        """Extrahiert strukturierte Daten aus einem raw_job HTML Element"""
        try:
            return {
                'title': self._get_text(raw_job, 'h2'),
                'company': self._get_text(raw_job, 'div', 'm-jobsListItem__company'),
                'location': self._get_text(raw_job, 'div', 'm-jobsListItem__location'),
                'description': self._get_text(raw_job, 'div', 'm-jobsListItem__description'),
                'link': self._get_link(raw_job),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"Error parsing job: {str(e)}")
            return None

    def _get_text(self, element, tag, class_name=None):
        """Helper method to extract text from HTML elements"""
        found = element.find(tag, class_=class_name) if class_name else element.find(tag)
        return found.text.strip() if found else ''

    def _get_link(self, element):
        """Helper method to extract job link"""
        link_element = element.find('a')
        return f"https://www.karriere.at{link_element['href']}" if link_element else '#'

    def clean_location(self, location):
        """Bereinigt Standortangaben"""
        location_mapping = {
            'wien': ['wien', 'vienna', 'österreich'],
            'graz': ['graz', 'steiermark'],
            'linz': ['linz', 'oberösterreich'],
            'salzburg': ['salzburg', 'sbg'],
            'stuttgart': ['stuttgart', 'baden-württemberg', 'bw'],
            'münchen': ['münchen', 'munich', 'munchen', 'bayern', 'bavaria']
        }
        
        location = location.lower()
        for city, variants in location_mapping.items():
            if any(variant in location for variant in variants):
                return city.title()
        return location
