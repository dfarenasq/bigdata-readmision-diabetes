# Readmisión hospitalaria temprana en pacientes con diabetes — Proyecto integrador Big Data 2026-2

**Universidad Santo Tomás, Seccional Tunja — Facultad de Ingeniería de Sistemas — Big Data 2026-2**

**Integrantes**
- Maria del Pilar Guzman Murillo
- Daniel Felipe Arenas Quiroga
- David Fernando Rico Mendivelso

**Repositorio:** https://github.com/dfarenasq/bigdata-readmision-diabetes

**Video de funcionamiento:** `PEGAR_AQUÍ_EL_ENLACE_PÚBLICO_DEL_VIDEO`
**Dashboard publicado:** `PEGAR_AQUÍ_EL_ENLACE_DE_STREAMLIT_CLOUD` (o ejecutarlo localmente, ver abajo)

---

## 1. De qué trata

Flujo de datos completo (ingesta → limpieza → procesamiento con PySpark → análisis → dashboard) sobre **101 766 hospitalizaciones de pacientes con diabetes** en 130 hospitales de EE. UU. (1999–2008), para identificar qué factores se asocian a la **readmisión en menos de 30 días**.

**Preguntas de análisis**
1. ¿Cómo cambia la tasa de readmisión temprana según las hospitalizaciones del paciente en el año anterior?
2. ¿Los pacientes a quienes se les midió la HbA1c tienen una tasa de readmisión distinta?
3. ¿Cómo varían la estancia, el número de medicamentos y la readmisión entre grupos de edad?
4. ¿Qué diagnósticos principales y destinos de egreso concentran la readmisión temprana?

**Dataset:** *Diabetes 130-US Hospitals for Years 1999-2008*, UCI Machine Learning Repository (https://archive.ics.uci.edu/dataset/296, DOI 10.24432/C5230J), licencia **CC BY 4.0**. 101 766 filas × 50 columnas (19,2 MB). El notebook lo descarga de la UCI y, si la UCI no responde, de una copia idéntica en GitHub; la fecha de descarga y el hash SHA-256 quedan en `data/bronze/_metadata.txt`.

## 2. Estructura del repositorio

```
├── Proyecto_Integrador_Readmision_Diabetes.ipynb   # notebook ejecutado (T1–T9)
├── app.py                                          # dashboard Streamlit + Plotly
├── requirements.txt                                # dependencias del dashboard (Streamlit Cloud)
├── requirements-notebook.txt                       # dependencias del notebook
├── Informe_Final_Readmision_Diabetes.docx            # informe editable
├── Informe_Final_Readmision_Diabetes.pdf             # informe para entregar
├── Diapositivas_Readmision_Diabetes.pptx
├── README.md
├── figs/                                           # gráficos exportados por el notebook
└── data/
    ├── bronze/   diabetic_data.csv, IDs_mapping.csv, _metadata.txt   ← dato crudo
    ├── silver/   encuentros.parquet                                  ← 99 340 encuentros limpios
    └── gold/     p1_… p4_*.parquet                                   ← tablas de PySpark por pregunta
```

## 3. Cómo ejecutarlo

### Requisitos
- Python 3.10 o superior
- Java 17 o superior (lo necesita PySpark). En Google Colab ya viene instalado.

### Local
```bash
git clone https://github.com/dfarenasq/bigdata-readmision-diabetes.git
cd bigdata-readmision-diabetes
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-notebook.txt   # notebook + dashboard (requirements.txt solo trae lo del dashboard)

# 1) Notebook: descarga los datos y genera las capas bronce, plata y oro (≈ 1 minuto)
jupyter notebook Proyecto_Integrador_Readmision_Diabetes.ipynb   # Kernel → Restart & Run All

# 2) Dashboard
streamlit run app.py
```
El dashboard abre en `http://localhost:8501` y lee `data/silver/encuentros.parquet`, así que el notebook se debe ejecutar antes (o subir la carpeta `data/` al repositorio).

### Google Colab
Subir el notebook, agregar al inicio una celda con `!pip install pyspark` y usar *Entorno de ejecución → Ejecutar todas*.

### Streamlit Community Cloud
1. Subir a GitHub (https://github.com/dfarenasq/bigdata-readmision-diabetes) la carpeta completa del proyecto **incluyendo `data/silver/encuentros.parquet`** (4,7 MB; el dashboard solo necesita ese archivo, `app.py` y `requirements.txt`).
2. Entrar a https://share.streamlit.io con la cuenta de GitHub → *Create app* → elegir el repositorio, rama `main` y archivo principal `app.py`.
3. Streamlit Cloud instala `requirements.txt`, que a propósito solo trae lo que usa el dashboard (streamlit, pandas, numpy, plotly, pyarrow). PySpark y Jupyter están en `requirements-notebook.txt` para que el despliegue sea rápido.

`requirements.txt` → dashboard (lo usa Streamlit Cloud) · `requirements-notebook.txt` → todo el proyecto.

## 4. Temáticas del syllabus aplicadas

| Temática | Dónde |
|---|---|
| Obligatoria 1 — PySpark y Spark SQL | Notebook T4 y T6: lectura del CSV y del Parquet, `filter`, `groupBy`, 3 consultas Spark SQL, `join` con la tabla de códigos de egreso, verificación con `count()` |
| Obligatoria 2 — Pandas, estadística, Streamlit | T5 y T7: limpieza, descriptiva, correlación de Spearman, chi-cuadrado, Kruskal-Wallis; `app.py` |
| Electiva B — Arquitectura por capas | `data/bronze`, `data/silver`, `data/gold`, diagrama, diccionario y responsables (T3) |
| Electiva E — Calidad, Ley 1581 y valor | Indicadores antes/después (T5.3), seudonimización y eliminación de dato sensible, estimación de valor |

## 5. Dashboard

- **4 KPIs:** encuentros, pacientes únicos, tasa de readmisión < 30 días (con diferencia frente al total) y estancia media.
- **4 filtros:** grupo de edad, sexo, tipo de admisión y "solo el primer encuentro de cada paciente".
- **7 gráficos Plotly** en 4 pestañas, una por pregunta.

## 6. Resultados principales

| Pregunta | Resultado |
|---|---|
| Global | 11,4 % de readmisión < 30 días (11 314 de 99 340 encuentros) |
| P1 | 8,6 % sin hospitalizaciones previas → 37,1 % con 5 o más (4,3 veces). Spearman ρ = 0,14, la correlación más alta |
| P2 | HbA1c medida en solo 16,9 %. Readmisión 9,9 % si se midió vs. 11,7 % si no (χ², p ≈ 8,6 × 10⁻¹¹); en diabetes como diagnóstico principal 9,6 % vs. 14,7 % |
| P3 | Estancia de 2,5 días (0–9 años) a 4,8 días (80–89); readmisión 11,9 % en 60+ vs. 10,3 % en menores de 60 |
| P4 | Diabetes como diagnóstico principal: 13,1 %. Egreso a centro de rehabilitación: 27,7 % vs. 9,3 % a casa |
| Valor | El grupo con 2+ hospitalizaciones previas (14,2 % de encuentros) concentra 27,5 % de las readmisiones; evitar 10 % ≈ USD 4,7 M en 10 años |

---

## 7. Referencias

- Anthropic. (2026). *Claude* (versión Opus 5.5) [Modelo de lenguaje de gran tamaño]. https://claude.ai
- Congreso de la República de Colombia. (2012). *Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales*.
- Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J. y Clore, J. N. (2014). Impact of HbA1c measurement on hospital readmission rates: Analysis of 70,000 clinical database patient records. *BioMed Research International, 2014*, Artículo 781670. https://doi.org/10.1155/2014/781670
- Strack, B. et al. (2014). *Diabetes 130-US Hospitals for Years 1999-2008* [Conjunto de datos]. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J
- Weiss, A. J. y Jiang, H. J. (2021). *Overview of clinical conditions with frequent and costly hospital readmissions by payer, 2018* (Statistical Brief n.º 278). Agency for Healthcare Research and Quality.

**Declaración de uso de IA:** el equipo usó Claude (Anthropic) como herramienta de apoyo para generar y depurar código y para redactar y revisar borradores del informe y las diapositivas. Los integrantes ejecutaron el código, verificaron las cifras contra las salidas del notebook y son responsables del trabajo entregado.
