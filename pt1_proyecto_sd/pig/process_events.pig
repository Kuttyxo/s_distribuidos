cleaned = LOAD 'data/clean/clean_events.csv'
    USING PigStorage(',')
    AS (id:chararray, type:chararray, comuna:chararray, timestamp:chararray, description:chararray);

-- ====================
-- 1. Por comuna
-- ====================
grouped_by_comuna = GROUP cleaned BY comuna;
count_by_comuna = FOREACH grouped_by_comuna GENERATE group AS comuna, COUNT(cleaned) AS total_incidentes;
STORE count_by_comuna INTO 'data/results/por_comuna' USING PigStorage(',');

-- ====================
-- 2. Por tipo de incidente
-- ====================
grouped_by_tipo = GROUP cleaned BY type;
count_by_tipo = FOREACH grouped_by_tipo GENERATE group AS tipo, COUNT(cleaned) AS total_tipo;
STORE count_by_tipo INTO 'data/results/por_tipo' USING PigStorage(',');

-- ====================
-- 3. Por hora del día
-- ====================
with_hour = FOREACH cleaned GENERATE
    id, type, comuna, SUBSTRING(timestamp, 11, 2) AS hora;

grouped_by_hour = GROUP with_hour BY hora;
count_by_hour = FOREACH grouped_by_hour GENERATE group AS hora, COUNT(with_hour) AS total_hora;
STORE count_by_hour INTO 'data/results/por_hora' USING PigStorage(',');

-- ====================
-- 4. Evolución temporal diaria
-- ====================
-- Asume timestamp en formato "YYYY-MM-DD HH:mm:ss"
with_day = FOREACH cleaned GENERATE
    id, type, comuna, SUBSTRING(timestamp, 0, 10) AS fecha;

grouped_by_day = GROUP with_day BY fecha;
count_by_day = FOREACH grouped_by_day GENERATE group AS fecha, COUNT(with_day) AS total_incidentes_dia;
STORE count_by_day INTO 'data/results/por_dia' USING PigStorage(',');

-- ====================
-- 5. Tipo + comuna combinados
-- ====================
by_tipo_comuna = FOREACH cleaned GENERATE comuna, type;
grouped_by_pair = GROUP by_tipo_comuna BY (comuna, type);
count_by_pair = FOREACH grouped_by_pair GENERATE
    group.$0 AS comuna,
    group.$1 AS tipo,
    COUNT(by_tipo_comuna) AS total;
STORE count_by_pair INTO 'data/results/por_comuna_tipo' USING PigStorage(',');
