# 📊 Configuration Airtable Multi-Tenant

Ce guide détaille la structure Airtable complète pour un système multi-tenant.

---

## 🏗️ ARCHITECTURE DES TABLES

### Vue d'ensemble

```
┌─────────────────┐
│   Restaurants   │ ← Table principale (1 par restaurant)
└────────┬────────┘
         │ Links to:
         ├─► Employés
         ├─► Planning Optimisé
         ├─► Heures des employés
         ├─► Hebdo Employé
         ├─► Dashboard RH
         ├─► Bibliothèque Photos Menu
         ├─► API Logs
         └─► Factures
```

---

## 📋 TABLE 1 : Restaurants (Existante - à modifier)

### Champs existants
- ✅ ID (Primary key)
- ✅ Nom Restaurant (Single line text)
- ✅ API Key (Single line text)
- ✅ Actif (Checkbox)

### Nouveaux champs à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Plan** | Single select | Options: Free, Standard, Premium, Enterprise | Niveau d'abonnement |
| **Limite Employés** | Number | Format: Integer | Nombre max d'employés |
| **Limite API Calls** | Number | Format: Integer | Appels API par mois |
| **Date Création** | Date | Include time: ✅ | Quand le restaurant a été créé |
| **Dernière Activité** | Date | Include time: ✅ | Dernière requête API |
| **Email Contact** | Email | - | Email du propriétaire |
| **Téléphone** | Phone number | - | Contact principal |
| **Adresse** | Long text | - | Adresse complète |
| **Fuseau Horaire** | Single select | Options: Europe/Paris, etc. | Timezone du restaurant |
| **Langue** | Single select | Options: fr, en, es, de | Langue de l'interface |
| **Notes Internes** | Long text | - | Notes pour l'équipe support |

### Formules calculées

**Statut** (Formula):
```
IF(
  {Actif},
  IF(
    DATETIME_DIFF(NOW(), {Dernière Activité}, 'days') > 7,
    "🟡 Inactif 7j",
    "🟢 Actif"
  ),
  "🔴 Désactivé"
)
```

**Utilisation API** (Rollup depuis API Logs):
```
COUNT(values)
From: API Logs
Field: ID
Condition: Last 30 days
```

---

## 📋 TABLE 2 : API Logs (NOUVELLE)

### Structure complète

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **ID** | Autonumber | - | ID unique du log |
| **Restaurant** | Link to Restaurants | ✅ Required | Quel restaurant |
| **Timestamp** | Date | Include time: ✅ | Quand |
| **Type** | Single select | Options: INFO, ERROR, WARNING, SUCCESS | Niveau de gravité |
| **Endpoint** | Single line text | - | Quelle opération (ex: get_employees) |
| **Message** | Long text | - | Description de l'opération |
| **Request Data** | Long text | - | Données de la requête (JSON) |
| **Response Data** | Long text | - | Données de la réponse (JSON) |
| **Error Stack** | Long text | - | Stack trace en cas d'erreur |
| **Duration** | Number | Format: Integer, Suffix: ms | Durée de l'opération |
| **User Agent** | Single line text | - | Client qui a fait la requête |
| **IP Address** | Single line text | - | IP du client |
| **Request ID** | Single line text | - | ID unique de la requête |

### Vues à créer

#### Vue 1 : "Dernières erreurs"
- **Filtre** : Type = ERROR
- **Tri** : Timestamp (décroissant)
- **Grouper par** : Restaurant
- **Champs visibles** : Restaurant, Timestamp, Message, Endpoint

#### Vue 2 : "Performance par endpoint"
- **Grouper par** : Endpoint
- **Résumés** :
  - COUNT(ID) → Nombre total
  - AVG(Duration) → Durée moyenne
  - MAX(Duration) → Durée max
- **Filtre** : Type = SUCCESS

#### Vue 3 : "Activité par restaurant"
- **Grouper par** : Restaurant
- **Résumés** :
  - COUNT(ID) → Total requêtes
  - COUNT(Type=ERROR) → Total erreurs
- **Tri** : Par nombre de requêtes (décroissant)

#### Vue 4 : "Alertes critiques"
- **Filtre** : Type = ERROR AND Duration > 5000
- **Tri** : Timestamp (décroissant)
- **Couleur** : Rouge pour toutes les lignes

---

## 📋 TABLE 3 : Employés (Modifier l'existante)

### Champ à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Restaurant** | Link to Restaurants | ✅ Required | À quel restaurant appartient l'employé |

### Modifier la formule RID Employé

**Avant** :
```
{Nom} & "-" & RECORD_ID()
```

**Après** :
```
{Nom} & "-" & {Restaurant} & "-" & RECORD_ID()
```

### Vues à créer

#### Vue par restaurant
- **Grouper par** : Restaurant
- **Filtre** : Actif (si vous avez ce champ)

---

## 📋 TABLE 4 : Planning Optimisé (Modifier l'existante)

### Champ à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Restaurant** | Link to Restaurants | ✅ Required | À quel restaurant |

### Modifier la formule ID_Planning

**Avant** :
```
{Date} & "-" & {Service}
```

**Après** :
```
{Restaurant} & "-" & {Date} & "-" & {Service}
```

---

## 📋 TABLE 5 : Heures des employés (Modifier l'existante)

### Champ à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Restaurant** | Link to Restaurants | ✅ Required | À quel restaurant |

### Formule pour Semaine ISO (modifier si existe)

**Nouvelle formule** :
```
YEAR({Date}) & "-W" & IF(
  WEEKNUM({Date}) < 10,
  "0" & WEEKNUM({Date}),
  WEEKNUM({Date})
)
```

---

## 📋 TABLE 6 : Hebdo Employé (Modifier l'existante)

### Champ à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Restaurant** | Link to Restaurants | ✅ Required | À quel restaurant |

### Modifier Clé Employé+Semaine

**Nouvelle formule** :
```
{Employé} & "|" & {Semaine ISO} & "|" & {Restaurant}
```

---

## 📋 TABLE 7 : Dashboard RH (Modifier l'existante)

### Champ à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Restaurant** | Link to Restaurants | ✅ Required | À quel restaurant |

---

## 📋 TABLE 8 : Bibliothèque Photos Menu (Modifier l'existante)

### Champ à ajouter

| Nom du champ | Type | Configuration | Description |
|--------------|------|---------------|-------------|
| **Restaurant** | Link to Restaurants | - | Si la photo est spécifique à un restaurant (optionnel) |
| **Partagée** | Checkbox | Default: ✅ | Si ✅, disponible pour tous les restaurants |

---

## 🔧 SCRIPT DE MIGRATION DES DONNÉES

### Étape 1 : Lier les données existantes

Si vous avez déjà des données, vous devez les lier à un restaurant.

**Option A : Via l'interface Airtable**

1. Créer un enregistrement de test dans "Restaurants"
   - Nom: "Restaurant Test"
   - API Key: "test_restaurant_001"
   - Actif: ✅

2. Dans chaque table (Employés, Planning, etc.) :
   - Sélectionner toutes les lignes
   - Bulk edit le champ "Restaurant"
   - Choisir "Restaurant Test"

**Option B : Via script Airtable**

Dans Airtable, ouvrir "Extensions" → "Scripting" → Nouveau script :

```javascript
// Script de migration - Lier toutes les données au restaurant par défaut

const restaurantTable = base.getTable("Restaurants");
const employeesTable = base.getTable("Employés");
const planningTable = base.getTable("Planning Optimisé");
const heuresTable = base.getTable("Heures des employés");

// 1. Récupérer le restaurant par défaut
const restaurantQuery = await restaurantTable.selectRecordsAsync();
const defaultRestaurant = restaurantQuery.records[0]; // Premier restaurant

if (!defaultRestaurant) {
    throw new Error("Aucun restaurant trouvé !");
}

console.log(`Restaurant par défaut: ${defaultRestaurant.name}`);

// 2. Fonction pour mettre à jour les enregistrements
async function linkRecordsToRestaurant(table, fieldName) {
    const query = await table.selectRecordsAsync();
    const records = query.records;

    // Filtrer seulement ceux qui n'ont pas encore de restaurant
    const recordsToUpdate = records.filter(r => !r.getCellValue(fieldName));

    console.log(`${table.name}: ${recordsToUpdate.length} enregistrements à lier`);

    // Mise à jour par lots de 50 (limite Airtable)
    while (recordsToUpdate.length > 0) {
        const batch = recordsToUpdate.splice(0, 50);
        await table.updateRecordsAsync(
            batch.map(record => ({
                id: record.id,
                fields: {
                    [fieldName]: [{id: defaultRestaurant.id}]
                }
            }))
        );
    }

    console.log(`✅ ${table.name} mis à jour`);
}

// 3. Exécuter pour chaque table
await linkRecordsToRestaurant(employeesTable, "Restaurant");
await linkRecordsToRestaurant(planningTable, "Restaurant");
await linkRecordsToRestaurant(heuresTable, "Restaurant");

console.log("✅ Migration terminée !");
```

---

## 🧪 DONNÉES DE TEST

### Créer un restaurant de test

**Restaurant 1 : Brasserie Test**
```
Nom Restaurant: Brasserie du Centre
API Key: test_brasserie_2025_abc123
Actif: ✅
Plan: Standard
Email Contact: test@brasserie.fr
Fuseau Horaire: Europe/Paris
Langue: fr
```

**Restaurant 2 : Pizzeria Test**
```
Nom Restaurant: Pizzeria Roma
API Key: test_pizzeria_2025_xyz789
Actif: ✅
Plan: Free
Email Contact: test@pizzeria.fr
Fuseau Horaire: Europe/Paris
Langue: fr
```

### Créer des employés de test

Pour **Brasserie du Centre** :
```
Nom: Sarah Martin
Rôle: Cuisine
E-mail: sarah@brasserie.fr
Restaurant: [Link to Brasserie du Centre]

Nom: Paul Dupont
Rôle: Serveur
E-mail: paul@brasserie.fr
Restaurant: [Link to Brasserie du Centre]
```

Pour **Pizzeria Roma** :
```
Nom: Marco Rossi
Rôle: Pizzaiolo
E-mail: marco@pizzeria.fr
Restaurant: [Link to Pizzeria Roma]

Nom: Luigi Verdi
Rôle: Serveur
E-mail: luigi@pizzeria.fr
Restaurant: [Link to Pizzeria Roma]
```

---

## 🔍 VALIDATION DE LA STRUCTURE

### Checklist de validation

- [ ] Table "Restaurants" existe avec tous les champs
- [ ] Table "API Logs" créée avec tous les champs
- [ ] Champ "Restaurant" ajouté à toutes les tables métier
- [ ] Au moins 2 restaurants de test créés
- [ ] Chaque restaurant a au moins 2 employés
- [ ] Les formules ID ont été mises à jour
- [ ] Les vues recommandées sont créées
- [ ] Script de migration exécuté (si données existantes)

### Test de filtrage

Pour vérifier que le filtrage fonctionne, créer une vue dans "Employés" :

**Vue "Test Isolation - Brasserie"**
- Filtre: Restaurant = Brasserie du Centre
- Résultat attendu: Seulement les employés de la brasserie

**Vue "Test Isolation - Pizzeria"**
- Filtre: Restaurant = Pizzeria Roma
- Résultat attendu: Seulement les employés de la pizzeria

---

## 📊 DASHBOARD AIRTABLE RECOMMANDÉ

### Page 1 : Vue d'ensemble

**Bloc 1 : Statistiques restaurants**
- Type: Number
- Table: Restaurants
- Metric: COUNT(ID)
- Filtre: Actif = ✅

**Bloc 2 : Total API Calls (30 jours)**
- Type: Number
- Table: API Logs
- Metric: COUNT(ID)
- Filtre: Timestamp > Last 30 days

**Bloc 3 : Taux d'erreur**
- Type: Number
- Table: API Logs
- Formula: COUNT(Type=ERROR) / COUNT(ID) * 100
- Format: Percentage

**Bloc 4 : Activité par restaurant**
- Type: Chart (Bar)
- Table: API Logs
- X-axis: Restaurant
- Y-axis: COUNT(ID)
- Groupé par: Type

### Page 2 : Monitoring

**Bloc 1 : Dernières erreurs**
- Type: List
- Table: API Logs
- Filtre: Type = ERROR
- Tri: Timestamp DESC
- Limite: 10

**Bloc 2 : Performance moyenne**
- Type: Chart (Line)
- Table: API Logs
- X-axis: Timestamp (by day)
- Y-axis: AVG(Duration)

**Bloc 3 : Top endpoints lents**
- Type: List
- Table: API Logs
- Tri: Duration DESC
- Limite: 10

---

## 🔐 SÉCURITÉ DES DONNÉES

### Permissions Airtable recommandées

Si vous utilisez Airtable Teams/Enterprise :

**Rôle "Restaurant Owner"**
- Peut voir/éditer uniquement les données de son restaurant
- Filtre automatique: Restaurant = leur restaurant
- Accès aux tables: Employés, Planning, Heures, Dashboard RH
- Pas d'accès à: API Logs, Restaurants

**Rôle "Admin Système"**
- Accès complet à toutes les tables
- Peut créer/modifier des restaurants
- Accès aux logs et au monitoring

**Rôle "Support"**
- Lecture seule sur toutes les tables
- Peut voir les logs d'erreur
- Ne peut pas modifier les données

---

## 🚀 ÉTAPES D'ACTIVATION

1. **Créer la structure Airtable** (1-2h)
   - Créer table API Logs
   - Ajouter champs Restaurant partout
   - Créer les vues recommandées

2. **Migrer les données existantes** (30min - 2h)
   - Exécuter le script de migration
   - Vérifier que tout est lié

3. **Créer les restaurants de test** (15min)
   - 2 restaurants minimum
   - Avec employés de test

4. **Tester l'isolation** (30min)
   - Vérifier les vues filtrées
   - Tester avec différentes API keys

5. **Modifier le workflow n8n** (2-4h)
   - Suivre le MIGRATION_GUIDE.md
   - Tester chaque modification

6. **Tests de bout en bout** (1h)
   - Tester avec chaque restaurant
   - Vérifier les logs
   - Valider l'isolation

**Durée totale estimée : 6-10 heures**

---

## 📞 SUPPORT

En cas de problème :

1. Vérifier la checklist de validation ci-dessus
2. Consulter les logs dans Airtable (table API Logs)
3. Vérifier que le champ "Restaurant" existe partout
4. Tester avec un restaurant de test d'abord

---

**Version** : 1.0
**Dernière mise à jour** : 2025-01-XX
