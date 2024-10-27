import streamlit as st
import pandas as pd
from datetime import datetime

# Dunkles Theme und breites Layout
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'Job Search Assistant • Built by JFdC/Claude'
    }
)

def search_jobs(keywords, locations):
    jobs_data = [
        {
            'title': 'Head of Human Resources',
            'company': 'Erste Group Bank AG',
            'location': 'Wien',
            'salary': '120k-150k',
            'match_score': 95,
            'description': '''Strategische HR-Führungsposition mit Fokus auf Transformation

Aufgaben:
• Gestaltung und Umsetzung der HR-Strategie
• Führung und Weiterentwicklung des HR-Teams
• Transformation der HR-Prozesse und -Systeme
• Talent Management und Succession Planning

Anforderungen:
• Mehrjährige Führungserfahrung im HR-Bereich
• Erfahrung mit digitaler Transformation
• Exzellente Kommunikationsfähigkeiten
• Verhandlungssicheres Deutsch und Englisch''',
            'url': 'https://www.erstegroup.com/en/career'
        },
        {
            'title': 'Leiter People & Culture',
            'company': 'Österreichische Post AG',
            'location': 'Wien',
            'salary': '110k-140k',
            'match_score': 88,
            'description': '''Gesamtverantwortung für den HR-Bereich

Aufgaben:
• Strategische Personalentwicklung
• Change Management und Kulturwandel
• Recruitment und Employer Branding
• Performance Management

Anforderungen:
• HR-Führungserfahrung
• Change Management Know-how
• Stark in Konzeption und Umsetzung
• Ausgeprägte Führungskompetenz''',
            'url': 'https://karriere.post.at'
        }
    ]
    return pd.DataFrame(jobs_data)

# Hauptanwendung
st.title("Persönlicher Job Search Assistant")
st.write("Optimiert für HR & Organisationsentwicklung Positionen in DACH")

# Sidebar Filter
with st.sidebar:
    st.header("🔍 Suchfilter")
    
    keywords = st.multiselect(
        "Position",
        ["HR Leitung", "Head of HR", "Personalleitung", "People & Culture"],
        ["HR Leitung"]
    )
    
    locations = st.multiselect(
        "Standorte",
        ["Wien", "Graz", "Linz", "Salzburg", "Stuttgart", "München"],
        ["Wien"]
    )
    
    salary_range = st.slider(
        "Gehaltsrange (k€)",
        min_value=80,
        max_value=200,
        value=(120, 160),
        step=10
    )
    
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
        df = search_jobs(keywords, locations)
        
        if not df.empty:
            st.write(f"🎯 Gefunden: {len(df)} passende Positionen")
            
            # Formatierte Tabelle
            st.dataframe(
                df[['title', 'company', 'location', 'salary', 'match_score']].style
                .background_gradient(subset=['match_score'], cmap='Blues')
                .format({'match_score': '{:.0f}%'})
                .set_properties(**{
                    'background-color': '#0e1117',
                    'color': 'white',
                    'border-color': '#21262d'
                }),
                height=400
            )
            
            # Job Details
            st.subheader("🔍 Job Details")
            selected_job = st.selectbox(
                "Wähle eine Position für mehr Details:",
                df['title'].tolist()
            )
            
            if selected_job:
                job = df[df['title'] == selected_job].iloc[0]
                
                col1, col2 = st.columns([2,1])
                
                with col1:
                    st.markdown(f"""
                    ### {job['title']}
                    **Unternehmen:** {job['company']}  
                    **Standort:** {job['location']}  
                    **Gehalt:** {job['salary']}  
                    **Match Score:** {job['match_score']}%
                    
                    **Beschreibung:**  
                    {job['description']}
                    
                    [🔗 Zur Stellenanzeige]({job['url']})
                    """)
                
                with col2:
                    st.markdown("""
                    #### Match Details
                    - ✅ Führungserfahrung
                    - ✅ Transformationserfahrung
                    - ✅ Internationale Erfahrung
                    - ✅ Sprachkenntnisse
                    """)

# Footer
st.markdown("---")
st.markdown("*Powered by Streamlit* • *JFdC/Claude*")
