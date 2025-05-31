-- processing/analyze_data.pig

-- Cargar los datos filtrados y estandarizados del módulo anterior
processed_data = LOAD '/user/waze/filtered_data' USING PigStorage(',') AS (
    uuid:chararray,
    pubMillis:long,
    standardized_type:chararray,
    comuna:chararray,
    description:chararray,
    lat:double,
    lon:double
);

-- 1. Agrupar incidentes por comuna y contar
incidents_by_comuna = GROUP processed_data BY comuna;
count_by_comuna = FOREACH incidents_by_comuna GENERATE
    group AS comuna,
    COUNT(processed_data) AS total_incidents;
STORE count_by_comuna INTO '/user/waze/analysis_results/incidents_by_comuna' USING PigStorage(',');

-- 2. Contar la frecuencia de ocurrencia de los diferentes tipos de incidentes
incidents_by_type = GROUP processed_data BY standardized_type;
count_by_type = FOREACH incidents_by_type GENERATE
    group AS incident_type,
    COUNT(processed_data) AS total_occurrences;
STORE count_by_type INTO '/user/waze/analysis_results/incidents_by_type' USING PigStorage(',');

-- 3. Analizar la evolución temporal (ejemplo: incidentes por día y tipo)
-- Convertir milisegundos a formato de fecha para agrupar por día
temporal_data = FOREACH processed_data GENERATE
    standardized_type,
    comuna,
    ToDate(pubMillis, 'yyyy-MM-dd') AS event_date;

incidents_by_date_type = GROUP temporal_data BY (event_date, standardized_type);
count_by_date_type = FOREACH incidents_by_date_type GENERATE
    group.event_date AS event_date,
    group.standardized_type AS incident_type,
    COUNT(temporal_data) AS daily_occurrences;
STORE count_by_date_type INTO '/user/waze/analysis_results/incidents_by_date_type' USING PigStorage(',');

-- Puedes añadir más análisis aquí, por ejemplo:
-- Incidentes por comuna y tipo
incidents_by_comuna_type = GROUP processed_data BY (comuna, standardized_type);
count_by_comuna_type = FOREACH incidents_by_comuna_type GENERATE
    group.comuna AS comuna,
    group.standardized_type AS incident_type,
    COUNT(processed_data) AS total_occurrences;
STORE count_by_comuna_type INTO '/user/waze/analysis_results/incidents_by_comuna_type' USING PigStorage(',');