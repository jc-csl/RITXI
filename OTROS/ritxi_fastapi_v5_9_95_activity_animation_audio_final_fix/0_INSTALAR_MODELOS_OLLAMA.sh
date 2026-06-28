#!/usr/bin/env bash
set -e

echo "============================================================"
echo " RITXI - INSTALADOR DE OLLAMA Y MODELOS DE LENGUAJE"
echo "============================================================"
echo
echo "Modelos recomendados:"
echo "  Rapido        - qwen3:0.6b"
echo "  Equilibrado   - gemma3:1b"
echo "  Llama rapido  - llama3.2:1b"
echo "  Calidad       - llama3.2:3b"
echo

if ! command -v ollama >/dev/null 2>&1; then
  echo "[Ritxi] Ollama no está instalado. Instalando con el instalador oficial..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "[Ritxi] Ollama encontrado."
fi

echo
echo "[Ritxi] Modelos actuales:"
ollama list || true

echo
echo "[Ritxi] Instalando modelos recomendados..."
ollama pull qwen3:0.6b
ollama pull gemma3:1b
ollama pull llama3.2:1b
ollama pull llama3.2:3b

echo
echo "============================================================"
echo " Modelos instalados / disponibles"
echo "============================================================"
ollama list
echo
echo "[Ritxi] Recomendado por defecto para Ritxi: gemma3:1b"
