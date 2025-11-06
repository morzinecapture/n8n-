# 🧪 Scripts de Test Multi-Tenant

Ce fichier contient tous les scripts pour tester votre système multi-tenant.

---

## 📋 TESTS CURL - API

### Test 1 : API Key invalide

```bash
curl -X POST https://votre-webhook-n8n.app.n8n.cloud/webhook/23ed6cad-a469-446c-bccd-fe294d0f1839 \
  -H "Content-Type: application/json" \
  -H "x-api-key: INVALID_KEY_123" \
  -d '{
    "type": "conversation",
    "message": "test",
    "restaurant_id": "recUpZqg63Xvpv9iD"
  }'
```

**Résultat attendu** :
```json
{
  "success": false,
  "error": {
    "type": "AUTH_ERROR",
    "code": "ERR_AUTH",
    "message": "Restaurant non identifié - Vérifiez votre clé API",
    "timestamp": "2025-01-XX..."
  },
  "restaurantId": "unknown",
  "requestId": null
}
```

**Vérifications** :
- ✅ HTTP Status: 200 (ou 401 selon config)
- ✅ success: false
- ✅ Type d'erreur: AUTH_ERROR
- ✅ Log créé dans Airtable (Type: ERROR)

---

### Test 2 : Requête valide - Restaurant 1

```bash
curl -X POST https://votre-webhook-n8n.app.n8n.cloud/webhook/23ed6cad-a469-446c-bccd-fe294d0f1839 \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -d '{
    "type": "conversation",
    "message": "liste des employés",
    "audio": null
  }'
```

**Résultat attendu** :
```json
{
  "success": true,
  "data": {
    "employees": [
      {"nom": "Sarah Martin", "role": "Cuisine"},
      {"nom": "Paul Dupont", "role": "Serveur"}
    ]
  },
  "metadata": {
    "restaurantId": "recXXXXXXXXXXXXXX",
    "requestId": "recXXXXXXXXXXXXXX_1234567890",
    "timestamp": "2025-01-XX..."
  }
}
```

**Vérifications** :
- ✅ HTTP Status: 200
- ✅ success: true
- ✅ Données retournées
- ✅ Log créé dans Airtable (Type: SUCCESS)
- ✅ Seulement les employés du restaurant 1

---

### Test 3 : Requête valide - Restaurant 2

```bash
curl -X POST https://votre-webhook-n8n.app.n8n.cloud/webhook/23ed6cad-a469-446c-bccd-fe294d0f1839 \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_pizzeria_2025_xyz789" \
  -d '{
    "type": "conversation",
    "message": "liste des employés",
    "audio": null
  }'
```

**Résultat attendu** :
```json
{
  "success": true,
  "data": {
    "employees": [
      {"nom": "Marco Rossi", "role": "Pizzaiolo"},
      {"nom": "Luigi Verdi", "role": "Serveur"}
    ]
  },
  "metadata": {
    "restaurantId": "recYYYYYYYYYYYYYY",
    "requestId": "recYYYYYYYYYYYYYY_1234567891",
    "timestamp": "2025-01-XX..."
  }
}
```

**Vérifications** :
- ✅ HTTP Status: 200
- ✅ success: true
- ✅ Données DIFFÉRENTES du test 2
- ✅ Seulement les employés du restaurant 2
- ✅ **AUCUN employé du restaurant 1 visible**

---

### Test 4 : Création de planning - Restaurant 1

```bash
curl -X POST https://votre-webhook-n8n.app.n8n.cloud/webhook/23ed6cad-a469-446c-bccd-fe294d0f1839 \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -d '{
    "type": "conversation",
    "message": "planning de la semaine",
    "audio": null
  }'
```

**Vérifications Airtable après exécution** :
1. Ouvrir table "Planning Optimisé"
2. Filtrer par Restaurant = "Brasserie du Centre"
3. Vérifier que les nouvelles entrées sont présentes
4. Vérifier qu'elles ont TOUTES le bon Restaurant

**SQL-like vérification** :
```
SELECT * FROM "Planning Optimisé"
WHERE Restaurant = "Brasserie du Centre"
AND Date >= TODAY()
```

---

### Test 5 : Création d'heures - Restaurant 2

```bash
curl -X POST https://votre-webhook-n8n.app.n8n.cloud/webhook/23ed6cad-a469-446c-bccd-fe294d0f1839 \
  -H "Content-Type: application/json" \
  -H "x-api-key: test_pizzeria_2025_xyz789" \
  -d '{
    "type": "conversation",
    "message": "Marco est arrivé à 9h et parti à 17h",
    "audio": null
  }'
```

**Vérifications Airtable** :
1. Table "Heures des employés"
2. Vérifier qu'une nouvelle entrée existe
3. Vérifier que Restaurant = "Pizzeria Roma"
4. Vérifier que l'employé est bien "Marco Rossi"

---

## 🔍 TESTS D'ISOLATION

### Test Isolation 1 : Employés

**But** : Vérifier qu'un restaurant ne peut pas voir les employés d'un autre

**Étape 1** : Requête restaurant 1
```bash
curl -X POST https://votre-webhook-url \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -d '{"message": "liste des employés"}'
```

**Étape 2** : Requête restaurant 2
```bash
curl -X POST https://votre-webhook-url \
  -H "x-api-key: test_pizzeria_2025_xyz789" \
  -d '{"message": "liste des employés"}'
```

**Validation** :
```javascript
// Script de validation (à exécuter dans un nœud Code n8n)
const response1 = [/* réponse restaurant 1 */];
const response2 = [/* réponse restaurant 2 */];

const employees1 = response1.data.employees.map(e => e.nom);
const employees2 = response2.data.employees.map(e => e.nom);

// Vérifier qu'il n'y a AUCUN employé en commun
const intersection = employees1.filter(name => employees2.includes(name));

if (intersection.length > 0) {
  throw new Error(`❌ ÉCHEC: ${intersection.length} employés visibles par les 2 restaurants !`);
}

console.log('✅ Test d\'isolation: OK - Aucun employé partagé');
```

---

### Test Isolation 2 : Planning

**But** : Vérifier que le planning créé par restaurant 1 n'est pas visible par restaurant 2

**Étape 1** : Restaurant 1 crée un planning
```bash
curl -X POST https://votre-webhook-url \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -d '{"message": "planning de la semaine"}'
```

**Étape 2** : Vérifier dans Airtable
1. Aller dans "Planning Optimisé"
2. Filtrer par date du planning créé
3. Compter combien ont Restaurant = "Brasserie du Centre"
4. Compter combien ont Restaurant = "Pizzeria Roma"

**Résultat attendu** :
- ✅ Toutes les entrées créées ont Restaurant = "Brasserie du Centre"
- ✅ ZÉRO entrée avec Restaurant = "Pizzeria Roma"

---

### Test Isolation 3 : Logs

**But** : Vérifier que les logs sont bien séparés par restaurant

**Requête Airtable (via API ou interface)** :

```javascript
// Formule Airtable dans la table API Logs
filterByFormula: "AND(
  {Restaurant} = 'recRestaurant1ID',
  {Timestamp} >= TODAY()
)"
```

**Validation manuelle** :
1. Ouvrir table "API Logs"
2. Grouper par "Restaurant"
3. Vérifier que chaque groupe ne contient QUE les logs de ce restaurant

---

## 📊 TESTS DE PERFORMANCE

### Test Perf 1 : Temps de réponse

```bash
#!/bin/bash

# Test de temps de réponse
for i in {1..10}; do
  echo "Test $i"
  time curl -X POST https://votre-webhook-url \
    -H "x-api-key: test_brasserie_2025_abc123" \
    -H "Content-Type: application/json" \
    -d '{"message": "liste des employés"}' \
    -s -o /dev/null -w "Time: %{time_total}s\n"
  sleep 1
done
```

**Résultat attendu** :
- Temps moyen < 2 secondes
- Pas d'erreur timeout

---

### Test Perf 2 : Concurrence

```bash
#!/bin/bash

# Test de concurrence (10 requêtes simultanées)
for i in {1..10}; do
  (
    curl -X POST https://votre-webhook-url \
      -H "x-api-key: test_brasserie_2025_abc123" \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"test $i\"}" \
      -s -o /dev/null -w "Request $i: %{http_code} in %{time_total}s\n"
  ) &
done

wait
echo "Tous les tests terminés"
```

**Résultat attendu** :
- ✅ Toutes les requêtes retournent 200
- ✅ Pas de conflit de données
- ✅ Logs corrects dans Airtable

---

## 🧪 TESTS UNITAIRES (dans n8n)

### Test Unit 1 : extractRestaurantId

**Nœud Code de test** :

```javascript
// Test de la fonction extractRestaurantId

// Simuler différents contextes
const testCases = [
  {
    name: "Contexte normal",
    context: {
      $json: { restaurant_id: "rec123" }
    },
    expected: "rec123"
  },
  {
    name: "Via Global Error Handler",
    context: {
      $: (nodeName) => ({
        item: { json: { restaurant_id: "rec456" } }
      })
    },
    expected: "rec456"
  },
  {
    name: "Manquant",
    context: {},
    expected: null
  }
];

// Fonction à tester (copier depuis multi-tenant-error-handler.js)
function extractRestaurantId(context) {
  const sources = [
    context.$json?.restaurant_id,
    context.$?.('Global Error Handler')?.item?.json?.restaurant_id,
    context.restaurant_id
  ];

  for (const source of sources) {
    if (source) return source;
  }

  return null;
}

// Exécuter les tests
let passed = 0;
let failed = 0;

testCases.forEach(test => {
  const result = extractRestaurantId(test.context);

  if (result === test.expected) {
    console.log(`✅ ${test.name}: PASS`);
    passed++;
  } else {
    console.error(`❌ ${test.name}: FAIL (got ${result}, expected ${test.expected})`);
    failed++;
  }
});

console.log(`\nRésultats: ${passed} passed, ${failed} failed`);

if (failed > 0) {
  throw new Error(`${failed} tests failed`);
}

return [{ json: { passed, failed } }];
```

---

### Test Unit 2 : categorizeError

**Nœud Code de test** :

```javascript
// Test de la fonction categorizeError

const testCases = [
  {
    error: new Error("Airtable API error"),
    expected: "API_ERROR"
  },
  {
    error: new Error("Network timeout"),
    expected: "NETWORK_ERROR"
  },
  {
    error: new Error("Invalid data provided"),
    expected: "VALIDATION_ERROR"
  },
  {
    error: new Error("Resource not found"),
    expected: "NOT_FOUND_ERROR"
  },
  {
    error: new Error("Something weird"),
    expected: "UNKNOWN_ERROR"
  }
];

// Fonction à tester
function categorizeError(error) {
  const message = error.message?.toLowerCase() || '';

  if (message.includes('airtable') || message.includes('api')) {
    return 'API_ERROR';
  }
  if (message.includes('network') || message.includes('timeout')) {
    return 'NETWORK_ERROR';
  }
  if (message.includes('validation') || message.includes('invalid')) {
    return 'VALIDATION_ERROR';
  }
  if (message.includes('not found')) {
    return 'NOT_FOUND_ERROR';
  }

  return 'UNKNOWN_ERROR';
}

// Exécuter les tests
let passed = 0;
let failed = 0;

testCases.forEach((test, index) => {
  const result = categorizeError(test.error);

  if (result === test.expected) {
    console.log(`✅ Test ${index + 1}: PASS (${test.error.message} → ${result})`);
    passed++;
  } else {
    console.error(`❌ Test ${index + 1}: FAIL (got ${result}, expected ${test.expected})`);
    failed++;
  }
});

console.log(`\nRésultats: ${passed} passed, ${failed} failed`);

return [{ json: { passed, failed } }];
```

---

## 🔐 TESTS DE SÉCURITÉ

### Test Sécu 1 : Tentative d'accès cross-restaurant

**But** : Essayer d'accéder aux données d'un autre restaurant en modifiant la requête

```bash
# Requête normale avec API key restaurant 1
curl -X POST https://votre-webhook-url \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "liste des employés",
    "restaurant_id": "recRestaurant2ID"  # ← Tentative de forcer un autre restaurant
  }'
```

**Résultat attendu** :
- ✅ Le système ignore le restaurant_id fourni dans le body
- ✅ Utilise uniquement celui de l'API key
- ✅ Retourne seulement les données du restaurant 1

---

### Test Sécu 2 : Injection dans filterByFormula

**But** : Tenter une injection de formule Airtable

```bash
curl -X POST https://votre-webhook-url \
  -H "x-api-key: test_brasserie_2025_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "'); OR 1=1; --",
    "restaurant_id": "recXXX"
  }'
```

**Résultat attendu** :
- ✅ Pas d'erreur Airtable
- ✅ Pas de données non autorisées retournées
- ✅ Log d'erreur si la requête est invalide

---

### Test Sécu 3 : API Key vide

```bash
curl -X POST https://votre-webhook-url \
  -H "Content-Type: application/json" \
  -d '{
    "message": "test"
  }'
# Pas de header x-api-key
```

**Résultat attendu** :
```json
{
  "success": false,
  "error": {
    "type": "AUTH_ERROR",
    "message": "API Key manquante"
  }
}
```

---

## 📈 TESTS DE MONITORING

### Test Monitoring 1 : Logs correctement créés

**Après avoir exécuté plusieurs requêtes** :

1. Ouvrir Airtable → Table "API Logs"
2. Vérifier qu'il y a des logs pour chaque requête
3. Grouper par "Type"
4. Compter :
   - SUCCESS : Devrait être > 0
   - ERROR : Devrait exister si vous avez testé les erreurs
   - INFO : Peut être 0

**Validation SQL-like** :
```
SELECT Type, COUNT(*)
FROM "API Logs"
WHERE Timestamp >= TODAY()
GROUP BY Type
```

---

### Test Monitoring 2 : Durée des opérations

**Requête Airtable** :

```
SELECT Endpoint, AVG(Duration), MAX(Duration), COUNT(*)
FROM "API Logs"
WHERE Type = 'SUCCESS'
GROUP BY Endpoint
ORDER BY AVG(Duration) DESC
```

**Seuils attendus** :
- get_employees : < 1000ms
- create_planning : < 3000ms
- create_hours : < 1000ms

**Si > seuils** : Investiguer les causes (trop de données, réseau lent, etc.)

---

## 🎯 CHECKLIST COMPLÈTE DE TESTS

### Phase 1 : Tests de base
- [ ] Test 1 : API Key invalide → Erreur AUTH_ERROR
- [ ] Test 2 : Requête valide restaurant 1 → Succès
- [ ] Test 3 : Requête valide restaurant 2 → Succès
- [ ] Test 4 : Création planning restaurant 1 → Succès
- [ ] Test 5 : Création heures restaurant 2 → Succès

### Phase 2 : Tests d'isolation
- [ ] Isolation employés : Aucun employé partagé entre restaurants
- [ ] Isolation planning : Planning créé visible seulement par le bon restaurant
- [ ] Isolation logs : Logs séparés par restaurant

### Phase 3 : Tests de performance
- [ ] Temps de réponse < 2s
- [ ] Concurrence : 10 requêtes simultanées OK
- [ ] Pas de timeout

### Phase 4 : Tests de sécurité
- [ ] Tentative cross-restaurant bloquée
- [ ] Injection formule bloquée
- [ ] API key vide → Erreur

### Phase 5 : Tests de monitoring
- [ ] Logs créés pour chaque requête
- [ ] Durées enregistrées correctement
- [ ] Types d'erreur corrects

### Phase 6 : Tests de bout en bout
- [ ] Création complète planning (employés → planning → email)
- [ ] Création heures (parsing → création → dashboard)
- [ ] Plat du jour (IA → photo → overlay → réponse)

---

## 🔄 SCRIPT D'AUTOMATISATION DES TESTS

### Bash script complet

```bash
#!/bin/bash

# Configuration
WEBHOOK_URL="https://votre-webhook-url"
API_KEY_1="test_brasserie_2025_abc123"
API_KEY_2="test_pizzeria_2025_xyz789"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASSED=0
FAILED=0

# Fonction de test
test_request() {
  local test_name=$1
  local api_key=$2
  local message=$3
  local expected_success=$4

  echo -e "\n${YELLOW}🧪 Test: $test_name${NC}"

  response=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $api_key" \
    -d "{\"message\": \"$message\"}")

  success=$(echo "$response" | jq -r '.success')

  if [ "$success" == "$expected_success" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
  else
    echo -e "${RED}❌ FAIL${NC}"
    echo "Response: $response"
    ((FAILED++))
  fi
}

# Exécuter les tests
echo "🚀 Démarrage des tests multi-tenant"

test_request "API Key invalide" "INVALID_KEY" "test" "false"
test_request "Restaurant 1 - Liste employés" "$API_KEY_1" "liste des employés" "true"
test_request "Restaurant 2 - Liste employés" "$API_KEY_2" "liste des employés" "true"
test_request "Restaurant 1 - Planning" "$API_KEY_1" "planning de la semaine" "true"

# Résumé
echo -e "\n${YELLOW}📊 Résultats:${NC}"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
  echo -e "\n${GREEN}🎉 Tous les tests sont passés !${NC}"
  exit 0
else
  echo -e "\n${RED}⚠️ Certains tests ont échoué${NC}"
  exit 1
fi
```

**Utilisation** :
```bash
chmod +x test-multi-tenant.sh
./test-multi-tenant.sh
```

---

## 📝 RAPPORT DE TESTS

### Template de rapport

```markdown
# Rapport de Tests Multi-Tenant

**Date** : YYYY-MM-DD
**Version système** : 1.0
**Testeur** : [Nom]

## Résultats

| Test | Statut | Durée | Notes |
|------|--------|-------|-------|
| API Key invalide | ✅ PASS | 120ms | - |
| Restaurant 1 - Employés | ✅ PASS | 850ms | - |
| Restaurant 2 - Employés | ✅ PASS | 920ms | - |
| Isolation employés | ✅ PASS | - | Aucun leak détecté |
| Création planning R1 | ✅ PASS | 2.3s | 14 entrées créées |
| Logs correctement créés | ✅ PASS | - | 12 logs trouvés |

## Problèmes identifiés

- Aucun

## Recommandations

- Système prêt pour la production
- Monitoring à activer

## Signatures

Testeur : _________________
Chef de projet : _________________
```

---

**FIN DES SCRIPTS DE TEST**

Pour exécuter tous ces tests :
1. Commencer par les tests CURL (manuels)
2. Exécuter les tests unitaires dans n8n
3. Lancer le script bash d'automatisation
4. Valider manuellement dans Airtable
5. Remplir le rapport de tests

**Durée estimée des tests : 2-3 heures**
