import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Plataforma EcoBusCABA - Centro de Control",
    page_icon="🚌",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS (Alineado a la marca EcoBusCABA) ---
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1E5631; margin-bottom:5px; }
    .subtitle { font-size:16px; color:#555; margin-bottom:25px; }
    .metric-box { background-color:#f8f9fa; padding:15px; border-radius:10px; border-left:5px solid #1E5631; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.markdown('<div class="main-title">Plataforma EcoBusCABA 🚌☀️</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Escenario 3: Monitoreo Energético Unificado (EV + Solar) — Centro de Control Operacional (CCO)</div>', unsafe_allow_html=True)

# --- SIDEBAR: CONTROL DE LA SIMULACIÓN ---
st.sidebar.header("⚙️ Configuración del Piloto")
selected_bus = st.sidebar.selectbox("Seleccionar Colectivo", ["Interno 101 (Agrale EV)", "Interno 102 (BYD)", "Interno 103 (Mercedes EV)"])
clima = st.sidebar.select_slider("Condición Climática (Impacto Solar/HVAC)", options=["Despejado / Calor Extremo", "Soleado / Templado", "Nublado / Lluvia"])

# Simulación de estados base según el clima
hvac_base = 4.5 if "Calor Extremo" in clima else (2.0 if "Templado" in clima else 1.0)
solar_base = 350 if "Despejado" in clima else (200 if "Soleado" in clima else 30)

# --- CAPA 1 & 2: SIMULACIÓN DE DATOS (EDGE & CLOUD) ---
# Generamos datos telemáticos simulados en tiempo real
np.random.seed(int(time.time()) % 1000)
soc = np.random.uniform(62.0, 68.0)
temp_bat = np.random.uniform(34.0, 39.0) if "Calor" in clima else np.random.uniform(25.0, 29.0)
solar_gen = np.random.uniform(solar_base - 20, solar_base + 20)
consumo_motor = np.random.uniform(1.1, 1.4) # kWh/km

# Algoritmo Predictivo HVAC (Requisito Especial del TP)
consumo_hvac = np.random.uniform(hvac_base - 0.3, hvac_base + 0.3) # kW
mitigacion_solar_pct = min(100.0, (solar_gen / 1000 / (consumo_hvac + 0.1)) * 100)
autonomia_estimada = max(10, int((soc * 3.2) - (consumo_hvac * 4)))

# --- CAPA 3: VISUALIZACIÓN (CCO) ---

# 1. Alertas Operacionales (Semaforización)
if temp_bat > 38.0:
    st.error(f"⚠️ ALERTA TÉRMICA: Alta temperatura en Batería Principal del {selected_bus}: {temp_bat:.1f}°C. Módulo HVAC optimizando refrigeración.")
elif soc < 20:
    st.warning("⚠️ ALERTA DE AUTONOMÍA: Batería principal por debajo del 20%. Notificando a Despacho.")
else:
    st.success("✅ Estado de Flota: Operando de manera óptima. Conectividad Edge-Cloud TLS 1.3 Activa (Latencia < 2s).")

st.write("---")

# 2. Fila de Métricas Críticas (KPIs Funcionales del Project Charter)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("⚡🔋 Tren Motriz")
    st.metric(label="Estado de Carga (SoC)", value=f"{soc:.1f} %", delta="-1.2 % (Última hora)")
    st.caption(f"Temp. Batería: {temp_bat:.1f} °C")

with col2:
    st.subheader("☀️ Generación Solar")
    st.metric(label="Potencia Instantánea", value=f"{solar_gen:.0f} W/m²")
    st.caption("Aporte a Sistemas Auxiliares (SUBE/Cámaras)")

with col3:
    st.subheader("❄️ Módulo Predictivo HVAC")
    st.metric(label="Consumo Aire Acond.", value=f"{consumo_hvac:.2f} kW")
    st.caption(f"Mitigación Solar del HVAC: {mitigacion_solar_pct:.1f} %")

with col4:
    st.subheader("📍 Autonomía Real")
    st.metric(label="Proyección en Ruta", value=f"{autonomia_estimada} km")
    st.caption(f"Consumo promedio: {consumo_motor:.2f} kWh/km")

st.write("---")

# 3. Gráficos en Tiempo Real (Simulación de Historial de Ruta)
st.subheader("📈 Monitoreo Energético Dual Desacoplado (Últimos 15 min)")

# Crear datos históricos falsos dinámicos
times = pd.date_range(end=datetime.now(), periods=15, freq='min')
hist_soc = np.linspace(soc+3, soc, 15)
hist_solar = np.random.uniform(solar_base - 40, solar_base + 40, 15)
hist_hvac = np.random.uniform(consumo_hvac - 0.2, consumo_hvac + 0.2, 15)

df_historico = pd.DataFrame({
    'Tiempo': times,
    'Batería (%)': hist_soc,
    'Generación Solar (W)': hist_solar,
    'Consumo HVAC (kW)': hist_hvac
})

g1, g2 = st.columns(2)

with g1:
    fig_bat = go.Figure()
    fig_bat.add_trace(go.Scatter(x=df_historico['Tiempo'], y=df_historico['Batería (%)'], mode='lines+markers', name='SoC (%)', line=dict(color='#1E5631', width=3)))
    fig_bat.update_layout(title="Curva de Descarga - Batería de Tracción", xaxis_title="Tiempo", yaxis_title="Porcentaje (%)", template="plotly_white")
    st.plotly_chart(fig_bat, use_container_width=True)

with g2:
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Scatter(x=df_historico['Tiempo'], y=df_historico['Generación Solar (W)'], mode='lines', name='Gen. Solar (W)', line=dict(color='#FFD700')))
    fig_dual.add_trace(go.Scatter(x=df_historico['Tiempo'], y=df_historico['Consumo HVAC (kW)'] * 100, mode='lines', name='Consumo HVAC (kW x100)', line=dict(color='#00BFFF', dash='dash')))
    fig_dual.update_layout(title="Interacción Energía Solar vs Carga Auxiliar HVAC", xaxis_title="Tiempo", yaxis_title="Escala Normalizada", template="plotly_white")
    st.plotly_chart(fig_dual, use_container_width=True)

st.write("---")

# 4. Cumplimiento Regulatorio e Impacto Ambiental (API Abierta GCBA)
st.subheader("🌱 Reporte de Cumplimiento Regulatorio (Resolución 111/SECT/25)")
c_api1, c_api2, c_api3 = st.columns(3)

with c_api1:
    st.info("**API REST Abierta (GCBA)**\n\nEstado: Homologada ✅\n\nFormato: GTFS-RT / OCPP v2.0.1\n\nSincronización: Automática cada 5s.")
with c_api2:
    co2_evitado = (solar_gen * 0.0004) + 12.4 # Simulación acumulada
    st.metric(label="CO₂ Evitado Hoy (Total Flota)", value=f"{co2_evitado:.2f} kg", delta="Mitigación de Huella Activa")
with c_api3:
    st.metric(label="Eficiencia Energética Auxiliar", value="10.0 %", delta="Cumple Objetivo SMART 4")
    st.caption("6.2% Aporte Solar + 3.8% Optimización Algorítmica HVAC")

# Botón para refrescar/simular nueva trama IoT
if st.button("🔄 Capturar nueva trama de datos (CAN-Bus Edge)"):
    st.rerun()

