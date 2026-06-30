# 09 — v0.4.42: Memory estable tipo v0.34

## Motivo

La secuencia añadida en versiones posteriores separaba demasiado el proceso:

```text
1. Reachy decía "Vamos a ver..."
2. Después debía llamar a la herramienta
```

En la práctica podía ocurrir que Reachy hablara pero no llegara a girar las cartas.

## Corrección

Se vuelve a un comportamiento más estable:

```text
- Si el usuario dice dos números, se llama inmediatamente a choose_memory_cards.
- La herramienta gira las cartas enseguida.
- Después Reachy reacciona.
- La frase "Vamos a ver la X y la Y" forma parte de la respuesta de la herramienta, no bloquea el giro.
```

## Resultado esperado

```text
Usuario: uno y tres
Cartas: se giran enseguida
Reachy: reacciona una sola vez
```

## Lo que se mantiene

```text
- cartas visibles 4 segundos si falla;
- reacción única;
- estilo visual de Memory;
- voz Sohee;
- documentación limpia;
- tests en /test.
```
