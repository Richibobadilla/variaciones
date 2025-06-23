import pandas as pd
import streamlit as st

# ✅ Archivo Excel desde GitHub
excel_url = "https://raw.githubusercontent.com/Richibobadilla/variaciones/main/TEST.xlsx"

st.set_page_config(page_title="Análisis de Variaciones", layout="wide")

# 🎨 Estilos personalizados
st.markdown('''
    <style>
    body {
        background: linear-gradient(to bottom, #00bcd4, #ffffff);
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-color: transparent;
    }
    h1, h2, h3 {
        color: #0d47a1;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
''', unsafe_allow_html=True)

st.title("📊 Análisis de Variaciones por Mes")

# 🧠 Función con caché
@st.cache_data(ttl=60)
def cargar_datos():
    real = pd.read_excel(excel_url, sheet_name='REAL')
    budget = pd.read_excel(excel_url, sheet_name='BUDGET')
    return real, budget

try:
    real_df, budget_df = cargar_datos()

    # --- VAR GENERAL ---
    real_grouped = real_df.groupby(['MES', 'GASTO'])['IMPORTE'].sum().reset_index()
    budget_grouped = budget_df.groupby(['MES', 'GASTO'])['IMPORTE'].sum().reset_index()

    variaciones = pd.merge(
        real_grouped,
        budget_grouped,
        on=['MES', 'GASTO'],
        how='outer',
        suffixes=('_REAL', '_BUDGET')
    ).fillna(0)

    variaciones['VARIACION_ABS'] = variaciones['IMPORTE_REAL'] - variaciones['IMPORTE_BUDGET']
    variaciones['VARIACION_%'] = (variaciones['VARIACION_ABS'] / variaciones['IMPORTE_BUDGET'].replace(0, pd.NA)) * 100

    meses = sorted(variaciones['MES'].unique())
    mes_seleccionado = st.selectbox("📅 Selecciona un mes:", meses)

    df_mes = variaciones[variaciones['MES'] == mes_seleccionado].copy().reset_index(drop=True)

    def resaltar_variaciones(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: red'
            elif val < 0:
                return 'color: green'
        return ''

    styled_df = df_mes.style.format({
        "IMPORTE_REAL": "${:,.0f}",
        "IMPORTE_BUDGET": "${:,.0f}",
        "VARIACION_ABS": "${:,.0f}",
        "VARIACION_%": "{:.1f}%"
    }).applymap(resaltar_variaciones, subset=["VARIACION_ABS", "VARIACION_%"])

    st.subheader(f"📊 Variaciones generales del mes: {mes_seleccionado}")
    st.dataframe(styled_df, use_container_width=True)

    # --- VAR CECO DETALLADO ---
    st.subheader("🔍 Detalle por CECO y Gasto")

    real_mes = real_df[real_df['MES'] == mes_seleccionado]
    budget_mes = budget_df[budget_df['MES'] == mes_seleccionado]

    cecos_disponibles = sorted(set(real_mes['CECO']).intersection(set(budget_mes['CECO'])))
    ceco_seleccionado = st.selectbox("🏢 Selecciona un CECO:", cecos_disponibles)

    real_filtrado = real_mes[real_mes['CECO'] == ceco_seleccionado]
    budget_filtrado = budget_mes[budget_mes['CECO'] == ceco_seleccionado]

    real_ceco = real_filtrado.groupby(['MES', 'CECO', 'GASTO'])['IMPORTE'].sum().reset_index()
    budget_ceco = budget_filtrado.groupby(['MES', 'CECO', 'GASTO'])['IMPORTE'].sum().reset_index()

    detalle = pd.merge(
        real_ceco,
        budget_ceco,
        on=['MES', 'CECO', 'GASTO'],
        how='outer',
        suffixes=('_REAL', '_BUDGET')
    ).fillna(0)

    detalle['VARIACION_ABS'] = detalle['IMPORTE_REAL'] - detalle['IMPORTE_BUDGET']
    detalle['VARIACION_%'] = (detalle['VARIACION_ABS'] / detalle['IMPORTE_BUDGET'].replace(0, pd.NA)) * 100

    styled_detalle = detalle.style.format({
        "IMPORTE_REAL": "${:,.0f}",
        "IMPORTE_BUDGET": "${:,.0f}",
        "VARIACION_ABS": "${:,.0f}",
        "VARIACION_%": "{:.1f}%"
    }).applymap(resaltar_variaciones, subset=["VARIACION_ABS", "VARIACION_%"])

    st.dataframe(styled_detalle, use_container_width=True)

    st.success("✅ Análisis generado exitosamente.")

except Exception as e:
    st.error(f"❌ Error al procesar el archivo: {e}")
