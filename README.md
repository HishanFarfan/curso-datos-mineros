# Curso — Análisis y Pronóstico de Datos Mineros con Python

Materiales de apoyo generados a partir de los apuntes del curso (16 h, 8 clases, Google Colab).

```
CURSO_MINERO/
├── datos/        dataset sintético de planta concentradora + generador
├── notebooks/    8 notebooks de Google Colab (uno por módulo) + constructor
└── slides/       9 decks Beamer (.tex + .pdf) + preámbulo compartido
```

## Para alumnos — abrir en Colab

Haz clic y ejecuta de arriba hacia abajo. **Los datos se descargan solos**, no
tienes que subir ni montar nada.

| Módulo | Abrir |
|---|---|
| 1 · Preparación de datos | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/01_Modulo_1_Preparacion_de_datos.ipynb) |
| 2 · Estadística aplicada | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/02_Modulo_2_Estadistica_aplicada.ipynb) |
| 3 · Introducción a series temporales | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/03_Modulo_3_Introduccion_series_temporales.ipynb) |
| 4 · Dependencia y diagnóstico | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/04_Modulo_4_Dependencia_y_diagnostico.ipynb) |
| 5 · Modelamiento | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/05_Modulo_5_Modelamiento.ipynb) |
| 6 · Pronóstico y evaluación | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/06_Modulo_6_Pronostico_y_evaluacion.ipynb) |
| 7 · Detección de anomalías | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/07_Modulo_7_Deteccion_de_anomalias.ipynb) |
| 8 · Taller integrador | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HishanFarfan/curso-datos-mineros/blob/main/notebooks/08_Modulo_8_Taller_integrador.ipynb) |

> Para guardar tu avance: en Colab, **Archivo → Guardar una copia en Drive**.

## 1. Dataset (`datos/`)

| Archivo | Descripción |
|---|---|
| `datos_proceso_planta.csv` | Versión "de campo" para el alumno. `sep=";"`, `decimal=","`, `encoding="latin-1"`, fecha `dd-mm-YYYY HH:MM`. Incluye problemas de calidad y un cambio de régimen. |
| `datos_proceso_planta_LIMPIO.csv` | Respaldo ya limpio (CSV estándar, fecha ISO). Para quien se atrase en M1–M2. |
| `generar_dataset.py` | Regenera ambos archivos (semilla fija). Solo requiere `numpy`. |
| `diccionario_datos.md` | Variables, estructura temporal incorporada y catálogo de problemas inyectados. |

Regenerar:

```bash
cd datos && python generar_dataset.py
```

Serie horaria enero–junio 2025 (4344 h). Tonelaje, ley de Cu, recuperación y potencia,
con estacionalidad diaria (`m=24`), deriva lenta, ruido AR(1), correlaciones realistas
y un **cambio de campaña A→B el día 112** (nivel + variabilidad).

## 2. Notebooks (`notebooks/`)

Un notebook por módulo (`01_...` a `08_...`). Diseñados para **Google Colab**:
`statsmodels`, `scikit-learn` y `scipy` vienen preinstalados; `pmdarima` y `ruptures`
se instalan con `%pip` en la celda correspondiente.

La celda `SETUP` define `cargar_datos(nombre, **kw)`, que descarga el CSV desde
`datos/` de este repo (variable `REPO_DATOS`) y, si no hay internet, cae a
`files.upload()`. M2–M8 parten de `datos_proceso_planta_LIMPIO.csv`; M1 y M8
trabajan la versión de campo. Si haces *fork* del repo o lo mueves, actualiza
`REPO_DATOS` en `_construir_notebooks.py` y regenera.

Regenerar los `.ipynb` desde la especificación:

```bash
cd notebooks && python _construir_notebooks.py
```

## 3. Diapositivas (`slides/`)

- `preambulo.tex` — tema Beamer construido a mano sobre la base `default`
  (**no requiere `metropolis`** ni temas externos; compila con MiKTeX / TeX Live).
- `00_Presentacion_general.tex` — presentación del curso.
- `01_Modulo_1.tex` … `08_Modulo_8.tex` — un deck por módulo.

Compilar todo:

```bash
cd slides && make          # o:  pwsh ./compilar.ps1
```

Cada deck hace `\input{preambulo.tex}`, así que edita el preámbulo una sola vez para
cambiar colores, fuente o pie de página en las 9 presentaciones.

### Convenciones del preámbulo

| Comando | Uso |
|---|---|
| `\portada{N}{Título}` | portada estándar del módulo |
| `\idea{...}` | caja destacada con la idea central |
| `\ojo{...}` | advertencia en rojo |
| `\ruta{ ... }` | cadena de flujo `a \fl b \fl c` escalada al ancho |
| `\fl` | flecha de flujo (texto o matemático) |
| `\begin{recordar}...\end{recordar}` | bloque "Qué deberías recordar" |
| `lstlisting` | código Python (el frame debe llevar `[fragile]`) |
