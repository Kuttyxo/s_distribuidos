-- filter_waze_data.pig (Versión final con UDF Python para parsing robusto - ESQUEMA Y FLUJO CORREGIDOS)

-- Eliminar la línea REGISTER piggybank.jar (ya no es necesaria)
-- REGISTER /usr/local/pig/lib/piggybank.jar;

-- Registrar el script Python como una UDF
REGISTER '/opt/pig_scripts/filtering/json_parser_udf.py' USING jython AS myfuncs;

-- Mantener las configuraciones generales de UTF-8, son buenas prácticas.
SET default_charset 'UTF-8';
SET io.file.default.charset 'UTF-8';
SET mapred.textoutputformat.charset 'UTF-8';
SET mapreduce.textoutputformat.charset 'UTF-8';
SET mapreduce.map.java.opts -Dfile.encoding=UTF-8;
SET mapreduce.reduce.java.opts -Dfile.encoding=UTF-8;
SET textloader.charset 'UTF-8'; 
SET pig.exec.reducers.bytes.per.reducer 1000000000; 
SET pig.logfile /app/pig.log;
SET pig.log4j.properties /app/log4j.properties;



-- ==========================================================
-- CARGAR LOS DATOS COMO LINEAS DE TEXTO Y PARSEAR EL JSON CON UDF PYTHON
-- ==========================================================
-- Cargamos el archivo JSON (que es JSON Lines) como texto plano, una línea por registro.
raw_json_lines = LOAD '/user/hadoop/waze_events_raw.json'
                 USING PigStorage()
                 AS (line:chararray);

-- Usamos la UDF Python para parsear cada línea JSON en una tupla estructurada.
-- Como la UDF ahora devuelve una tupla llamada 'parsed_data', usamos FLATTEN para extraer sus campos.
parsed_and_projected_events = FOREACH raw_json_lines GENERATE
                                FLATTEN(myfuncs.parse_waze_json(line)); -- <<< ¡CAMBIO AQUÍ! (Quitamos el AS y añadimos FLATTEN)

-- Pig inferirá los nombres de los campos de la tupla devuelta por la UDF,
-- que ahora están definidos en el @outputSchema de la UDF.


-- ==============================================================================
-- PASO 1: Filtering y Limpieza (Eliminar incompletos/erróneos)
-- ==============================================================================

-- Filtrar registros donde los campos clave son nulos o vacíos.
-- NOTA: Si parse_waze_json devuelve NULL (ej. por un JSON inválido), toda la tupla es NULL,
-- y esto se filtra automáticamente aquí.
cleaned_events_non_null = FILTER parsed_and_projected_events BY
                          event_id IS NOT NULL AND event_id != '' AND
                          type IS NOT NULL AND type != '' AND
                          city IS NOT NULL AND city != '' AND
                          longitude IS NOT NULL AND latitude IS NOT NULL AND
                          timestamp_ms IS NOT NULL;

cleaned_data_for_dedup = cleaned_events_non_null;


-- ==============================================================================
-- PASO 2: Homogeneización (Eliminar Duplicados)
-- ==============================================================================

homogenized_events = DISTINCT cleaned_data_for_dedup;


-- ==============================================================================
-- PASO 3: Estandarización de Subtipos
-- ==============================================================================

standardized_subtypes = FOREACH homogenized_events GENERATE
                          event_id,
                          type,
                          LOWER(subtype) AS normalized_subtype, -- Convertir a minúsculas
                          street,
                          city,
                          longitude,
                          latitude,
                          timestamp_ms;


-- ==============================================================================
-- PASO 4: Filtrado Final (INCLUIR TODOS LOS TIPOS DESPUÉS DE LA LIMPIEZA)
-- ==============================================================================

-- Simplemente asignamos el alias 'standardized_subtypes' al alias de salida final.
-- Esto significa que todos los eventos que han pasado por la limpieza, deduplicación y estandarización
-- del subtipo serán incluidos.
final_filtered_output = standardized_subtypes;


-- ==============================================================================
-- ALMACENAR los datos procesados en HDFS
-- ==============================================================================

STORE final_filtered_output INTO '/user/hadoop/waze_filtered_events' USING PigStorage();