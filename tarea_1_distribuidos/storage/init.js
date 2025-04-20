// Crear la base de datos y colección si no existen
db = db.getSiblingDB('traffic_data');

// Crear la colección de eventos
db.createCollection('events', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["type", "location", "timestamp"],
      properties: {
        type: {
          bsonType: "string",
          description: "Tipo de evento (ACCIDENT, JAM, etc.)"
        },
        location: {
          bsonType: "string",
          description: "Ubicación del evento"
        },
        timestamp: {
          bsonType: ["long", "int"], 
          description: "Timestamp del evento"
        },
        severity: {
          bsonType: "int",
          minimum: 1,
          maximum: 5,
          description: "Severidad del evento (1-5)"
        },
        description: {
          bsonType: "string",
          description: "Descripción detallada"
        }
      }
    }
  }
});

// Crear índices para mejor rendimiento
db.events.createIndex({ location: 1 });
db.events.createIndex({ timestamp: -1 });
db.events.createIndex({ type: 1, severity: 1 });

print('Base de datos traffic_data y colección events creadas con éxito');
