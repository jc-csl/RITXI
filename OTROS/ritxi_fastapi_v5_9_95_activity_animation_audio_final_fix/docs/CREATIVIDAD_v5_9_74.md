# Creatividad v5.9.74

## Qué se ha conectado

El deslizador controla dos cosas:

1. `temperature` enviada al backend y aplicada en Ollama.
2. Instrucción interna de estilo añadida al texto enviado al modelo.

## Niveles

```text
0.00 - 0.20  precisa
0.25 - 0.55  equilibrada
0.60 - 0.80  variada
0.85 - 1.00  creativa
```

## Verificación visual

Cada burbuja de Ritxi indica:

```text
creatividad: 0.85
```

Si entra fallback local seguro, aparece:

```text
fallback seguro
```

Eso significa que el texto mostrado no viene directamente de Ollama porque la respuesta del modelo estaba vacía o solo contenía una etiqueta.
