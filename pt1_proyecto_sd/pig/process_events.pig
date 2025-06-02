-- pig/process_events.pig

cleaned = LOAD '/data/clean/clean_events.csv'
    USING PigStorage(',')
    AS (id:chararray, type:chararray, comuna:chararray, timestamp:chararray, description:chararray);

-- Conteo por comuna
grouped_by_comuna = GROUP cleaned BY comuna;
count_by_comuna = FOREACH grouped_by_comuna GENERATE group AS comuna, COUNT(cleaned) AS total_incidentes;
STORE count_by_comuna INTO '/data/results/por_comuna.csv' USING PigStorage(',');

-- Conteo por tipo de incidente
grouped_by_tipo = GROUP cleaned BY type;
count_by_tipo = FOREACH grouped_by_tipo GENERATE group AS tipo, COUNT(cleaned) AS total_tipo;
STORE count_by_tipo INTO '/data/results/por_tipo.csv' USING PigStorage(',');

-- Conteo por hora (asume timestamp como string con HH:mm:ss)
with_hour = FOREACH cleaned GENERATE
    id, type, comuna, SUBSTRING(timestamp, 11, 2) AS hora;

grouped_by_hour = GROUP with_hour BY hora;
count_by_hour = FOREACH grouped_by_hour GENERATE group AS hora, COUNT(with_hour) AS total_hora;
STORE count_by_hour INTO '/data/results/por_hora.csv' USING PigStorage(',');
