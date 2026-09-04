# -*- coding: utf-8 -*-
"""
Generador del dataset sintetico para el curso
ANALISIS Y PRONOSTICO DE DATOS MINEROS CON PYTHON.

Produce dos archivos:

  datos_proceso_planta.csv         -> version "de campo" para el alumno.
                                      separador ';', decimal ',', encoding latin-1,
                                      fechas dd-mm-YYYY HH:MM, con problemas de calidad
                                      inyectados a proposito (faltantes, -999, duplicados,
                                      sensor congelado, filas desordenadas, encabezados con
                                      espacios) y un CAMBIO DE REGIMEN a mitad de la serie.

  datos_proceso_planta_LIMPIO.csv  -> respaldo ya limpio (separador ',', decimal '.',
                                      encoding utf-8, fecha ISO). Contiene la senal
                                      "verdadera" sin inyecciones. Sirve para quien se
                                      atrase en los Modulos 1-2.

Solo usa numpy + stdlib (no pandas), para poder ejecutarse en cualquier entorno.

Uso:
    python generar_dataset.py
"""

import csv
import numpy as np
from datetime import datetime, timedelta

RNG = np.random.default_rng(7)

# ----------------------------------------------------------------------
# 1. Eje temporal: horario, 2025-01-01 .. 2025-06-30  (181 dias)
# ----------------------------------------------------------------------
INICIO = datetime(2025, 1, 1, 0, 0, 0)
N_DIAS = 181
N = N_DIAS * 24
tiempos = [INICIO + timedelta(hours=i) for i in range(N)]

hora = np.array([t.hour for t in tiempos])
dia_idx = np.arange(N) // 24
dow = np.array([t.weekday() for t in tiempos])          # 0=lunes ... 6=domingo
turno_dia = ((hora >= 8) & (hora < 20)).astype(float)   # 1 = turno dia

# Cambio de regimen: mineral A hasta el dia 112 (aprox 23-abr), luego mineral B
CORTE_DIA = 112
mineral_B = (dia_idx >= CORTE_DIA).astype(float)
tipo_mineral = np.where(mineral_B == 1.0, "B", "A")
turno = np.where(turno_dia == 1.0, "Dia", "Noche")


def ruido_ar1(n, phi, sigma, rng):
    """Ruido autorregresivo AR(1): e[t] = phi*e[t-1] + N(0, sigma)."""
    e = np.zeros(n)
    innov = rng.normal(0.0, sigma, n)
    for t in range(1, n):
        e[t] = phi * e[t - 1] + innov[t]
    return e


# ----------------------------------------------------------------------
# 2. Senales "verdaderas"
# ----------------------------------------------------------------------
# --- Tonelaje [t/h] --------------------------------------------------
tonelaje = (
    1500.0
    + 120.0 * turno_dia                                   # estacionalidad de turno
    + 55.0 * np.sin(2 * np.pi * (hora - 6) / 24.0)        # onda diaria suave
    - 70.0 * (dow == 6)                                   # domingos algo mas bajos
    + 0.045 * dia_idx                                     # leve deriva creciente
    - 45.0 * mineral_B                                    # mineral B alimenta un poco menos
    + ruido_ar1(N, phi=0.75, sigma=42.0, rng=RNG)         # persistencia
)
tonelaje = np.clip(tonelaje, 850.0, None)

# --- Ley de Cu [%] -------------------------------------------------
ley = (
    np.where(mineral_B == 1.0, 1.06, 0.85)               # cambio de nivel por mineral
    + 0.05 * np.sin(2 * np.pi * (hora - 3) / 24.0)
    + ruido_ar1(N, phi=0.55, sigma=1.0, rng=RNG)
      * np.where(mineral_B == 1.0, 0.075, 0.045)          # cambio de variabilidad
)
ley = np.clip(ley, 0.45, 1.75)

# --- Recuperacion [%] --------------------------------------------
recuperacion = (
    np.where(mineral_B == 1.0, 85.0, 88.0)               # baja al cambiar de mineral
    + 6.0 * (ley - 0.90)                                  # depende de la ley
    - 0.011 * dia_idx                                     # desgaste progresivo del equipo
    + 0.8 * np.sin(2 * np.pi * (hora - 9) / 24.0)
    + ruido_ar1(N, phi=0.60, sigma=1.0, rng=RNG)
      * np.where(mineral_B == 1.0, 2.1, 1.2)              # mas inestable con mineral B
)
recuperacion = np.clip(recuperacion, 70.0, 96.5)

# --- Potencia [kW] (fuertemente ligada al tonelaje) --------------
potencia = (
    2600.0
    + 0.62 * tonelaje
    + 12.0 * np.sin(2 * np.pi * (hora - 6) / 24.0)
    + RNG.normal(0.0, 38.0, N)
)

# Copias limpias (sin inyecciones) para el respaldo
tonelaje_limpio = tonelaje.copy()
ley_limpio = ley.copy()
recuperacion_limpio = recuperacion.copy()
potencia_limpio = potencia.copy()

# ----------------------------------------------------------------------
# 3. Inyeccion de problemas de calidad (solo version "de campo")
# ----------------------------------------------------------------------
tonelaje_s = tonelaje.copy()
ley_s = ley.copy()
recuperacion_s = recuperacion.copy()
potencia_s = potencia.copy()

# Marcador de faltante: usamos np.nan y luego escribimos "" en el CSV
NAN = np.nan

# 3.1 Picos aislados de sensor en tonelaje (glitches)
for k in (1503, 1504, 2778, 3910):
    tonelaje_s[k] = tonelaje_s[k] * 1.55

# 3.2 Sensor de potencia "congelado" ~11 h
potencia_s[3200:3211] = potencia_s[3200]

# 3.3 Codigos -999 = "sin medicion" en tonelaje
idx_999 = RNG.choice(np.arange(300, N - 300), size=40, replace=False)
COD_999 = idx_999                       # se escriben como -999 literal

# 3.4 Faltantes aislados en ley de Cu
idx_ley_na = RNG.choice(np.arange(200, N - 200), size=32, replace=False)
ley_s[idx_ley_na] = NAN

# 3.5 Detencion de planta: bloque de 8 h sin datos en varias variables
PARO = slice(2000, 2008)
tonelaje_s[PARO] = NAN
potencia_s[PARO] = NAN
recuperacion_s[PARO] = NAN
ley_s[PARO] = NAN

# ----------------------------------------------------------------------
# 4. Construccion de filas
# ----------------------------------------------------------------------
def fmt_es(x, dec):
    """Numero con coma decimal; '' si es NaN."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    return f"{x:.{dec}f}".replace(".", ",")


filas = []
for i in range(N):
    ton = tonelaje_s[i]
    if i in set(COD_999.tolist()):
        ton_str = "-999"
    else:
        ton_str = fmt_es(ton, 1)
    filas.append([
        tiempos[i].strftime("%d-%m-%Y %H:%M"),
        turno[i],
        tipo_mineral[i],
        ton_str,
        fmt_es(ley_s[i], 3),
        fmt_es(recuperacion_s[i], 2),
        fmt_es(potencia_s[i], 1),
    ])

# 4.1 Timestamps duplicados (dos lecturas para la misma hora)
for j in (600, 1801):
    dup = list(filas[j])
    # lectura ligeramente distinta
    try:
        dup[3] = fmt_es(float(dup[3].replace(",", ".")) + 18.0, 1)
    except ValueError:
        pass
    filas.insert(j + 1, dup)

# 4.2 Un tramo de ~40 filas exportado fuera de orden cronologico
bloque = filas[70:110]
del filas[70:110]
filas[130:130] = bloque

# ----------------------------------------------------------------------
# 5. Escritura: version "de campo"
# ----------------------------------------------------------------------
ENC_HEADER = ["Fecha", "Turno", "Tipo_mineral", "Tonelaje_tph",
              " Ley_Cu_pct", "Recuperacion_pct", "Potencia_kW "]  # espacios a proposito

with open("datos_proceso_planta.csv", "w", newline="", encoding="latin-1") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(ENC_HEADER)
    w.writerows(filas)

# ----------------------------------------------------------------------
# 6. Escritura: respaldo LIMPIO (senal verdadera, ordenado, estandar)
# ----------------------------------------------------------------------
with open("datos_proceso_planta_LIMPIO.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=",")
    w.writerow(["Fecha", "Turno", "Tipo_mineral", "Tonelaje_tph",
                "Ley_Cu_pct", "Recuperacion_pct", "Potencia_kW"])
    for i in range(N):
        w.writerow([
            tiempos[i].strftime("%Y-%m-%d %H:%M:%S"),
            turno[i],
            tipo_mineral[i],
            f"{tonelaje_limpio[i]:.1f}",
            f"{ley_limpio[i]:.3f}",
            f"{recuperacion_limpio[i]:.2f}",
            f"{potencia_limpio[i]:.1f}",
        ])

# ----------------------------------------------------------------------
# 7. Resumen por consola
# ----------------------------------------------------------------------
print("OK - archivos generados")
print(f"  observaciones (senal)      : {N}")
print(f"  filas version de campo     : {len(filas)}  (incluye 2 duplicados)")
print(f"  -999 en tonelaje           : {len(COD_999)}")
print(f"  faltantes en ley           : {len(idx_ley_na)} aislados + bloque de paro")
print(f"  sensor potencia congelado  : indices 3200-3210")
print(f"  picos en tonelaje          : 1503, 1504, 2778, 3910")
print(f"  cambio de regimen (min. B) : dia {CORTE_DIA} -> {tiempos[CORTE_DIA*24]:%Y-%m-%d}")
print(f"  tramo desordenado          : filas 70-110 movidas tras la fila 130")
