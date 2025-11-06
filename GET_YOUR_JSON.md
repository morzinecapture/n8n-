# 🎯 Obtenez votre JSON Multi-Tenant en 2 MINUTES

## ⚡ Méthode ULTRA-RAPIDE

### Étape 1 : Télécharger votre workflow actuel

Dans n8n :
1. Ouvrir votre workflow
2. Cliquer sur `⋮` (3 points en haut)
3. **Download** → Sauvegarder sous `mon-workflow.json`

### Étape 2 : Convertir automatiquement

```bash
# Copier le script Python dans le même dossier que votre JSON
python3 auto_convert_multitenant.py mon-workflow.json
```

**Résultat** : Un fichier `mon-workflow_MULTITENANT.json` est créé automatiquement

### Étape 3 : Importer dans n8n

1. Dans n8n : **New Workflow**
2. Cliquer sur `⋮` → **Import from File**
3. Sélectionner `mon-workflow_MULTITENANT.json`
4. ✅ **C'est prêt !**

---

## 🔧 Ce que le script fait pour vous

✅ Ajoute le nœud **Global Error Handler**
✅ Modifie **TOUS** les filtres Airtable pour isoler par restaurant
✅ Ajoute le champ **Restaurant** à toutes les créations
✅ Connecte tout automatiquement

**Temps total** : 2 minutes

---

## 📋 Prérequis avant d'utiliser le JSON

### Dans Airtable (OBLIGATOIRE)

1. **Créer la table "Restaurants"** (si pas déjà fait)
   - Champs : Nom Restaurant, API Key, Actif

2. **Ajouter le champ "Restaurant"** à ces tables :
   - Employés
   - Planning Optimisé
   - Heures des employés

3. **Créer un restaurant de test**
   ```
   Nom: Restaurant Test
   API Key: test_restaurant_2025_abc123
   Actif: ✓
   ```

4. **Lier vos données existantes**
   - Ouvrir table Employés
   - Sélectionner tous les employés
   - Bulk edit : Restaurant → Restaurant Test

---

## 🧪 Tester le workflow

```bash
curl -X POST https://votre-webhook-url \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_restaurant_2025_abc123" \
  -d '{"message": "test"}'
```

**Résultat attendu** :
```json
{
  "success": true,
  "data": {...}
}
```

---

## ❓ Problèmes courants

### "Python not found"

```bash
# Installer Python
sudo apt install python3  # Linux
brew install python3       # Mac
```

### "Global Error Handler manquant"

Le script l'ajoute automatiquement. Si erreur, vérifier que le nœud "Extract Restaurant ID" existe dans votre JSON.

### "Filtres ne fonctionnent pas"

Vérifier dans Airtable que :
- La colonne "Restaurant" existe
- Les données sont liées à un restaurant

---

## 🎁 Alternative : JSON Minimal

Si vous voulez juste **tester** sans tout modifier, voici un workflow minimal fonctionnel :

**Télécharger** : `workflow-minimal-multitenant.json` (dans ce repo)

**Importer** dans n8n et tester avec :
```bash
curl -X POST https://webhook-url \
  -H "x-api-key: test_restaurant_2025_abc123" \
  -d '{"message": "planning"}'
```

---

## 📚 Fichiers disponibles

| Fichier | Description | Usage |
|---------|-------------|-------|
| **auto_convert_multitenant.py** | Script de conversion | Convertir votre JSON |
| **workflow-minimal-multitenant.json** | Workflow test | Tester rapidement |
| **COPY_PASTE_MODIFICATIONS.md** | Modifications manuelles | Si vous préférez modifier à la main |

---

## 🚀 Vous voulez le JSON COMPLET modifié ?

### Option A : Vous me l'envoyez

1. Télécharger votre workflow JSON depuis n8n
2. Me l'envoyer
3. Je vous renvoie la version multi-tenant modifiée

### Option B : Vous le créez vous-même

```bash
# 1. Télécharger votre workflow
# 2. Exécuter
python3 auto_convert_multitenant.py votre-workflow.json

# 3. Résultat dans votre-workflow_MULTITENANT.json
```

---

**⏱️ Temps total** : 2-5 minutes
**✅ Prêt pour la production** : Oui, après tests
