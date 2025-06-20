import pandas as pd
import streamlit as st

# ✅ Tu archivo Excel desde GitHub
excel_url = "https://raw.githubusercontent.com/Richibobadilla/variaciones/main/TEST.xlsx"

st.set_page_config(page_title="Análisis de Variaciones", layout="centered")
st.title("📊 Análisis de Variaciones por Mes")

# 🧠 Función con caché controlado (refresca cada 60 segundos como máximo)
@st.cache_data(ttl=60)
def cargar_datos():
    real = pd.read_excel(excel_url, sheet_name='REAL')
    budget = pd.read_excel(excel_url, sheet_name='BUDGET')
    return real, budget

try:
    # Usar la función con caché
    real_df, budget_df = cargar_datos()

    # Agrupar datos por MES y GASTO
    real_grouped = real_df.groupby(['MES', 'GASTO'])['IMPORTE'].sum().reset_index()
    budget_grouped = budget_df.groupby(['MES', 'GASTO'])['IMPORTE'].sum().reset_index()

    # Unir y calcular variaciones
    variaciones = pd.merge(
        real_grouped,
        budget_grouped,
        on=['MES', 'GASTO'],
        how='outer',
        suffixes=('_REAL', '_BUDGET')
    ).fillna(0)

    variaciones['VARIACION_ABS'] = variaciones['IMPORTE_REAL'] - variaciones['IMPORTE_BUDGET']
    variaciones['VARIACION_%'] = (variaciones['VARIACION_ABS'] /
                                  variaciones['IMPORTE_BUDGET'].replace(0, pd.NA)) * 100

    # Selector por mes
    meses = sorted(variaciones['MES'].unique())
    mes_seleccionado = st.selectbox("📅 Selecciona un mes para ver sus variaciones:", meses)

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

    st.subheader(f"📊 Variaciones del mes: {mes_seleccionado}")
    st.dataframe(styled_df, use_container_width=True)

    st.success("✅ Análisis generado exitosamente.")

except Exception as e:
    st.error(f"❌ Error al procesar el archivo: {e}")
