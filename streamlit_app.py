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

def get_job_data():
    return [
        {
            'title': 'Head of Human Resources',
            'company': 'Erste Group Bank AG',
            'location': 'Wien',
            'salary': '120k-150k',
            'match_score': 95,
            'description': '''### Rolle & Verantwortung
• Strategische Führung des HR-Bereichs
• Weiterentwicklung der HR-Organisation
• Gestaltung der Transformationsprozesse
• Management des 15-köpfigen Teams

### Schwerpunkte
• Digitale Transformation des HR-Bereichs
• Modernisierung der HR-Prozesse
• Talent Management & Entwicklung
• Change Management & Kulturwandel

### Anforderungsprofil
• Mehrjährige HR-Führungserfahrung
• Nachweisliche Transformationserfolge
• Exzellente Kommunikationsfähigkeiten
• Deutsch & Englisch verhandlungssicher''',
            'url': 'https://www.erstegroup.com/career',
            'requirements': [
                'Führungserfahrung',
                'Change Management',
                'Digitale Transformation',
                'Mehrsprachigkeit',
                'Banking-Hintergrund'
            ],
            'match_details': {
                'perfect_matches': [
                    'Führungserfahrung HR',
                    'Transformationserfahrung',
                    'Internationale Teams',
                    'Sprachkenntnisse'
                ],
                'good_matches': [
                    'Change Management',
                    'Digitalisierung',
                    'Talent Development'
                ],
                'development_areas': [
                    'Banking-Regulierung',
                    'Fintech-Entwicklungen'
                ]
            },
            'posting_date': '2024-10-25',
            'company_benefits': [
                'Flexible Arbeitszeiten',
                'Internationale Karriere',
                'Weiterbildungsbudget',
                'Remote Work Möglichkeit'
            ],
            'application_deadline': '2024-11-30'
        },
                {
            'title': 'Leiter People & Culture',
            'company': 'Österreichische Post AG',
            'location': 'Wien',
            'salary': '110k-140k',
            'match_score': 88,
            'description': '''### Rolle & Verantwortung
• Strategische P&C Leitung
• Transformation der HR-Funktion
• Kulturentwicklung & Change
• Führung des P&C Teams

### Schwerpunkte
• New Work & Kulturwandel
• Employee Experience
• Talent & Leadership Development
• Employer Branding

### Anforderungsprofil
• HR-Führungserfahrung
• Change Management Expertise
• Innovatives Mindset
• Exzellente Kommunikation''',
            'url': 'https://karriere.post.at',
            'requirements': [
                'HR-Führung',
                'Change Management',
                'Kulturentwicklung',
                'Kommunikation'
            ],
            'match_details': {
                'perfect_matches': [
                    'Organisationsentwicklung',
                    'Change Management',
                    'Führungserfahrung'
                ],
                'good_matches': [
                    'Kulturentwicklung',
                    'Talent Management',
                    'Kommunikation'
                ],
                'development_areas': [
                    'Logistik-Branche',
                    'Gewerkschaftsarbeit'
                ]
            },
            'posting_date': '2024-10-26',
            'company_benefits': [
                'Work-Life-Balance',
                'Entwicklungsmöglichkeiten',
                'Betriebliche Sozialleistungen',
                'Gesundheitsförderung'
            ],
            'application_deadline': '2024-11-25'
        }
    ]

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
