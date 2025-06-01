-- processing/process_waze_data.pig

-- REGISTRO DE LIBRERÍAS
-- Registrar Piggybank para funciones de fecha/hora avanzadas.
-- Verifica si este JAR está en tu contenedor en /usr/local/pig/
REGISTER /usr/local/pig/piggybank.jar;


-- ==============================================================================
-- CARGAR DATOS LIMPIOS Y HOMOGENEIZADOS
-- ==============================================================================

-- Cargar los datos que fueron filtrados y homogeneizados por filter_waze_data.pig
-- Los datos están en HDFS en '/user/hadoop/waze_filtered_events'
-- Asegúrate de que el esquema coincida con la salida de filter_waze_data.pig
-- El campo 'subtype' ahora será 'normalized_subtype' debido a la transformación en el script de filtrado.
clean_events = LOAD '/user/hadoop/waze_filtered_events' USING PigStorage()
               AS (event_id:chararray,
                   type:chararray,
                   normalized_subtype:chararray, -- Asumimos que filter_waze_data.pig lo llamó así
                   street:chararray,
                   city:chararray,
                   longitude:double,
                   latitude:double,
                   timestamp_ms:long); -- UNIX timestamp en milisegundos


-- ==============================================================================
-- ANÁLISIS 1: Agrupar incidentes por comuna y contar el total
-- Objetivo: Identificar patrones geográficos y volumen por área.
-- ==============================================================================

-- Agrupar todos los eventos limpios por el campo 'city' (comuna)
grouped_by_city = GROUP clean_events BY city;

-- Para cada comuna, contar el número total de incidentes
incidents_per_city = FOREACH grouped_by_city GENERATE
                       group AS city_name,
                       COUNT(clean_events) AS total_incidents;

-- Ordenar los resultados por el número de incidentes de forma descendente
sorted_incidents_per_city = ORDER incidents_per_city BY total_incidents DESC;

-- DUMP sorted_incidents_per_city; -- Descomenta para ver la salida por consola
STORE sorted_incidents_per_city INTO '/user/hadoop/waze_analysis/incidents_by_city' USING PigStorage();


-- ==============================================================================
-- ANÁLISIS 2: Contar la frecuencia de ocurrencia de los diferentes tipos de incidentes
-- Objetivo: Entender qué tipos de incidentes son más comunes.
-- ==============================================================================

-- Agrupar todos los eventos limpios por el campo 'type' (tipo principal de incidente)
grouped_by_type = GROUP clean_events BY type;

-- Para cada tipo de incidente, contar su frecuencia global
type_frequency = FOREACH grouped_by_type GENERATE
                   group AS event_type,
                   COUNT(clean_events) AS frequency;

-- Ordenar los resultados por frecuencia de forma descendente
sorted_type_frequency = ORDER type_frequency BY frequency DESC;

-- DUMP sorted_type_frequency; -- Descomenta para ver la salida por consola
STORE sorted_type_frequency INTO '/user/hadoop/waze_analysis/type_frequency' USING PigStorage();


-- Opcional: Contar frecuencia de subtipos también (si 'normalized_subtype' es relevante)
grouped_by_subtype = GROUP clean_events BY normalized_subtype;
subtype_frequency = FOREACH grouped_by_subtype GENERATE
                      group AS event_subtype,
                      COUNT(clean_events) AS frequency;
-- DUMP subtype_frequency;
STORE subtype_frequency INTO '/user/hadoop/waze_analysis/subtype_frequency' USING PigStorage();


-- ==============================================================================
-- ANÁLISIS 3: Analizar la evolución temporal de los incidentes
-- Objetivo: Identificar tendencias y picos en momentos específicos.
-- ==============================================================================

-- Convertir timestamp_ms (long) a un tipo de fecha Pig para usar funciones de tiempo.
-- Usaremos la función ToDate de Piggybank y luego ToString para extraer el formato deseado.
-- (long) timestamp_ms / 1000 porque ToDate espera segundos, no milisegundos.

-- Análisis por hora del día (para ver patrones diarios)
events_with_hourly_info = FOREACH clean_events GENERATE
                            type,
                            city,
                            ToString(ToDate(timestamp_ms / 1000L), 'HH') AS hour_of_day; -- 'HH' para hora (00-23)

grouped_by_hour_type_city = GROUP events_with_hourly_info BY (hour_of_day, type, city);

hourly_trends = FOREACH grouped_by_hour_type_city GENERATE
                  FLATTEN(group) AS (hour_of_day, event_type, city_name),
                  COUNT(events_with_hourly_info) AS incident_count;

sorted_hourly_trends = ORDER hourly_trends BY hour_of_day ASC, incident_count DESC;

-- DUMP sorted_hourly_trends; -- Descomenta para ver la salida por consola
STORE sorted_hourly_trends INTO '/user/hadoop/waze_analysis/hourly_trends' USING PigStorage();


-- Análisis por día de la semana (para ver patrones semanales)
events_with_daily_info = FOREACH clean_events GENERATE
                           type,
                           city,
                           -- Usa GetDayOfWeek de Piggybank (devuelve 0 para lunes, 1 para martes, etc.)
                           ToString(ToDate(timestamp_ms / 1000L), 'EEEE') AS day_of_week_name, -- ej. "Monday"
                           ToString(ToDate(timestamp_ms / 1000L), 'yyyy-MM-dd') AS event_date;


grouped_by_day_type_city = GROUP events_with_daily_info BY (day_of_week_name, type, city);

daily_trends = FOREACH grouped_by_day_type_city GENERATE
                 FLATTEN(group) AS (day_of_week, event_type, city_name),
                 COUNT(events_with_daily_info) AS incident_count;

-- Ordenar por día de la semana (si quieres un orden específico, necesitarías un mapeo numérico)
-- Por ahora, orden alfabético por nombre del día
sorted_daily_trends = ORDER daily_trends BY day_of_week ASC, incident_count DESC;

-- DUMP sorted_daily_trends; -- Descomenta para ver la salida por consola
STORE sorted_daily_trends INTO '/user/hadoop/waze_analysis/daily_trends' USING PigStorage();


-- Opcional: Análisis por día (ej. para ver tendencias a lo largo del tiempo)
events_with_date_info = FOREACH clean_events GENERATE
                          type,
                          city,
                          ToString(ToDate(timestamp_ms / 1000L), 'yyyy-MM-dd') AS event_date;

grouped_by_date_type_city = GROUP events_with_date_info BY (event_date, type, city);

date_trends = FOREACH grouped_by_date_type_city GENERATE
                FLATTEN(group) AS (event_date, event_type, city_name),
                COUNT(events_with_date_info) AS incident_count;

sorted_date_trends = ORDER date_trends BY event_date ASC, incident_count DESC;

-- DUMP sorted_date_trends;
STORE sorted_date_trends INTO '/user/hadoop/waze_analysis/date_trends' USING PigStorage();