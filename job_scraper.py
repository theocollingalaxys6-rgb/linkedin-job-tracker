#!/usr/bin/env python3
"""
LinkedIn Job Tracker - Automated job search with AI scoring
Author: Théo Collin
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict
import google.generativeai as genai

class LinkedInJobTracker:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
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
    
    def build_search_urls(self) -> List[str]:
        """Build LinkedIn search URLs based on config"""
        urls = []
        
        for location in self.config['locations']:
            for keyword in self.config['keywords']:
                params = {
                    'keywords': f"{keyword} alternance",
                    'location': location,
                    'f_WT': '2',  # Filter for contract type (alternance)
                    'f_TPR': 'r604800',  # Jobs posted in last 7 days
                    'start': '0'
                }
                
                url = self.base_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
                urls.append(url)
                
        return urls
    
    def scrape_jobs(self, url: str) -> List[Dict]:
        """Scrape jobs from LinkedIn API"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML to extract job data
            jobs = self.parse_job_listings(response.text)
            return jobs
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def parse_job_listings(self, html_content: str) -> List[Dict]:
        """Parse job listings from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        for job_card in soup.find_all('li'):
            try:
                job_data = {
                    'id': job_card.get('data-occludable-job-id', ''),
                    'title': '',
                    'company': '',
                    'location': '',
                    'link': '',
                    'posted_date': '',
                    'description_preview': ''
                }
                
                # Extract job ID from the base-card div
                base_card = job_card.find('div', class_='base-card')
                if base_card and base_card.get('data-entity-urn'):
                    job_id = base_card.get('data-entity-urn').split(':')[-1]
                    job_data['id'] = job_id
                
                # Extract title
                title_elem = job_card.find('h3', class_='base-search-card__title')
                if title_elem:
                    job_data['title'] = title_elem.text.strip()
                
                # Extract company
                company_elem = job_card.find('h4', class_='base-search-card__subtitle')
                if company_elem:
                    job_data['company'] = company_elem.text.strip()
                
                # Extract location
                location_elem = job_card.find('span', class_='job-search-card__location')
                if location_elem:
                    job_data['location'] = location_elem.text.strip()
                
                # Extract link
                link_elem = job_card.find('a', class_='base-card__full-link')
                if link_elem:
                    job_data['link'] = link_elem.get('href', '')
                
                # Extract posted date
                time_elem = job_card.find('time')
                if time_elem:
                    job_data['posted_date'] = time_elem.get('datetime', '')
                
                # Only add if we have minimum required data
                if job_data['id'] and job_data['title'] and job_data['company']:
                    jobs.append(job_data)
                    
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue
        
        return jobs
    
    def get_job_details(self, job_id: str) -> str:
        """Fetch full job description"""
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            description_elem = soup.find('div', class_='description__text')
            if description_elem:
                return description_elem.text.strip()
            
            return ""
            
        except Exception as e:
            print(f"Error fetching job details for {job_id}: {e}")
            return ""
    
    def analyze_job_with_ai(self, job: Dict) -> Dict:
        """Analyze job with Gemini Pro AI"""
        
        # Fetch full description if not already present
        if not job.get('description'):
            job['description'] = self.get_job_details(job['id'])
            time.sleep(1)  # Be respectful with rate limiting
        
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
Titre : {job['title']}
Entreprise : {job['company']}
Localisation : {job['location']}
Description : {job.get('description', 'Non disponible')[:1500]}

CRITÈRES DE SCORING :
- Match avec le profil (compétences data, automatisation, operations)
- Type d'entreprise (Start-up/Scale-up = bonus, Grand groupe = acceptable)
- Mission (opérations, supply chain, project management, data analysis)
- Opportunités d'apprentissage et technologies utilisées
- Red flags (stage déguisé, mission floue, surqualification requise)

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
            
            # Extract JSON from response (Gemini sometimes adds markdown)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(result_text)
            
            # Add metadata
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['analyzer'] = 'gemini-pro'
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing job {job['id']}: {e}")
            return {
                "score": 0,
                "verdict": "Erreur d'analyse",
                "points_forts": [],
                "points_faibles": ["Erreur lors de l'analyse IA"],
                "recommandation": "Analyse manuelle requise",
                "error": str(e)
            }
    
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
    
    def run(self):
        """Main execution flow"""
        print("🚀 Starting LinkedIn Job Tracker...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load existing jobs
        all_jobs = self.load_existing_jobs()
        new_jobs_count = 0
        
        # Build search URLs
        search_urls = self.build_search_urls()
        print(f"🔍 Searching {len(search_urls)} different criteria combinations...")
        
        # Scrape each URL
        for i, url in enumerate(search_urls, 1):
            print(f"\n📊 Scraping search {i}/{len(search_urls)}...")
            jobs = self.scrape_jobs(url)
            print(f"   Found {len(jobs)} jobs")
            
            # Process each job
            for job in jobs:
                job_id = job['id']
                
                # Skip if already analyzed
                if job_id in all_jobs:
                    print(f"   ⏭️  Skipping {job['title']} (already analyzed)")
                    continue
                
                print(f"   🆕 New job: {job['title']} at {job['company']}")
                
                # Analyze with AI
                print(f"   🤖 Analyzing with Gemini...")
                analysis = self.analyze_job_with_ai(job)
                
                # Combine job data with analysis
                job['analysis'] = analysis
                job['found_at'] = datetime.now().isoformat()
                
                # Add to database
                all_jobs[job_id] = job
                new_jobs_count += 1
                
                print(f"   ✅ Score: {analysis['score']}/10 - {analysis['verdict']}")
                
                # Rate limiting
                time.sleep(2)
        
        # Save updated database
        self.save_jobs(all_jobs)
        
        print(f"\n✨ Done! Found {new_jobs_count} new jobs")
        print(f"📁 Total jobs in database: {len(all_jobs)}")
        
        # Generate report
        self.generate_report(all_jobs)
    
    def generate_report(self, all_jobs: Dict):
        """Generate HTML report of top jobs"""
        
        # Filter and sort jobs by score
        jobs_list = list(all_jobs.values())
        jobs_list.sort(key=lambda x: x.get('analysis', {}).get('score', 0), reverse=True)
        
        # Get top jobs (score >= 7)
        top_jobs = [j for j in jobs_list if j.get('analysis', {}).get('score', 0) >= 7]
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Job Tracker - Théo Collin</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #2d3748;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #718096;
            font-size: 14px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            font-size: 32px;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-card p {{
            color: #718096;
            font-size: 14px;
        }}
        .job-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .job-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        .job-title {{
            font-size: 20px;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .job-company {{
            color: #667eea;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .job-location {{
            color: #718096;
            font-size: 14px;
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
        .verdict {{
            font-size: 16px;
            color: #2d3748;
            font-weight: 500;
            margin-bottom: 15px;
        }}
        .points {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .points-section {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
        }}
        .points-section h4 {{
            font-size: 14px;
            color: #2d3748;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .points-section ul {{
            list-style: none;
            padding-left: 0;
        }}
        .points-section li {{
            padding: 5px 0;
            color: #4a5568;
            font-size: 14px;
        }}
        .points-section li:before {{
            content: "• ";
            color: #667eea;
            font-weight: bold;
            margin-right: 5px;
        }}
        .recommendation {{
            background: #edf2f7;
            padding: 12px 16px;
            border-radius: 8px;
            color: #2d3748;
            font-size: 14px;
            margin-bottom: 15px;
        }}
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
        .job-link:hover {{
            background: #5568d3;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 LinkedIn Job Tracker</h1>
            <p>Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{len(all_jobs)}</h3>
                <p>Offres totales</p>
            </div>
            <div class="stat-card">
                <h3>{len(top_jobs)}</h3>
                <p>Offres pertinentes (≥7/10)</p>
            </div>
            <div class="stat-card">
                <h3>{len([j for j in jobs_list if j.get('analysis', {}).get('score', 0) >= 8])}</h3>
                <p>Excellentes offres (≥8/10)</p>
            </div>
        </div>
"""
        
        if top_jobs:
            html += "<h2 style='color: white; margin: 20px 0;'>🌟 Top Opportunités</h2>"
            
            for job in top_jobs[:20]:  # Top 20
                analysis = job.get('analysis', {})
                score = analysis.get('score', 0)
                
                score_class = 'high' if score >= 8 else 'medium' if score >= 7 else 'low'
                
                html += f"""
        <div class="job-card">
            <div class="job-header">
                <div>
                    <div class="job-title">{job['title']}</div>
                    <div class="job-company">{job['company']}</div>
                    <div class="job-location">📍 {job['location']}</div>
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
            
            <a href="{job.get('link', '#')}" class="job-link" target="_blank">Voir l'offre sur LinkedIn →</a>
        </div>
"""
        else:
            html += "<p style='color: white; text-align: center; font-size: 18px;'>Aucune offre pertinente pour le moment. Le prochain scan aura lieu bientôt !</p>"
        
        html += """
        <div class="footer">
            <p>Développé avec ❤️ par Théo Collin | Propulsé par Gemini Pro AI</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📊 Report generated: index.html")

if __name__ == "__main__":
    tracker = LinkedInJobTracker()
    tracker.run()
