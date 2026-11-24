"""Dashboard — Readmisión hospitalaria temprana en pacientes con diabetes.
Proyecto integrador Big Data 2026-2, Universidad Santo Tomás Seccional Tunja.
Requiere la capa plata generada por el notebook (data/silver/encuentros.parquet).
Ejecutar:  streamlit run app.py
"""
import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Readmisión en diabetes — Big Data", page_icon="🏥", layout="wide")

SILVER = "data/silver/encuentros.parquet"
NAVY, CYAN, RED, GRAY = "#222656", "#00C6D2", "#E4505A", "#8A8FA3"
EDADES = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99"]
HOSP = ["0", "1", "2", "3", "4", "5+"]
COLS = ["paciente_id", "primer_encuentro", "gender", "grupo_edad", "admission_type", "discharge_disposition",
        "time_in_hospital", "num_medications", "number_inpatient", "A1Cresult", "hba1c_medida",
        "diag_principal_grupo", "readmit_30"]


@st.cache_data
def cargar():
    df = pd.read_parquet(SILVER, columns=COLS)
    df["hosp_previas"] = np.where(df.number_inpatient >= 5, "5+", df.number_inpatient.astype(str))
    df["sexo"] = df.gender.map({"Female": "Mujer", "Male": "Hombre"})
    df["HbA1c"] = np.where(df.hba1c_medida == 1, "Medida", "No medida")
    return df


if not os.path.exists(SILVER):
    st.error("No se encontró data/silver/encuentros.parquet. Ejecute primero el notebook (ver README).")
    st.stop()
df = cargar()

# ---------------- Filtros ----------------
st.sidebar.header("Filtros")
edades = st.sidebar.select_slider("Grupo de edad", options=EDADES, value=(EDADES[0], EDADES[-1]))
sexo = st.sidebar.multiselect("Sexo", ["Mujer", "Hombre"], default=["Mujer", "Hombre"])
tipos = sorted(df.admission_type.unique())
tipo = st.sidebar.multiselect("Tipo de admisión", tipos, default=tipos)
solo_primero = st.sidebar.checkbox("Solo el primer encuentro de cada paciente", value=False)

rango = EDADES[EDADES.index(edades[0]): EDADES.index(edades[1]) + 1]
f = df[df.grupo_edad.isin(rango) & df.sexo.isin(sexo) & df.admission_type.isin(tipo)]
if solo_primero:
    f = f[f.primer_encuentro == 1]

st.title("🏥 Readmisión temprana en pacientes con diabetes")
st.caption("Diabetes 130-US Hospitals 1999–2008 (UCI, CC BY 4.0) · capa plata limpia: 99 340 encuentros · "
           "readmisión temprana = reingreso en menos de 30 días")

if f.empty:
    st.warning("No hay encuentros con esos filtros.")
    st.stop()

tasa_total = df.readmit_30.mean() * 100
k1, k2, k3, k4 = st.columns(4)
k1.metric("Encuentros", f"{len(f):,}".replace(",", "."))
k2.metric("Pacientes únicos", f"{f.paciente_id.nunique():,}".replace(",", "."))
k3.metric("Readmisión < 30 días", f"{f.readmit_30.mean()*100:.1f} %".replace(".", ","),
          f"{f.readmit_30.mean()*100 - tasa_total:+.1f} pp vs. total".replace(".", ","), delta_color="inverse")
k4.metric("Estancia media", f"{f.time_in_hospital.mean():.1f} días".replace(".", ","))


def tasa(data, col, orden=None):
    t = data.groupby(col, observed=True).readmit_30.agg(encuentros="size", tasa="mean").reset_index()
    t["tasa"] *= 100
    if orden:
        t[col] = pd.Categorical(t[col], orden, ordered=True)
        t = t.sort_values(col)
    return t


t1, t2, t3, t4 = st.tabs(["P1 · Hospitalizaciones previas", "P2 · HbA1c", "P3 · Edad", "P4 · Diagnóstico y egreso"])

with t1:
    d = tasa(f, "hosp_previas", HOSP)
    fig = px.bar(d, x="hosp_previas", y="tasa", text=d.tasa.round(1).astype(str).str.replace(".", ",") + " %", hover_data=["encuentros"],
                 labels={"hosp_previas": "Hospitalizaciones en el año previo", "tasa": "% readmitidos < 30 días"},
                 title="Readmisión temprana según hospitalizaciones previas")
    fig.update_traces(marker_color=[RED if x == "5+" else CYAN for x in d.hosp_previas])
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Las hospitalizaciones previas son la variable con mayor correlación con la readmisión (Spearman ρ = 0,14).")

with t2:
    c1, c2 = st.columns(2)
    d = tasa(f, "HbA1c")
    fig = px.bar(d, x="HbA1c", y="tasa", text=d.tasa.round(1).astype(str).str.replace(".", ",") + " %", color="HbA1c",
                 color_discrete_map={"Medida": CYAN, "No medida": GRAY}, hover_data=["encuentros"],
                 labels={"tasa": "% readmitidos < 30 días", "HbA1c": ""}, title="Readmisión según medición de HbA1c")
    fig.update_layout(showlegend=False)
    c1.plotly_chart(fig, use_container_width=True)
    d = f.groupby(["diag_principal_grupo", "HbA1c"]).readmit_30.mean().mul(100).reset_index()
    fig = px.bar(d, y="diag_principal_grupo", x="readmit_30", color="HbA1c", barmode="group", orientation="h",
                 color_discrete_map={"Medida": CYAN, "No medida": GRAY},
                 labels={"readmit_30": "% readmitidos", "diag_principal_grupo": ""},
                 title="HbA1c y readmisión por diagnóstico principal")
    c2.plotly_chart(fig, use_container_width=True)
    st.caption(f"La HbA1c se midió en {f.hba1c_medida.mean()*100:.1f} % de los encuentros filtrados.".replace(".", ",", 1))

with t3:
    d = (f.groupby("grupo_edad").agg(estancia=("time_in_hospital", "mean"), medicamentos=("num_medications", "mean"),
                                    readmision=("readmit_30", "mean"), encuentros=("readmit_30", "size"))
          .reindex([e for e in EDADES if e in f.grupo_edad.unique()]).reset_index())
    d["readmision"] *= 100
    c1, c2 = st.columns(2)
    fig = px.line(d, x="grupo_edad", y=["estancia", "medicamentos"], markers=True,
                  color_discrete_sequence=[NAVY, CYAN], labels={"value": "promedio", "grupo_edad": "Grupo de edad",
                                                                "variable": ""},
                  title="Estancia (días) y medicamentos distintos por edad")
    c1.plotly_chart(fig, use_container_width=True)
    fig = px.bar(d, x="grupo_edad", y="readmision", hover_data=["encuentros"], color_discrete_sequence=[RED],
                 labels={"grupo_edad": "Grupo de edad", "readmision": "% readmitidos < 30 días"},
                 title="Readmisión temprana por grupo de edad")
    c2.plotly_chart(fig, use_container_width=True)

with t4:
    c1, c2 = st.columns(2)
    d = tasa(f, "diag_principal_grupo").sort_values("tasa")
    fig = px.bar(d, y="diag_principal_grupo", x="tasa", orientation="h", hover_data=["encuentros"],
                 text=d.tasa.round(1).astype(str).str.replace(".", ",") + " %", labels={"tasa": "% readmitidos", "diag_principal_grupo": ""},
                 title="Por grupo de diagnóstico principal")
    fig.update_traces(marker_color=[RED if g == "Diabetes" else CYAN for g in d.diag_principal_grupo])
    c1.plotly_chart(fig, use_container_width=True)
    d = tasa(f, "discharge_disposition")
    d = d[d.encuentros >= 200].sort_values("tasa")
    fig = px.bar(d, y="discharge_disposition", x="tasa", orientation="h", hover_data=["encuentros"],
                 text=d.tasa.round(1).astype(str).str.replace(".", ",") + " %", color_discrete_sequence=[NAVY],
                 labels={"tasa": "% readmitidos", "discharge_disposition": ""},
                 title="Por destino de egreso (≥ 200 encuentros)")
    c2.plotly_chart(fig, use_container_width=True)

with st.expander("Ver tabla agregada por diagnóstico y egreso"):
    st.dataframe(f.pivot_table(index="diag_principal_grupo", columns="HbA1c", values="readmit_30", aggfunc="mean")
                  .mul(100).round(1), use_container_width=True)
