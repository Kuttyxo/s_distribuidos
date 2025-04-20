# Usamos la imagen oficial de MongoDB
FROM mongo:latest

# Copiamos el script de inicialización
COPY init.js /docker-entrypoint-initdb.d/

# Exponemos el puerto estándar de MongoDB
EXPOSE 27017

# Comando por defecto (ya está definido en la imagen base)
CMD ["mongod"]
