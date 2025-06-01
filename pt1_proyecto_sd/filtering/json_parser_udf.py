# -*- coding: utf-8 -*-
# json_parser_udf.py (VERSION FINAL FINAL FINAL PARA EL ESQUEMA Y CODIFICACIÓN)
import json

# Define el esquema de salida como UNA SOLA TUPLA que contiene todos los campos.
# Esto es lo que Pig espera cuando una UDF devuelve múltiples valores lógicos.
@outputSchema("parsed_data:tuple(event_id:chararray,type:chararray,subtype:chararray,street:chararray,city:chararray,longitude:double,latitude:double,timestamp_ms:long)")
def parse_waze_json(json_string):
    """
    Parses a single JSON string (from Waze) into a Pig tuple.
    Handles missing fields by returning None.
    """
    try:
        data = json.loads(json_string)

        event_id = data.get('id')
        event_type = data.get('event_type')
        subtype = data.get('subtype')
        street = data.get('street')
        city = data.get('city')
        timestamp_ms = data.get('timestamp')

        location = data.get('location', {})
        coordinates = location.get('coordinates', [])
        longitude = coordinates[0] if len(coordinates) > 0 else None
        latitude = coordinates[1] if len(coordinates) > 1 else None

        # Devuelve los campos en el ORDEN exacto del @outputSchema y con los VALORES correctos
        return (event_id, event_type, subtype, street, city, longitude, latitude, timestamp_ms)
    except Exception as e:
        # Puedes imprimir el error para depuración si es necesario
        # print(f"Error parsing JSON: {e} - Data: {json_string}")
        return None # Devuelve None si el parsing falla