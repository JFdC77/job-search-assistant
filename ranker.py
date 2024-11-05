import pandas as pd

class JobRanker:
    def __init__(self):
        self.min_score = 60

    def rank_jobs(self, jobs, locations=None, min_score=None):
        """Filtert und sortiert Jobs nach Kriterien"""
        if not jobs:
            return pd.DataFrame()

        df = pd.DataFrame(jobs)
        
        # Apply filters
        if locations:
            location_mask = df['location'].isin(locations) | \
                          df['location'].str.contains('|'.join(locations), case=False)
            df = df[location_mask]

        if min_score:
            df = df[df['match_score'] >= min_score]

        # Sort by match score
        df = df.sort_values('match_score', ascending=False)
        
        return df

    def get_statistics(self, df):
        """Erstellt Statistiken über die Jobs"""
        return {
            'total_jobs': len(df),
            'locations': df['location'].value_counts().to_dict(),
            'avg_score': df['match_score'].mean(),
            'score_distribution': df['match_score'].value_counts().to_dict()
        }
