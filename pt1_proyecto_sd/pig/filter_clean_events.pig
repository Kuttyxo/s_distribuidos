-- pig/filter_clean_events.pig

raw_data = LOAD '/pig/data/raw/events.csv'
    USING PigStorage(',')
    AS (id:chararray, type:chararray, comuna:chararray, timestamp:chararray, description:chararray);

cleaned = FILTER raw_data BY
    (id IS NOT NULL AND id != '') AND
    (type IS NOT NULL AND type != '') AND
    (comuna IS NOT NULL AND comuna != '');

STORE cleaned INTO '/pig/data/clean/clean_events.csv' USING PigStorage(',');
