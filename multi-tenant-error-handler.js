// ============================================
// GESTIONNAIRE D'ERREURS MULTI-TENANT
// À utiliser dans les nœuds Code de n8n
// ============================================

/**
 * Fonction principale de gestion d'erreurs
 * @param {Object} options - Configuration
 * @param {string} options.restaurantId - ID du restaurant (obligatoire)
 * @param {string} options.operation - Nom de l'opération en cours
 * @param {Function} options.fn - Fonction à exécuter
 * @param {Object} options.context - Contexte n8n ($input, $json, etc.)
 * @returns {Object} - Résultat ou erreur formatée
 */
async function executeWithErrorHandling({ restaurantId, operation, fn, context }) {
  const startTime = Date.now();

  // Validation du restaurant_id
  if (!restaurantId) {
    return {
      success: false,
      error: {
        type: 'VALIDATION_ERROR',
        message: 'Restaurant ID manquant',
        code: 'MISSING_RESTAURANT_ID',
        timestamp: new Date().toISOString()
      },
      log: {
        type: 'ERROR',
        operation: operation,
        message: 'Restaurant ID manquant',
        duration: Date.now() - startTime
      }
    };
  }

  try {
    // Exécuter la fonction métier
    const result = await fn();

    // Log de succès
    const duration = Date.now() - startTime;

    return {
      success: true,
      data: result,
      log: {
        type: 'SUCCESS',
        operation: operation,
        message: `${operation} exécuté avec succès`,
        duration: duration,
        restaurantId: restaurantId,
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    const duration = Date.now() - startTime;

    // Catégoriser l'erreur
    const errorType = categorizeError(error);

    // Formater l'erreur
    const formattedError = {
      type: errorType,
      message: error.message || 'Erreur inconnue',
      code: error.code || 'UNKNOWN_ERROR',
      stack: error.stack,
      timestamp: new Date().toISOString(),
      operation: operation
    };

    // Préparer le log
    const logEntry = {
      type: 'ERROR',
      operation: operation,
      message: error.message,
      errorStack: error.stack,
      duration: duration,
      restaurantId: restaurantId,
      timestamp: new Date().toISOString(),
      requestData: JSON.stringify(context.input || {}),
      errorDetails: JSON.stringify(formattedError)
    };

    return {
      success: false,
      error: formattedError,
      log: logEntry
    };
  }
}

/**
 * Catégorise le type d'erreur
 */
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
  if (message.includes('permission') || message.includes('unauthorized')) {
    return 'PERMISSION_ERROR';
  }
  if (message.includes('not found')) {
    return 'NOT_FOUND_ERROR';
  }

  return 'UNKNOWN_ERROR';
}

/**
 * Formatte une réponse standardisée pour le webhook
 */
function formatWebhookResponse({ success, data, error, restaurantId }) {
  const baseResponse = {
    success: success,
    timestamp: new Date().toISOString(),
    restaurantId: restaurantId
  };

  if (success) {
    return {
      ...baseResponse,
      data: data
    };
  } else {
    return {
      ...baseResponse,
      error: {
        type: error.type,
        message: error.message,
        code: error.code,
        // Ne pas exposer le stack trace en production
        ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
      }
    };
  }
}

/**
 * Prépare les données pour le log Airtable
 */
function prepareAirtableLog(logData, restaurantId) {
  return {
    "Restaurant": [restaurantId],
    "Timestamp": logData.timestamp,
    "Type": logData.type,
    "Endpoint": logData.operation || "unknown",
    "Message": logData.message || "",
    "Request Data": logData.requestData || "",
    "Response Data": logData.responseData || "",
    "Error Stack": logData.errorStack || "",
    "Duration": logData.duration || 0
  };
}

/**
 * Extrait le restaurant_id depuis différentes sources
 */
function extractRestaurantId(context) {
  // Essayer plusieurs sources possibles
  const sources = [
    context.$json?.restaurant_id,
    context.$('Extraire Restaurant ID')?.first()?.json?.restaurant_id,
    context.$('Search records4')?.first()?.json?.id,
    context.$input?.first()?.json?.restaurant_id,
    context.restaurant_id
  ];

  for (const source of sources) {
    if (source) return source;
  }

  return null;
}

// ============================================
// EXEMPLES D'UTILISATION
// ============================================

/*
// EXEMPLE 1 : Dans un nœud Code après une opération Airtable

const restaurantId = extractRestaurantId({ $json, $ });

const result = await executeWithErrorHandling({
  restaurantId: restaurantId,
  operation: 'get_employees',
  fn: async () => {
    // Votre logique métier ici
    const employees = $('get employes').all();
    return employees;
  },
  context: { $input, $json }
});

if (!result.success) {
  // Retourner l'erreur au webhook
  return [{
    json: formatWebhookResponse({
      success: false,
      error: result.error,
      restaurantId: restaurantId
    })
  }];
}

// Continuer avec les données
return result.data;
*/

/*
// EXEMPLE 2 : Wrapper pour création Airtable

const restaurantId = extractRestaurantId({ $json, $ });

const result = await executeWithErrorHandling({
  restaurantId: restaurantId,
  operation: 'create_planning',
  fn: async () => {
    const planningData = $json;
    // Ajouter le restaurant_id aux données
    return {
      ...planningData,
      Restaurant: [restaurantId]
    };
  },
  context: { $input, $json }
});

// Log automatique (à envoyer vers Airtable)
const logData = prepareAirtableLog(result.log, restaurantId);

return [{
  json: {
    data: result.data,
    log: logData
  }
}];
*/

// Export des fonctions
module.exports = {
  executeWithErrorHandling,
  formatWebhookResponse,
  prepareAirtableLog,
  extractRestaurantId,
  categorizeError
};
