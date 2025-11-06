# ✅ Checklist de Déploiement Multi-Tenant

## Phase 1 : Préparation (2-3 heures)

### 📊 Airtable Setup

- [ ] **Créer table "API Logs"**
  - [ ] Champs : Restaurant, Timestamp, Type, Endpoint, Message, Request Data, Response Data, Error Stack, Duration
  - [ ] Vues : Dernières erreurs, Performance, Activité par restaurant

- [ ] **Ajouter champ "Restaurant" aux tables existantes**
  - [ ] Employés
  - [ ] Planning Optimisé
  - [ ] Heures des employés
  - [ ] Hebdo Employé
  - [ ] Dashboard RH
  - [ ] Bibliothèque Photos Menu

- [ ] **Créer restaurants de test**
  - [ ] Restaurant 1 : Brasserie Test (API Key: test_brasserie_2025_abc123)
  - [ ] Restaurant 2 : Pizzeria Test (API Key: test_pizzeria_2025_xyz789)

- [ ] **Lier données existantes**
  - [ ] Exécuter script de migration
  - [ ] Vérifier que toutes les données ont un Restaurant

- [ ] **Créer employés de test**
  - [ ] 2 employés minimum par restaurant
  - [ ] Avec emails valides

---

## Phase 2 : Modification Workflow n8n (3-4 heures)

### 🔧 Nœuds de base

- [ ] **Ajouter "Global Error Handler"**
  - [ ] Après "Extraire Restaurant ID"
  - [ ] Code copié depuis `node-codes-ready-to-use.md`
  - [ ] Testé avec un restaurant

- [ ] **Créer "Error Trigger"**
  - [ ] Type: Error Trigger
  - [ ] Connecté à "Format Error Response"

- [ ] **Ajouter "Format Error Response"**
  - [ ] Code copié depuis `node-codes-ready-to-use.md`
  - [ ] Connecté à "Send Error Log" et "Respond Error to Webhook"

### 📝 Modification filtres Airtable

- [ ] **"get employes"**
  - [ ] filterByFormula modifié avec Restaurant
  - [ ] Testé avec les 2 restaurants

- [ ] **"Search records" (Employés)**
  - [ ] filterByFormula avec AND(RID, Restaurant)
  - [ ] Testé

- [ ] **"Search records1" (Hebdo)**
  - [ ] filterByFormula avec AND(Semaine, Restaurant)
  - [ ] Testé

- [ ] **"Search records2" (Hebdo Employé)**
  - [ ] filterByFormula avec AND(Clé, Restaurant)
  - [ ] Testé

- [ ] **"Search records3" (Dashboard RH)**
  - [ ] filterByFormula avec AND(Code Semaine, Restaurant)
  - [ ] Testé

- [ ] **"Get Photo Airtable"**
  - [ ] filterByFormula avec Restaurant
  - [ ] Testé

- [ ] **"Récupérer Tous Employés"**
  - [ ] filterByFormula avec Restaurant
  - [ ] Testé

### ➕ Ajout restaurant_id aux créations

- [ ] **"Create a record" (Planning)**
  - [ ] Champ "Restaurant" ajouté
  - [ ] Valeur: `{{ [$('Global Error Handler').item.json.restaurant_id] }}`
  - [ ] Testé

- [ ] **"Create a record1" (Heures)**
  - [ ] Champ "Restaurant" ajouté
  - [ ] Valeur: `{{ [$('Global Error Handler').item.json.restaurant_id] }}`
  - [ ] Testé

- [ ] **"Create a record2" (Hebdo Employé)**
  - [ ] Champ "Restaurant" ajouté (si existe)
  - [ ] Testé

- [ ] **"Create a record3" (Dashboard RH)**
  - [ ] Champ "Restaurant" ajouté (si existe)
  - [ ] Testé

### 🔍 Wrappers de validation

- [ ] **"Validate Before Create Planning"**
  - [ ] Ajouté AVANT "Create a record"
  - [ ] Code copié depuis `node-codes-ready-to-use.md`
  - [ ] Testé

- [ ] **"Handle Create Planning Success"**
  - [ ] Ajouté APRÈS "Create a record"
  - [ ] Code copié depuis `node-codes-ready-to-use.md`
  - [ ] Testé

- [ ] **"Validate Before Create Hours"**
  - [ ] Ajouté AVANT "Create a record1"
  - [ ] Code copié
  - [ ] Testé

### 📊 Système de logging

- [ ] **"Prepare Log Entry"**
  - [ ] Créé après opérations importantes
  - [ ] Code copié
  - [ ] Connecté à "Log to Airtable"

- [ ] **"Log to Airtable"**
  - [ ] Type: Airtable Create
  - [ ] Table: API Logs
  - [ ] Mapping correct
  - [ ] Testé manuellement

- [ ] **"Send Error Log"**
  - [ ] Créé après "Format Error Response"
  - [ ] Connecté à "Respond Error to Webhook"
  - [ ] Testé avec une erreur

---

## Phase 3 : Tests (2 heures)

### 🧪 Tests de base

- [ ] **Test 1 : API Key invalide**
  - [ ] CURL avec mauvaise key
  - [ ] Résultat : AUTH_ERROR
  - [ ] Log créé dans Airtable (Type: ERROR)

- [ ] **Test 2 : Restaurant 1 valide**
  - [ ] CURL avec API key restaurant 1
  - [ ] Résultat : SUCCESS
  - [ ] Données retournées correctes
  - [ ] Log créé (Type: SUCCESS)

- [ ] **Test 3 : Restaurant 2 valide**
  - [ ] CURL avec API key restaurant 2
  - [ ] Résultat : SUCCESS
  - [ ] Données DIFFÉRENTES de restaurant 1

### 🔐 Tests d'isolation

- [ ] **Isolation employés**
  - [ ] Requête restaurant 1 : Seulement employés R1
  - [ ] Requête restaurant 2 : Seulement employés R2
  - [ ] AUCUN employé en commun

- [ ] **Isolation planning**
  - [ ] Créer planning restaurant 1
  - [ ] Vérifier dans Airtable : Seulement R1
  - [ ] Créer planning restaurant 2
  - [ ] Vérifier : Seulement R2, aucune entrée R1

- [ ] **Isolation logs**
  - [ ] Grouper API Logs par Restaurant
  - [ ] Vérifier que chaque groupe est correct

### ⚡ Tests de performance

- [ ] **Temps de réponse**
  - [ ] 10 requêtes séquentielles
  - [ ] Moyenne < 2 secondes
  - [ ] Aucun timeout

- [ ] **Concurrence**
  - [ ] 10 requêtes simultanées
  - [ ] Toutes retournent 200
  - [ ] Pas de conflit de données

### 🛡️ Tests de sécurité

- [ ] **Tentative cross-restaurant**
  - [ ] Envoyer restaurant_id différent dans body
  - [ ] Système ignore et utilise celui de l'API key

- [ ] **API Key vide**
  - [ ] Requête sans header x-api-key
  - [ ] Résultat : AUTH_ERROR

---

## Phase 4 : Validation finale (1 heure)

### 📋 Vérifications générales

- [ ] **Tous les nœuds Airtable**
  - [ ] Ont un filtre avec {Restaurant}
  - [ ] Aucune exception trouvée

- [ ] **Toutes les créations**
  - [ ] Ajoutent le champ Restaurant
  - [ ] Valeur correcte propagée

- [ ] **Gestion d'erreurs**
  - [ ] Error Trigger actif
  - [ ] Toutes les erreurs loggées
  - [ ] Réponses standardisées

- [ ] **Logs Airtable**
  - [ ] Au moins 1 SUCCESS
  - [ ] Au moins 1 ERROR (testé)
  - [ ] Tous ont un Restaurant

### 🎯 Tests de bout en bout

- [ ] **Scénario complet restaurant 1**
  - [ ] Création planning
  - [ ] Création heures
  - [ ] Email envoyé
  - [ ] Logs corrects

- [ ] **Scénario complet restaurant 2**
  - [ ] Création planning
  - [ ] Données isolées de R1
  - [ ] Logs corrects

---

## Phase 5 : Documentation (30 min)

### 📚 Documentation équipe

- [ ] **Guide utilisateur**
  - [ ] Comment obtenir l'API Key
  - [ ] Comment tester
  - [ ] Que faire en cas d'erreur

- [ ] **Guide développeur**
  - [ ] Architecture du système
  - [ ] Comment ajouter un nouveau restaurant
  - [ ] Comment débugger

- [ ] **Runbook opérations**
  - [ ] Monitoring quotidien
  - [ ] Gestion des erreurs
  - [ ] Escalade

---

## Phase 6 : Mise en production (1 heure)

### 🚀 Préparation

- [ ] **Backup Airtable**
  - [ ] Export de toutes les tables
  - [ ] Sauvegarde locale

- [ ] **Backup workflow n8n**
  - [ ] Export JSON du workflow
  - [ ] Commit dans Git

- [ ] **Configuration production**
  - [ ] Variables d'environnement (si applicable)
  - [ ] Credentials Airtable vérifiées
  - [ ] Webhooks URL finales

### 🎬 Activation

- [ ] **Désactiver ancien workflow**
  - [ ] Si migration d'un existant
  - [ ] Garder accessible en lecture seule

- [ ] **Activer nouveau workflow**
  - [ ] Mode "Active" sur n8n
  - [ ] Tester immédiatement avec API Key prod

- [ ] **Monitoring initial**
  - [ ] Ouvrir dashboard Airtable
  - [ ] Surveiller pendant 30 minutes
  - [ ] Vérifier taux de succès

### 📧 Communication

- [ ] **Informer les restaurants**
  - [ ] Email avec leur API Key
  - [ ] Instructions d'utilisation
  - [ ] Contact support

- [ ] **Informer l'équipe technique**
  - [ ] Système en production
  - [ ] Procédure de support
  - [ ] On-call si nécessaire

---

## Phase 7 : Suivi post-prod (1 semaine)

### 📊 Monitoring quotidien

#### Jour 1
- [ ] Vérifier API Logs toutes les heures
- [ ] Taux de succès > 95%
- [ ] Temps de réponse < 2s
- [ ] Aucune alerte critique

#### Jour 2-3
- [ ] Vérifier API Logs 2x par jour
- [ ] Analyser les erreurs
- [ ] Optimiser si nécessaire

#### Jour 4-7
- [ ] Vérifier API Logs 1x par jour
- [ ] Rapport hebdomadaire
- [ ] Ajustements si besoin

### 🐛 Problèmes à surveiller

- [ ] **Erreurs répétées**
  - [ ] Même endpoint qui fail
  - [ ] Corriger la cause racine

- [ ] **Performance dégradée**
  - [ ] Temps de réponse qui augmente
  - [ ] Optimiser les requêtes

- [ ] **Fuite de données**
  - [ ] Audit d'isolation hebdomadaire
  - [ ] Vérifier logs cross-restaurant

---

## 🎉 Critères de réussite

Le déploiement est considéré comme réussi si :

- ✅ Taux de succès > 95% sur 7 jours
- ✅ Temps de réponse moyen < 2 secondes
- ✅ ZÉRO fuite de données entre restaurants
- ✅ Tous les logs sont créés correctement
- ✅ Aucune erreur critique non résolue
- ✅ Les restaurants utilisent le système sans problème

---

## 📞 Contacts urgence

| Rôle | Nom | Contact | Disponibilité |
|------|-----|---------|---------------|
| Développeur principal | [Nom] | [Email/Tel] | 24/7 semaine 1 |
| Support technique | [Nom] | [Email] | Heures bureau |
| Admin Airtable | [Nom] | [Email] | Heures bureau |
| Responsable n8n | [Nom] | [Email] | Sur appel |

---

## 🔄 Rollback Plan

En cas de problème majeur :

1. **Désactiver le nouveau workflow**
   - [ ] Mode "Inactive" sur n8n

2. **Réactiver l'ancien système**
   - [ ] Si existant

3. **Analyser le problème**
   - [ ] Consulter les logs
   - [ ] Identifier la cause

4. **Corriger hors prod**
   - [ ] Tester en environnement de dev
   - [ ] Valider la correction

5. **Redéployer**
   - [ ] Suivre cette checklist à nouveau

---

**Version** : 1.0
**Dernière mise à jour** : 2025-01-XX
**Temps estimé total** : 10-15 heures
