# Diccionario de datos — Planta concentradora (dataset del curso)

Dataset **sintético** creado para el curso *Análisis y Pronóstico de Datos Mineros con Python*.
Simula registros horarios de una planta concentradora de cobre.

## Archivos

| Archivo | Uso | Formato |
|---|---|---|
| `datos_proceso_planta.csv` | Entrega al alumno (Módulos 1–8) | `sep=";"`, `decimal=","`, `encoding="latin-1"`, fecha `dd-mm-YYYY HH:MM` |
| `datos_proceso_planta_LIMPIO.csv` | Respaldo ya limpio para quien se atrase | `sep=","`, `decimal="."`, `encoding="utf-8"`, fecha ISO |
| `generar_dataset.py` | Script reproducible que crea ambos (semilla fija) | — |

Carga sugerida de la versión de campo:

```python
df = pd.read_csv("datos_proceso_planta.csv", sep=";", decimal=",", encoding="latin-1")
```

## Variables

| Columna | Unidad | Descripción |
|---|---|---|
| `Fecha` | — | Marca de tiempo horaria (texto en la versión de campo) |
| `Turno` | — | `Dia` (08:00–19:59) / `Noche` (20:00–07:59) |
| `Tipo_mineral` | — | Campaña de mineral procesado: `A` o `B` |
| `Tonelaje_tph` | t/h | Tratamiento de la planta |
| `Ley_Cu_pct` | % | Ley de cobre de alimentación |
| `Recuperacion_pct` | % | Recuperación metalúrgica de cobre |
| `Potencia_kW` | kW | Potencia del molino (ligada al tonelaje) |

## Estructura temporal incorporada (señal verdadera)

- **Estacionalidad diaria** (`m = 24`): tonelaje y potencia más altos en turno día.
- **Componente semanal leve**: domingos con menor tratamiento.
- **Deriva lenta**: tonelaje sube muy suavemente; recuperación **baja ~0,011 pts/día** (desgaste).
- **Persistencia**: ruido AR(1) (`phi ≈ 0,6–0,75`) → la ACF decae de forma gradual.
- **Correlaciones**: `Tonelaje ↔ Potencia` fuerte (~0,9); `Ley ↔ Recuperación` moderada.
- **Cambio de régimen**: el **día 112 (2025-04-23)** cambia la campaña de mineral A → B.
  Efecto simultáneo: sube la ley (~0,85 → ~1,06 %), baja la recuperación (~88 → ~85 %)
  y **aumenta la variabilidad** de ambas.

## Problemas de calidad inyectados (solo versión de campo)

| Problema | Dónde | Para qué módulo |
|---|---|---|
| Encabezados con espacios (`" Ley_Cu_pct"`, `"Potencia_kW "`) | fila 0 | M1 (`str.strip()`) |
| `sep=";"`, `decimal=","`, `encoding="latin-1"` | todo el archivo | M1 (argumentos de `read_csv`) |
| Código `-999` = "sin medición" | 40 filas en `Tonelaje_tph` | M1 (`replace(-999, np.nan)`) |
| Faltantes aislados | 32 filas en `Ley_Cu_pct` | M1 (interpolación) |
| Bloque de 8 h sin datos (detención de planta) | ~`2025-03-25`, varias columnas | M1 (mantener `NaN`, no interpolar) |
| Sensor congelado | `Potencia_kW` constante ~11 h (índices 3200–3210) | M1 / M7 |
| Timestamps duplicados | 2 filas | M1 (`duplicated`, timestamps repetidos) |
| Tramo exportado fuera de orden | ~40 filas al inicio | M1 (`sort_values`) |
| Picos aislados de sensor | `Tonelaje_tph` ×1,55 en 4 instantes | M2 / M7 (anomalía puntual) |

La versión `_LIMPIO.csv` **no** contiene ninguna de estas inyecciones y ya viene ordenada.
