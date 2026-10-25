# Simulación de Monte Carlo - Yahtzee

## Descripción

Este proyecto implementa una simulación del juego Yahtzee utilizando el método de Monte Carlo. La simulación permite analizar diferentes estrategias de juego y estudiar el comportamiento de los resultados cuando se realizan múltiples experimentos aleatorios.

El proyecto fue desarrollado para la actividad didáctica del módulo de Simulaciones.

## Objetivo

Aplicar el método de Monte Carlo mediante la simulación de partidas de Yahtzee entre dos jugadores, utilizando cinco dados de seis caras y hasta tres lanzamientos por turno.

Además, se busca analizar la estabilidad de los resultados al aumentar el número de simulaciones y relacionarlos con la Ley de los Grandes Números.

## Modelo probabilístico

Cada dado utilizado en la simulación tiene seis resultados posibles:

- 1
- 2
- 3
- 4
- 5
- 6

Cada resultado tiene la misma probabilidad:

P(X = x) = 1/6

Por lo tanto, se utiliza una distribución uniforme discreta.

## Método de Monte Carlo

La simulación utiliza números aleatorios para generar los lanzamientos de los dados y repite los experimentos una gran cantidad de veces.

El proceso general es:

1. Generar los lanzamientos aleatorios.
2. Evaluar el resultado obtenido.
3. Calcular la puntuación correspondiente.
4. Repetir el experimento miles de veces.
5. Analizar las frecuencias y probabilidades obtenidas.
6. Comparar los resultados simulados con valores teóricos cuando corresponde.

## USA, MODIFICA y CREA

### USA

Se utiliza la estructura base de la simulación de Yahtzee y el modelo probabilístico basado en cinco dados de seis caras.

### MODIFICA

Se incorporan modificaciones para analizar diferentes estrategias de juego y comparar su comportamiento mediante múltiples partidas simuladas.

### CREA

Se crean experimentos adicionales para:

- Verificar la uniformidad de los lanzamientos.
- Estimar la probabilidad de obtener un Yahtzee.
- Comparar estrategias mediante torneos.
- Analizar los resultados estadísticamente.
- Observar la estabilidad de los resultados al realizar muchas simulaciones.

## Estructura del proyecto

```text
yahtzee-montecarlo/
│
├── README.md
│
├── src/
│   └── yahtzee_montecarlo.py
│
├── docs/
│   └── SIMULACION_DE_MONTECARLO.docx
│
└── resultados/
    └── resultados.txt