# ⚡ Guide de Démarrage Rapide

> **Pour les pressés** : Ce guide vous permet de démarrer en 30 minutes (version minimale)

---

## 🎯 Objectif

Transformer votre workflow n8n mono-tenant en système multi-tenant sécurisé.

**Temps estimé** : 30 min à 2h selon votre niveau

---

## 🚀 EN 3 ÉTAPES

### ÉTAPE 1 : Airtable (10 minutes)

#### 1.1 Créer table "API Logs"

Dans Airtable, créer une nouvelle table avec ces champs :

```
API Logs
├─ ID (Autonumber)
├─ Restaurant (Link to Restaurants)
├─ Timestamp (Date avec heure)
├─ Type (Single select: INFO, ERROR, WARNING, SUCCESS)
├─ Endpoint (Text)
├─ Message (Long text)
└─ Duration (Number)
```

#### 1.2 Ajouter champ "Restaurant" partout

Dans ces tables, ajouter un champ :
- Type : Link to Restaurants
- Nom : Restaurant

Tables concernées :
- ✅ Employés
- ✅ Planning Optimisé
- ✅ Heures des employés

#### 1.3 Créer un restaurant de test

Dans table "Restaurants" :
```
Nom : Restaurant Test
API Key : test_restaurant_2025_abc123
Actif : ✓
```

✅ **Airtable prêt**

---

### ÉTAPE 2 : Workflow n8n (15 minutes)

#### 2.1 Ajouter "Global Error Handler"

Après le nœud "Extraire Restaurant ID", ajouter un nœud **Code** :

**Nom** : Global Error Handler

**Code** :
```javascript
const restaurantId = $json.restaurant_id;

if (!restaurantId) {
  throw new Error('Restaurant non identifié');
}

return [{
  json: {
    restaurant_id: restaurantId,
    restaurant_name: $json.restaurant_name,
    chatInput: $json.chatInput,
    timestamp: new Date().toISOString(),
    requestId: `${restaurantId}_${Date.now()}`
  }
}];
```

#### 2.2 Modifier UN filtre Airtable (exemple)

Dans le nœud **"get employes"** :

**Avant** :
```
filterByFormula: "="
```

**Après** :
```javascript
"={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

#### 2.3 Ajouter Restaurant aux créations

Dans **"Create a record"** (Planning), ajouter dans le mapping :

```javascript
"Restaurant": "={{ [$('Global Error Handler').item.json.restaurant_id] }}"
```

✅ **Workflow modifié**

---

### ÉTAPE 3 : Test (5 minutes)

#### Test 1 : Requête de test

```bash
curl -X POST https://votre-webhook-url \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_restaurant_2025_abc123" \
  -d '{"message": "liste des employés"}'
```

**Résultat attendu** :
```json
{
  "success": true,
  "data": { ... }
}
```

#### Test 2 : Vérifier dans Airtable

1. Ouvrir table "Employés"
2. Filtrer par Restaurant = "Restaurant Test"
3. Vérifier que vous voyez seulement les employés liés

✅ **Système fonctionnel !**

---

## ⚠️ VERSION MINIMALE vs COMPLÈTE

### Ce que vous avez maintenant (version minimale)

- ✅ Contexte global avec restaurant_id
- ✅ Un filtre Airtable de test
- ✅ Une création avec restaurant_id
- ⚠️ Pas de gestion d'erreurs complète
- ⚠️ Pas de logs
- ⚠️ Tous les filtres ne sont pas modifiés

### Pour aller vers la version complète

Suivez le guide complet : **MIGRATION_GUIDE.md**

---

## 📚 Prochaines étapes

1. **Copier tous les filtres Airtable**
   - Voir `node-codes-ready-to-use.md` section 2
   - Modifier tous les nœuds Airtable

2. **Ajouter la gestion d'erreurs**
   - Voir `node-codes-ready-to-use.md` section 5
   - Ajouter Error Trigger

3. **Activer les logs**
   - Voir `node-codes-ready-to-use.md` section 4
   - Connecter à Airtable

4. **Tester complètement**
   - Utiliser `test-scripts.md`
   - Valider l'isolation

---

## 🎓 Pour en savoir plus

| Document | Quand l'utiliser |
|----------|------------------|
| **README.md** | Vue d'ensemble complète |
| **MIGRATION_GUIDE.md** | Migration complète étape par étape |
| **node-codes-ready-to-use.md** | Codes à copier-coller |
| **test-scripts.md** | Tests complets |
| **DEPLOYMENT_CHECKLIST.md** | Checklist de déploiement |

---

## ❓ FAQ Rapide

**Q : Dois-je vraiment modifier TOUS les nœuds Airtable ?**
A : Oui, pour garantir l'isolation complète. Mais vous pouvez commencer par les principaux.

**Q : Que se passe-t-il si j'oublie un filtre ?**
A : Risque de fuite de données entre restaurants. Testez bien l'isolation.

**Q : Puis-je utiliser en production après ce quick start ?**
A : Non, complétez d'abord avec MIGRATION_GUIDE.md pour avoir tous les garde-fous.

---

## 🚨 Aide rapide

**Erreur "Restaurant ID manquant"** :
→ Vérifier que l'API Key existe dans Airtable

**Données d'autres restaurants visibles** :
→ Vérifier que le filtre Airtable est bien ajouté

**Rien ne fonctionne** :
→ Vérifier que "Global Error Handler" est bien connecté

---

**⏱️ Temps total** : 30 minutes pour version minimale
**📈 Prochaine étape** : Lire MIGRATION_GUIDE.md pour version complète

**🎉 Vous avez un système multi-tenant fonctionnel !**
