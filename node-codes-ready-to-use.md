# 📦 Codes Prêts à Utiliser - Multi-Tenant

Ce fichier contient tous les codes à copier-coller dans vos nœuds n8n.

---

## 🔐 SECTION 1 : AUTHENTIFICATION & CONTEXTE

### ✅ Nœud : "Global Error Handler"
**Type** : Code
**Position** : Après "Extraire Restaurant ID"
**Connexions** :
- Input: "Extraire Restaurant ID"
- Output: Vers tous les flux principaux

```javascript
// ============================================
// GLOBAL ERROR HANDLER & CONTEXT MANAGER
// ============================================

const input = $input.first().json;

// Validation du restaurant_id
const restaurantId = input.restaurant_id;
const restaurantName = input.restaurant_name || '';

if (!restaurantId) {
  console.error('❌ Restaurant ID manquant dans le contexte');
  throw new Error('Restaurant non identifié - API Key invalide ou restaurant inactif');
}

// Créer un contexte global réutilisable
const globalContext = {
  // Identité du restaurant
  restaurant_id: restaurantId,
  restaurant_name: restaurantName,

  // Données de la requête
  originalRequest: input.originalBody || {},
  originalHeaders: input.originalHeaders || {},
  chatInput: input.chatInput || '',

  // Métadonnées
  timestamp: new Date().toISOString(),
  requestId: `${restaurantId}_${Date.now()}`,

  // Pour le debugging
  debug: {
    nodeExecuted: 'Global Error Handler',
    executionTime: new Date().toISOString()
  }
};

console.log(`✅ [${restaurantName}] Contexte initialisé - Request ID: ${globalContext.requestId}`);
console.log(`📝 Message utilisateur: "${globalContext.chatInput}"`);

return [{
  json: globalContext
}];
```

---

## 📊 SECTION 2 : FILTRES AIRTABLE PAR RESTAURANT

### ✅ Nœud : "get employes" (MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifications** :
1. Dans `filterByFormula`, remplacer `"="` par :

```javascript
"={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

2. Ajouter dans `options.fields` :
```javascript
["Nom", "Rôle", "E-mail", "Restaurant"]
```

---

### ✅ Nœud : "Search records" (Employés - MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifier** `filterByFormula` :

```javascript
"=AND(
  {RID Employé} = '{{ $json.employee_id }}',
  {Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'
)"
```

---

### ✅ Nœud : "Search records1" (Hebdo - MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifier** `filterByFormula` :

```javascript
"=AND(
  {Semaine ISO} >= '{{ $('Code in JavaScript8').first().json.yearStart }}',
  {Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'
)"
```

---

### ✅ Nœud : "Search records2" (Hebdo Employé - MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifier** `filterByFormula` :

```javascript
"=AND(
  {Clé Employé+Semaine} = \"{{ $json.employeeId }}|{{ $json.weekISO }}\",
  {Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'
)"
```

---

### ✅ Nœud : "Search records3" (Dashboard RH - MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifier** `filterByFormula` :

```javascript
"=AND(
  {Code Semaine} = '{{ $json.codeSemine }}',
  {Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'
)"
```

---

### ✅ Nœud : "Get Photo Airtable" (MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifier** `filterByFormula` :

```javascript
"={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

---

### ✅ Nœud : "Récupérer Tous Employés" (MODIFIÉ)
**Type** : Airtable
**Operation** : Search

**Modifier** `filterByFormula` :

```javascript
"={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
```

---

## 🔨 SECTION 3 : CRÉATION DE DONNÉES

### ✅ Nœud : "Validate Before Create Planning"
**Type** : Code
**Position** : AVANT "Create a record" (Planning)

```javascript
// ============================================
// VALIDATION AVANT CRÉATION PLANNING
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const planningData = $input.all();

// Validation du restaurant
if (!restaurantId) {
  console.error('❌ Restaurant ID manquant pour création planning');
  throw new Error('Impossible de créer le planning : Restaurant non identifié');
}

// Validation des données
if (!planningData || planningData.length === 0) {
  console.error('❌ Aucune donnée de planning à créer');
  throw new Error('Aucune donnée de planning reçue');
}

// Validation de la structure des données
const invalidRecords = planningData.filter(entry => {
  const data = entry.json;
  return !data.Date || !data.Service || !data.Employes;
});

if (invalidRecords.length > 0) {
  console.error(`❌ ${invalidRecords.length} entrées invalides détectées`);
  throw new Error(`${invalidRecords.length} entrées de planning invalides (champs manquants)`);
}

console.log(`✅ [${restaurantId}] Validation OK - ${planningData.length} entrées à créer`);

// Ajouter le restaurant_id à chaque entrée
const enrichedData = planningData.map((entry, index) => {
  return {
    json: {
      ...entry.json,
      Restaurant: [restaurantId], // ← CRUCIAL pour l'isolation
      CreatedBy: 'n8n_automation',
      CreatedAt: new Date().toISOString()
    },
    pairedItem: { item: index }
  };
});

console.log(`📝 [${restaurantId}] ${enrichedData.length} entrées enrichies avec Restaurant ID`);

return enrichedData;
```

---

### ✅ Nœud : "Create a record" (Planning - MODIFIÉ)
**Type** : Airtable
**Operation** : Create

**Ajouter dans** `columns.value` :

```javascript
{
  "Date": "={{ $json.Date }}",
  "Service": "={{ $json.Service }}",
  "Employes": "={{ $json.Employes }}",
  "Restaurant": "={{ $json.Restaurant }}", // ← NOUVEAU
  "Statut": "Planifié"
}
```

---

### ✅ Nœud : "Handle Create Planning Success"
**Type** : Code
**Position** : APRÈS "Create a record" (Planning)

```javascript
// ============================================
// GESTION SUCCÈS CRÉATION PLANNING
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const createdRecords = $input.all();

if (!createdRecords || createdRecords.length === 0) {
  console.warn('⚠️ Aucun enregistrement créé');
  return [{
    json: {
      success: true,
      count: 0,
      message: 'Aucun enregistrement créé',
      restaurantId: restaurantId
    }
  }];
}

const recordIds = createdRecords.map(r => r.json.id).filter(Boolean);

console.log(`✅ [${restaurantId}] ${createdRecords.length} entrées de planning créées`);
console.log(`📋 IDs créés: ${recordIds.slice(0, 3).join(', ')}${recordIds.length > 3 ? '...' : ''}`);

// Préparer les données pour le log
const logData = {
  restaurant_id: restaurantId,
  logType: 'SUCCESS',
  endpoint: 'create_planning',
  message: `${createdRecords.length} entrées de planning créées avec succès`,
  responseData: JSON.stringify({
    count: createdRecords.length,
    ids: recordIds
  }),
  timestamp: new Date().toISOString(),
  duration: 0
};

return [{
  json: {
    success: true,
    count: createdRecords.length,
    records: createdRecords.map(r => r.json),
    _log: logData
  }
}];
```

---

### ✅ Nœud : "Validate Before Create Hours"
**Type** : Code
**Position** : AVANT "Create a record1" (Heures)

```javascript
// ============================================
// VALIDATION AVANT CRÉATION HEURES
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const hourData = $input.first().json;

// Validation du restaurant
if (!restaurantId) {
  console.error('❌ Restaurant ID manquant pour création heures');
  throw new Error('Impossible de créer les heures : Restaurant non identifié');
}

// Validation des données obligatoires
if (!hourData.id) {
  console.error('❌ ID employé manquant');
  throw new Error('ID employé manquant pour la création des heures');
}

const date = $('Code in JavaScript3').item.json.date_service;
const heureDebut = $('Code in JavaScript3').item.json.datetime_debut;
const heureFin = $('Code in JavaScript3').item.json.datetime_fin;

if (!date || !heureDebut || !heureFin) {
  console.error('❌ Données de temps manquantes');
  throw new Error('Date ou heures manquantes');
}

console.log(`✅ [${restaurantId}] Validation OK - Création heures pour employé ${hourData.id}`);

return [{
  json: {
    ...hourData,
    Restaurant: [restaurantId], // ← CRUCIAL
    date_service: date,
    datetime_debut: heureDebut,
    datetime_fin: heureFin
  }
}];
```

---

### ✅ Nœud : "Create a record1" (Heures - MODIFIÉ)
**Type** : Airtable
**Operation** : Create

**Modifier** `columns.value` :

```javascript
{
  "Nom de l'employé": "={{ $json.id }}",
  "Date": "={{ $json.date_service }}",
  "Heure d'arrivée": "={{ $json.datetime_debut }}",
  "Heure de départ": "={{ $json.datetime_fin }}",
  "Restaurant": "={{ $json.Restaurant }}" // ← NOUVEAU
}
```

---

## 📝 SECTION 4 : SYSTÈME DE LOGGING

### ✅ Nœud : "Prepare Log Entry"
**Type** : Code
**Position** : Après chaque opération importante

```javascript
// ============================================
// PRÉPARATION D'UNE ENTRÉE DE LOG
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const operation = $input.first().json;

// Déterminer le type de log
let logType = 'INFO';
let message = '';
let responseData = '';

if (operation._log) {
  // Si le nœud précédent a déjà préparé un log
  logType = operation._log.logType || 'INFO';
  message = operation._log.message || '';
  responseData = operation._log.responseData || '';
} else {
  // Créer un log par défaut
  logType = operation.success ? 'SUCCESS' : 'ERROR';
  message = operation.message || `Opération ${operation.operation || 'inconnue'}`;
  responseData = JSON.stringify(operation);
}

const logEntry = {
  Restaurant: [restaurantId],
  Timestamp: new Date().toISOString(),
  Type: logType,
  Endpoint: operation.operation || $node.name,
  Message: message,
  "Request Data": JSON.stringify($('Global Error Handler').item.json.originalRequest || {}),
  "Response Data": responseData.substring(0, 10000), // Limiter à 10k caractères
  "Error Stack": operation.errorStack || '',
  Duration: operation.duration || 0
};

console.log(`📊 [${restaurantId}] Log préparé: ${logType} - ${message}`);

return [{
  json: logEntry
}];
```

---

### ✅ Nœud : "Log to Airtable"
**Type** : Airtable
**Operation** : Create
**Table** : API Logs

**Configuration** `columns.value` :

```javascript
{
  "Restaurant": "={{ $json.Restaurant }}",
  "Timestamp": "={{ $json.Timestamp }}",
  "Type": "={{ $json.Type }}",
  "Endpoint": "={{ $json.Endpoint }}",
  "Message": "={{ $json.Message }}",
  "Request Data": "={{ $json['Request Data'] }}",
  "Response Data": "={{ $json['Response Data'] }}",
  "Error Stack": "={{ $json['Error Stack'] }}",
  "Duration": "={{ $json.Duration }}"
}
```

---

## ❌ SECTION 5 : GESTION D'ERREURS

### ✅ Nœud : "Error Trigger"
**Type** : Error Trigger
**Settings** :
- Trigger on workflow error: ✅

**Output** : Vers "Format Error Response"

---

### ✅ Nœud : "Format Error Response"
**Type** : Code
**Position** : Après "Error Trigger"

```javascript
// ============================================
// FORMATAGE DES ERREURS
// ============================================

const error = $input.first().json.error || $input.first().json;
let restaurantId = 'unknown';

// Essayer de récupérer le restaurant_id depuis différentes sources
try {
  restaurantId = $('Global Error Handler')?.item?.json?.restaurant_id ||
                 $('Extraire Restaurant ID')?.first()?.json?.restaurant_id ||
                 'unknown';
} catch (e) {
  console.warn('Impossible de récupérer le restaurant_id pour l\'erreur');
}

// Catégoriser l'erreur
let errorType = 'UNKNOWN_ERROR';
let errorCode = 'ERR_UNKNOWN';
let errorMessage = error.message || 'Une erreur inconnue s\'est produite';
let userMessage = errorMessage; // Message pour l'utilisateur final

const errorLower = errorMessage.toLowerCase();

if (errorLower.includes('airtable') || errorLower.includes('api')) {
  errorType = 'API_ERROR';
  errorCode = 'ERR_API';
  userMessage = 'Erreur de communication avec la base de données';
} else if (errorLower.includes('restaurant') && errorLower.includes('id')) {
  errorType = 'AUTH_ERROR';
  errorCode = 'ERR_AUTH';
  userMessage = 'Restaurant non identifié - Vérifiez votre clé API';
} else if (errorLower.includes('validation') || errorLower.includes('invalid')) {
  errorType = 'VALIDATION_ERROR';
  errorCode = 'ERR_VALIDATION';
  userMessage = 'Données invalides';
} else if (errorLower.includes('not found') || errorLower.includes('aucun')) {
  errorType = 'NOT_FOUND_ERROR';
  errorCode = 'ERR_NOT_FOUND';
  userMessage = 'Ressource non trouvée';
} else if (errorLower.includes('network') || errorLower.includes('timeout')) {
  errorType = 'NETWORK_ERROR';
  errorCode = 'ERR_NETWORK';
  userMessage = 'Erreur réseau - Veuillez réessayer';
}

// Formater la réponse d'erreur
const errorResponse = {
  success: false,
  error: {
    type: errorType,
    code: errorCode,
    message: userMessage,
    timestamp: new Date().toISOString(),
    // En développement seulement
    ...(process.env.NODE_ENV === 'development' && {
      technicalMessage: errorMessage,
      stack: error.stack
    })
  },
  restaurantId: restaurantId,
  requestId: $('Global Error Handler')?.item?.json?.requestId || null
};

// Préparer le log d'erreur
const logData = {
  restaurant_id: restaurantId,
  logType: 'ERROR',
  endpoint: error.node || $node.name || 'unknown',
  message: errorMessage,
  errorStack: error.stack || '',
  requestData: JSON.stringify($('Global Error Handler')?.item?.json?.originalRequest || {}),
  timestamp: new Date().toISOString(),
  duration: 0
};

console.error(`❌ [${restaurantId}] ${errorType}: ${errorMessage}`);
console.error(`📍 Node: ${error.node || 'unknown'}`);

return [{
  json: {
    ...errorResponse,
    _log: logData
  }
}];
```

---

### ✅ Nœud : "Send Error Log"
**Type** : Airtable
**Position** : Après "Format Error Response"
**Operation** : Create
**Table** : API Logs

**Configuration** `columns.value` :

```javascript
{
  "Restaurant": "={{ [$json._log.restaurant_id] }}",
  "Timestamp": "={{ $json._log.timestamp }}",
  "Type": "ERROR",
  "Endpoint": "={{ $json._log.endpoint }}",
  "Message": "={{ $json._log.message }}",
  "Request Data": "={{ $json._log.requestData }}",
  "Error Stack": "={{ $json._log.errorStack }}",
  "Duration": "={{ $json._log.duration }}"
}
```

---

### ✅ Nœud : "Respond Error to Webhook"
**Type** : Respond to Webhook
**Position** : Après "Send Error Log"

**Configuration** :
- Respond With: JSON
- Response Body:

```javascript
={
  "success": false,
  "error": {
    "type": {{ $json.error.type }},
    "code": {{ $json.error.code }},
    "message": {{ $json.error.message }},
    "timestamp": {{ $json.error.timestamp }}
  },
  "restaurantId": {{ $json.restaurantId }},
  "requestId": {{ $json.requestId }}
}
```

---

## ✅ SECTION 6 : RÉPONSES STANDARDISÉES

### ✅ Nœud : "Format Success Response"
**Type** : Code
**Position** : AVANT chaque "Respond to Webhook" de succès

```javascript
// ============================================
// FORMATAGE RÉPONSE DE SUCCÈS
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const requestId = $('Global Error Handler').item.json.requestId;
const data = $input.first().json;

// Retirer les données internes
const cleanData = { ...data };
delete cleanData._log;
delete cleanData.Restaurant;
delete cleanData.restaurant_id;

const response = {
  success: true,
  data: cleanData,
  metadata: {
    restaurantId: restaurantId,
    requestId: requestId,
    timestamp: new Date().toISOString()
  }
};

console.log(`✅ [${restaurantId}] Réponse de succès préparée`);

return [{
  json: response
}];
```

---

## 🧪 SECTION 7 : TESTS & VALIDATION

### ✅ Nœud : "Test Multi-Tenant Isolation"
**Type** : Code
**Usage** : À exécuter manuellement pour tester l'isolation

```javascript
// ============================================
// TEST D'ISOLATION MULTI-TENANT
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;

console.log('🧪 Démarrage du test d\'isolation multi-tenant');
console.log(`📍 Restaurant testé: ${restaurantId}`);

// Récupérer les employés du restaurant
const employees = $('get employes').all();
console.log(`👥 ${employees.length} employés trouvés`);

// Vérifier que tous appartiennent au bon restaurant
const invalidEmployees = employees.filter(emp => {
  const empRestaurant = emp.json.Restaurant;
  return !empRestaurant || !empRestaurant.includes(restaurantId);
});

if (invalidEmployees.length > 0) {
  console.error(`❌ ÉCHEC: ${invalidEmployees.length} employés ne sont pas liés au restaurant ${restaurantId}`);
  throw new Error(`Isolation compromise: ${invalidEmployees.length} employés invalides`);
}

console.log('✅ Test d\'isolation: OK - Tous les employés appartiennent au restaurant');

// Récupérer le planning
const planning = $('Create a record')?.all() || [];
console.log(`📅 ${planning.length} entrées de planning trouvées`);

const invalidPlanning = planning.filter(entry => {
  const planRestaurant = entry.json.fields?.Restaurant || entry.json.Restaurant;
  return !planRestaurant || !planRestaurant.includes(restaurantId);
});

if (invalidPlanning.length > 0) {
  console.error(`❌ ÉCHEC: ${invalidPlanning.length} entrées de planning invalides`);
  throw new Error(`Isolation compromise: ${invalidPlanning.length} entrées de planning invalides`);
}

console.log('✅ Test d\'isolation: OK - Toutes les entrées de planning sont isolées');

return [{
  json: {
    testPassed: true,
    restaurantId: restaurantId,
    employeesCount: employees.length,
    planningCount: planning.length,
    message: 'Isolation multi-tenant validée avec succès'
  }
}];
```

---

## 📊 SECTION 8 : MONITORING

### ✅ Nœud : "Performance Monitor"
**Type** : Code
**Usage** : Optionnel - Pour tracker les performances

```javascript
// ============================================
// MONITORING DES PERFORMANCES
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const requestId = $('Global Error Handler').item.json.requestId;
const startTime = new Date($('Global Error Handler').item.json.timestamp);
const endTime = new Date();
const duration = endTime - startTime;

// Récupérer des métriques
const metrics = {
  restaurantId: restaurantId,
  requestId: requestId,
  duration: duration,
  timestamp: endTime.toISOString(),

  // Compter les opérations effectuées
  operations: {
    employeesQueried: $('get employes')?.all()?.length || 0,
    planningCreated: $('Create a record')?.all()?.length || 0,
    hoursCreated: $('Create a record1')?.all()?.length || 0
  },

  // Statut
  status: 'completed',
  success: true
};

console.log(`⏱️ [${restaurantId}] Durée totale: ${duration}ms`);
console.log(`📊 Opérations: ${JSON.stringify(metrics.operations)}`);

// Si la durée est trop longue, logger un avertissement
if (duration > 5000) {
  console.warn(`⚠️ [${restaurantId}] Requête lente: ${duration}ms`);

  return [{
    json: {
      ...metrics,
      _log: {
        restaurant_id: restaurantId,
        logType: 'WARNING',
        endpoint: 'performance_monitor',
        message: `Requête lente détectée: ${duration}ms`,
        duration: duration,
        timestamp: endTime.toISOString()
      }
    }
  }];
}

return [{
  json: metrics
}];
```

---

## 🔄 SECTION 9 : PROPAGATION DU CONTEXTE

### ✅ Nœud : "Propagate Restaurant Context"
**Type** : Code
**Usage** : À insérer avant les branches qui perdent le contexte

```javascript
// ============================================
// PROPAGATION DU CONTEXTE RESTAURANT
// ============================================

const restaurantId = $('Global Error Handler').item.json.restaurant_id;
const currentData = $input.first().json;

// Ajouter le restaurant_id aux données actuelles
const enrichedData = {
  ...currentData,
  _context: {
    restaurant_id: restaurantId,
    restaurant_name: $('Global Error Handler').item.json.restaurant_name,
    requestId: $('Global Error Handler').item.json.requestId
  }
};

console.log(`🔗 [${restaurantId}] Contexte propagé vers ${$node.name}`);

return [{
  json: enrichedData
}];
```

---

## 📱 SECTION 10 : ALERTES

### ✅ Nœud : "Check Critical Alerts"
**Type** : Code
**Position** : Après "Send Error Log"

```javascript
// ============================================
// VÉRIFICATION DES ALERTES CRITIQUES
// ============================================

const restaurantId = $json._log.restaurant_id;
const errorMessage = $json._log.message;

// Définir les seuils d'alerte
const CRITICAL_THRESHOLD = 5; // Nombre d'erreurs en 5 minutes

// Simuler une vérification (à remplacer par une vraie requête Airtable)
// const recentErrors = await queryRecentErrors(restaurantId, 5);

// Pour l'exemple, on alerte sur certains types d'erreurs
const criticalKeywords = [
  'database',
  'airtable',
  'crash',
  'fatal',
  'timeout'
];

const isCritical = criticalKeywords.some(keyword =>
  errorMessage.toLowerCase().includes(keyword)
);

if (isCritical) {
  console.error(`🚨 [${restaurantId}] ALERTE CRITIQUE: ${errorMessage}`);

  return [{
    json: {
      alert: true,
      severity: 'CRITICAL',
      restaurantId: restaurantId,
      message: errorMessage,
      timestamp: new Date().toISOString(),

      // Données pour l'email d'alerte
      emailData: {
        to: 'admin@restaurant.com',
        subject: `🚨 ALERTE CRITIQUE - Restaurant ${restaurantId}`,
        body: `Une erreur critique a été détectée:\n\n${errorMessage}\n\nRestaurant: ${restaurantId}\nTimestamp: ${new Date().toISOString()}`
      }
    }
  }];
}

// Pas d'alerte nécessaire
return [];
```

---

## 📧 SECTION 11 : EMAIL D'ALERTE

### ✅ Nœud : "Send Alert Email"
**Type** : Gmail / Send Email
**Position** : Après "Check Critical Alerts"

**Configuration** :
```javascript
{
  "sendTo": "{{ $json.emailData.to }}",
  "subject": "{{ $json.emailData.subject }}",
  "message": "{{ $json.emailData.body }}"
}
```

---

**FIN DES CODES PRÊTS À UTILISER**

Pour utiliser ces codes :
1. Copiez le code correspondant au nœud
2. Collez-le dans le nœud Code de n8n
3. Vérifiez les connexions input/output
4. Testez avec un restaurant de test

Consultez le fichier `MIGRATION_GUIDE.md` pour l'ordre d'implémentation.
