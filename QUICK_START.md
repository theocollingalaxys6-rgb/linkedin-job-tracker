# 🚀 GUIDE RAPIDE - Démarrage en 5 étapes

## Ce que vous allez créer

Un système qui :
- Scanne LinkedIn automatiquement 2x/jour
- Analyse chaque offre avec l'IA Gemini
- Vous donne un score /10 et des recommandations
- Génère un beau dashboard HTML
- Tourne tout seul sans intervention

## Les 5 étapes (15 minutes chrono)

### 1️⃣ Obtenez votre clé API Gemini (GRATUITE)

👉 https://aistudio.google.com/app/apikey

- Cliquez "Create API Key"
- Copiez la clé (commence par AIzaSy...)
- GARDEZ-LA SECRÈTE

### 2️⃣ Créez un repo GitHub

👉 https://github.com/new

- Nom : `linkedin-job-tracker`
- Privé ou Public (au choix)
- Cochez "Add README"
- Créez

### 3️⃣ Uploadez les fichiers

Deux options :

**Option A - Interface web (recommandé si débutant)**
1. Dans votre nouveau repo → "Add file" → "Upload files"
2. Glissez TOUS les fichiers de ce dossier
3. Commit

**Option B - Ligne de commande**
```bash
git clone https://github.com/VOTRE_USERNAME/linkedin-job-tracker.git
cd linkedin-job-tracker
# Copiez tous les fichiers ici
git add .
git commit -m "Initial setup"
git push
```

### 4️⃣ Ajoutez votre clé API

Dans votre repo GitHub :
1. **Settings** (en haut)
2. **Secrets and variables** → **Actions**
3. **New repository secret**
4. Name : `GEMINI_API_KEY`
5. Secret : VOTRE_CLÉ_API
6. Add secret

### 5️⃣ Lancez !

1. Onglet **Actions**
2. "I understand, enable them" (si affiché)
3. **LinkedIn Job Tracker** (menu gauche)
4. **Run workflow** → **Run workflow**
5. Attendez 2-3 minutes ⏱️

## ✅ C'est prêt !

**Votre dashboard sera à :**
`https://VOTRE_USERNAME.github.io/linkedin-job-tracker/`

(Activez GitHub Pages : Settings → Pages → Branch: main → Save)

## 🎯 Que faire ensuite ?

1. **Personnalisez** `config.json` avec VOS critères
2. **Consultez** votre dashboard chaque matin
3. **Postulez** aux offres avec score ≥8/10

## ⚡ Astuces

- Le script tourne **automatiquement** à 8h et 18h
- Vous pouvez le **lancer manuellement** quand vous voulez
- Les offres sont **déduplicatées** automatiquement
- Modifiez `config.json` pour affiner les résultats

## 🆘 Besoin d'aide ?

Lisez le **README.md** complet pour plus de détails !

---

**Temps estimé : 15 minutes**
**Coût : 0€ (100% gratuit)**
**Niveau : Débutant OK**
