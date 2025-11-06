# 🚀 Guide de Migration Multi-Tenant

## Vue d'ensemble

Ce guide vous aide à transformer votre workflow n8n en système multi-tenant complet avec gestion d'erreurs robuste.

---

## 📊 Modifications Airtable Requises

### 1. Table "API Logs" (NOUVELLE)

Créez cette table pour tracker toutes les opérations :

```
Nom de la table : API Logs

Champs :
- ID (Autonumber)
- Restaurant (Link to Restaurants) - REQUIRED
- Timestamp (Date avec heure)
- Type (Single select: INFO, ERROR, WARNING, SUCCESS)
- Endpoint (Single line text)
- Message (Long text)
- Request Data (Long text)
- Response Data (Long text)
- Error Stack (Long text)
- Duration (Number - en ms)
- User Agent (Single line text)
```

### 2. Modifications des tables existantes

Ajoutez un champ **"Restaurant"** (Link to Restaurants) à :
- ✅ Employés
- ✅ Planning Optimisé
- ✅ Heures des employés
- ✅ Hebdo Employé
- ✅ Dashboard RH

---

## 🔧 Modifications du Workflow n8n

### Étape 1 : Ajouter les nœuds de base

#### 1.1 Nœud "Global Error Handler" (Code)

**Position** : Après "Extraire Restaurant ID"

```javascript
// Code du nœud "Global Error Handler"
const restaurantId = $json.restaurant_id;

if (!restaurantId) {
  return [{
    json: {
      success: false,
      error: {
        type: 'AUTH_ERROR',
        message: 'Restaurant non identifié',
        code: 'MISSING_RESTAURANT_ID'
      },
      timestamp: new Date().toISOString()
    }
  }];
}

// Créer un contexte global
return [{
  json: {
    restaurant_id: restaurantId,
    restaurant_name: $json.restaurant_name,
    originalRequest: $json.originalBody,
    chatInput: $json.chatInput,
    timestamp: new Date().toISOString(),
    requestId: `${restaurantId}_${Date.now()}`
  }
}];
```

#### 1.2 Nœud "Log to Airtable" (Airtable Create)

**Configuration** :
- Operation: Create
- Table: API Logs
- Mapping:
  ```
  Restaurant: ={{ [$json.restaurant_id] }}
  Timestamp: ={{ $json.timestamp }}
  Type: ={{ $json.logType }}
  Endpoint: ={{ $json.endpoint }}
  Message: ={{ $json.message }}
  Request Data: ={{ $json.requestData }}
  Response Data: ={{ $json.responseData }}
  Error Stack: ={{ $json.errorStack }}
  Duration: ={{ $json.duration }}
  ```

---

### Étape 2 : Modifier les nœuds Airtable existants

#### 2.1 Nœud "get employes" (ligne 260)

**AVANT** :
```javascript
filterByFormula: "="
```

**APRÈS** :
```javascript
filterByFormula: "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

#### 2.2 Nœud "Search records" (ligne 528)

**AVANT** :
```javascript
filterByFormula: "={RID Employé} = '{{ $json.employee_id }}'"
```

**APRÈS** :
```javascript
filterByFormula: "=AND({RID Employé} = '{{ $json.employee_id }}', {Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}')"
```

#### 2.3 Nœud "Create a record" (Planning - ligne 345)

Ajouter dans les colonnes mappées :
```javascript
"Restaurant": "={{ [$('Global Error Handler').item.json.restaurant_id] }}"
```

#### 2.4 Nœud "Create a record1" (Heures - ligne 589)

Ajouter dans les colonnes mappées :
```javascript
"Restaurant": "={{ [$('Global Error Handler').item.json.restaurant_id] }}"
```

---

### Étape 3 : Ajouter la gestion d'erreurs par opération

#### 3.1 Wrapper pour "get employes"

Insérer un nœud Code **AVANT** "get employes" :

```javascript
// Nœud: "Validate Get Employees Request"
const restaurantId = $('Global Error Handler').item.json.restaurant_id;

if (!restaurantId) {
  throw new Error('Restaurant ID manquant pour la récupération des employés');
}

console.log(`[${restaurantId}] Récupération des employés`);

return [{
  json: {
    restaurant_id: restaurantId,
    operation: 'get_employees',
    timestamp: new Date().toISOString()
  }
}];
```

Insérer un nœud Code **APRÈS** "get employes" :

```javascript
// Nœud: "Handle Get Employees Result"
const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const employees = $input.all();

console.log(`[${restaurantId}] ${employees.length} employés trouvés`);

// Préparer le log
const logData = {
  restaurant_id: restaurantId,
  logType: 'SUCCESS',
  endpoint: 'get_employees',
  message: `${employees.length} employés récupérés`,
  requestData: JSON.stringify({ restaurant_id: restaurantId }),
  responseData: JSON.stringify({ count: employees.length }),
  timestamp: new Date().toISOString(),
  duration: 0 // Calculer si nécessaire
};

// Envoyer le log (via un nœud Airtable séparé)
return employees.map(emp => ({
  json: {
    ...emp.json,
    _log: logData
  }
}));
```

#### 3.2 Wrapper pour "Create a record" (Planning)

Insérer un nœud Code **AVANT** :

```javascript
// Nœud: "Validate Create Planning Request"
const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const planningData = $input.all();

if (!restaurantId) {
  throw new Error('Restaurant ID manquant pour la création du planning');
}

if (!planningData || planningData.length === 0) {
  throw new Error('Aucune donnée de planning à créer');
}

console.log(`[${restaurantId}] Création de ${planningData.length} entrées de planning`);

// Ajouter le restaurant_id à chaque entrée
return planningData.map(entry => ({
  json: {
    ...entry.json,
    Restaurant: [restaurantId]
  }
}));
```

Insérer un nœud Code **APRÈS** :

```javascript
// Nœud: "Handle Create Planning Result"
const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const createdRecords = $input.all();

console.log(`[${restaurantId}] ${createdRecords.length} entrées de planning créées`);

// Log de succès
const logData = {
  restaurant_id: restaurantId,
  logType: 'SUCCESS',
  endpoint: 'create_planning',
  message: `${createdRecords.length} entrées de planning créées avec succès`,
  responseData: JSON.stringify({
    count: createdRecords.length,
    ids: createdRecords.map(r => r.json.id)
  }),
  timestamp: new Date().toISOString(),
  duration: 0
};

return [{
  json: {
    success: true,
    count: createdRecords.length,
    records: createdRecords,
    _log: logData
  }
}];
```

---

### Étape 4 : Centraliser la gestion d'erreurs

#### 4.1 Créer un nœud "Error Trigger" global

Ajouter un nœud **Error Trigger** au workflow :

```
Type: Error Trigger
Conditions: Capture toutes les erreurs
```

Connecter à un nœud Code "Format Error Response" :

```javascript
// Nœud: "Format Error Response"
const error = $input.first().json.error;
const restaurantId = $('Global Error Handler')?.item?.json?.restaurant_id || 'unknown';

// Catégoriser l'erreur
let errorType = 'UNKNOWN_ERROR';
let errorMessage = error.message || 'Une erreur inconnue s\'est produite';

if (errorMessage.includes('Airtable') || errorMessage.includes('API')) {
  errorType = 'API_ERROR';
} else if (errorMessage.includes('Restaurant ID')) {
  errorType = 'AUTH_ERROR';
} else if (errorMessage.includes('validation') || errorMessage.includes('invalid')) {
  errorType = 'VALIDATION_ERROR';
}

// Formater la réponse
const errorResponse = {
  success: false,
  error: {
    type: errorType,
    message: errorMessage,
    code: error.code || 'ERR_UNKNOWN',
    timestamp: new Date().toISOString()
  },
  restaurantId: restaurantId
};

// Préparer le log
const logData = {
  restaurant_id: restaurantId,
  logType: 'ERROR',
  endpoint: $node?.name || 'unknown',
  message: errorMessage,
  errorStack: error.stack || '',
  timestamp: new Date().toISOString(),
  duration: 0
};

console.error(`[${restaurantId}] ERREUR:`, errorMessage);

return [{
  json: {
    ...errorResponse,
    _log: logData
  }
}];
```

Connecter à deux branches :
1. **Log to Airtable** (pour logger l'erreur)
2. **Respond to Webhook** (pour retourner l'erreur au client)

---

### Étape 5 : Standardiser les réponses Webhook

#### 5.1 Créer un nœud "Format Success Response"

Avant chaque **Respond to Webhook**, insérer :

```javascript
// Nœud: "Format Success Response"
const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const data = $input.first().json;

return [{
  json: {
    success: true,
    data: data,
    restaurantId: restaurantId,
    timestamp: new Date().toISOString(),
    requestId: $('Global Error Handler').item.json.requestId
  }
}];
```

---

## 📈 Monitoring et Logs

### Dashboard Airtable recommandé

Créez une vue dans "API Logs" :

**Vue "Dernières erreurs"** :
- Filtre: Type = ERROR
- Tri: Timestamp (décroissant)
- Grouper par: Restaurant

**Vue "Performance par restaurant"** :
- Grouper par: Restaurant
- Résumé: COUNT(ID), AVG(Duration)

### Alertes automatiques

Vous pouvez ajouter un nœud après "Log to Airtable" pour envoyer des alertes :

```javascript
// Nœud: "Check Critical Errors"
const log = $json;

if (log.logType === 'ERROR') {
  const errorCount = /* récupérer le nombre d'erreurs récentes */;

  if (errorCount > 10) {
    // Envoyer une alerte email
    return [{
      json: {
        alert: true,
        restaurantId: log.restaurant_id,
        message: `${errorCount} erreurs détectées`
      }
    }];
  }
}

return [];
```

---

## 🧪 Tests de validation

### Test 1 : API Key invalide

```bash
curl -X POST https://votre-webhook-url \
  -H "Content-Type: application/json" \
  -H "x-api-key: invalid_key" \
  -d '{"message": "test"}'
```

**Réponse attendue** :
```json
{
  "success": false,
  "error": {
    "type": "AUTH_ERROR",
    "message": "Restaurant non identifié",
    "code": "MISSING_RESTAURANT_ID"
  },
  "timestamp": "2025-01-XX..."
}
```

### Test 2 : Requête valide

```bash
curl -X POST https://votre-webhook-url \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -d '{
    "type": "conversation",
    "message": "planning de la semaine"
  }'
```

**Vérifications** :
- ✅ Réponse success: true
- ✅ Log créé dans "API Logs"
- ✅ Données filtrées par restaurant

---

## 🔒 Sécurité Multi-Tenant

### Checklist de sécurité

- [ ] Tous les nœuds Airtable filtrent par Restaurant
- [ ] L'API key est validée en premier
- [ ] Le restaurant_id est propagé partout
- [ ] Les logs ne contiennent pas de données sensibles
- [ ] Les erreurs ne révèlent pas de détails techniques en production

---

## 📝 Checklist de migration

### Phase 1 : Préparation
- [ ] Créer la table "API Logs" dans Airtable
- [ ] Ajouter le champ "Restaurant" aux tables existantes
- [ ] Lier manuellement les données existantes à leur restaurant
- [ ] Tester l'accès API à la nouvelle table

### Phase 2 : Modification du workflow
- [ ] Ajouter le nœud "Global Error Handler"
- [ ] Modifier "get employes" avec filtre restaurant
- [ ] Modifier "Search records" avec filtre restaurant
- [ ] Ajouter restaurant_id à "Create a record"
- [ ] Ajouter restaurant_id à "Create a record1"
- [ ] Ajouter les wrappers de validation

### Phase 3 : Gestion d'erreurs
- [ ] Ajouter Error Trigger global
- [ ] Créer "Format Error Response"
- [ ] Connecter "Log to Airtable" pour les erreurs
- [ ] Standardiser toutes les réponses webhook

### Phase 4 : Tests
- [ ] Tester avec API key valide
- [ ] Tester avec API key invalide
- [ ] Tester avec 2 restaurants différents
- [ ] Vérifier l'isolation des données
- [ ] Vérifier les logs dans Airtable

### Phase 5 : Production
- [ ] Activer le workflow en production
- [ ] Monitorer les logs pendant 24h
- [ ] Configurer les alertes d'erreur
- [ ] Documenter pour l'équipe

---

## 🆘 Dépannage

### Problème : "Restaurant ID manquant"

**Cause** : Le nœud "Extraire Restaurant ID" n'est pas connecté correctement

**Solution** :
1. Vérifier que "Search records4" retourne bien un résultat
2. Vérifier que l'API key dans Airtable correspond
3. Vérifier le code de "Extraire Restaurant ID"

### Problème : Données d'un autre restaurant visibles

**Cause** : Un filtre Airtable manque le restaurant_id

**Solution** :
1. Vérifier TOUS les nœuds Airtable
2. S'assurer que la formule contient `{Restaurant} = '...'`
3. Tester avec 2 restaurants différents

### Problème : Logs non créés

**Cause** : Connexion au nœud "Log to Airtable" manquante

**Solution** :
1. Vérifier que le nœud existe
2. Vérifier les credentials Airtable
3. Tester manuellement le nœud

---

## 📚 Ressources

- [Documentation n8n Error Handling](https://docs.n8n.io/workflows/error-workflows/)
- [Airtable API Reference](https://airtable.com/developers/web/api/introduction)
- Fichier de code : `/multi-tenant-error-handler.js`

---

**Version** : 1.0
**Dernière mise à jour** : 2025-01-XX
