# ✂️ Modifications Copy-Paste pour votre Workflow

> **Pour les ultra-pressés** : Modifications exactes à faire dans l'éditeur JSON n8n

---

## 🎯 Méthode rapide (10 minutes)

### Étape 1 : Ouvrir l'éditeur JSON dans n8n

1. Ouvrir votre workflow dans n8n
2. Cliquer sur les 3 points `⋮` → **Download**
3. Vous avez maintenant votre fichier JSON

---

## ✂️ MODIFICATIONS À FAIRE

### Modification 1 : Ajouter le nœud "Global Error Handler"

Dans votre JSON, **après** le nœud `"Extract Restaurant ID"`, ajouter :

```json
{
  "parameters": {
    "jsCode": "const input = $input.first().json;\nconst restaurantId = input.restaurant_id;\nconst restaurantName = input.restaurant_name || '';\n\nif (!restaurantId) {\n  console.error('❌ Restaurant ID manquant');\n  throw new Error('Restaurant non identifié');\n}\n\nconst globalContext = {\n  restaurant_id: restaurantId,\n  restaurant_name: restaurantName,\n  originalRequest: input.originalBody || {},\n  originalHeaders: input.originalHeaders || {},\n  chatInput: input.chatInput || '',\n  timestamp: new Date().toISOString(),\n  requestId: `${restaurantId}_${Date.now()}`\n};\n\nconsole.log(`✅ [${restaurantName}] Contexte initialisé`);\n\nreturn [{ json: globalContext }];"
  },
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [528, 1360],
  "id": "global-error-handler-NEW",
  "name": "Global Error Handler"
}
```

---

### Modification 2 : Modifier TOUS les nœuds Airtable "search"

Chercher tous les nœuds avec `"type": "n8n-nodes-base.airtable"` et `"operation": "search"`

**REMPLACER** :
```json
"filterByFormula": "="
```

**PAR** :
```json
"filterByFormula": "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

**Exemple complet pour "get employes"** :

```json
{
  "parameters": {
    "operation": "search",
    "base": { "__rl": true, "value": "app4f09d4qu9atKpR", "mode": "list" },
    "table": { "__rl": true, "value": "tblNYFxq1SoepyjAh", "mode": "list" },
    "filterByFormula": "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'",
    "returnAll": false,
    "options": {
      "fields": ["Nom", "Rôle", "E-mail", "Restaurant"]
    }
  },
  "type": "n8n-nodes-base.airtable",
  "name": "get employes"
}
```

---

### Modification 3 : Ajouter Restaurant aux créations Airtable

Chercher tous les nœuds avec `"operation": "create"`

**AJOUTER** dans `columns.value` :

```json
"Restaurant": "={{ [$('Global Error Handler').item.json.restaurant_id] }}"
```

**Exemple complet pour "Create a record" (Planning)** :

```json
{
  "parameters": {
    "operation": "create",
    "columns": {
      "mappingMode": "defineBelow",
      "value": {
        "Date": "={{ $json.Date }}",
        "Service": "={{ $json.Service }}",
        "Employes": "={{ $json.Employes }}",
        "Restaurant": "={{ [$('Global Error Handler').item.json.restaurant_id] }}",
        "Statut": "Planifié"
      }
    }
  },
  "name": "Create a record"
}
```

---

### Modification 4 : Connecter Global Error Handler

Dans la section `"connections"`, **REMPLACER** :

```json
"Extract Restaurant ID": {
  "main": [[{"node": "Switch", "type": "main", "index": 0}]]
}
```

**PAR** :

```json
"Extract Restaurant ID": {
  "main": [[{"node": "Global Error Handler", "type": "main", "index": 0}]]
},
"Global Error Handler": {
  "main": [[{"node": "Switch", "type": "main", "index": 0}]]
}
```

---

## 🔍 Liste COMPLÈTE des nœuds à modifier

### ✅ Nœuds Airtable Search à filtrer

Chercher et modifier ces noms de nœuds :

1. **"get employes"** → Ajouter filtre Restaurant
2. **"Search records"** (Employés) → Ajouter `AND({Restaurant} = '...')`
3. **"Search records1"** (Hebdo) → Ajouter `AND({Restaurant} = '...')`
4. **"Search records2"** (Hebdo Employé) → Ajouter `AND({Restaurant} = '...')`
5. **"Search records3"** (Dashboard RH) → Ajouter `AND({Restaurant} = '...')`
6. **"Get Photo Airtable"** → Ajouter filtre Restaurant
7. **"Récupérer Tous Employés"** → Ajouter filtre Restaurant

### ✅ Nœuds Airtable Create à enrichir

Ajouter le champ Restaurant à :

1. **"Create a record"** (Planning Optimisé)
2. **"Create a record1"** (Heures des employés)
3. **"Create a record2"** (Hebdo Employé)
4. **"Create a record3"** (Dashboard RH)

---

## 📝 Template de remplacement pour Search

Pour **TOUS** les `filterByFormula` qui n'ont pas encore de filtre :

```json
"filterByFormula": "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

Pour ceux qui ont **DÉJÀ** un filtre (exemple avec RID Employé) :

```json
"filterByFormula": "=AND({RID Employé} = '{{ $json.employee_id }}', {Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}')"
```

---

## 🚀 Méthode automatisée (RECOMMANDÉ)

Au lieu de modifier manuellement, utilisez ce script Python :

```python
#!/usr/bin/env python3
import json
import sys

def add_restaurant_filter(workflow_json):
    """Ajoute automatiquement les filtres restaurant"""

    # Ajouter Global Error Handler si absent
    has_global_handler = any(
        node.get('name') == 'Global Error Handler'
        for node in workflow_json.get('nodes', [])
    )

    if not has_global_handler:
        print("❌ Global Error Handler manquant - ajoutez-le d'abord")
        return workflow_json

    # Modifier tous les nœuds Airtable
    for node in workflow_json.get('nodes', []):
        if node.get('type') != 'n8n-nodes-base.airtable':
            continue

        params = node.get('parameters', {})

        # Modifier les SEARCH
        if params.get('operation') == 'search':
            formula = params.get('filterByFormula', '=')

            # Si pas de filtre restaurant déjà
            if '{Restaurant}' not in formula:
                if formula == '=':
                    # Remplacer le filtre vide
                    params['filterByFormula'] = "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
                else:
                    # Ajouter AND au filtre existant
                    params['filterByFormula'] = f"=AND({formula[1:]}, {{Restaurant}} = '{{{{ $('Global Error Handler').item.json.restaurant_id }}}}')"

                print(f"✅ Filtre ajouté au nœud: {node.get('name')}")

        # Modifier les CREATE
        elif params.get('operation') == 'create':
            columns = params.get('columns', {})
            value = columns.get('value', {})

            # Ajouter Restaurant si absent
            if 'Restaurant' not in value:
                value['Restaurant'] = "={{ [$('Global Error Handler').item.json.restaurant_id] }}"
                print(f"✅ Restaurant ajouté à la création: {node.get('name')}")

    return workflow_json

# Utilisation
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 add_multitenant.py workflow.json")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        workflow = json.load(f)

    modified = add_restaurant_filter(workflow)

    output_file = sys.argv[1].replace('.json', '_MODIFIED.json')
    with open(output_file, 'w') as f:
        json.dump(modified, f, indent=2)

    print(f"\n✅ Fichier modifié créé: {output_file}")
    print("Importez-le dans n8n !")
```

**Utilisation** :

```bash
# Télécharger votre workflow depuis n8n (format JSON)
# Puis exécuter :
python3 add_multitenant.py votre-workflow.json

# Importer votre-workflow_MODIFIED.json dans n8n
```

---

## ⚡ Méthode ULTRA-RAPIDE (5 minutes)

### Utiliser la recherche/remplacement dans VSCode

1. Télécharger votre workflow JSON
2. Ouvrir dans VSCode
3. Rechercher/Remplacer (Ctrl+H) :

**Remplacement 1 : Filtres vides**
- Chercher : `"filterByFormula": "="`
- Remplacer par : `"filterByFormula": "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"`

**Remplacement 2 : Ajouter aux colonnes**
- Chercher : `"value": {` (dans les nœuds create)
- Remplacer manuellement en ajoutant `"Restaurant": "={{ [$('Global Error Handler').item.json.restaurant_id] }}",`

4. Sauvegarder et importer dans n8n

---

## 🎯 Checklist finale

Avant de réimporter dans n8n :

- [ ] Nœud "Global Error Handler" ajouté
- [ ] Tous les Search Airtable ont un filtre {Restaurant}
- [ ] Tous les Create Airtable ont le champ Restaurant
- [ ] Connexions mises à jour (Extract → Global → Switch)
- [ ] JSON valide (tester avec jsonlint.com)

---

## 📞 Besoin d'aide ?

Si vous préférez que je fasse les modifications pour vous :

1. Téléchargez votre workflow JSON depuis n8n
2. Envoyez-le moi
3. Je vous renvoie la version modifiée prête à importer

---

**Temps estimé** : 5-10 minutes avec la méthode automatisée
