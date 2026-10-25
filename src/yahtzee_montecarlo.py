# -*- coding: utf-8 -*-
"""
YAHTZEE CLÁSICO (2 JUGADORES) + MÉTODO DE MONTECARLO - versión 2

Modelo: cada dado ~ Uniforme discreta {1..6}, P(X=k)=1/6, dados independientes.
Estructuras: list (dados), Counter (frecuencias), dict (tabla), set (casillas libres).
Nota: en Yahtzee los jugadores NO interactúan; cada partida son dos puntajes independientes.

USA:      reglas base del juego y el generador pseudoaleatorio de Python.
MODIFICA: generador con semilla (reproducible); reglas completas (bonus de 100 y comodín).
CREA:     p-valor exacto + réplicas de la prueba de uniformidad, P(Yahtzee) teórica exacta
          por enumeración, calibración Monte Carlo de la estrategia, torneos con IC 95 %.
"""

import random
import math
import statistics
import os
import sys
from contextlib import redirect_stdout
from collections import Counter
from fractions import Fraction
from itertools import product


# ---------------------------------------------------------------------------
# CONSTANTES DEL JUEGO
# ---------------------------------------------------------------------------

NUM_DADOS, NUM_CARAS, MAX_LANZ = 5, 6, 3

SUPERIORES = [
    "unos",
    "doses",
    "treses",
    "cuatros",
    "cincos",
    "seises"
]

CATEGORIAS = SUPERIORES + [
    "trio",
    "poker",
    "full",
    "escala_corta",
    "escala_larga",
    "yahtzee",
    "azar"
]

FIJOS = {
    "full": 25,
    "escala_corta": 30,
    "escala_larga": 40,
    "yahtzee": 50
}


# ---------------------------------------------------------------------------
# MODELO Y REGLAS
# ---------------------------------------------------------------------------

def lanzar(n, rng):
    """Simula n dados uniformes en {1..6}."""
    return [rng.randint(1, NUM_CARAS) for _ in range(n)]


def racha(dados):
    """Longitud de la secuencia consecutiva más larga entre las caras distintas."""
    caras = sorted(set(dados))
    mejor = actual = 1

    for a, b in zip(caras, caras[1:]):
        actual = actual + 1 if b == a + 1 else 1
        mejor = max(mejor, actual)

    return mejor


def puntuar(cat, dados, comodin=False):
    """Puntos de anotar dados en una categoría."""
    f, total = Counter(dados), sum(dados)
    m = max(f.values())

    if cat in SUPERIORES:
        n = SUPERIORES.index(cat) + 1
        return n * f[n]

    if cat == "azar":
        return total

    if cat == "trio":
        return total if m >= 3 else 0

    if cat == "poker":
        return total if m >= 4 else 0

    if cat == "full":
        ok = comodin or sorted(f.values()) == [2, 3]

    elif cat == "escala_corta":
        ok = comodin or racha(dados) >= 4

    elif cat == "escala_larga":
        ok = comodin or racha(dados) == 5

    elif cat == "yahtzee":
        ok = m == 5

    else:
        raise ValueError(cat)

    return FIJOS[cat] if ok else 0


def opciones(dados, libres):
    """Casillas permitidas y aplicación del comodín."""
    if len(set(dados)) == 1 and "yahtzee" not in libres:

        sup = SUPERIORES[dados[0] - 1]

        if sup in libres:
            return [sup], True

        inf = sorted(
            c for c in libres
            if c not in SUPERIORES
        )

        return (inf or sorted(libres)), True

    return sorted(libres), False


# ---------------------------------------------------------------------------
# ESTRATEGIAS
# ---------------------------------------------------------------------------

def conservar(dados, estrategia, rng):
    """Dados que se guardan antes de relanzar."""
    f = Counter(dados)

    top = max(
        f,
        key=lambda c: (f[c], c)
    )

    if estrategia == "aleatoria":
        return [
            d for d in dados
            if rng.random() < 0.5
        ]

    if estrategia == "julian":

        if any(
            puntuar(c, dados)
            for c in ("full", "escala_larga", "yahtzee")
        ):
            return list(dados)

        ventana = max(
            ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}),
            key=lambda w: len(w & set(dados))
        )

        if f[top] <= 2 and len(
            ventana & set(dados)
        ) >= 4:

            return sorted(
                ventana & set(dados)
            )

    return [
        d for d in dados
        if d == top
    ]


def elegir(dados, libres, estrategia, rng, ref):
    """Selecciona la casilla donde anotar el turno."""
    cats, joker = opciones(
        dados,
        libres
    )

    if estrategia == "aleatoria":
        return rng.choice(cats), joker

    if estrategia == "july":
        clave = lambda c: puntuar(
            c,
            dados,
            joker
        )

    else:
        clave = lambda c: (
            puntuar(c, dados, joker) - ref[c]
        )

    return max(cats, key=clave), joker


# ---------------------------------------------------------------------------
# TURNO Y PARTIDA
# ---------------------------------------------------------------------------

def lanzamientos(estrategia, rng):
    """Hasta 3 lanzamientos de un turno."""
    dados = lanzar(
        NUM_DADOS,
        rng
    )

    for _ in range(MAX_LANZ - 1):

        guardar = conservar(
            dados,
            estrategia,
            rng
        )

        if len(guardar) == NUM_DADOS:
            break

        dados = (
            guardar
            + lanzar(
                NUM_DADOS - len(guardar),
                rng
            )
        )

    return dados


def jugar_partida(
    estrategias,
    rng,
    ref,
    verbose=False
):
    """Partida de 2 jugadores de 13 rondas."""

    tablas = [
        {},
        {}
    ]

    libres = [
        set(CATEGORIAS),
        set(CATEGORIAS)
    ]

    bonos = [
        0,
        0
    ]

    for ronda in range(1, 14):

        for j in (0, 1):

            dados = lanzamientos(
                estrategias[j],
                rng
            )

            cat, joker = elegir(
                dados,
                libres[j],
                estrategias[j],
                rng,
                ref
            )

            pts = puntuar(
                cat,
                dados,
                joker
            )

            if (
                joker
                and tablas[j]["yahtzee"] == 50
            ):
                bonos[j] += 100

            tablas[j][cat] = pts

            libres[j].remove(cat)

            if verbose:
                print(
                    f"  R{ronda:2d} "
                    f"J{j + 1} "
                    f"{sorted(dados)} "
                    f"-> {cat}: {pts}"
                )

    totales = []

    for t, b in zip(tablas, bonos):

        sup = sum(
            t[c]
            for c in SUPERIORES
        )

        totales.append(
            sum(t.values())
            + (35 if sup >= 63 else 0)
            + b
        )

    return totales


# ---------------------------------------------------------------------------
# MONTE CARLO
# ---------------------------------------------------------------------------

def ic95(p, n):
    """Intervalo de confianza 95 % para una proporción."""
    e = 1.96 * math.sqrt(
        p * (1 - p) / n
    )

    return (
        max(0, p - e),
        min(1, p + e)
    )


def pvalor_chi2_5gl(x):
    """
    P(chi2_5 >= x):
    fórmula cerrada para 5 grados de libertad.
    """
    return (
        math.erfc(
            math.sqrt(x / 2)
        )
        + math.sqrt(
            2 * x / math.pi
        )
        * math.exp(-x / 2)
        * (1 + x / 3)
    )


def chi2_uniforme(n, rng):
    """
    Chi-cuadrado de bondad de ajuste
    a la distribución uniforme.
    """

    esp = n / NUM_CARAS

    assert esp >= 5, (
        "Chi-cuadrado exige frecuencia "
        "esperada >= 5 por celda"
    )

    obs = Counter(
        lanzar(n, rng)
    )

    chi2 = sum(
        (
            obs[k] - esp
        ) ** 2 / esp
        for k in range(
            1,
            NUM_CARAS + 1
        )
    )

    return (
        chi2,
        pvalor_chi2_5gl(chi2)
    )


def exp_uniformidad(rng, reps=2000):
    """
    Comprueba que el generador
    se comporte como una distribución uniforme.
    """

    chi2, p = chi2_uniforme(
        600_000,
        rng
    )

    print(
        f"[1] Uniformidad: "
        f"n=600,000 -> "
        f"chi2={chi2:.2f}, "
        f"p-valor={p:.3f}"
    )

    rech = sum(
        chi2_uniforme(
            600,
            rng
        )[1] < 0.05
        for _ in range(reps)
    )

    f = rech / reps

    lo, hi = ic95(
        f,
        reps
    )

    ok = (
        lo <= 0.05 <= hi
    )

    print(
        f"    {reps} réplicas "
        f"(n=600): "
        f"rechazos={f:.3f} "
        f"[IC95 {lo:.3f}-{hi:.3f}] "
        f"-> "
        f"{'consistente con alfa=0.05' if ok else 'INCONSISTENTE'}"
    )


def yahtzee_exacto():
    """
    Calcula la probabilidad teórica exacta
    de obtener Yahtzee en 3 lanzamientos
    usando la estrategia codiciosa.
    """

    p = Counter()

    for t in product(
        range(NUM_CARAS),
        repeat=NUM_DADOS
    ):

        p[
            max(
                Counter(t).values()
            )
        ] += Fraction(
            1,
            NUM_CARAS ** NUM_DADOS
        )

    for _ in range(
        MAX_LANZ - 1
    ):

        nuevo = Counter()

        for k, pk in p.items():

            if k == NUM_DADOS:
                nuevo[k] += pk
                continue

            n = NUM_DADOS - k

            for t in product(
                range(NUM_CARAS),
                repeat=n
            ):

                m = max(
                    Counter(
                        (0,) * k + t
                    ).values()
                )

                nuevo[m] += (
                    pk
                    * Fraction(
                        1,
                        NUM_CARAS ** n
                    )
                )

        p = nuevo

    return p[NUM_DADOS]


def exp_yahtzee(
    rng,
    n=200_000
):
    """
    Compara Monte Carlo contra
    el valor teórico exacto.
    """

    teo = float(
        yahtzee_exacto()
    )

    print(
        f"[2] P(Yahtzee en un turno). "
        f"Teórico exacto (codiciosa) = "
        f"{teo:.5f}"
    )

    for est in (
        "aleatoria",
        "codiciosa",
        "inteligente"
    ):

        p = sum(
            puntuar(
                "yahtzee",
                lanzamientos(
                    est,
                    rng
                )
            ) == 50
            for _ in range(n)
        ) / n

        lo, hi = ic95(
            p,
            n
        )

        extra = ""

        if est == "codiciosa":

            z = (
                p - teo
            ) / math.sqrt(
                teo * (1 - teo) / n
            )

            extra = (
                f" | z={z:+.2f} "
                f"-> "
                f"{'consistente' if abs(z) < 1.96 else 'DISCREPANTE'}"
            )

        print(
            f"    {est:<12} "
            f"p={p:.5f} "
            f"[IC95 {lo:.5f}-{hi:.5f}]"
            f"{extra}"
        )


def calibrar(n, rng):
    """
    Puntaje medio por casilla
    mediante simulación Monte Carlo.
    """

    suma = dict.fromkeys(
        CATEGORIAS,
        0
    )

    for _ in range(n):

        d = lanzamientos(
            "codiciosa",
            rng
        )

        for c in CATEGORIAS:

            suma[c] += puntuar(
                c,
                d
            )

    return {
        c: s / n
        for c, s in suma.items()
    }


def torneo(
    a,
    b,
    n,
    rng,
    ref
):
    """
    Simula n partidas entre dos estrategias.
    """

    res = [
        jugar_partida(
            [a, b],
            rng,
            ref
        )
        for _ in range(n)
    ]

    print(
        f"\n    {a} vs {b} "
        f"({n:,} partidas)"
    )

    for i, nombre in enumerate(
        (a, b)
    ):

        pts = [
            r[i]
            for r in res
        ]

        gana = sum(
            r[i] > r[1 - i]
            for r in res
        ) / n

        lo, hi = ic95(
            gana,
            n
        )

        print(
            f"      {nombre:<12} "
            f"gana {gana:6.1%} "
            f"[{lo:.1%}-{hi:.1%}] "
            f"| media "
            f"{statistics.mean(pts):6.1f} "
            f"| desv. "
            f"{statistics.pstdev(pts):5.1f}"
        )

    print(
        f"      empates: "
        f"{sum(r[0] == r[1] for r in res) / n:.1%}"
    )


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def main():

    # Semilla fija para que los resultados sean reproducibles
    rng = random.Random(2024)

    # Valores de referencia calculados mediante Monte Carlo
    ref = calibrar(
        100_000,
        rng
    )

    print(
        "--- Partida de demostración "
        "(julian vs july) ---"
    )

    t = jugar_partida(
        ["inteligente", "codiciosa"],
        rng,
        ref,
        verbose=True
    )

    print(
        f"  TOTAL J1={t[0]} | "
        f"J2={t[1]}\n\n"
        f"--- Experimentos Monte Carlo ---"
    )

    # Experimento 1: validar el modelo
    exp_uniformidad(
        rng
    )

    # Experimento 2: contraste con teoría exacta
    exp_yahtzee(
        rng
    )

    print(
        "[3] Torneos"
    )

    # Experimento 3: comparación de estrategias
    for a, b in (
        ("codiciosa", "aleatoria"),
        ("inteligente", "codiciosa")
    ):

        torneo(
            a,
            b,
            5_000,
            rng,
            ref
        )


# ---------------------------------------------------------------------------
# EJECUCIÓN Y GUARDADO AUTOMÁTICO DE RESULTADOS
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # Crear la carpeta resultados si no existe
    os.makedirs(
        "resultados",
        exist_ok=True
    )

    # Archivo donde se guardará la salida
    archivo_resultados = os.path.join(
        "resultados",
        "resultados.txt"
    )

    class SalidaConsola:

        def __init__(
            self,
            consola,
            archivo
        ):
            self.consola = consola
            self.archivo = archivo

        def write(self, texto):
            # Mostrar en consola
            self.consola.write(texto)

            # Guardar en archivo
            self.archivo.write(texto)

        def flush(self):
            self.consola.flush()
            self.archivo.flush()

    # Abrir el archivo de resultados
    # "w" reemplaza los resultados anteriores
    # por los resultados de la nueva ejecución.
    with open(
        archivo_resultados,
        "w",
        encoding="utf-8"
    ) as archivo:

        salida = SalidaConsola(
            sys.stdout,
            archivo
        )

        # Todo lo que imprima main()
        # aparecerá en consola y se guardará
        # simultáneamente en resultados.txt.
        with redirect_stdout(salida):
            main()