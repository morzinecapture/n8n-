#!/usr/bin/env python3
"""
Script automatique pour convertir un workflow n8n en multi-tenant
Usage: python3 auto_convert_multitenant.py workflow.json
"""

import json
import sys
import os
from copy import deepcopy

def add_global_error_handler(workflow):
    """Ajoute le nœud Global Error Handler si absent"""

    nodes = workflow.get('nodes', [])

    # Vérifier si déjà présent
    has_handler = any(n.get('name') == 'Global Error Handler' for n in nodes)
    if has_handler:
        print("✅ Global Error Handler déjà présent")
        return workflow

    # Trouver le nœud Extract Restaurant ID
    extract_node = None
    extract_index = None
    for i, node in enumerate(nodes):
        if node.get('id') == '19bde283-19d4-450b-a013-ee706345464e':
            extract_node = node
            extract_index = i
            break

    if not extract_node:
        print("⚠️ Nœud 'Extract Restaurant ID' non trouvé - ajout manuel nécessaire")
        return workflow

    # Créer le nœud Global Error Handler
    handler_node = {
        "parameters": {
            "jsCode": """const input = $input.first().json;
const restaurantId = input.restaurant_id;
const restaurantName = input.restaurant_name || '';

if (!restaurantId) {
  console.error('❌ Restaurant ID manquant');
  throw new Error('Restaurant non identifié');
}

const globalContext = {
  restaurant_id: restaurantId,
  restaurant_name: restaurantName,
  originalRequest: input.originalBody || {},
  originalHeaders: input.originalHeaders || {},
  chatInput: input.chatInput || '',
  timestamp: new Date().toISOString(),
  requestId: `${restaurantId}_${Date.now()}`
};

console.log(`✅ [${restaurantName}] Contexte initialisé`);

return [{ json: globalContext }];"""
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [
            extract_node['position'][0] + 224,
            extract_node['position'][1]
        ],
        "id": "global-error-handler-AUTO",
        "name": "Global Error Handler"
    }

    # Insérer après Extract Restaurant ID
    nodes.insert(extract_index + 1, handler_node)

    # Modifier les connexions
    connections = workflow.get('connections', {})

    # Trouver la connexion sortante d'Extract Restaurant ID
    extract_conn = connections.get('Extract Restaurant ID', {})
    original_target = extract_conn.get('main', [[]])[0][0] if extract_conn.get('main') else None

    # Rediriger Extract → Global Error Handler
    connections['Extract Restaurant ID'] = {
        "main": [[{"node": "Global Error Handler", "type": "main", "index": 0}]]
    }

    # Global Error Handler → ancienne cible
    if original_target:
        connections['Global Error Handler'] = {
            "main": [[original_target]]
        }

    print("✅ Global Error Handler ajouté")
    return workflow


def add_restaurant_filters(workflow):
    """Ajoute les filtres Restaurant à tous les nœuds Airtable Search"""

    nodes = workflow.get('nodes', [])
    modified_count = 0

    for node in nodes:
        if node.get('type') != 'n8n-nodes-base.airtable':
            continue

        params = node.get('parameters', {})

        # Modifier les SEARCH
        if params.get('operation') == 'search':
            formula = params.get('filterByFormula', '=')

            # Si pas de filtre restaurant déjà
            if '{Restaurant}' not in formula and 'Global Error Handler' not in formula:
                if formula == '=' or formula == '':
                    # Remplacer le filtre vide
                    params['filterByFormula'] = "={Restaurant} = '{{ $('Global Error Handler').item.json.restaurant_id }}'"
                    modified_count += 1
                    print(f"✅ Filtre ajouté: {node.get('name')}")
                else:
                    # Ajouter AND au filtre existant
                    clean_formula = formula[1:] if formula.startswith('=') else formula
                    params['filterByFormula'] = f"=AND({clean_formula}, {{Restaurant}} = '{{{{ $('Global Error Handler').item.json.restaurant_id }}}}')"
                    modified_count += 1
                    print(f"✅ Filtre AND ajouté: {node.get('name')}")

    print(f"\n📊 Total filtres ajoutés: {modified_count}")
    return workflow


def add_restaurant_to_creates(workflow):
    """Ajoute le champ Restaurant aux créations Airtable"""

    nodes = workflow.get('nodes', [])
    modified_count = 0

    for node in nodes:
        if node.get('type') != 'n8n-nodes-base.airtable':
            continue

        params = node.get('parameters', {})

        # Modifier les CREATE
        if params.get('operation') == 'create':
            columns = params.get('columns', {})
            value = columns.get('value', {})

            # Ajouter Restaurant si absent
            if 'Restaurant' not in value:
                value['Restaurant'] = "={{ [$('Global Error Handler').item.json.restaurant_id] }}"
                modified_count += 1
                print(f"✅ Restaurant ajouté: {node.get('name')}")

    print(f"\n📊 Total créations modifiées: {modified_count}")
    return workflow


def validate_workflow(workflow):
    """Valide que toutes les modifications sont correctes"""

    nodes = workflow.get('nodes', [])

    # Vérifier Global Error Handler
    has_handler = any(n.get('name') == 'Global Error Handler' for n in nodes)
    if not has_handler:
        print("❌ Global Error Handler manquant")
        return False

    # Compter les nœuds modifiés
    search_count = 0
    search_with_filter = 0
    create_count = 0
    create_with_restaurant = 0

    for node in nodes:
        if node.get('type') != 'n8n-nodes-base.airtable':
            continue

        params = node.get('parameters', {})

        if params.get('operation') == 'search':
            search_count += 1
            formula = params.get('filterByFormula', '')
            if '{Restaurant}' in formula or 'Global Error Handler' in formula:
                search_with_filter += 1

        elif params.get('operation') == 'create':
            create_count += 1
            value = params.get('columns', {}).get('value', {})
            if 'Restaurant' in value:
                create_with_restaurant += 1

    print("\n📊 Validation:")
    print(f"  - Search Airtable: {search_with_filter}/{search_count} avec filtre")
    print(f"  - Create Airtable: {create_with_restaurant}/{create_count} avec Restaurant")

    if search_with_filter < search_count:
        print(f"⚠️ {search_count - search_with_filter} nœuds Search sans filtre Restaurant")

    if create_with_restaurant < create_count:
        print(f"⚠️ {create_count - create_with_restaurant} nœuds Create sans champ Restaurant")

    return True


def main():
    if len(sys.argv) < 2:
        print("""
🔧 Convertisseur Multi-Tenant pour n8n

Usage:
  python3 auto_convert_multitenant.py workflow.json

Résultat:
  - Crée workflow_MULTITENANT.json
  - Ajoute Global Error Handler
  - Ajoute filtres Restaurant aux recherches
  - Ajoute champ Restaurant aux créations

Importez ensuite dans n8n !
        """)
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"❌ Fichier non trouvé: {input_file}")
        sys.exit(1)

    print(f"\n🚀 Conversion en multi-tenant de: {input_file}\n")

    # Charger le workflow
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"❌ Erreur de lecture: {e}")
        sys.exit(1)

    # Faire une copie
    workflow_modified = deepcopy(workflow)

    # Appliquer les modifications
    print("📝 Étape 1: Ajout Global Error Handler...")
    workflow_modified = add_global_error_handler(workflow_modified)

    print("\n📝 Étape 2: Ajout filtres Restaurant aux recherches...")
    workflow_modified = add_restaurant_filters(workflow_modified)

    print("\n📝 Étape 3: Ajout Restaurant aux créations...")
    workflow_modified = add_restaurant_to_creates(workflow_modified)

    # Valider
    print("\n📝 Étape 4: Validation...")
    validate_workflow(workflow_modified)

    # Sauvegarder
    output_file = input_file.replace('.json', '_MULTITENANT.json')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_modified, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Fichier créé: {output_file}")
        print(f"📁 Taille: {os.path.getsize(output_file) / 1024:.1f} KB")
        print("\n🎉 Conversion terminée !")
        print(f"\n📥 Importez {output_file} dans n8n")

    except Exception as e:
        print(f"❌ Erreur de sauvegarde: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
