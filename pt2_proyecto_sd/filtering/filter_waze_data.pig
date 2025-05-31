-- filtering/filter_waze_data.pig

-- Registrar el conector MongoDB para Pig
REGISTER /usr/local/pig/lib/mongo-hadoop-core-2.0.2.jar;
REGISTER /usr/local/pig/lib/mongo-hadoop-pig-2.0.2.jar;

-- Definir la URL de conexión a MongoDB con autenticación y los nombres correctos
-- ¡CLAVE! Añadir authSource=admin
SET mongo.job.input.uri 'mongodb://root:example@mongodb:27017/traffic_data.traffic_events?authSource=admin';


-- Cargar los datos desde MongoDB
-- Los datos se cargarán como un mapa (Map) en Pig.
raw_events = LOAD 'mongodb://root:example@mongodb:27017/traffic_data.traffic_events?authSource=admin'
             USING com.mongodb.hadoop.pig.MongoLoader()
             AS (doc:map[]);

-- Proyectar los campos que nos interesan
-- Aquí, la clave es acceder a 'location.coordinates' y luego a los elementos.
projected_events = FOREACH raw_events GENERATE
                     doc#'id' AS event_id:chararray,
                     doc#'event_type' AS type:chararray,
                     doc#'subtype' AS subtype:chararray,
                     doc#'street' AS street:chararray,
                     doc#'city' AS city:chararray,
                     -- Acceder a los elementos del array 'coordinates' dentro del mapa 'location'
                     -- y castarlos a double.
                     doc#'location'#'coordinates' AS coords_tuple:tuple(longitude:double, latitude:double),
                     doc#'timestamp' AS timestamp:chararray;

-- Ahora, extraemos los campos individuales de la tupla coords_tuple
final_projected_events = FOREACH projected_events GENERATE
                         event_id,
                         type,
                         subtype,
                         street,
                         city,
                         coords_tuple.longitude AS longitude,
                         coords_tuple.latitude AS latitude,
                         timestamp;

-- Filtrar eventos. Por ejemplo, solo eventos de tipo 'JAM' (atasco)
filtered_jams = FILTER final_projected_events BY type == 'JAM';

-- Opcional: Para verificar los datos antes de almacenar en HDFS
-- DUMP final_projected_events; -- Descomenta para ver la salida de la proyección
-- DUMP filtered_jams; -- Descomenta para ver la salida del filtro

-- ALMACENAR los datos procesados en HDFS
STORE filtered_jams INTO '/user/hadoop/waze_filtered_events' USING PigStorage();