-- Cargar datos desde archivo CSV
raw_data = LOAD '/pig/data/raw/events.csv'
    USING PigStorage(',')
    AS (id:chararray, type:chararray, comuna:chararray, timestamp:chararray, description:chararray);

-- Filtro básico: eliminar registros incompletos
filtered = FILTER raw_data BY
    (id IS NOT NULL AND id != '') AND
    (type IS NOT NULL AND type != '') AND
    (comuna IS NOT NULL AND comuna != '') AND
    (timestamp IS NOT NULL AND timestamp != '') AND
    (description IS NOT NULL AND description != '');

-- Normalización: minúsculas y quitar espacios extremos
normalized = FOREACH filtered GENERATE
    id,
    LOWER(TRIM(type)) AS type,
    LOWER(TRIM(comuna)) AS comuna,
    TRIM(timestamp) AS timestamp,
    LOWER(TRIM(description)) AS street;

-- Eliminar duplicados exactos
deduplicated = DISTINCT normalized;

-- Extraer fecha y minuto desde timestamp
with_time = FOREACH deduplicated GENERATE
    id, type, comuna, timestamp, street,
    SUBSTRING(timestamp, 0, 10) AS fecha,
    (INT)SUBSTRING(timestamp, 11, 2) * 60 + (INT)SUBSTRING(timestamp, 14, 2) AS minuto;

-- Agrupar por comuna, tipo, calle, fecha, minuto exacto
grouped = GROUP with_time BY (comuna, type, street, fecha, minuto);

-- Dejar solo un evento representativo por grupo
unique_events = FOREACH grouped {
    one = LIMIT with_time 1;
    GENERATE FLATTEN(one);
};

-- Guardar resultado final
STORE unique_events INTO '/pig/data/clean/clean_events.csv' USING PigStorage(',');