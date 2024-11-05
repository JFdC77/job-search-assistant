class JobMatcher:
    def __init__(self):
        self.keywords = {
            'high_value': [
                'führung', 'leitung', 'head', 'director',
                'transformation', 'change management',
                'strategisch', 'digital', 'entwicklung',
                'personal', 'hr', 'human resources'
            ],
            'medium_value': [
                'international', 'talent', 'kultur',
                'organisation', 'team', 'strategie',
                'projekt', 'prozess', 'management'
            ]
        }

    def calculate_match_score(self, job):
        """Berechnet Match Score für einen Job"""
        score = 60  # Base score
        text = f"{job['title']} {job['description']}".lower()
        
        for word in self.keywords['high_value']:
            if word in text:
                score += 5
                
        for word in self.keywords['medium_value']:
            if word in text:
                score += 3
                
        return min(99, score)

    def get_matching_details(self, job):
        """Gibt detaillierte Match-Informationen zurück"""
        return {
            'perfect_matches': self._get_matches(job, self.keywords['high_value']),
            'good_matches': self._get_matches(job, self.keywords['medium_value'])
        }

    def _get_matches(self, job, keywords):
        """Helper method to find matching keywords"""
        text = f"{job['title']} {job['description']}".lower()
        return [word for word in keywords if word in text]
