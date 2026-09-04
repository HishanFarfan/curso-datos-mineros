# -*- coding: utf-8 -*-
"""
Construye los 8 notebooks (.ipynb) del curso a partir de una especificacion
compacta. Solo usa la libreria estandar (json), asi que corre en cualquier parte.

Uso:
    python _construir_notebooks.py
"""
import json
import os

NBFORMAT = 4
NBFORMAT_MINOR = 5

META = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
    "colab": {"provenance": []},
}


def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(lines)}


def code(*lines):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(lines)}


def _src(lines):
    text = "\n".join(lines)
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


def build(fname, cells):
    nb = {"cells": cells, "metadata": META,
          "nbformat": NBFORMAT, "nbformat_minor": NBFORMAT_MINOR}
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("  escrito", fname, f"({len(cells)} celdas)")


# ----------------------------------------------------------------------
# Cabecera comun
# ----------------------------------------------------------------------
PORTADA = lambda n, titulo, objetivo: md(
    f"# Módulo {n} — {titulo}",
    "",
    "**Curso: Análisis y Pronóstico de Datos Mineros con Python**",
    "",
    f"> {objetivo}",
    "",
    "---",
    "",
    "### Cómo usar este notebook",
    "1. Ábrelo en **Google Colab** y ejecuta las celdas **de arriba hacia abajo**.",
    "2. Los datos se descargan solos desde el repositorio del curso; no tienes que subir nada.",
    "3. Lee las salidas: cada bloque responde una pregunta concreta, no ejecutes por ejecutar.",
)

SETUP = lambda: code(
    "# Librerías base",
    "import numpy as np",
    "import pandas as pd",
    "import matplotlib.pyplot as plt",
    "import seaborn as sns          # gráficos estadísticos (preinstalado en Colab)",
    "",
    "plt.rcParams['figure.figsize'] = (12, 4)",
    "pd.set_option('display.width', 120)",
    "",
    "# --- Datos del curso -------------------------------------------------",
    "# Los CSV viven en el repositorio del curso y se descargan solos.",
    "# Si no hubiera internet, la función pide subir el archivo a mano.",
    "REPO_DATOS = 'https://raw.githubusercontent.com/HishanFarfan/curso-datos-mineros/main/datos'",
    "",
    "def cargar_datos(nombre, **kw):",
    "    try:",
    "        return pd.read_csv(f'{REPO_DATOS}/{nombre}', **kw)",
    "    except Exception as e:",
    "        print('No se pudo descargar desde GitHub:', e)",
    "    try:",
    "        from google.colab import files          # Colab: subir a mano",
    "        print(f\"Sube '{nombre}':\")",
    "        return pd.read_csv(next(iter(files.upload())), **kw)",
    "    except ModuleNotFoundError:",
    "        return pd.read_csv(nombre, **kw)         # local: archivo en el cwd",
)

CARGA_CAMPO = lambda: [
    md("## 1. Carga de datos (versión de campo)",
       "",
       "El archivo viene de un sistema en español: separador `;`, coma decimal y "
       "codificación `latin-1`. Si no se lo indicamos a pandas, las columnas numéricas "
       "se leerían como texto."),
    code(
        "df = cargar_datos('datos_proceso_planta.csv',",
        "                  sep=';', decimal=',', encoding='latin-1')",
        "df.head()",
    ),
]

CARGA_LIMPIO = lambda extra="": [
    md("## 1. Carga de la serie preparada",
       "",
       "Partimos de la versión ya limpia y ordenada (`_LIMPIO.csv`). En un flujo real "
       "usarías la salida del Módulo 1." + (("\n\n" + extra) if extra else "")),
    code(
        "df = cargar_datos('datos_proceso_planta_LIMPIO.csv', parse_dates=['Fecha'])",
        "df = df.sort_values('Fecha').set_index('Fecha')",
        "df = df.asfreq('h')   # eje horario regular; expone huecos como NaN",
        "df.head()",
    ),
]

ACT = lambda *items: md("## Actividades sugeridas", "", *[f"{i+1}. {t}" for i, t in enumerate(items)])

CIERRE = lambda texto: md("---", "## Cierre", "", texto)


# ======================================================================
# MÓDULO 1
# ======================================================================
def modulo_1():
    c = [PORTADA(1, "Preparación de datos con Python",
                 "Tomar una base cruda de proceso y dejarla limpia, ordenada y con el "
                 "tiempo bien interpretado."),
         SETUP()]
    c += CARGA_CAMPO()
    c += [
        md("## 2. Primera inspección"),
        code("df.shape"),
        code("df.info()"),
        code("df.dtypes"),
        code("# Encabezados con espacios sobrantes\n"
             "list(df.columns)"),
        code("df.columns = df.columns.str.strip()\n"
             "list(df.columns)"),
        md("## 3. Resumen estadístico — buscar lo sospechoso"),
        code("df.describe()"),
        md("El mínimo de `Tonelaje_tph` es `-999`: es un **código de 'sin medición'**, "
           "no un valor físico. Lo convertimos en dato ausente."),
        code("df['Tonelaje_tph'] = df['Tonelaje_tph'].replace(-999, np.nan)\n"
             "df['Tonelaje_tph'].describe()"),
        md("## 4. El tiempo como variable"),
        code("df = df.reset_index(drop=True)\n"
             "df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)\n"
             "df['Fecha'].head()"),
        code("# ¿Están ordenados cronológicamente?\n"
             "df['Fecha'].is_monotonic_increasing"),
        code("df = df.sort_values('Fecha').reset_index(drop=True)\n"
             "df['Fecha'].is_monotonic_increasing"),
        md("## 5. Duplicados"),
        code("df.duplicated().sum()"),
        code("# Filas idénticas\n"
             "df = df.drop_duplicates()\n"
             "# Timestamps repetidos (dos lecturas para la misma hora)\n"
             "df['Fecha'].duplicated().sum()"),
        code("# Criterio: promediar las lecturas de una misma hora\n"
             "df = df.groupby('Fecha', as_index=False).agg({\n"
             "    'Turno': 'first', 'Tipo_mineral': 'first',\n"
             "    'Tonelaje_tph': 'mean', 'Ley_Cu_pct': 'mean',\n"
             "    'Recuperacion_pct': 'mean', 'Potencia_kW': 'mean'})\n"
             "df['Fecha'].duplicated().sum()"),
        md("## 6. Índice temporal y frecuencia"),
        code("df = df.set_index('Fecha')\n"
             "df = df.asfreq('h')   # impone paso horario; los huecos aparecen como NaN\n"
             "df.shape"),
        md("## 7. Valores faltantes"),
        code("df.isna().sum()"),
        code("(100 * df.isna().mean()).round(2)"),
        md("### 7.1 Faltantes aislados vs. hueco largo",
           "",
           "Interpolar una hora perdida es razonable. Reconstruir una **detención de "
           "planta** de 8 h sería inventar datos. Interpolamos solo huecos cortos."),
        code("# Interpolación limitada a huecos de a lo más 2 horas\n"
             "for col in ['Tonelaje_tph', 'Ley_Cu_pct', 'Recuperacion_pct', 'Potencia_kW']:\n"
             "    df[col] = df[col].interpolate(method='time', limit=2, limit_area='inside')\n"
             "df.isna().sum()"),
        code("# El sensor de potencia estuvo 'congelado' un tramo: valor repetido muchas horas\n"
             "rep = df['Potencia_kW'].eq(df['Potencia_kW'].shift())\n"
             "rep.groupby((~rep).cumsum()).sum().max()"),
        md("## 8. Primera visualización",
           "",
           "Cada gráfico va en dos versiones: **matplotlib** (control total, más código) y "
           "**seaborn** (recibe el DataFrame y nombres de columnas; estilo más legible)."),
        code("# matplotlib\n"
             "df['Tonelaje_tph'].plot(title='Evolución del tonelaje')\n"
             "plt.ylabel('t/h'); plt.show()"),
        code("# seaborn\n"
             "sns.lineplot(data=df['Tonelaje_tph'])\n"
             "plt.title('Evolución del tonelaje'); plt.ylabel('t/h'); plt.show()"),
        code("# matplotlib\n"
             "df['Tonelaje_tph'].dropna().hist(bins=40)\n"
             "plt.xlabel('t/h'); plt.title('Distribución del tonelaje'); plt.show()"),
        code("# seaborn\n"
             "sns.histplot(df['Tonelaje_tph'].dropna(), bins=40)\n"
             "plt.xlabel('t/h'); plt.title('Distribución del tonelaje'); plt.show()"),
        code("# matplotlib\n"
             "plt.boxplot(df['Tonelaje_tph'].dropna(), vert=True)\n"
             "plt.ylabel('t/h'); plt.title('Boxplot tonelaje'); plt.show()"),
        code("# seaborn\n"
             "sns.boxplot(y=df['Tonelaje_tph'])\n"
             "plt.ylabel('t/h'); plt.title('Boxplot tonelaje'); plt.show()"),
        code("# matplotlib\n"
             "plt.scatter(df['Tonelaje_tph'], df['Potencia_kW'], s=4, alpha=0.3)\n"
             "plt.xlabel('Tonelaje [t/h]'); plt.ylabel('Potencia [kW]')\n"
             "plt.title('Tonelaje vs Potencia'); plt.show()"),
        code("# seaborn\n"
             "sns.scatterplot(data=df, x='Tonelaje_tph', y='Potencia_kW', s=15, alpha=0.3)\n"
             "plt.title('Tonelaje vs Potencia'); plt.show()"),
        md("## 9. Guardar la base preparada"),
        code("df.to_csv('serie_preparada_M1.csv')\n"
             "df.describe()"),
        ACT("Repite la auditoría sobre `Ley_Cu_pct` y `Recuperacion_pct`.",
            "¿Cuántas horas de datos faltan en total y cómo se distribuyen en el tiempo?",
            "Compara el histograma del tonelaje antes y después de reemplazar los `-999`.",
            "Documenta en una celda de texto TODAS las decisiones de limpieza y su justificación."),
        CIERRE("La base quedó cargada, ordenada, con el tiempo como índice, la frecuencia "
               "regularizada y los problemas de calidad reconocidos. En el Módulo 2 "
               "cambiamos la pregunta: ¿qué información estadística podemos extraer?"),
    ]
    build("01_Modulo_1_Preparacion_de_datos.ipynb", c)


# ======================================================================
# MÓDULO 2
# ======================================================================
def modulo_2():
    c = [PORTADA(2, "Estadística aplicada a datos de proceso",
                 "Describir, comparar y relacionar variables — y descubrir que la "
                 "independencia de las observaciones no se sostiene."),
         SETUP()]
    c += CARGA_LIMPIO()
    c += [
        md("## 2. Descripción de una variable"),
        code("v = df['Tonelaje_tph'].dropna()\n"
             "v.describe()"),
        code("print('media  ', round(v.mean(), 1))\n"
             "print('mediana', round(v.median(), 1))\n"
             "print('std    ', round(v.std(), 1))\n"
             "print('CV %   ', round(100 * v.std() / v.mean(), 2))"),
        code("q1, q2, q3 = v.quantile([0.25, 0.5, 0.75])\n"
             "iqr = q3 - q1\n"
             "print('Q1, Q2, Q3 =', round(q1,1), round(q2,1), round(q3,1))\n"
             "print('IQR =', round(iqr, 1))"),
        md("## 3. Valores atípicos por regla IQR"),
        code("lim_inf, lim_sup = q1 - 1.5*iqr, q3 + 1.5*iqr\n"
             "at = v[(v < lim_inf) | (v > lim_sup)]\n"
             "print('límites:', round(lim_inf,1), round(lim_sup,1))\n"
             "print('n atípicos:', len(at))"),
        md("Cada figura va en dos versiones equivalentes: **matplotlib** y **seaborn**."),
        code("# matplotlib\n"
             "v.hist(bins=40); plt.title('Tonelaje'); plt.show()\n"
             "plt.boxplot(v); plt.title('Tonelaje'); plt.show()"),
        code("# seaborn\n"
             "sns.histplot(v, bins=40); plt.title('Tonelaje'); plt.show()\n"
             "sns.boxplot(x=v); plt.title('Tonelaje'); plt.show()"),
        md("## 4. Comparación entre condiciones de operación"),
        code("df.groupby('Turno')['Tonelaje_tph'].agg(['mean','median','std','count'])"),
        code("df.groupby('Tipo_mineral')[['Ley_Cu_pct','Recuperacion_pct']].agg(['mean','std'])"),
        code("# matplotlib\n"
             "df.boxplot(column='Tonelaje_tph', by='Turno')\n"
             "plt.suptitle(''); plt.title('Tonelaje por turno'); plt.show()"),
        code("# seaborn\n"
             "sns.boxplot(data=df, x='Turno', y='Tonelaje_tph')\n"
             "plt.title('Tonelaje por turno'); plt.show()"),
        md("**Ojo:** una diferencia entre periodos puede deberse al *tiempo* o a un "
           "*cambio de condición* (aquí, la campaña de mineral A→B)."),
        md("## 5. Relaciones entre variables"),
        code("num = df[['Tonelaje_tph','Ley_Cu_pct','Recuperacion_pct','Potencia_kW']]\n"
             "num.corr().round(2)"),
        code("num.corr(method='spearman').round(2)"),
        code("# matplotlib\n"
             "plt.scatter(df['Ley_Cu_pct'], df['Recuperacion_pct'], s=4, alpha=0.3)\n"
             "plt.xlabel('Ley Cu [%]'); plt.ylabel('Recuperación [%]'); plt.show()"),
        code("# seaborn — color por campaña de mineral\n"
             "sns.scatterplot(data=df, x='Ley_Cu_pct', y='Recuperacion_pct',\n"
             "                hue='Tipo_mineral', s=15, alpha=0.4)\n"
             "plt.show()"),
        code("# matplotlib\n"
             "im = plt.imshow(num.corr(), vmin=-1, vmax=1, cmap='coolwarm')\n"
             "plt.xticks(range(4), num.columns, rotation=45, ha='right')\n"
             "plt.yticks(range(4), num.columns); plt.colorbar(im); plt.show()"),
        code("# seaborn\n"
             "sns.heatmap(num.corr(), annot=True, fmt='.2f', vmin=-1, vmax=1,\n"
             "            cmap='coolwarm', square=True)\n"
             "plt.show()"),
        md("## 6. Una prueba de hipótesis (ejemplo)"),
        code("from scipy import stats\n"
             "dia = df.loc[df['Turno']=='Dia', 'Recuperacion_pct'].dropna()\n"
             "noc = df.loc[df['Turno']=='Noche', 'Recuperacion_pct'].dropna()\n"
             "t, p = stats.ttest_ind(dia, noc, equal_var=False)\n"
             "d = (dia.mean() - noc.mean()) / np.sqrt((dia.var()+noc.var())/2)\n"
             "print(f'diferencia de medias = {dia.mean()-noc.mean():.3f} pts')\n"
             "print(f'p-value = {p:.2e}   |   d de Cohen = {d:.3f}')"),
        md("Con miles de datos, casi cualquier diferencia sale 'significativa'. "
           "La pregunta real es si es **relevante para la operación**."),
        md("## 7. El experimento clave: mezclar el orden"),
        code("orig = df['Tonelaje_tph'].dropna()\n"
             "mezcla = orig.sample(frac=1, random_state=0).reset_index(drop=True)\n"
             "print('media / std originales:', round(orig.mean(),1), round(orig.std(),1))\n"
             "print('media / std mezcladas :', round(mezcla.mean(),1), round(mezcla.std(),1))"),
        code("# matplotlib\n"
             "fig, ax = plt.subplots(2, 1, figsize=(12, 6))\n"
             "orig.reset_index(drop=True).plot(ax=ax[0], title='Orden real')\n"
             "mezcla.plot(ax=ax[1], title='Orden mezclado (mismos valores)')\n"
             "plt.tight_layout(); plt.show()"),
        code("# seaborn\n"
             "fig, ax = plt.subplots(2, 1, figsize=(12, 6))\n"
             "sns.lineplot(data=orig.reset_index(drop=True), ax=ax[0])\n"
             "sns.lineplot(data=mezcla, ax=ax[1])\n"
             "ax[0].set_title('Orden real'); ax[1].set_title('Orden mezclado (mismos valores)')\n"
             "plt.tight_layout(); plt.show()"),
        md("Los descriptivos son idénticos; la **estructura temporal desapareció**. "
           "Eso es lo que la estadística clásica no captura."),
        ACT("Repite la comparación media/mediana para `Recuperacion_pct` por `Tipo_mineral`.",
            "Calcula la matriz de correlación separada para mineral A y para mineral B. ¿Cambian las relaciones?",
            "¿El t-test entre turnos sigue siendo válido si las observaciones consecutivas están correlacionadas? Argumenta.",
            "Construye dos series con igual media y std pero comportamiento temporal opuesto."),
        CIERRE("Sabemos describir y comparar, pero terminamos con una grieta: las "
               "observaciones de un proceso **tienen memoria**. El Módulo 3 introduce "
               "formalmente la estructura temporal."),
    ]
    build("02_Modulo_2_Estadistica_aplicada.ipynb", c)


# ======================================================================
# MÓDULO 3
# ======================================================================
def modulo_3():
    c = [PORTADA(3, "Introducción a las series temporales",
                 "Reconocer componentes, rezagos, diferencias y estadísticas móviles; "
                 "descomponer una serie."),
         SETUP()]
    c += CARGA_LIMPIO()
    c += [
        code("serie = df['Tonelaje_tph']\n"
             "serie.plot(title='Serie horaria de tonelaje'); plt.ylabel('t/h'); plt.show()"),
        md("## 2. Frecuencia y agregación"),
        code("serie.resample('D').mean().plot(title='Promedio diario de tonelaje')\n"
             "plt.ylabel('t/h'); plt.show()"),
        md("## 3. Rezagos (lags)"),
        code("tmp = pd.DataFrame({'X_t': serie,\n"
             "                    'X_t-1': serie.shift(1),\n"
             "                    'X_t-24': serie.shift(24)})\n"
             "tmp.head(30)"),
        code("plt.scatter(serie.shift(1), serie, s=4, alpha=0.2)\n"
             "plt.xlabel('X(t-1)'); plt.ylabel('X(t)'); plt.title('Dispersión con rezago 1'); plt.show()"),
        md("## 4. Diferencias"),
        code("serie.diff().plot(title='Primera diferencia  ΔX_t = X_t - X_{t-1}'); plt.show()"),
        code("serie.diff(24).plot(title='Diferencia estacional (24 h)'); plt.show()"),
        md("## 5. Estadísticas móviles"),
        code("fig, ax = plt.subplots(figsize=(12,4))\n"
             "serie.plot(ax=ax, alpha=0.4, label='serie')\n"
             "serie.rolling(24).mean().plot(ax=ax, label='media móvil 24 h')\n"
             "serie.rolling(168).mean().plot(ax=ax, label='media móvil 168 h')\n"
             "ax.legend(); plt.show()"),
        code("serie.rolling(24).std().plot(title='Desviación estándar móvil (24 h)'); plt.show()"),
        md("## 6. Suavizado exponencial"),
        code("fig, ax = plt.subplots(figsize=(12,4))\n"
             "serie.iloc[:500].plot(ax=ax, alpha=0.4, label='original')\n"
             "serie.iloc[:500].ewm(alpha=0.1).mean().plot(ax=ax, label='EWM alpha=0.1')\n"
             "serie.iloc[:500].ewm(alpha=0.4).mean().plot(ax=ax, label='EWM alpha=0.4')\n"
             "ax.legend(); plt.show()"),
        md("## 7. Descomposición"),
        code("from statsmodels.tsa.seasonal import seasonal_decompose\n"
             "res = seasonal_decompose(serie.dropna(), model='additive', period=24)\n"
             "res.plot(); plt.tight_layout(); plt.show()"),
        code("from statsmodels.tsa.seasonal import STL\n"
             "stl = STL(serie.dropna(), period=24, robust=True).fit()\n"
             "stl.plot(); plt.tight_layout(); plt.show()"),
        md("El residuo de la descomposición: ¿es ruido o todavía tiene estructura? "
           "Eso se responde en el Módulo 4."),
        ACT("Repite todo con `Recuperacion_pct` y compara la fuerza de la estacionalidad diaria.",
            "Prueba `period=168` (semana) en la descomposición de la serie diaria.",
            "¿Qué tamaño de ventana móvil aísla mejor la deriva de fondo de la recuperación?",
            "Grafica la media y la desviación móviles juntas: ¿el proceso es igual de estable todo el periodo?"),
        CIERRE("Ya vemos tendencia, estacionalidad, rezagos y cambios locales. Falta "
               "cuantificar la dependencia (ACF/PACF) y decidir si la serie es "
               "estacionaria: Módulo 4."),
    ]
    build("03_Modulo_3_Introduccion_series_temporales.ipynb", c)


# ======================================================================
# MÓDULO 4
# ======================================================================
def modulo_4():
    c = [PORTADA(4, "Dependencia temporal y diagnóstico de series",
                 "ACF/PACF, estacionariedad, ADF/KPSS, transformaciones y "
                 "diferenciación: dejar la serie lista para modelar."),
         SETUP()]
    c += CARGA_LIMPIO()
    c += [
        code("serie = df['Recuperacion_pct'].dropna()\n"
             "serie.plot(title='Recuperación'); plt.show()"),
        md("## 2. ACF y PACF"),
        code("from statsmodels.graphics.tsaplots import plot_acf, plot_pacf\n"
             "fig, ax = plt.subplots(1, 2, figsize=(13, 4))\n"
             "plot_acf(serie, lags=60, ax=ax[0])\n"
             "plot_pacf(serie, lags=60, ax=ax[1], method='ywm')\n"
             "plt.show()"),
        md("## 3. Diagnóstico visual de estacionariedad",
           "",
           "Nivel (~85–90) y dispersión (~2–5) están en escalas muy distintas: en un "
           "mismo eje la caída de la media no se aprecia. Un panel por estadístico."),
        code("fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)\n"
             "serie.rolling(168).mean().plot(ax=ax[0], color='tab:blue')\n"
             "ax[0].set(title='Media móvil (semana) — ¿cambia el nivel?', ylabel='Recuperación [%]')\n"
             "serie.rolling(168).std().plot(ax=ax[1], color='tab:orange')\n"
             "ax[1].set(title='Std móvil (semana) — ¿cambia la dispersión?', ylabel='desv. est. [%]')\n"
             "plt.tight_layout(); plt.show()"),
        md("## 4. Pruebas ADF y KPSS"),
        code("from statsmodels.tsa.stattools import adfuller, kpss\n"
             "\n"
             "def diagnostico(x, nombre=''):\n"
             "    x = pd.Series(x).dropna()\n"
             "    p_adf = adfuller(x)[1]\n"
             "    import warnings; warnings.filterwarnings('ignore')\n"
             "    p_kpss = kpss(x, regression='c', nlags='auto')[1]\n"
             "    print(f'{nombre:>22} | ADF p={p_adf:6.3f} ({\"estacionaria\" if p_adf<0.05 else \"raíz unitaria\"})'\n"
             "          f' | KPSS p={p_kpss:6.3f} ({\"no estac.\" if p_kpss<0.05 else \"estac.\"})')\n"
             "\n"
             "diagnostico(serie, 'Recuperación (nivel)')"),
        md("## 5. Transformaciones"),
        code("diagnostico(serie.diff(), 'Δ Recuperación')\n"
             "diagnostico(np.log(df['Tonelaje_tph'].dropna()), 'log Tonelaje')\n"
             "diagnostico(np.log(df['Tonelaje_tph'].dropna()).diff(), 'Δ log Tonelaje')\n"
             "diagnostico(df['Tonelaje_tph'].dropna().diff().diff(24), 'Δ Δ24 Tonelaje')"),
        code("# Comparar ACF antes y después de diferenciar\n"
             "fig, ax = plt.subplots(1, 2, figsize=(13, 4))\n"
             "plot_acf(serie, lags=60, ax=ax[0], title='ACF nivel')\n"
             "plot_acf(serie.diff().dropna(), lags=60, ax=ax[1], title='ACF Δ')\n"
             "plt.show()"),
        md("## 6. Hoja de decisión (complétala)"),
        md("| Característica | Recuperación | Tonelaje |",
           "|---|---|---|",
           "| ¿Tendencia? | | |",
           "| ¿Estacionalidad? (m) | | |",
           "| ¿Varianza estable? | | |",
           "| ¿ACF persistente? | | |",
           "| ADF / KPSS | | |",
           "| Transformación | | |",
           "| d | | |",
           "| D , m | | |"),
        ACT("Ejecuta `diagnostico` sobre `Ley_Cu_pct` en nivel y en primera diferencia.",
            "¿La diferenciación estacional (24) elimina los picos de la ACF en 24, 48, 72?",
            "Prueba `scipy.stats.boxcox` sobre el tonelaje y compara con `np.log`.",
            "Escribe en una frase la decisión final de preparación para cada variable."),
        CIERRE("La serie queda con una decisión documentada (transformación + d + D + m). "
               "El Módulo 5 la usa para construir ARIMA/SARIMA."),
    ]
    build("04_Modulo_4_Dependencia_y_diagnostico.ipynb", c)


# ======================================================================
# MÓDULO 5
# ======================================================================
def modulo_5():
    c = [PORTADA(5, "Modelamiento de series temporales",
                 "AR, MA, ARMA, ARIMA, SARIMA; selección con AIC/BIC; análisis de "
                 "residuos y Ljung-Box."),
         SETUP()]
    c += CARGA_LIMPIO()
    c += [
        code("serie = df['Recuperacion_pct'].dropna()"),
        md("## 2. Candidatos a partir de ACF/PACF"),
        code("from statsmodels.graphics.tsaplots import plot_acf, plot_pacf\n"
             "fig, ax = plt.subplots(1, 2, figsize=(13, 4))\n"
             "plot_acf(serie.diff().dropna(), lags=40, ax=ax[0])\n"
             "plot_pacf(serie.diff().dropna(), lags=40, ax=ax[1], method='ywm')\n"
             "plt.show()"),
        md("## 3. Ajuste y comparación AIC/BIC"),
        code("from statsmodels.tsa.arima.model import ARIMA\n"
             "\n"
             "ordenes = [(1,1,0), (2,1,0), (1,1,1), (2,1,1), (3,1,1)]\n"
             "filas = []\n"
             "ajustes = {}\n"
             "for orden in ordenes:\n"
             "    r = ARIMA(serie, order=orden).fit()\n"
             "    ajustes[orden] = r\n"
             "    filas.append({'orden': str(orden), 'AIC': r.aic, 'BIC': r.bic})\n"
             "tabla = pd.DataFrame(filas).sort_values('AIC').reset_index(drop=True)\n"
             "tabla"),
        md("## 4. Residuos del mejor candidato"),
        code("mejor = tabla.loc[0, 'orden']\n"
             "res = ajustes[eval(mejor)]\n"
             "print(res.summary())"),
        code("res.plot_diagnostics(figsize=(11, 8)); plt.tight_layout(); plt.show()"),
        code("from statsmodels.stats.diagnostic import acorr_ljungbox\n"
             "acorr_ljungbox(res.resid.dropna(), lags=[12, 24, 48], return_df=True)"),
        md("## 5. Componente estacional: SARIMA"),
        code("from statsmodels.tsa.statespace.sarimax import SARIMAX\n"
             "sar = SARIMAX(serie, order=(1,1,1), seasonal_order=(1,0,1,24),\n"
             "              enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)\n"
             "print('AIC SARIMA:', round(sar.aic, 1))\n"
             "acorr_ljungbox(sar.resid.iloc[50:], lags=[24, 48], return_df=True)"),
        md("## 6. (Opcional) búsqueda automática"),
        code("%pip -q install pmdarima\n"
             "import pmdarima as pm\n"
             "auto = pm.auto_arima(serie, seasonal=True, m=24, d=1,\n"
             "                     stepwise=True, suppress_warnings=True, trace=True)\n"
             "auto.summary()"),
        md("## 7. Hoja de selección (complétala)"),
        md("| Modelo | AIC | BIC | Ljung-Box (p) | ¿pasa a M6? |",
           "|---|---|---|---|---|",
           "| ARIMA(_ , _ , _) | | | | |",
           "| ARIMA(_ , _ , _) | | | | |",
           "| SARIMA(_)(_ )24 | | | | |"),
        ACT("Repite la comparación de órdenes para `Tonelaje_tph` (usa d y transformación de M4).",
            "¿El SARIMA reduce la autocorrelación residual respecto del ARIMA no estacional?",
            "Interpreta el coeficiente AR estimado en términos de persistencia, no de causalidad.",
            "Elige 2 modelos razonables y justifícalos; NO elijas solo por AIC mínimo."),
        CIERRE("Tenemos 1–2 modelos estadísticamente razonables. El Módulo 6 hace la "
               "prueba que importa: predecir datos nunca vistos."),
    ]
    build("05_Modulo_5_Modelamiento.ipynb", c)


# ======================================================================
# MÓDULO 6
# ======================================================================
def modulo_6():
    c = [PORTADA(6, "Pronóstico y evaluación de modelos",
                 "Partición cronológica, horizonte, intervalos, MAE/RMSE/MAPE, "
                 "baseline naïve y backtesting walk-forward."),
         SETUP()]
    c += CARGA_LIMPIO()
    c += [
        code("serie = df['Recuperacion_pct'].dropna()"),
        md("## 2. Partición cronológica (nunca aleatoria)"),
        code("n_train = int(len(serie) * 0.8)\n"
             "train, test = serie.iloc[:n_train], serie.iloc[n_train:]\n"
             "print(len(train), 'train  |', len(test), 'test')\n"
             "print('corte:', train.index[-1])"),
        md("## 3. Ajuste sobre train y pronóstico"),
        code("from statsmodels.tsa.statespace.sarimax import SARIMAX\n"
             "modelo = SARIMAX(train, order=(2,1,1), seasonal_order=(1,0,1,24),\n"
             "                 enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)\n"
             "pred = modelo.get_forecast(steps=len(test))\n"
             "fc = pred.predicted_mean\n"
             "ci = pred.conf_int()"),
        code("fig, ax = plt.subplots(figsize=(12,4))\n"
             "train.iloc[-300:].plot(ax=ax, label='train')\n"
             "test.plot(ax=ax, label='observado')\n"
             "fc.plot(ax=ax, label='pronóstico')\n"
             "ax.fill_between(ci.index, ci.iloc[:,0], ci.iloc[:,1], alpha=0.2)\n"
             "ax.legend(); plt.show()"),
        md("**El pronóstico es casi plano — y así debe ser.** La recuperación horaria es "
           "nivel + una onda diaria de ±1 pt + ruido AR(≈0.6) con desviación ≈ 2.6. La "
           "memoria del AR se agota en ~8 h; más allá, el mejor pronóstico posible es el "
           "nivel actual. El SARIMA no está fallando: está diciendo que esta variable "
           "**no se pronostica hora a hora**. Lo confirmamos en §5 (apenas le gana al naïve). "
           "En §8 se ve el contraste con una variable que sí tiene estructura."),
        md("## 4. Métricas de error"),
        code("def metricas(y, yhat):\n"
             "    y, yhat = np.asarray(y), np.asarray(yhat)\n"
             "    mae = np.mean(np.abs(y - yhat))\n"
             "    rmse = np.sqrt(np.mean((y - yhat)**2))\n"
             "    mape = 100 * np.mean(np.abs((y - yhat) / y))\n"
             "    me = np.mean(y - yhat)   # sesgo\n"
             "    return dict(MAE=mae, RMSE=rmse, MAPE=mape, ME=me)\n"
             "\n"
             "metricas(test, fc)"),
        md("## 5. Baselines"),
        code("naive = pd.Series(train.iloc[-1], index=test.index)\n"
             "naive_est = serie.shift(24).iloc[n_train:]\n"
             "print('naïve      ', {k: round(v,3) for k,v in metricas(test, naive).items()})\n"
             "print('naïve 24 h ', {k: round(v,3) for k,v in metricas(test.iloc[24:], naive_est.iloc[24:]).items()})\n"
             "print('SARIMA     ', {k: round(v,3) for k,v in metricas(test, fc).items()})"),
        md("## 6. Backtesting walk-forward (un paso, ventana expansiva)"),
        code("# Reajuste periódico para acotar el costo (cada 24 h)\n"
             "hist = list(train)\n"
             "idx = list(train.index)\n"
             "pasos = test.iloc[:240]           # 10 días de evaluación\n"
             "preds = []\n"
             "modelo_wf = None\n"
             "for i, (t, y) in enumerate(pasos.items()):\n"
             "    if i % 24 == 0:\n"
             "        modelo_wf = SARIMAX(pd.Series(hist, index=idx), order=(2,1,1),\n"
             "                            seasonal_order=(1,0,1,24),\n"
             "                            enforce_stationarity=False,\n"
             "                            enforce_invertibility=False).fit(disp=False)\n"
             "        res_wf = modelo_wf\n"
             "    else:\n"
             "        res_wf = modelo_wf.append(pd.Series(hist[-1:], index=idx[-1:]), refit=False)\n"
             "    preds.append(res_wf.forecast(1).iloc[0])\n"
             "    hist.append(y); idx.append(t)\n"
             "preds = pd.Series(preds, index=pasos.index)\n"
             "metricas(pasos, preds)"),
        code("err = (pasos - preds).abs()\n"
             "err.plot(title='|error| walk-forward'); plt.show()\n"
             "print('MAE medio backtest:', round(err.mean(), 3))"),
        md("## 7. Error por horizonte"),
        code("h_pred = modelo.get_forecast(steps=48).predicted_mean\n"
             "obs = test.iloc[:48]\n"
             "for h in [1, 2, 4, 8, 24, 48]:\n"
             "    print(f'h={h:>2}  MAE acumulado = {np.mean(np.abs(obs.iloc[:h].values - h_pred.iloc[:h].values)):.3f}')"),
        md("## 8. Contraste: una variable sí pronosticable",
           "",
           "`Tonelaje_tph` tiene estacionalidad de turno (±120 t/h) y onda diaria (±55): "
           "estructura determinista que un modelo estacional captura. Mismo procedimiento, "
           "otra variable."),
        code("serie_t = df['Tonelaje_tph'].dropna()\n"
             "nt = int(len(serie_t) * 0.8)\n"
             "train_t, test_t = serie_t.iloc[:nt], serie_t.iloc[nt:]\n"
             "mod_t = SARIMAX(train_t, order=(2,1,1), seasonal_order=(0,1,1,24),\n"
             "                enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)\n"
             "pred_t = mod_t.get_forecast(steps=len(test_t))\n"
             "fc_t = pred_t.predicted_mean\n"
             "ci_t = pred_t.conf_int()"),
        code("fig, ax = plt.subplots(1, 2, figsize=(13, 4))\n"
             "for a, sl, ttl in [(ax[0], slice(0, 96), 'primeras 96 h'),\n"
             "                   (ax[1], slice(None), 'horizonte completo')]:\n"
             "    train_t.iloc[-120:].plot(ax=a, label='train')\n"
             "    test_t.iloc[sl].plot(ax=a, label='observado')\n"
             "    fc_t.iloc[sl].plot(ax=a, label='pronóstico')\n"
             "    a.fill_between(ci_t.iloc[sl].index, ci_t.iloc[sl, 0], ci_t.iloc[sl, 1], alpha=0.2)\n"
             "    a.set_title(ttl)\n"
             "ax[1].legend(); plt.tight_layout(); plt.show()"),
        code("print('naïve  ', {k: round(v,1) for k,v in metricas(test_t, pd.Series(train_t.iloc[-1], index=test_t.index)).items()})\n"
             "print('SARIMA ', {k: round(v,1) for k,v in metricas(test_t, fc_t).items()})"),
        md("El pronóstico **repite el patrón diario**, la banda tiene forma y el SARIMA "
           "le gana al naïve con claridad. La diferencia no está en el modelo sino en la "
           "variable: **elegir un objetivo pronosticable es parte del trabajo.**"),
        md("## 9. Tabla de decisión (complétala)"),
        md("| Variable / Modelo | MAE | RMSE | MAPE | ¿supera naïve? | ¿estable en backtest? |",
           "|---|---|---|---|---|---|",
           "| Recuperación · naïve | | | | — | |",
           "| Recuperación · SARIMA | | | | | |",
           "| Tonelaje · SARIMA | | | | | — |"),
        ACT("Cambia el corte a 70/30 y observa si la conclusión se mantiene.",
            "Repite la evaluación para `Potencia_kW` (ruido casi blanco: ¿qué esperas?).",
            "¿A partir de qué horizonte el MAE supera el 5 % del valor típico de la variable?",
            "¿El modelo tiene sesgo (ME ≠ 0)? ¿Subestima o sobrestima?"),
        CIERRE("Sabemos cuánto se equivoca el modelo, a qué horizonte y si supera una "
               "referencia trivial. El Módulo 7 usa el error como señal de vigilancia."),
    ]
    build("06_Modulo_6_Pronostico_y_evaluacion.ipynb", c)


# ======================================================================
# MÓDULO 7
# ======================================================================
def modulo_7():
    c = [PORTADA(7, "Detección de anomalías y cambios en el proceso",
                 "Distinguir pico aislado de cambio persistente; métodos robustos, "
                 "límites dinámicos, residuos del modelo, CUSUM y change-point."),
         SETUP()]
    c += CARGA_LIMPIO()
    c += [
        md("Nota: este notebook usa la serie **verdadera**. Para ver anomalías de sensor "
           "reales, repite los pasos sobre `datos_proceso_planta.csv` (versión de campo)."),
        code("serie = df['Recuperacion_pct'].dropna()"),
        md("## 2. Z-score global vs. robusto (mediana / MAD)"),
        code("z = (serie - serie.mean()) / serie.std()\n"
             "med = serie.median()\n"
             "mad = (serie - med).abs().median()\n"
             "z_rob = 0.6745 * (serie - med) / mad\n"
             "print('|z|>3      :', int((z.abs() > 3).sum()))\n"
             "print('|z_rob|>3.5:', int((z_rob.abs() > 3.5).sum()))"),
        md("## 3. Límites dinámicos con estadística móvil"),
        code("w = 168\n"
             "mu = serie.rolling(w, center=True).mean()\n"
             "sg = serie.rolling(w, center=True).std()\n"
             "sup, inf = mu + 3*sg, mu - 3*sg\n"
             "fuera = serie[(serie > sup) | (serie < inf)]\n"
             "\n"
             "fig, ax = plt.subplots(figsize=(12,4))\n"
             "serie.plot(ax=ax, alpha=0.5)\n"
             "mu.plot(ax=ax, color='k'); sup.plot(ax=ax, ls='--', color='r'); inf.plot(ax=ax, ls='--', color='r')\n"
             "ax.scatter(fuera.index, fuera.values, color='red', zorder=5)\n"
             "plt.title(f'{len(fuera)} puntos fuera de banda dinámica'); plt.show()"),
        md("## 4. Filtro de Hampel"),
        code("def hampel(x, w=12, n_sig=3.0):\n"
             "    x = x.copy()\n"
             "    med = x.rolling(2*w+1, center=True).median()\n"
             "    mad = (x - med).abs().rolling(2*w+1, center=True).median()\n"
             "    umbral = n_sig * 1.4826 * mad\n"
             "    return (x - med).abs() > umbral\n"
             "\n"
             "marca = hampel(serie)\n"
             "print('anomalías Hampel:', int(marca.sum()))"),
        md("## 5. Residuos de un modelo como detector"),
        code("from statsmodels.tsa.statespace.sarimax import SARIMAX\n"
             "n_train = int(len(serie)*0.7)\n"
             "m = SARIMAX(serie.iloc[:n_train], order=(2,1,1), seasonal_order=(1,0,1,24),\n"
             "            enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)\n"
             "pred = m.get_forecast(steps=len(serie)-n_train)\n"
             "obs = serie.iloc[n_train:]\n"
             "e = obs - pred.predicted_mean\n"
             "ci = pred.conf_int()\n"
             "fuera_pi = obs[(obs < ci.iloc[:,0]) | (obs > ci.iloc[:,1])]\n"
             "\n"
             "fig, ax = plt.subplots(figsize=(12,4))\n"
             "obs.plot(ax=ax, label='observado')\n"
             "pred.predicted_mean.plot(ax=ax, label='esperado')\n"
             "ax.fill_between(ci.index, ci.iloc[:,0], ci.iloc[:,1], alpha=0.2)\n"
             "ax.scatter(fuera_pi.index, fuera_pi.values, color='red', zorder=5)\n"
             "ax.legend(); plt.title('Observaciones fuera del intervalo esperado'); plt.show()"),
        md("## 6. Cambio persistente: CUSUM sobre los residuos"),
        code("en = (e - e.mean()) / e.std()\n"
             "k = 0.5\n"
             "sp = np.zeros(len(en)); sm = np.zeros(len(en))\n"
             "for i in range(1, len(en)):\n"
             "    sp[i] = max(0, sp[i-1] + en.iloc[i] - k)\n"
             "    sm[i] = min(0, sm[i-1] + en.iloc[i] + k)\n"
             "cusum = pd.DataFrame({'S+': sp, 'S-': sm}, index=en.index)\n"
             "cusum.plot(title='CUSUM de residuos estandarizados'); plt.axhline(5, ls='--', color='r'); plt.show()"),
        md("## 7. Change-point (cambio de régimen A→B)"),
        code("%pip -q install ruptures\n"
             "import ruptures as rpt\n"
             "y = df['Ley_Cu_pct'].dropna().values\n"
             "algo = rpt.Pelt(model='rbf', min_size=200).fit(y)\n"
             "bkps = algo.predict(pen=15)\n"
             "idx = df['Ley_Cu_pct'].dropna().index\n"
             "print('puntos de cambio detectados:')\n"
             "for b in bkps[:-1]:\n"
             "    print('  ', idx[b])\n"
             "df['Ley_Cu_pct'].dropna().plot()\n"
             "for b in bkps[:-1]:\n"
             "    plt.axvline(idx[b], color='r', ls='--')\n"
             "plt.title('Ley de Cu con puntos de cambio'); plt.show()"),
        ACT("Ejecuta el Z-score y el Hampel sobre `datos_proceso_planta.csv`: ¿detectan los picos de sensor y el tramo congelado?",
            "¿Qué método marca el cambio de régimen del día 112 y cuál solo marca los picos?",
            "Ajusta el umbral de la banda dinámica (k=2,3,4) y discute falsas alarmas vs eventos perdidos.",
            "Interpreta operacionalmente: ¿qué registros pedirías para explicar el change-point detectado?"),
        CIERRE("El mismo modelo de pronóstico sirve para vigilar: observado − esperado → "
               "desviación → alerta → interpretación. El Módulo 8 integra todo en un caso."),
    ]
    build("07_Modulo_7_Deteccion_de_anomalias.ipynb", c)


# ======================================================================
# MÓDULO 8
# ======================================================================
def modulo_8():
    c = [PORTADA(8, "Taller integrador: de los datos a una decisión",
                 "Recorrer el flujo completo sobre un caso minero y terminar en una "
                 "recomendación respaldada por evidencia."),
         SETUP(),
         md("## Bloque 0 — El problema",
            "",
            "> Una operación dispone de registros horarios de una planta concentradora "
            "(`datos_proceso_planta.csv`). Se requiere **caracterizar** el comportamiento "
            "de la recuperación de cobre, **evaluar** si puede pronosticarse de forma útil "
            "y **detectar** episodios en que el proceso se alejó de lo esperado.",
            "",
            "Completa antes de programar:",
            "",
            "- Variable analizada: __________",
            "- Unidad: __________",
            "- Frecuencia temporal: __________",
            "- Periodo cubierto: __________",
            "- Pregunta operacional concreta: __________"),
         md("## Bloque 1 — Carga y preparación (M1)"),
         code("df = cargar_datos('datos_proceso_planta.csv', sep=';', decimal=',', encoding='latin-1')\n"
              "df.columns = df.columns.str.strip()\n"
              "df['Tonelaje_tph'] = df['Tonelaje_tph'].replace(-999, np.nan)\n"
              "df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)\n"
              "df = (df.sort_values('Fecha')\n"
              "        .groupby('Fecha', as_index=False).first()\n"
              "        .set_index('Fecha').asfreq('h'))\n"
              "df.isna().sum()"),
         code("# TODO: decide e implementa el tratamiento de faltantes. Documenta el porqué.\n"
              "serie = df['Recuperacion_pct']\n"
              "serie = serie.interpolate('time', limit=2, limit_area='inside')\n"
              "serie = serie.dropna()"),
         md("## Bloque 2 — Exploración estadística (M2)"),
         code("# TODO: describe la serie; compara por Turno y Tipo_mineral; matriz de correlación.\n"
              "serie.describe()"),
         md("## Bloque 3 — Estructura temporal (M3)"),
         code("# TODO: serie, media/std móviles, descomposición STL (period=24).\n"
              "serie.plot(); plt.show()"),
         md("## Bloque 4 — Diagnóstico (M4)"),
         code("# TODO: ACF/PACF, ADF/KPSS en nivel y diferenciado. Decide transformación, d, D, m.\n"
              "from statsmodels.tsa.stattools import adfuller\n"
              "print('ADF nivel p =', round(adfuller(serie)[1], 4))\n"
              "print('ADF Δ     p =', round(adfuller(serie.diff().dropna())[1], 4))"),
         md("## Bloque 5 — Modelamiento (M5)"),
         code("# TODO: 2-3 candidatos ARIMA/SARIMA, tabla AIC/BIC, residuos + Ljung-Box.\n"
              "from statsmodels.tsa.statespace.sarimax import SARIMAX"),
         md("## Bloque 6 — Pronóstico y validación (M6)"),
         code("# TODO: split cronológico, forecast + intervalo, MAE/RMSE/MAPE, baseline naïve, backtesting.\n"
              "n_train = int(len(serie) * 0.8)\n"
              "train, test = serie.iloc[:n_train], serie.iloc[n_train:]"),
         md("## Bloque 7 — Anomalías (M7)"),
         code("# TODO: residuos del modelo -> umbral / intervalo. ¿Eventos aislados o cambio persistente?\n"
              "# Recuerda el cambio de campaña de mineral A->B."),
         md("## Bloque 8 — Conclusión operacional",
            "",
            "Redacta un informe de **una página** con esta estructura:",
            "",
            "| Sección | Contenido |",
            "|---|---|",
            "| **Objetivo** | Qué se quería responder |",
            "| **Datos** | Periodo, frecuencia, limpieza aplicada y por qué |",
            "| **Método** | Diagnóstico, modelos comparados, validación |",
            "| **Resultados** | MAE/RMSE, mejora sobre naïve, autocorrelación residual, anomalías |",
            "| **Recomendación** | Uso propuesto del modelo, horizonte útil, límites, qué revisar |",
            "",
            "Cada decisión debe seguir la lógica **evidencia → decisión**. "
            "Ejemplo: *«la ACF mostró picos en múltiplos de 24 → se incorporó componente estacional»*.",
            "",
            "### Errores a evitar",
            "modelar sin mirar los datos · borrar outliers automáticamente · train/test aleatorio · "
            "elegir modelo solo por AIC · reportar solo métricas · confundir anomalía con causa · "
            "entregar forecast sin incertidumbre · recomendar algo que los datos no respaldan."),
         CIERRE("El taller empieza con una base de datos y termina con una **recomendación "
                "respaldada por evidencia**. Ese es el arco completo del curso: "
                "datos → información → modelo → evidencia → decisión."),
        ]
    build("08_Modulo_8_Taller_integrador.ipynb", c)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Construyendo notebooks...")
    modulo_1(); modulo_2(); modulo_3(); modulo_4()
    modulo_5(); modulo_6(); modulo_7(); modulo_8()
    print("Listo.")
