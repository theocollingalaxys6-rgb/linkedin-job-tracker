# 📖 GUIDE COMPLET - Pas à pas avec captures d'écran

## 🎯 Objectif
À la fin de ce guide, vous aurez un système qui scanne LinkedIn automatiquement 2x/jour et vous présente les meilleures offres d'alternance avec un score IA.

---

## ÉTAPE 1 : Obtenir votre clé API Gemini (2 min) 🔑

### 1.1 Aller sur Google AI Studio
👉 **https://aistudio.google.com/app/apikey**

### 1.2 Créer la clé
- Cliquez sur le bouton **"Get API Key"** ou **"Create API Key"**
- Sélectionnez un projet (ou "Create new project")
- Votre clé apparaît (commence par `AIzaSy...`)

### 1.3 Copier et sauvegarder
```
AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
⚠️ **IMPORTANT** : Gardez cette clé secrète ! Ne la partagez jamais publiquement.

---

## ÉTAPE 2 : Créer votre repository GitHub (3 min) 📦

### 2.1 Créer le repo
👉 **https://github.com/new**

Paramètres :
- **Repository name** : `linkedin-job-tracker`
- **Description** : "Automated LinkedIn job search with AI scoring"
- **Visibility** : 🔒 Private (recommandé) ou Public
- ✅ Cochez **"Add a README file"**
- Cliquez **"Create repository"**

### 2.2 Uploader les fichiers

**Méthode simple (recommandée)** :
1. Décompressez le ZIP que je vous ai fourni
2. Dans votre nouveau repo GitHub, cliquez **"Add file"** → **"Upload files"**
3. Glissez-déposez TOUS les fichiers :
   - `job_scraper.py`
   - `config.json`
   - `requirements.txt`
   - `index.html`
   - `jobs_database.json`
   - `.gitignore`
   - `README.md`
   - `QUICK_START.md`
   - Le dossier `.github/` (avec son contenu)

4. Message de commit : "Initial setup"
5. Cliquez **"Commit changes"**

**Méthode Git (si vous êtes à l'aise)** :
```bash
# Cloner votre repo
git clone https://github.com/VOTRE_USERNAME/linkedin-job-tracker.git
cd linkedin-job-tracker

# Copier tous les fichiers du ZIP ici
# Puis :
git add .
git commit -m "Initial setup"
git push
```

---

## ÉTAPE 3 : Configurer la clé API dans GitHub (1 min) 🔐

### 3.1 Accéder aux Secrets
Dans votre repo :
1. Cliquez sur **Settings** (onglet en haut à droite)
2. Menu gauche : **Secrets and variables** → **Actions**

### 3.2 Ajouter le secret
1. Cliquez **"New repository secret"**
2. **Name** : `GEMINI_API_KEY` (EXACTEMENT comme ça, en majuscules)
3. **Secret** : Collez votre clé API Gemini
4. Cliquez **"Add secret"**

✅ Vous devriez voir `GEMINI_API_KEY` dans la liste des secrets.

---

## ÉTAPE 4 : Activer GitHub Pages (2 min) 🌐

Pour voir votre dashboard en ligne :

### 4.1 Accéder aux paramètres Pages
1. Toujours dans **Settings**
2. Menu gauche : **Pages**

### 4.2 Configurer
1. **Source** : Deploy from a branch
2. **Branch** : `main` (ou `master`)
3. **Folder** : `/ (root)`
4. Cliquez **"Save"**

### 4.3 Récupérer l'URL
Après quelques secondes, vous verrez :
```
Your site is live at https://VOTRE_USERNAME.github.io/linkedin-job-tracker/
```

📌 **Sauvegardez cette URL** - c'est là que vous consulterez vos offres !

---

## ÉTAPE 5 : Personnaliser vos critères (2 min) ⚙️

### 5.1 Éditer config.json
Dans votre repo, cliquez sur le fichier **`config.json`**

### 5.2 Modifier selon vos besoins
Cliquez sur l'icône ✏️ (Edit this file)

Exemple de personnalisation :
```json
{
  "keywords": [
    "operations",
    "supply chain",
    "project management",
    "business operations",
    "logistics"
  ],
  "locations": [
    "Paris, Île-de-France, France",
    "Lille, Hauts-de-France, France",
    "Lyon, Auvergne-Rhône-Alpes, France"
  ]
}
```

💡 **Conseils** :
- Ajoutez des variations de vos mots-clés
- Pour chercher partout en France : `"France"`
- Pour remote : le script détecte automatiquement

### 5.3 Sauvegarder
1. Scroll en bas
2. Commit message : "Update search criteria"
3. Cliquez **"Commit changes"**

---

## ÉTAPE 6 : Lancer le premier scan ! 🚀

### 6.1 Activer GitHub Actions
1. Allez dans l'onglet **Actions** (en haut)
2. Si vous voyez "Workflows aren't being run on this forked repository"
   → Cliquez **"I understand my workflows, go ahead and enable them"**

### 6.2 Lancer manuellement
1. Menu gauche : Cliquez sur **"LinkedIn Job Tracker"**
2. À droite : Cliquez **"Run workflow"**
3. Dropdown : Assurez-vous que `main` est sélectionné
4. Cliquez **"Run workflow"** (le bouton vert)

### 6.3 Suivre l'exécution
- Vous voyez une ligne jaune 🟡 qui apparaît = en cours
- Cliquez dessus pour voir les logs en direct
- Attendre 2-5 minutes selon le nombre d'offres

### 6.4 Vérifier le succès
✅ Coche verte = Succès !
❌ Croix rouge = Erreur (vérifiez les logs)

---

## ÉTAPE 7 : Consulter vos résultats 🎉

### 7.1 Dashboard en ligne
Allez sur votre URL GitHub Pages :
```
https://VOTRE_USERNAME.github.io/linkedin-job-tracker/
```

Vous verrez :
- 📊 Statistiques (nombre d'offres, top offres)
- 🎯 Liste des meilleures opportunités triées par score
- 💡 Analyse IA pour chaque offre
- ✅ Points forts / ⚠️ Points faibles
- 🎯 Recommandations d'action

### 7.2 Consulter la base de données brute
Dans votre repo, ouvrez **`jobs_database.json`**
- Vous y verrez toutes les offres en JSON
- Chaque offre a son analyse complète

---

## 🔄 AUTOMATISATION

### C'est déjà fait !

Le système tourne maintenant **automatiquement** :
- 🌅 **8h00** (heure de Paris) - Scan du matin
- 🌆 **18h00** (heure de Paris) - Scan du soir

### Vérifier les runs automatiques
1. Onglet **Actions**
2. Vous verrez les exécutions automatiques apparaître

### Lancer manuellement à tout moment
Répétez l'**Étape 6** quand vous voulez !

---

## 📱 UTILISATION QUOTIDIENNE

### Votre routine idéale :

**Chaque matin** :
1. ☕ Prenez votre café
2. 📱 Ouvrez votre dashboard : `https://VOTRE_USERNAME.github.io/linkedin-job-tracker/`
3. 👀 Regardez les nouvelles offres avec score ≥7/10
4. ✅ Postulez aux meilleures (≥8/10) en priorité

**Personnalisation continue** :
- Affinez `config.json` selon les résultats
- Ajoutez des mots-clés si vous ratez des offres
- Retirez des mots-clés si trop de bruit

---

## 🎨 PERSONNALISATIONS AVANCÉES

### Changer la fréquence de scan

Éditez `.github/workflows/scrape-jobs.yml` :

```yaml
on:
  schedule:
    - cron: '0 7,17 * * *'  # Changez les heures ici
```

**Exemples** :
- Toutes les 2h : `'0 */2 * * *'`
- 3x/jour (9h, 14h, 19h) : `'0 8,13,18 * * *'`
- Seulement en semaine : `'0 7,17 * * 1-5'`

### Modifier le seuil de score

Dans `job_scraper.py`, ligne ~450 :
```python
top_jobs = [j for j in jobs_list if j.get('analysis', {}).get('score', 0) >= 7]
```
Changez `7` en `6` (moins strict) ou `8` (plus strict)

### Ajouter d'autres localisations

Dans `config.json` :
```json
"locations": [
  "Paris, Île-de-France, France",
  "Lille, Hauts-de-France, France",
  "Lyon, Auvergne-Rhône-Alpes, France",
  "Bordeaux, Nouvelle-Aquitaine, France",
  "Remote, France"
]
```

---

## 🔧 DÉPANNAGE

### ❌ Workflow échoue

**Vérifications** :
1. La clé API Gemini est bien dans **Settings → Secrets** ?
2. Le nom est exactement `GEMINI_API_KEY` ?
3. Regardez les logs dans Actions → Cliquez sur le run échoué

**Erreurs courantes** :
- `Invalid API key` → Vérifiez votre clé Gemini
- `Rate limit` → Attendez 1h, Gemini gratuit a des limites
- `Module not found` → Le fichier `requirements.txt` est bien uploadé ?

### 📭 Aucune offre trouvée

**Causes possibles** :
1. Mots-clés trop restrictifs → Élargissez dans `config.json`
2. Localisation trop précise → Essayez juste "France"
3. LinkedIn a changé sa structure → Attendez une mise à jour

**Tests** :
```python
# Testez avec des mots-clés ultra larges :
"keywords": ["alternance", "stage"]
```

### 🌐 Dashboard vide

**Vérifications** :
1. GitHub Pages activé ? (**Settings → Pages**)
2. Le workflow a bien tourné ? (coche verte ✅)
3. Le fichier `index.html` existe dans le repo ?
4. Attendez 2-3 min après activation de Pages

**Solution** :
Relancez le workflow manuellement (Étape 6)

---

## 📊 COMPRENDRE LES SCORES

### Comment l'IA note les offres ?

**Score 9-10/10** 🌟
- Match parfait avec votre profil
- Compétences data + operations
- Entreprise scale-up tech
- Mission claire et intéressante

**Score 7-8/10** ✅
- Bon match général
- Certaines compétences correspondent
- Entreprise correcte
- Quelques points d'interrogation

**Score 5-6/10** ⚠️
- Match partiel
- Mission pas totalement alignée
- Ou entreprise moins attractive

**Score 0-4/10** ❌
- Mauvais match
- Trop junior/senior
- Mission floue
- Red flags détectés

---

## 🚀 PROCHAINES ÉTAPES

Une fois le système en place :

1. **Semaine 1** : Observez les résultats, affinez `config.json`
2. **Semaine 2** : Identifiez les patterns des bonnes offres
3. **Semaine 3** : Automatisez vos candidatures (templates de CV/LM)
4. **Bonus** : Ajoutez ce projet à votre CV ! (Compétence : automation, IA, Python)

---

## 💡 ASTUCES PRO

### Boostez votre efficacité :

1. **Marquez vos favoris** : Gardez une liste des offres ≥8/10
2. **Postulez vite** : Les premières candidatures ont plus de chances
3. **Personnalisez** : Utilisez l'analyse IA pour adapter votre lettre
4. **Suivez** : Notez dans un tableau vos candidatures

### Ajoutez ce projet à votre CV :

```
Projet Personnel : LinkedIn Job Tracker
- Automatisation de recherche d'emploi avec Python
- Scraping LinkedIn & analyse IA (Gemini)
- GitHub Actions, CI/CD
- Résultat : 50+ offres analysées/semaine, gain 10h/semaine
```

---

## 🆘 BESOIN D'AIDE ?

### Ressources :

1. **README.md** : Documentation complète
2. **QUICK_START.md** : Guide rapide
3. **Logs GitHub Actions** : Pour debugger
4. **Google AI Studio** : https://aistudio.google.com

### Support :

Si vraiment bloqué :
1. Vérifiez les logs dans Actions
2. Relisez ce guide étape par étape
3. Vérifiez que TOUS les fichiers sont uploadés
4. Assurez-vous que `GEMINI_API_KEY` est correct

---

## ✅ CHECKLIST FINALE

Avant de commencer :
- [ ] Compte GitHub créé
- [ ] Compte Google pour Gemini
- [ ] 15 minutes disponibles

Pendant le setup :
- [ ] Clé API Gemini obtenue et copiée
- [ ] Repo GitHub créé
- [ ] Tous les fichiers uploadés
- [ ] Secret `GEMINI_API_KEY` ajouté
- [ ] GitHub Pages activé
- [ ] `config.json` personnalisé
- [ ] Premier workflow lancé
- [ ] Dashboard accessible

Après le setup :
- [ ] URL du dashboard sauvegardée
- [ ] Notifications (optionnel) configurées
- [ ] Routine quotidienne définie

---

**🎉 FÉLICITATIONS !**

Vous avez maintenant un système de recherche d'emploi automatisé et intelligent !

**Temps total** : ~15 minutes
**Coût** : 0€
**Gain de temps** : ~10h/semaine
**ROI** : ∞

Bonne recherche d'alternance ! 🚀

---

*Développé avec ❤️ pour Théo Collin*
*Propulsé par Gemini Pro AI 🤖*
