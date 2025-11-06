# 🎯 COMMENCEZ ICI - JSON Multi-Tenant

> **Ce que vous cherchez** : Un workflow n8n prêt à copier-coller

---

## ⚡ 2 OPTIONS SELON VOS BESOINS

### Option 1 : TEST RAPIDE (2 minutes)

**Pour** : Tester le système multi-tenant rapidement

**Fichier** : `workflow-minimal-test.json`

**Action** :
```bash
# 1. Dans n8n : Import from File
# 2. Sélectionner workflow-minimal-test.json
# 3. Activer le workflow
# 4. Tester :

curl -X POST https://votre-n8n-url/webhook/test-multitenant \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_restaurant_2025_abc123" \
  -d '{"message": "test"}'
```

**Résultat** : Liste des employés du restaurant

---

### Option 2 : VOTRE WORKFLOW COMPLET (5 minutes)

**Pour** : Convertir votre workflow actuel en multi-tenant

**Outil** : `auto_convert_multitenant.py`

**Actions** :

#### 1. Télécharger votre workflow actuel
```
Dans n8n → Votre workflow → ⋮ → Download → mon-workflow.json
```

#### 2. Convertir automatiquement
```bash
python3 auto_convert_multitenant.py mon-workflow.json
```

#### 3. Résultat
```
✅ mon-workflow_MULTITENANT.json créé
```

#### 4. Importer dans n8n
```
Dans n8n → New → Import from File → mon-workflow_MULTITENANT.json
```

---

## 📋 Ce que le script fait

✅ **Ajoute** le nœud Global Error Handler
✅ **Modifie** tous les filtres Airtable (ajoute filtre par Restaurant)
✅ **Ajoute** le champ Restaurant à toutes les créations
✅ **Connecte** tout automatiquement

**Temps** : 30 secondes d'exécution

---

## ⚙️ Prérequis Airtable

**AVANT** d'utiliser le JSON, dans Airtable :

### 1. Vérifier table "Restaurants"
```
Champs requis :
- Nom Restaurant (texte)
- API Key (texte)
- Actif (checkbox)
```

### 2. Ajouter champ "Restaurant" à :
- Table Employés
- Table Planning Optimisé
- Table Heures des employés

Type : **Link to Restaurants**

### 3. Créer un restaurant de test
```
Nom Restaurant: Restaurant Test
API Key: test_restaurant_2025_abc123
Actif: ✓
```

### 4. Lier vos données existantes
```
Table Employés → Sélectionner tous → Bulk edit Restaurant → Restaurant Test
```

---

## 🧪 Tester

```bash
# Avec API Key valide
curl -X POST https://webhook-url \
  -H "x-api-key: test_restaurant_2025_abc123" \
  -d '{"message": "liste des employés"}'

# Résultat attendu
{
  "success": true,
  "data": {
    "employees": [...]
  }
}
```

```bash
# Avec API Key invalide
curl -X POST https://webhook-url \
  -H "x-api-key: MAUVAISE_KEY" \
  -d '{"message": "test"}'

# Résultat attendu
{
  "success": false,
  "error": "API Key invalide"
}
```

---

## 📁 Fichiers disponibles

| Fichier | Usage | Durée |
|---------|-------|-------|
| **workflow-minimal-test.json** | Tester rapidement | 2 min |
| **auto_convert_multitenant.py** | Convertir votre workflow | 5 min |
| **GET_YOUR_JSON.md** | Guide détaillé conversion | Lecture |
| **MIGRATION_GUIDE.md** | Guide complet migration | 1h |

---

## ❓ Quelle option choisir ?

### Vous voulez juste **TESTER** ?
→ `workflow-minimal-test.json`

### Vous voulez **CONVERTIR** votre workflow ?
→ `auto_convert_multitenant.py votre-workflow.json`

### Vous voulez **COMPRENDRE** avant ?
→ `README.md` puis `MIGRATION_GUIDE.md`

---

## 🆘 Problèmes ?

### "Python not found"
```bash
# Installer Python
sudo apt install python3  # Linux
brew install python3       # Mac
# Windows : télécharger sur python.org
```

### "Airtable credentials error"
```
Dans n8n :
1. Credentials → Airtable
2. Vérifier le token
3. Re-tester
```

### "Restaurant ID manquant"
```
Vérifier dans Airtable :
1. Table Restaurants existe
2. API Key est correcte
3. Restaurant est Actif (✓)
```

---

## 🎉 C'est prêt !

**Vous avez maintenant** :
1. ✅ Un workflow de test minimal
2. ✅ Un script de conversion automatique
3. ✅ Une documentation complète

**Prochaine étape** :
```bash
# Tester le workflow minimal
# OU
# Convertir votre workflow complet
python3 auto_convert_multitenant.py votre-workflow.json
```

---

**Version** : 1.0
**Support** : Voir MIGRATION_GUIDE.md section Dépannage
