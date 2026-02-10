#!/usr/bin/env python3
"""
LinkedIn Job Tracker - Multi-source version
Scrapes from: LinkedIn Jobs, Welcome to the Jungle, Indeed, and Google (LinkedIn posts)
Author: Théo Collin
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict
import google.generativeai as genai
from urllib.parse import quote_plus

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
    # LINKEDIN JOBS SCRAPING
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
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ⚠️ Error scraping LinkedIn: {e}")
        
        print(f"   Found {len(all_jobs)} jobs from LinkedIn")
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
    # WELCOME TO THE JUNGLE SCRAPING
    # ============================================
    
    def scrape_wttj(self) -> List[Dict]:
        """Scrape jobs from Welcome to the Jungle"""
        print("\n🟢 Scraping Welcome to the Jungle...")
        all_jobs = []
        base_url = "https://www.welcometothejungle.com/api/graphql"
        
        # WTTJ uses GraphQL API
        for location in ['Paris', 'Lille', 'Lyon']:  # Simplified locations
            for keyword in self.config['keywords']:
                try:
                    query = f"{keyword} alternance"
                    
                    # GraphQL query for WTTJ
                    payload = {
                        "query": """
                        query JobSearch($query: String!, $page: Int) {
                          jobs(query: $query, page: $page) {
                            nodes {
                              id
                              name
                              slug
                              contractType
                              office {
                                name
                                city
                              }
                              organization {
                                name
                                slug
                              }
                              publishedAt
                            }
                          }
                        }
                        """,
                        "variables": {
                            "query": query,
                            "page": 1
                        }
                    }
                    
                    headers = {
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0'
                    }
                    
                    response = requests.post(base_url, json=payload, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        jobs_data = data.get('data', {}).get('jobs', {}).get('nodes', [])
                        
                        for job in jobs_data:
                            job_obj = {
                                'id': f"wttj_{job['id']}",
                                'title': job.get('name', ''),
                                'company': job.get('organization', {}).get('name', ''),
                                'location': job.get('office', {}).get('city', ''),
                                'link': f"https://www.welcometothejungle.com/fr/companies/{job.get('organization', {}).get('slug', '')}/jobs/{job.get('slug', '')}",
                                'posted_date': job.get('publishedAt', ''),
                                'description': '',
                                'source': 'Welcome to the Jungle'
                            }
                            
                            if job_obj['title'] and job_obj['company']:
                                all_jobs.append(job_obj)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ⚠️ Error scraping WTTJ: {e}")
        
        print(f"   Found {len(all_jobs)} jobs from WTTJ")
        return all_jobs
    
    # ============================================
    # INDEED SCRAPING
    # ============================================
    
    def scrape_indeed(self) -> List[Dict]:
        """Scrape jobs from Indeed"""
        print("\n🔴 Scraping Indeed...")
        all_jobs = []
        base_url = "https://fr.indeed.com/jobs"
        
        for location in ['Paris', 'Lille']:
            for keyword in self.config['keywords']:
                try:
                    params = {
                        'q': f"{keyword} alternance",
                        'l': location,
                        'fromage': '30',  # Last 30 days
                        'sort': 'date'
                    }
                    
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                    response = requests.get(base_url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    jobs = self.parse_indeed_html(response.text)
                    for job in jobs:
                        job['source'] = 'Indeed'
                    all_jobs.extend(jobs)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ⚠️ Error scraping Indeed: {e}")
        
        print(f"   Found {len(all_jobs)} jobs from Indeed")
        return all_jobs
    
    def parse_indeed_html(self, html_content: str) -> List[Dict]:
        """Parse Indeed job listings from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        # Indeed uses different selectors
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards:
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
                
                # Extract job ID
                job_key = card.get('data-jk', '')
                if job_key:
                    job_data['id'] = f"indeed_{job_key}"
                
                # Extract title
                title_elem = card.find('h2', class_='jobTitle')
                if title_elem:
                    title_link = title_elem.find('a')
                    if title_link:
                        job_data['title'] = title_link.get('title', '') or title_link.text.strip()
                        job_data['link'] = 'https://fr.indeed.com' + title_link.get('href', '')
                
                # Extract company
                company_elem = card.find('span', {'data-testid': 'company-name'})
                if company_elem:
                    job_data['company'] = company_elem.text.strip()
                
                # Extract location
                location_elem = card.find('div', {'data-testid': 'text-location'})
                if location_elem:
                    job_data['location'] = location_elem.text.strip()
                
                if job_data['id'] and job_data['title'] and job_data['company']:
                    jobs.append(job_data)
                    
            except Exception as e:
                continue
        
        return jobs
    
    # ============================================
    # GOOGLE SEARCH FOR LINKEDIN POSTS
    # ============================================
    
    def scrape_google_linkedin_posts(self) -> List[Dict]:
        """Search Google for LinkedIn posts containing job offers"""
        print("\n🟡 Searching Google for LinkedIn posts...")
        all_jobs = []
        
        for keyword in self.config['keywords']:
            for location in ['Paris', 'Lille']:
                try:
                    # Google search query
                    query = f'site:linkedin.com/posts "{keyword}" "alternance" "{location}"'
                    encoded_query = quote_plus(query)
                    
                    url = f"https://www.google.com/search?q={encoded_query}&num=20"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    jobs = self.parse_google_results(response.text, keyword, location)
                    for job in jobs:
                        job['source'] = 'LinkedIn Post (via Google)'
                    all_jobs.extend(jobs)
                    
                    time.sleep(3)  # Be nice to Google
                    
                except Exception as e:
                    print(f"   ⚠️ Error searching Google: {e}")
        
        print(f"   Found {len(all_jobs)} LinkedIn posts from Google")
        return all_jobs
    
    def parse_google_results(self, html_content: str, keyword: str, location: str) -> List[Dict]:
        """Parse Google search results for LinkedIn posts"""
        from bs4 import BeautifulSoup
        import hashlib
        
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        # Find all search result divs
        results = soup.find_all('div', class_='g')
        
        for result in results:
            try:
                # Extract title and link
                title_elem = result.find('h3')
                link_elem = result.find('a')
                
                if title_elem and link_elem:
                    link = link_elem.get('href', '')
                    
                    # Only process LinkedIn post URLs
                    if 'linkedin.com/posts/' in link or 'linkedin.com/feed/update/' in link:
                        title = title_elem.text.strip()
                        
                        # Extract snippet
                        snippet_elem = result.find('div', class_='VwiC3b')
                        snippet = snippet_elem.text.strip() if snippet_elem else ''
                        
                        # Generate unique ID from URL
                        job_id = hashlib.md5(link.encode()).hexdigest()[:12]
                        
                        job_data = {
                            'id': f"linkedin_post_{job_id}",
                            'title': title,
                            'company': 'À identifier',  # Will be analyzed by AI
                            'location': location,
                            'link': link,
                            'posted_date': '',
                            'description': snippet
                        }
                        
                        jobs.append(job_data)
            
            except Exception as e:
                continue
        
        return jobs
    
    # ============================================
    # AI ANALYSIS
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
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(result_text)
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['analyzer'] = 'gemini-pro'
            
            return analysis
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing job {job['id']}: {e}")
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
        print("🚀 Starting Multi-Source Job Tracker...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load existing jobs
        all_jobs_db = self.load_existing_jobs()
        new_jobs_count = 0
        
        # Scrape from all sources
        all_scraped_jobs = []
        
        all_scraped_jobs.extend(self.scrape_linkedin_jobs())
        all_scraped_jobs.extend(self.scrape_wttj())
        all_scraped_jobs.extend(self.scrape_indeed())
        all_scraped_jobs.extend(self.scrape_google_linkedin_posts())
        
        print(f"\n📊 Total jobs scraped: {len(all_scraped_jobs)}")
        
        # Process each job
        for job in all_scraped_jobs:
            job_id = job['id']
            
            # Skip if already analyzed
            if job_id in all_jobs_db:
                continue
            
            print(f"\n🆕 New: {job['title']} at {job['company']} ({job['source']})")
            print(f"   🤖 Analyzing...")
            
            # Analyze with AI
            analysis = self.analyze_job_with_ai(job)
            
            # Combine job data with analysis
            job['analysis'] = analysis
            job['found_at'] = datetime.now().isoformat()
            
            # Add to database
            all_jobs_db[job_id] = job
            new_jobs_count += 1
            
            print(f"   ✅ Score: {analysis['score']}/10 - {analysis['verdict']}")
            
            # Rate limiting
            time.sleep(2)
        
        # Save updated database
        self.save_jobs(all_jobs_db)
        
        print(f"\n✨ Done! Found {new_jobs_count} new jobs")
        print(f"📁 Total jobs in database: {len(all_jobs_db)}")
        
        # Generate report
        self.generate_report(all_jobs_db)
    
    def generate_report(self, all_jobs: Dict):
        """Generate HTML report of all jobs"""
        
        # Sort jobs by score
        jobs_list = list(all_jobs.values())
        jobs_list.sort(key=lambda x: x.get('analysis', {}).get('score', 0), reverse=True)
        
        # Get all jobs (changed from >= 7 to show everything)
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
