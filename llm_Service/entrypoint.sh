#!/bin/bash

# Iniciar Ollama en segundo plano
ollama serve &

# Esperar a que el servicio esté disponible
echo "Esperando a que Ollama inicie..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
  sleep 2
done

# Descargar el modelo especificado
echo "Descargando el modelo $MODEL_NAME..."
ollama pull $MODEL_NAME

# Mantener el proceso principal en primer plano para que el contenedor no se cierre
wait