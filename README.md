# 🎯 LinkedIn Job Tracker - Théo Collin

Système automatisé de recherche et d'analyse d'offres d'alternance sur LinkedIn avec scoring IA (Gemini Pro).

## ✨ Fonctionnalités

- 🔍 **Scraping automatique** des offres LinkedIn 2x/jour
- 🤖 **Analyse IA** avec Gemini Pro et scoring /10
- 📊 **Dashboard HTML** avec les meilleures opportunités
- 🔄 **Déduplication** intelligente des offres
- 📧 **Base de données JSON** de toutes les offres analysées
- 🚀 **Zéro maintenance** - Tourne automatiquement sur GitHub Actions

## 🎬 Setup Complet (15 minutes)

### Étape 1 : Obtenir votre clé API Gemini (2 min)

1. Allez sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Cliquez sur **"Create API Key"**
3. Sélectionnez votre projet Google Cloud (ou créez-en un)
4. Copiez la clé (elle ressemble à : `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
5. **GARDEZ-LA SECRÈTE** ⚠️

### Étape 2 : Créer votre repo GitHub (3 min)

1. **Créez un nouveau repository sur GitHub :**
   - Allez sur [github.com/new](https://github.com/new)
   - Nom : `linkedin-job-tracker` (ou autre)
   - Visibilité : **Private** (recommandé) ou Public
   - Cochez **"Add a README file"**
   - Cliquez **"Create repository"**

2. **Uploadez les fichiers du projet :**
   
   Option A - Via l'interface GitHub (plus simple) :
   - Cliquez sur **"Add file"** → **"Upload files"**
   - Glissez-déposez tous les fichiers de ce dossier
   - Commit : "Initial commit"
   
   Option B - Via Git en ligne de commande :
   ```bash
   git clone https://github.com/VOTRE_USERNAME/linkedin-job-tracker.git
   cd linkedin-job-tracker
   # Copiez tous les fichiers dans ce dossier
   git add .
   git commit -m "Initial commit"
   git push
   ```

### Étape 3 : Ajouter votre clé API dans les secrets (1 min)

1. Sur votre repo GitHub, allez dans **Settings** (onglet en haut)
2. Dans le menu de gauche : **Secrets and variables** → **Actions**
3. Cliquez sur **"New repository secret"**
4. Name : `GEMINI_API_KEY`
5. Secret : Collez votre clé API Gemini
6. Cliquez **"Add secret"**

### Étape 4 : Activer GitHub Pages (2 min)

Pour voir votre dashboard en ligne :

1. Sur votre repo : **Settings** → **Pages**
2. Source : **Deploy from a branch**
3. Branch : **main** → Dossier : **/ (root)**
4. Cliquez **"Save"**

Votre dashboard sera accessible à : `https://VOTRE_USERNAME.github.io/linkedin-job-tracker/`

### Étape 5 : Personnaliser vos critères (2 min)

Éditez le fichier `config.json` sur GitHub :

```json
{
  "keywords": [
    "operations",
    "supply chain",
    "project management"
  ],
  "locations": [
    "Paris, Île-de-France, France",
    "Lille, Hauts-de-France, France"
  ]
}
```

Ajoutez/modifiez les mots-clés et localisations selon vos besoins.

### Étape 6 : Lancer le premier scan (1 min)

1. Allez dans l'onglet **Actions** de votre repo
2. Si vous voyez un message "Workflows aren't being run", cliquez **"I understand, enable them"**
3. Dans le menu de gauche, cliquez sur **"LinkedIn Job Tracker"**
4. Cliquez sur **"Run workflow"** → **"Run workflow"**
5. Attendez 2-3 minutes ⏱️

### Étape 7 : Voir vos résultats 🎉

Une fois le workflow terminé (coche verte ✅) :

1. Votre dashboard est en ligne : `https://VOTRE_USERNAME.github.io/linkedin-job-tracker/`
2. Ou consultez le fichier `index.html` directement dans le repo
3. Les offres sont sauvegardées dans `jobs_database.json`

## 📅 Automatisation

Le script tourne **automatiquement 2x/jour** :
- 🌅 8h00 (Paris) - Scan du matin
- 🌆 18h00 (Paris) - Scan du soir

Vous pouvez aussi le lancer manuellement à tout moment via l'onglet **Actions**.

## 🎨 Personnalisation Avancée

### Modifier la fréquence de scan

Éditez `.github/workflows/scrape-jobs.yml` :

```yaml
schedule:
  - cron: '0 7,17 * * *'  # Changez les heures ici
```

Exemples :
- Toutes les 2h : `'0 */2 * * *'`
- 3x/jour (8h, 14h, 20h) : `'0 7,13,19 * * *'`
- Uniquement en semaine : `'0 7,17 * * 1-5'`

### Ajouter des mots-clés

Éditez `config.json` :

```json
"keywords": [
  "operations",
  "supply chain",
  "project management",
  "data analyst",      // Nouveau
  "business analyst"   // Nouveau
]
```

### Changer le seuil de score

Dans `job_scraper.py`, ligne 450 :

```python
top_jobs = [j for j in jobs_list if j.get('analysis', {}).get('score', 0) >= 7]
# Changez 7 en 6 pour être moins strict, ou 8 pour être plus strict
```

## 🔧 Dépannage

### Le workflow échoue

1. Vérifiez que votre clé API Gemini est bien configurée dans **Settings → Secrets**
2. Regardez les logs dans **Actions** → Cliquez sur le workflow échoué
3. Si erreur "rate limit" : Gemini gratuit est limité, attendez quelques heures

### Aucune offre trouvée

1. Vérifiez vos mots-clés dans `config.json` (peut-être trop restrictifs)
2. LinkedIn a peut-être changé sa structure HTML → Ouvrez une issue
3. Essayez de lancer manuellement pour voir les logs

### Le dashboard ne s'affiche pas

1. Vérifiez que GitHub Pages est activé (**Settings → Pages**)
2. Attendez 2-3 minutes après l'activation
3. Vérifiez que `index.html` existe dans le repo

## 📊 Structure des fichiers

```
linkedin-job-tracker/
├── job_scraper.py          # Script principal
├── config.json             # Vos critères de recherche
├── requirements.txt        # Dépendances Python
├── jobs_database.json      # Base de données (généré)
├── index.html              # Dashboard (généré)
├── .github/
│   └── workflows/
│       └── scrape-jobs.yml # Configuration GitHub Actions
└── README.md               # Ce fichier
```

## 🚀 Améliorations Futures

Idées d'évolutions possibles :

- [ ] Notifications email pour offres >8/10
- [ ] Export Excel hebdomadaire
- [ ] Filtre par salaire minimum
- [ ] Détection de mots-clés négatifs
- [ ] Statistiques par entreprise
- [ ] Intégration Notion/Airtable

## 🤝 Support

Problème ? Question ? Ouvrez une [Issue](https://github.com/VOTRE_USERNAME/linkedin-job-tracker/issues) !

---

Développé avec ❤️ par Théo Collin | Propulsé par Gemini Pro AI 🤖
