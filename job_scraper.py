#!/usr/bin/env python3
"""
LinkedIn Job Tracker - Enhanced Multi-source version
More robust scraping with better error handling
Author: Théo Collin
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict
import google.generativeai as genai
from urllib.parse import quote_plus, urlencode

class MultiSourceJobTracker:
    def __init__(self):
        self.jobs_file = "jobs_database.json"
        self.config_file = "config.json"
        self.load_config()
        
        # Configure Gemini
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
    def load_config(self):
        """Load search criteria from config file"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    # ============================================
    # LINKEDIN JOBS SCRAPING (Working)
    # ============================================
    
    def scrape_linkedin_jobs(self) -> List[Dict]:
        """Scrape jobs from LinkedIn Jobs API"""
        print("\n🔵 Scraping LinkedIn Jobs...")
        all_jobs = []
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        
        for location in self.config['locations']:
            for keyword in self.config['keywords']:
                params = {
                    'keywords': f"{keyword} alternance",
                    'location': location,
                    'f_WT': '2',
                    'f_TPR': 'r2592000',  # Last 30 days
                    'start': '0'
                }
                
                url = base_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
                
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    jobs = self.parse_linkedin_html(response.text)
                    for job in jobs:
                        job['source'] = 'LinkedIn Jobs'
                    all_jobs.extend(jobs)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ⚠️ Error with {keyword} in {location}: {e}")
        
        print(f"   ✅ Found {len(all_jobs)} jobs from LinkedIn")
        return all_jobs
    
    def parse_linkedin_html(self, html_content: str) -> List[Dict]:
        """Parse LinkedIn job listings from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        for job_card in soup.find_all('li'):
            try:
                job_data = {
                    'id': '',
                    'title': '',
                    'company': '',
                    'location': '',
                    'link': '',
                    'posted_date': '',
                    'description': ''
                }
                
                base_card = job_card.find('div', class_='base-card')
                if base_card and base_card.get('data-entity-urn'):
                    job_id = base_card.get('data-entity-urn').split(':')[-1]
                    job_data['id'] = f"linkedin_{job_id}"
                
                title_elem = job_card.find('h3', class_='base-search-card__title')
                if title_elem:
                    job_data['title'] = title_elem.text.strip()
                
                company_elem = job_card.find('h4', class_='base-search-card__subtitle')
                if company_elem:
                    job_data['company'] = company_elem.text.strip()
                
                location_elem = job_card.find('span', class_='job-search-card__location')
                if location_elem:
                    job_data['location'] = location_elem.text.strip()
                
                link_elem = job_card.find('a', class_='base-card__full-link')
                if link_elem:
                    job_data['link'] = link_elem.get('href', '')
                
                time_elem = job_card.find('time')
                if time_elem:
                    job_data['posted_date'] = time_elem.get('datetime', '')
                
                if job_data['id'] and job_data['title'] and job_data['company']:
                    jobs.append(job_data)
                    
            except Exception as e:
                continue
        
        return jobs
    
    # ============================================
    # WELCOME TO THE JUNGLE - Alternative approach
    # ============================================
    
    def scrape_wttj_simple(self) -> List[Dict]:
        """Scrape WTTJ using simple URL approach"""
        print("\n🟢 Scraping Welcome to the Jungle...")
        all_jobs = []
        
        # WTTJ simple search URLs
        locations = ['paris', 'lille', 'lyon']
        
        for location in locations:
            for keyword in ['alternance', 'apprentissage']:
                try:
                    # Direct URL to WTTJ search
                    url = f"https://www.welcometothejungle.com/fr/jobs?query={keyword}&page=1&aroundQuery={location}"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        jobs = self.parse_wttj_html(response.text, location)
                        for job in jobs:
                            job['source'] = 'Welcome to the Jungle'
                        all_jobs.extend(jobs)
                        print(f"   Found {len(jobs)} jobs for {keyword} in {location}")
                    
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"   ⚠️ Error with WTTJ {keyword}/{location}: {e}")
        
        print(f"   ✅ Total WTTJ: {len(all_jobs)} jobs")
        return all_jobs
    
    def parse_wttj_html(self, html_content: str, location: str) -> List[Dict]:
        """Parse WTTJ HTML"""
        from bs4 import BeautifulSoup
        import hashlib
        
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        # WTTJ uses different selectors - look for job cards
        job_elements = soup.find_all('a', href=lambda x: x and '/fr/companies/' in x and '/jobs/' in x)
        
        for elem in job_elements[:20]:  # Limit to first 20
            try:
                link = elem.get('href', '')
                if not link.startswith('http'):
                    link = 'https://www.welcometothejungle.com' + link
                
                # Extract info from the card
                title_elem = elem.find('h3') or elem.find('h2')
                title = title_elem.text.strip() if title_elem else 'Titre non disponible'
                
                # Generate ID from URL
                job_id = hashlib.md5(link.encode()).hexdigest()[:12]
                
                job_data = {
                    'id': f"wttj_{job_id}",
                    'title': title,
                    'company': 'À identifier',  # Will be analyzed by AI
                    'location': location.capitalize(),
                    'link': link,
                    'posted_date': '',
                    'description': ''
                }
                
                jobs.append(job_data)
                
            except Exception as e:
                continue
        
        return jobs
    
    # ============================================
    # INDEED - Simplified approach
    # ============================================
    
    def scrape_indeed_simple(self) -> List[Dict]:
        """Scrape Indeed using RSS feed (more reliable)"""
        print("\n🔴 Scraping Indeed...")
        all_jobs = []
        
        locations = ['Paris', 'Lille']
        
        for location in locations:
            for keyword in ['alternance operations', 'alternance supply chain', 'alternance']:
                try:
                    # Indeed RSS feed (more stable than HTML scraping)
                    params = {
                        'q': keyword,
                        'l': location,
                        'sort': 'date',
                        'fromage': '30'
                    }
                    
                    # Use the XML/RSS endpoint
                    url = f"https://fr.indeed.com/rss?{urlencode(params)}"
                    
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        jobs = self.parse_indeed_rss(response.text, location)
                        for job in jobs:
                            job['source'] = 'Indeed'
                        all_jobs.extend(jobs)
                        print(f"   Found {len(jobs)} jobs for {keyword} in {location}")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ⚠️ Error with Indeed {keyword}/{location}: {e}")
        
        print(f"   ✅ Total Indeed: {len(all_jobs)} jobs")
        return all_jobs
    
    def parse_indeed_rss(self, xml_content: str, location: str) -> List[Dict]:
        """Parse Indeed RSS feed"""
        from bs4 import BeautifulSoup
        import hashlib
        
        soup = BeautifulSoup(xml_content, 'xml')
        jobs = []
        
        items = soup.find_all('item')
        
        for item in items[:20]:  # Limit to 20
            try:
                title = item.find('title').text if item.find('title') else ''
                link = item.find('link').text if item.find('link') else ''
                description = item.find('description').text if item.find('description') else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                
                # Extract company from title (format: "Title - Company")
                parts = title.split(' - ')
                job_title = parts[0] if parts else title
                company = parts[1] if len(parts) > 1 else 'À identifier'
                
                job_id = hashlib.md5(link.encode()).hexdigest()[:12]
                
                job_data = {
                    'id': f"indeed_{job_id}",
                    'title': job_title,
                    'company': company,
                    'location': location,
                    'link': link,
                    'posted_date': pub_date,
                    'description': description[:500]  # Truncate
                }
                
                jobs.append(job_data)
                
            except Exception as e:
                continue
        
        return jobs
    
    # ============================================
    # LINKEDIN POSTS via Google - Conservative approach
    # ============================================
    
    def scrape_linkedin_posts_google(self) -> List[Dict]:
        """Search for LinkedIn posts via Google (limited to avoid blocking)"""
        print("\n🟡 Searching LinkedIn posts via Google...")
        all_jobs = []
        
        # Only do a few searches to avoid Google blocking
        searches = [
            'site:linkedin.com/posts "alternance" "operations" "Paris"',
            'site:linkedin.com/posts "alternance" "supply chain" "Paris"',
            'site:linkedin.com/feed/update "alternance" "operations"'
        ]
        
        for query in searches:
            try:
                encoded_query = quote_plus(query)
                url = f"https://www.google.com/search?q={encoded_query}&num=10"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    jobs = self.parse_google_results(response.text)
                    for job in jobs:
                        job['source'] = 'LinkedIn Post (via Google)'
                    all_jobs.extend(jobs)
                
                time.sleep(5)  # Long delay to be respectful
                
            except Exception as e:
                print(f"   ⚠️ Error with Google search: {e}")
        
        print(f"   ✅ Total LinkedIn posts: {len(all_jobs)}")
        return all_jobs
    
    def parse_google_results(self, html_content: str) -> List[Dict]:
        """Parse Google search results"""
        from bs4 import BeautifulSoup
        import hashlib
        
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        results = soup.find_all('div', class_='g')
        
        for result in results[:5]:  # Only first 5
            try:
                title_elem = result.find('h3')
                link_elem = result.find('a')
                
                if title_elem and link_elem:
                    link = link_elem.get('href', '')
                    
                    if 'linkedin.com/posts/' in link or 'linkedin.com/feed/update/' in link:
                        title = title_elem.text.strip()
                        
                        snippet_elem = result.find('div', class_='VwiC3b')
                        snippet = snippet_elem.text.strip() if snippet_elem else ''
                        
                        job_id = hashlib.md5(link.encode()).hexdigest()[:12]
                        
                        job_data = {
                            'id': f"linkedin_post_{job_id}",
                            'title': title,
                            'company': 'À identifier',
                            'location': 'Paris',
                            'link': link,
                            'posted_date': '',
                            'description': snippet
                        }
                        
                        jobs.append(job_data)
            
            except Exception as e:
                continue
        
        return jobs
    
    # ============================================
    # AI ANALYSIS (unchanged)
    # ============================================
    
    def analyze_job_with_ai(self, job: Dict) -> Dict:
        """Analyze job with Gemini Pro AI"""
        
        prompt = f"""
Analyse cette offre d'alternance et donne un score sur 10 basé sur le profil suivant :

PROFIL DU CANDIDAT :
- Étudiant SKEMA Business School - Master Project Management & Supply Chain
- Expérience : Strategy & Operations chez Snap Inc. et papernest
- Compétences : Data analysis (SQL, Big Query, Looker Studio), Automatisation (Make, Axiom, IA)
- Langues : Français (natif), Anglais (avancé), Espagnol (B2)
- Cherche : Alternance en Operations, Supply Chain ou Project Management
- Préférence : Start-ups/Scale-ups tech, mais ouvert aux grands groupes
- Localisation : Paris, Région Parisienne, Lille (Remote est un plus)

OFFRE À ANALYSER :
Source : {job.get('source', 'Unknown')}
Titre : {job['title']}
Entreprise : {job['company']}
Localisation : {job['location']}
Description : {job.get('description', 'Non disponible')[:1500]}
Lien : {job.get('link', '')}

CRITÈRES DE SCORING :
- Match avec le profil (compétences data, automatisation, operations)
- Type d'entreprise (Start-up/Scale-up = bonus, Grand groupe = acceptable)
- Mission (opérations, supply chain, project management, data analysis)
- Opportunités d'apprentissage et technologies utilisées
- Red flags (stage déguisé, mission floue, surqualification requise)

IMPORTANT : Sois GÉNÉREUX dans les scores. Un score de 7/10 signifie "intéressant à considérer", pas "match parfait".
- 9-10/10 : Match excellent
- 7-8/10 : Bon match, à considérer sérieusement  
- 5-6/10 : Match partiel mais potentiel
- 3-4/10 : Peu pertinent
- 0-2/10 : Hors sujet

RETOURNE UNIQUEMENT un JSON avec ce format exact :
{{
  "score": 8,
  "verdict": "Excellente opportunité",
  "points_forts": ["Match parfait avec data + operations", "Scale-up tech dynamique"],
  "points_faibles": ["Localisation excentrée"],
  "recommandation": "Postuler rapidement"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(result_text)
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['analyzer'] = 'gemini-pro'
            
            return analysis
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing: {e}")
            return {
                "score": 0,
                "verdict": "Erreur d'analyse",
                "points_forts": [],
                "points_faibles": ["Erreur lors de l'analyse IA"],
                "recommandation": "Analyse manuelle requise",
                "error": str(e)
            }
    
    # ============================================
    # DATABASE MANAGEMENT
    # ============================================
    
    def load_existing_jobs(self) -> Dict:
        """Load existing jobs database"""
        if os.path.exists(self.jobs_file):
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_jobs(self, jobs: Dict):
        """Save jobs to database"""
        with open(self.jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    # ============================================
    # MAIN EXECUTION
    # ============================================
    
    def run(self):
        """Main execution flow"""
        print("🚀 Starting Multi-Source Job Tracker (Enhanced)...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_jobs_db = self.load_existing_jobs()
        new_jobs_count = 0
        
        # Scrape from all sources with error handling
        all_scraped_jobs = []
        
        # LinkedIn Jobs (most reliable)
        try:
            all_scraped_jobs.extend(self.scrape_linkedin_jobs())
        except Exception as e:
            print(f"❌ LinkedIn scraping failed: {e}")
        
        # WTTJ (try but don't fail if it doesn't work)
        try:
            all_scraped_jobs.extend(self.scrape_wttj_simple())
        except Exception as e:
            print(f"⚠️  WTTJ skipped: {e}")
        
        # Indeed (try RSS feed)
        try:
            all_scraped_jobs.extend(self.scrape_indeed_simple())
        except Exception as e:
            print(f"⚠️  Indeed skipped: {e}")
        
        # Google/LinkedIn posts (conservative)
        try:
            all_scraped_jobs.extend(self.scrape_linkedin_posts_google())
        except Exception as e:
            print(f"⚠️  Google search skipped: {e}")
        
        print(f"\n📊 Total jobs scraped: {len(all_scraped_jobs)}")
        
        # Deduplicate by ID
        unique_jobs = {job['id']: job for job in all_scraped_jobs}
        all_scraped_jobs = list(unique_jobs.values())
        print(f"📊 After deduplication: {len(all_scraped_jobs)} unique jobs")
        
        # Process each job
        for i, job in enumerate(all_scraped_jobs, 1):
            job_id = job['id']
            
            if job_id in all_jobs_db:
                continue
            
            print(f"\n🆕 [{i}/{len(all_scraped_jobs)}] {job['title'][:50]}... at {job['company']} ({job['source']})")
            print(f"   🤖 Analyzing...")
            
            analysis = self.analyze_job_with_ai(job)
            job['analysis'] = analysis
            job['found_at'] = datetime.now().isoformat()
            
            all_jobs_db[job_id] = job
            new_jobs_count += 1
            
            print(f"   ✅ Score: {analysis['score']}/10 - {analysis['verdict']}")
            
            time.sleep(2)
        
        self.save_jobs(all_jobs_db)
        
        print(f"\n✨ Done! Found {new_jobs_count} new jobs")
        print(f"📁 Total jobs in database: {len(all_jobs_db)}")
        
        self.generate_report(all_jobs_db)
    
    def generate_report(self, all_jobs: Dict):
        """Generate HTML report - same as before"""
        
        jobs_list = list(all_jobs.values())
        jobs_list.sort(key=lambda x: x.get('analysis', {}).get('score', 0), reverse=True)
        
        top_jobs = jobs_list
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Source Job Tracker - Théo Collin</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{ color: #2d3748; font-size: 28px; margin-bottom: 10px; }}
        .header p {{ color: #718096; font-size: 14px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{ font-size: 32px; color: #667eea; margin-bottom: 5px; }}
        .stat-card p {{ color: #718096; font-size: 14px; }}
        .job-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .job-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }}
        .job-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px; }}
        .job-title {{ font-size: 20px; color: #2d3748; font-weight: 600; margin-bottom: 5px; }}
        .job-company {{ color: #667eea; font-size: 16px; margin-bottom: 5px; }}
        .job-location {{ color: #718096; font-size: 14px; }}
        .source-badge {{
            background: #edf2f7;
            color: #4a5568;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-top: 5px;
            display: inline-block;
        }}
        .score-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 18px;
            font-weight: bold;
        }}
        .score-badge.high {{ background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); }}
        .score-badge.medium {{ background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); }}
        .score-badge.low {{ background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%); }}
        .verdict {{ font-size: 16px; color: #2d3748; font-weight: 500; margin-bottom: 15px; }}
        .points {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }}
        .points-section {{ background: #f7fafc; padding: 15px; border-radius: 8px; }}
        .points-section h4 {{ font-size: 14px; color: #2d3748; margin-bottom: 10px; text-transform: uppercase; }}
        .points-section ul {{ list-style: none; padding-left: 0; }}
        .points-section li {{ padding: 5px 0; color: #4a5568; font-size: 14px; }}
        .points-section li:before {{ content: "• "; color: #667eea; font-weight: bold; margin-right: 5px; }}
        .recommendation {{ background: #edf2f7; padding: 12px 16px; border-radius: 8px; color: #2d3748; font-size: 14px; margin-bottom: 15px; }}
        .job-link {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
        }}
        .job-link:hover {{ background: #5568d3; }}
        .footer {{ text-align: center; color: white; margin-top: 30px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Multi-Source Job Tracker</h1>
            <p>Sources : LinkedIn Jobs, Welcome to the Jungle, Indeed, LinkedIn Posts</p>
            <p>Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{len(all_jobs)}</h3>
                <p>Offres totales</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if j.get('analysis', {}).get('score', 0) >= 7])}</h3>
                <p>Score ≥7/10</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if j.get('analysis', {}).get('score', 0) >= 8])}</h3>
                <p>Score ≥8/10</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if j.get('source') == 'LinkedIn Jobs'])}</h3>
                <p>LinkedIn Jobs</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if j.get('source') == 'Welcome to the Jungle'])}</h3>
                <p>WTTJ</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if j.get('source') == 'Indeed'])}</h3>
                <p>Indeed</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if 'LinkedIn Post' in j.get('source', '')])}</h3>
                <p>Posts LinkedIn</p>
            </div>
        </div>
"""
        
        if top_jobs:
            html += "<h2 style='color: white; margin: 20px 0;'>🌟 Toutes les opportunités</h2>"
            
            for job in top_jobs:
                analysis = job.get('analysis', {})
                score = analysis.get('score', 0)
                score_class = 'high' if score >= 8 else 'medium' if score >= 5 else 'low'
                
                html += f"""
        <div class="job-card">
            <div class="job-header">
                <div>
                    <div class="job-title">{job['title']}</div>
                    <div class="job-company">{job['company']}</div>
                    <div class="job-location">📍 {job['location']}</div>
                    <span class="source-badge">🔗 {job.get('source', 'Unknown')}</span>
                </div>
                <div class="score-badge {score_class}">{score}/10</div>
            </div>
            
            <div class="verdict">💡 {analysis.get('verdict', 'N/A')}</div>
            
            <div class="points">
                <div class="points-section">
                    <h4>✅ Points forts</h4>
                    <ul>
"""
                
                for point in analysis.get('points_forts', []):
                    html += f"<li>{point}</li>"
                
                html += """
                    </ul>
                </div>
                <div class="points-section">
                    <h4>⚠️ Points faibles</h4>
                    <ul>
"""
                
                for point in analysis.get('points_faibles', []):
                    html += f"<li>{point}</li>"
                
                html += f"""
                    </ul>
                </div>
            </div>
            
            <div class="recommendation">
                🎯 <strong>Recommandation :</strong> {analysis.get('recommandation', 'N/A')}
            </div>
            
            <a href="{job.get('link', '#')}" class="job-link" target="_blank">Voir l'offre →</a>
        </div>
"""
        
        html += """
        <div class="footer">
            <p>Développé avec ❤️ par Théo Collin | Multi-source scraping + Gemini Pro AI</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📊 Report generated: index.html")

if __name__ == "__main__":
    tracker = MultiSourceJobTracker()
    tracker.run()
