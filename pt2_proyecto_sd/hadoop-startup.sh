#!/bin/bash
# Script para iniciar los servicios de Hadoop y Pig

# Formatear NameNode solo si es la primera vez
# Comprueba si el directorio del NameNode está vacío
if [ -z "$(ls -A /usr/local/hadoop/hdfs/namenode)" ]; then
  echo "Formateando NameNode de HDFS..."
  hdfs namenode -format -force -nonInteractive
fi

# Iniciar NameNode
hdfs --daemon start namenode

# Iniciar DataNode
hdfs --daemon start datanode

# Iniciar ResourceManager
yarn --daemon start resourcemanager

# Iniciar NodeManager
yarn --daemon start nodemanager

echo "Hadoop y Pig Master listos."

# Mantener el contenedor en ejecución
tail -f /dev/null